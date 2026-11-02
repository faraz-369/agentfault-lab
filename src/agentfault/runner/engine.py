from __future__ import annotations

import copy
import time
from typing import Any
from uuid import uuid4

from agentfault.faults.injector import FaultInjector, InjectedFault
from agentfault.invariants.checker import check_invariants
from agentfault.models import EventType, RunResult, ScenarioSpec
from agentfault.recorder.recorder import EventRecorder
from agentfault.recovery.policies import get_policy


class ToolExecutionError(RuntimeError):
    pass


def _execute_tool(
    tool_name: str,
    args: dict[str, Any],
    state: dict[str, Any],
    fault_injector: FaultInjector,
) -> dict[str, Any]:
    fault_injector.before_call(tool_name)

    if tool_name == "validate_order":
        order_id = args.get("order_id", "order-1")
        state.setdefault("validated_orders", [])
        if order_id not in state["validated_orders"]:
            state["validated_orders"].append(order_id)
        result = {"order_id": order_id, "valid": True}
    elif tool_name == "update_order_status":
        order_id = args.get("order_id", "order-1")
        status = args.get("status", "processed")
        state.setdefault("orders", {})
        state["orders"].setdefault(order_id, {"status": "new", "updates": 0})
        state["orders"][order_id]["status"] = status
        state["orders"][order_id]["updates"] += 1
        result = {"order_id": order_id, "status": status, "updates": state["orders"][order_id]["updates"]}
    elif tool_name == "send_notification":
        operation_id = args.get("operation_id", "notification-1")
        state.setdefault("notifications", [])
        state["notifications"].append(operation_id)
        result = {"operation_id": operation_id, "sent": True}
    elif tool_name == "read_file":
        path = args.get("path", "input.txt")
        result = {"path": path, "content": state.get("files", {}).get(path, "sample content")}
    elif tool_name == "transform_data":
        payload = args.get("payload", {})
        result = {"transformed": True, "payload": payload}
    elif tool_name == "mark_complete":
        state["completed"] = True
        result = {"completed": True}
    else:
        raise ToolExecutionError(f"Unknown tool: {tool_name}")

    return fault_injector.transform_result(tool_name, result)


def _check_tool_result(tool_name: str, result: Any) -> None:
    if isinstance(result, dict) and result.get("_malformed"):
        raise ToolExecutionError(f"Malformed response from {tool_name}")


def run_scenario(
    scenario: ScenarioSpec,
    policy_name: str = "none",
    *,
    seed: int = 7,
) -> RunResult:
    """Run a scenario in a local deterministic simulator."""
    policy = get_policy(policy_name)
    run_id = str(uuid4())
    recorder = EventRecorder(run_id)
    injector = FaultInjector(scenario.fault)
    state = copy.deepcopy(scenario.initial_state)
    actions = state.pop("actions", [])
    # Keep state clean: action plan is configuration, not runtime state.
    state.setdefault("operation_history", [])
    start = time.perf_counter()
    retries = 0
    tool_calls = 0
    error: str | None = None
    success = False
    step = 0

    recorder.emit(EventType.RUN_STARTED, details={
        "scenario_id": scenario.scenario_id, "policy": policy_name, "seed": seed
    })

    for action_index, action in enumerate(actions):
        if step >= scenario.max_steps:
            error = "max_steps_exceeded"
            break
        step += 1
        tool_name = action.get("tool", "")
        args = copy.deepcopy(action.get("args", {}))
        recorder.emit(EventType.STEP_STARTED, step=step, name=tool_name, details={"action_index": action_index})

        attempt = 0
        while True:
            if tool_calls >= scenario.max_tool_calls:
                error = "max_tool_calls_exceeded"
                break
            tool_calls += 1
            recorder.emit(EventType.TOOL_CALL, step=step, name=tool_name, details={"args": args, "attempt": attempt + 1})
            result: Any = None
            try:
                before_state = copy.deepcopy(state)
                result = _execute_tool(tool_name, args, state, injector)
                if state != before_state and tool_name in {"update_order_status", "send_notification", "mark_complete"}:
                    operation_id = args.get("operation_id") or f"{tool_name}:{args.get('order_id', 'default')}"
                    recorder.emit(EventType.STATE_CHANGED, step=step, name=tool_name, details={
                        "operation_id": operation_id,
                        "attempt": attempt + 1,
                        "state_snapshot": copy.deepcopy(state),
                    })
                _check_tool_result(tool_name, result)
                recorder.emit(EventType.TOOL_RESULT, step=step, name=tool_name, details={
                    "result": result,
                    "malformed_used": False,
                    "attempt": attempt + 1,
                })
                break
            except InjectedFault as exc:
                recorder.emit(EventType.FAULT_INJECTED, step=step, name=tool_name, details={
                    "kind": exc.kind, "message": str(exc), "attempt": attempt + 1
                })
                recorder.emit(EventType.TOOL_ERROR, step=step, name=tool_name, details={
                    "error": str(exc), "kind": exc.kind, "attempt": attempt + 1
                })
                if attempt < policy.max_retries:
                    attempt += 1
                    retries += 1
                    recorder.emit(EventType.RECOVERY, step=step, name=policy_name, details={
                        "action": "retry", "attempt": attempt, "state_aware": policy.state_aware
                    })
                    # For state-aware policy, avoid replaying a state-changing operation
                    # if the operation's effect is already visible in state.
                    if policy.state_aware and tool_name == "update_order_status":
                        order_id = args.get("order_id", "order-1")
                        order = state.get("orders", {}).get(order_id, {})
                        if order.get("status") == args.get("status") and order.get("updates", 0) > 0:
                            result = {"order_id": order_id, "status": order["status"], "resumed": True}
                            recorder.emit(EventType.TOOL_RESULT, step=step, name=tool_name, details={
                                "result": result, "resumed_from_state": True, "attempt": attempt + 1
                            })
                            break
                    continue
                error = f"{exc.kind}: {exc}"
                break
            except ToolExecutionError as exc:
                # Preserve rejected payloads in the trace for debugging without treating
                # them as accepted tool outputs. This makes malformed-output checks auditable.
                if isinstance(result, dict) and result.get("_malformed"):
                    recorder.emit(EventType.TOOL_RESULT, step=step, name=tool_name, details={
                        "result": result,
                        "malformed": True,
                        "malformed_used": False,
                        "accepted": False,
                        "attempt": attempt + 1,
                    })
                recorder.emit(EventType.TOOL_ERROR, step=step, name=tool_name, details={
                    "error": str(exc), "kind": "tool_execution_error", "attempt": attempt + 1
                })
                if attempt < policy.max_retries:
                    attempt += 1
                    retries += 1
                    recorder.emit(EventType.RECOVERY, step=step, name=policy_name, details={
                        "action": "retry", "attempt": attempt, "state_aware": policy.state_aware
                    })
                    if policy.state_aware and tool_name == "update_order_status":
                        order_id = args.get("order_id", "order-1")
                        order = state.get("orders", {}).get(order_id, {})
                        if order.get("status") == args.get("status") and order.get("updates", 0) > 0:
                            result = {"order_id": order_id, "status": order["status"], "resumed": True}
                            recorder.emit(EventType.TOOL_RESULT, step=step, name=tool_name, details={
                                "result": result, "resumed_from_state": True, "attempt": attempt + 1
                            })
                            break
                    continue
                error = str(exc)
                break

        if error:
            break

    # Task-specific success contract: all configured actions completed without errors,
    # and a required final state (if configured) is satisfied.
    required = scenario.initial_state.get("expected_final_state", {})
    final_state = copy.deepcopy(state)
    success = error is None and step == len(actions) and all(
        final_state.get(key) == value for key, value in required.items()
    )
    recorder.emit(EventType.RUN_FINISHED, step=step, details={
        "success": success, "error": error, "final_state": final_state
    })
    violations = check_invariants(scenario.invariants, recorder.events, final_state)
    first_sequence = min(
        (v.get("sequence") for v in violations if isinstance(v.get("sequence"), int)),
        default=None,
    )
    duration_ms = (time.perf_counter() - start) * 1000
    return RunResult(
        run_id=run_id,
        scenario_id=scenario.scenario_id,
        policy=policy_name,
        success=success,
        final_state=final_state,
        event_count=len(recorder.events),
        tool_calls=tool_calls,
        retries=retries,
        invariant_violations=violations,
        first_violation_sequence=first_sequence,
        fault_injected=injector.injected,
        error=error,
        duration_ms=duration_ms,
        events=recorder.events,
    )
