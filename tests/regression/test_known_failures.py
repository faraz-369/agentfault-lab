from pathlib import Path
from agentfault.runner.engine import run_scenario
from agentfault.scenarios import load_scenarios

ROOT = Path(__file__).resolve().parents[2]


def test_malformed_update_regression_is_detected_for_blind_retry():
    scenarios = load_scenarios(ROOT / "scenarios")
    result = run_scenario(scenarios["order_malformed_response"], "retry")
    assert result.final_state["orders"]["order-1"]["updates"] == 2
    assert result.invariant_violations
