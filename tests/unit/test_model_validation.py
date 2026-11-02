import pytest
from pydantic import ValidationError

from agentfault.models import ScenarioSpec


def test_scenario_rejects_non_positive_execution_budgets():
    with pytest.raises(ValidationError):
        ScenarioSpec(
            scenario_id="invalid",
            name="invalid",
            task="test",
            max_steps=0,
        )
