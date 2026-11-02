from __future__ import annotations

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from agentfault.experiment import run_experiment
from agentfault.models import ExperimentConfig
from agentfault.runner.engine import run_scenario
from agentfault.scenarios import load_scenarios

app = FastAPI(
    title="AgentFault Lab API",
    version="0.1.0",
    description="Local API for reproducible agent fault-injection experiments.",
)


class RunRequest(BaseModel):
    scenario_id: str
    policy: str = "none"
    seed: int = 7


class ExperimentRequest(BaseModel):
    scenario_ids: list[str]
    policies: list[str] = Field(default_factory=lambda: ["none", "retry", "state_aware"])
    trials: int = 1
    output_dir: str = "results"


@app.get("/health")
def health():
    return {"status": "ok", "service": "agentfault-lab"}


@app.get("/scenarios")
def list_scenarios():
    scenarios = load_scenarios("scenarios")
    return [
        {"scenario_id": s.scenario_id, "name": s.name, "description": s.description, "tags": s.tags}
        for s in scenarios.values()
    ]


@app.post("/runs")
def create_run(request: RunRequest):
    scenarios = load_scenarios("scenarios")
    scenario = scenarios.get(request.scenario_id)
    if scenario is None:
        raise HTTPException(status_code=404, detail="Scenario not found")
    try:
        result = run_scenario(scenario, request.policy, seed=request.seed)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return result.model_dump(exclude={"events"}) | {"events": [e.model_dump(mode="json") for e in result.events]}


@app.post("/experiments")
def create_experiment(request: ExperimentRequest):
    config = ExperimentConfig(
        scenario_ids=request.scenario_ids,
        policies=request.policies,
        trials=request.trials,
        output_dir=request.output_dir,
    )
    try:
        results, report = run_experiment(config, "scenarios", request.output_dir)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"report": report, "run_count": len(results)}
