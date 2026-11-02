from pathlib import Path
from agentfault.runner.engine import run_scenario
from agentfault.scenarios import load_scenarios

ROOT = Path(__file__).resolve().parents[2]


def test_all_scenarios_respect_tool_call_budget():
    scenarios = load_scenarios(ROOT / "scenarios")
    for scenario in scenarios.values():
        result = run_scenario(scenario, "state_aware")
        assert result.tool_calls <= scenario.max_tool_calls
        assert result.event_count >= 2
