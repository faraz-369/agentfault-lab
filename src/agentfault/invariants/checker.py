from __future__ import annotations

from typing import Any

from agentfault.models import ExecutionEvent, EventType, InvariantSpec


def check_invariants(
    invariants: list[InvariantSpec],
    events: list[ExecutionEvent],
    final_state: dict[str, Any],
) -> list[dict[str, Any]]:
    """Evaluate deterministic invariants against events and final state.

    Supported kinds:
      - required_final_state: params.field equals params.equals
      - unique_operation: each state-changing operation id occurs at most once
      - no_false_completion: completion event requires params.required_state_field == value
      - no_malformed_result_used: malformed tool outputs must not be marked consumed
    """
    violations: list[dict[str, Any]] = []
    for invariant in invariants:
        params = invariant.params
        if invariant.kind == "required_final_state":
            field = params.get("field")
            expected = params.get("equals")
            if final_state.get(field) != expected:
                violations.append({
                    "invariant_id": invariant.invariant_id,
                    "description": invariant.description,
                    "kind": invariant.kind,
                    "sequence": events[-1].sequence if events else None,
                    "observed": final_state.get(field),
                    "expected": expected,
                })
        elif invariant.kind == "unique_operation":
            seen: set[str] = set()
            for event in events:
                if event.event_type == EventType.STATE_CHANGED:
                    operation_id = event.details.get("operation_id")
                    if operation_id is None:
                        continue
                    if operation_id in seen:
                        violations.append({
                            "invariant_id": invariant.invariant_id,
                            "description": invariant.description,
                            "kind": invariant.kind,
                            "sequence": event.sequence,
                            "operation_id": operation_id,
                        })
                        break
                    seen.add(operation_id)
        elif invariant.kind == "no_false_completion":
            field = params.get("required_state_field")
            expected = params.get("equals")
            for event in events:
                if event.event_type == EventType.RUN_FINISHED and event.details.get("success"):
                    if final_state.get(field) != expected:
                        violations.append({
                            "invariant_id": invariant.invariant_id,
                            "description": invariant.description,
                            "kind": invariant.kind,
                            "sequence": event.sequence,
                            "observed": final_state.get(field),
                            "expected": expected,
                        })
                        break
        elif invariant.kind == "no_malformed_result_used":
            for event in events:
                if event.event_type == EventType.TOOL_RESULT and event.details.get("malformed_used"):
                    violations.append({
                        "invariant_id": invariant.invariant_id,
                        "description": invariant.description,
                        "kind": invariant.kind,
                        "sequence": event.sequence,
                    })
                    break
        else:
            violations.append({
                "invariant_id": invariant.invariant_id,
                "description": invariant.description,
                "kind": invariant.kind,
                "error": "unsupported_invariant_kind",
            })
    return violations
