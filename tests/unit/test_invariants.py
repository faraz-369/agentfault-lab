from agentfault.invariants.checker import check_invariants
from agentfault.models import EventType, ExecutionEvent, InvariantSpec


def test_required_final_state_violation():
    invariant = InvariantSpec(
        invariant_id="done", description="must complete",
        kind="required_final_state", params={"field": "completed", "equals": True}
    )
    events = [ExecutionEvent(run_id="r1", sequence=1, event_type=EventType.RUN_FINISHED)]
    result = check_invariants([invariant], events, {"completed": False})
    assert len(result) == 1
    assert result[0]["invariant_id"] == "done"


def test_unique_operation_detects_duplicate():
    invariant = InvariantSpec(
        invariant_id="unique", description="unique ids", kind="unique_operation"
    )
    events = [
        ExecutionEvent(run_id="r", sequence=1, event_type=EventType.STATE_CHANGED,
                       details={"operation_id": "op-1"}),
        ExecutionEvent(run_id="r", sequence=2, event_type=EventType.STATE_CHANGED,
                       details={"operation_id": "op-1"}),
    ]
    assert check_invariants([invariant], events, {})[0]["kind"] == "unique_operation"


def test_no_malformed_result_used_allows_rejected_payload():
    invariant = InvariantSpec(
        invariant_id="no-malformed-use",
        description="Rejected malformed output must not be consumed",
        kind="no_malformed_result_used",
    )
    event = ExecutionEvent(
        run_id="r1",
        sequence=1,
        event_type=EventType.TOOL_RESULT,
        details={"malformed": True, "malformed_used": False, "accepted": False},
    )
    assert check_invariants([invariant], [event], {}) == []


def test_wilson_interval_is_bounded():
    from agentfault.evaluation.metrics import wilson_score_interval

    lower, upper = wilson_score_interval(8, 10)
    assert 0 <= lower <= 0.8 <= upper <= 1
