from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RecoveryPolicy:
    name: str
    max_retries: int
    state_aware: bool = False


POLICIES = {
    "none": RecoveryPolicy("none", max_retries=0),
    "retry": RecoveryPolicy("retry", max_retries=2),
    "state_aware": RecoveryPolicy("state_aware", max_retries=2, state_aware=True),
}


def get_policy(name: str) -> RecoveryPolicy:
    try:
        return POLICIES[name]
    except KeyError as exc:
        raise ValueError(f"Unknown policy '{name}'. Choose from {', '.join(POLICIES)}") from exc
