from __future__ import annotations

from collections import defaultdict
from typing import Any

from agentfault.models import FaultSpec


class InjectedFault(RuntimeError):
    def __init__(self, kind: str, message: str):
        super().__init__(message)
        self.kind = kind


class FaultInjector:
    """Deterministic, call-count-based fault injector."""

    SUPPORTED = {"timeout", "exception", "malformed", "repeat_response"}

    def __init__(self, spec: FaultSpec | None):
        self.spec = spec
        self.calls: dict[str, int] = defaultdict(int)
        self.injected = False

    def before_call(self, tool_name: str) -> None:
        self.calls[tool_name] += 1
        spec = self.spec
        if not spec or spec.tool_name != tool_name:
            return
        if spec.kind not in self.SUPPORTED:
            raise ValueError(f"Unsupported fault kind: {spec.kind}")
        should_trigger = self.calls[tool_name] == spec.trigger_call_number
        if spec.repeat and self.calls[tool_name] >= spec.trigger_call_number:
            should_trigger = True
        if should_trigger:
            self.injected = True
            if spec.kind in {"timeout", "exception"}:
                raise InjectedFault(spec.kind, spec.message)

    def transform_result(self, tool_name: str, result: Any) -> Any:
        spec = self.spec
        if not spec or spec.tool_name != tool_name:
            return result
        if not self.injected:
            return result
        if spec.kind == "malformed" and self.calls[tool_name] == spec.trigger_call_number:
            return {"_malformed": True, "unexpected": spec.message}
        if spec.kind == "repeat_response" and self.calls[tool_name] == spec.trigger_call_number:
            return {"_repeated_response": True, "original": result}
        return result
