from agentfault.store import SQLiteRunStore
from agentfault.models import RunResult


def test_sqlite_store_persists_run(tmp_path):
    store = SQLiteRunStore(tmp_path / "agentfault.db")
    result = RunResult(
        run_id="r1", scenario_id="s1", policy="none", success=True,
        final_state={}, event_count=0, tool_calls=0, retries=0,
        invariant_violations=[], duration_ms=1.0
    )
    store.save_results("e1", [result])
    assert store.count_runs("e1") == 1
