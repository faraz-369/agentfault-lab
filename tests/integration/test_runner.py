from pathlib import Path

from agentfault.runner.engine import run_scenario
from agentfault.scenarios import load_scenarios

ROOT = Path(__file__).resolve().parents[2]


def test_state_aware_recovery_avoids_duplicate_order_update():
    scenarios = load_scenarios(ROOT / "scenarios")
    scenario = scenarios["order_malformed_response"]
    retry = run_scenario(scenario, "retry")
    state_aware = run_scenario(scenario, "state_aware")

    assert retry.fault_injected
    assert state_aware.fault_injected
    assert retry.final_state["orders"]["order-1"]["updates"] == 2
    assert state_aware.final_state["orders"]["order-1"]["updates"] == 1
    assert any(v["invariant_id"] == "unique-state-operation" for v in retry.invariant_violations)
    assert not any(v["invariant_id"] == "unique-state-operation" for v in state_aware.invariant_violations)
    assert state_aware.success


def test_no_recovery_fails_on_timeout():
    scenarios = load_scenarios(ROOT / "scenarios")
    result = run_scenario(scenarios["notification_timeout"], "none")
    assert not result.success
    assert result.fault_injected
    assert result.error is not None


def test_retry_recovers_transient_timeout():
    scenarios = load_scenarios(ROOT / "scenarios")
    result = run_scenario(scenarios["notification_timeout"], "retry")
    assert result.success
    assert result.retries == 1
    assert result.final_state["notifications"] == ["notification-42"]


def test_rejected_malformed_result_is_recorded_but_not_used():
    from agentfault.models import EventType

    scenarios = load_scenarios(ROOT / "scenarios")
    result = run_scenario(scenarios["malformed_transform"], "none")
    rejected = [
        event for event in result.events
        if event.event_type == EventType.TOOL_RESULT and event.details.get("malformed")
    ]
    assert len(rejected) == 1
    assert rejected[0].details["accepted"] is False
    assert rejected[0].details["malformed_used"] is False
