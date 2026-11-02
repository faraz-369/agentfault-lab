from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field, ConfigDict


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class EventType(str, Enum):
    RUN_STARTED = "run_started"
    STEP_STARTED = "step_started"
    TOOL_CALL = "tool_call"
    TOOL_RESULT = "tool_result"
    TOOL_ERROR = "tool_error"
    FAULT_INJECTED = "fault_injected"
    STATE_CHANGED = "state_changed"
    INVARIANT_VIOLATION = "invariant_violation"
    RECOVERY = "recovery"
    RUN_FINISHED = "run_finished"


class ExecutionEvent(BaseModel):
    model_config = ConfigDict(extra="forbid")

    event_id: str = Field(default_factory=lambda: str(uuid4()))
    run_id: str
    sequence: int
    timestamp: datetime = Field(default_factory=utc_now)
    event_type: EventType
    step: int = 0
    name: str = ""
    details: dict[str, Any] = Field(default_factory=dict)


class FaultSpec(BaseModel):
    fault_id: str
    kind: str
    tool_name: str
    trigger_call_number: int = Field(default=1, ge=1)
    message: str = "Injected fault"
    repeat: bool = False


class InvariantSpec(BaseModel):
    invariant_id: str
    description: str
    kind: str
    params: dict[str, Any] = Field(default_factory=dict)


class ScenarioSpec(BaseModel):
    scenario_id: str
    name: str
    description: str = ""
    initial_state: dict[str, Any] = Field(default_factory=dict)
    task: str
    fault: FaultSpec | None = None
    invariants: list[InvariantSpec] = Field(default_factory=list)
    max_steps: int = Field(default=20, ge=1)
    max_tool_calls: int = Field(default=50, ge=1)
    tags: list[str] = Field(default_factory=list)


class RunResult(BaseModel):
    run_id: str
    scenario_id: str
    policy: str
    success: bool
    final_state: dict[str, Any]
    event_count: int
    tool_calls: int
    retries: int
    invariant_violations: list[dict[str, Any]]
    first_violation_sequence: int | None = None
    fault_injected: bool = False
    error: str | None = None
    duration_ms: float
    events: list[ExecutionEvent] = Field(default_factory=list)


class ExperimentConfig(BaseModel):
    experiment_id: str = Field(default_factory=lambda: str(uuid4()))
    scenario_ids: list[str]
    policies: list[str] = Field(default_factory=lambda: ["none", "retry", "state_aware"])
    trials: int = Field(default=1, ge=1)
    seed: int = 7
    output_dir: str = "results"
