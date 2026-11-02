from pathlib import Path
import json

from agentfault.models import ScenarioSpec


def load_scenario(path: str | Path) -> ScenarioSpec:
    return ScenarioSpec.model_validate_json(Path(path).read_text(encoding="utf-8"))


def load_scenarios(directory: str | Path) -> dict[str, ScenarioSpec]:
    scenarios = {}
    for path in sorted(Path(directory).rglob("*.json")):
        scenario = load_scenario(path)
        scenarios[scenario.scenario_id] = scenario
    return scenarios
