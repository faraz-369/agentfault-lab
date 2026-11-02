from __future__ import annotations

from collections import defaultdict
from statistics import median
from typing import Any

from agentfault.models import RunResult


def summarize_runs(results: list[RunResult]) -> dict[str, Any]:
    if not results:
        return {"runs": 0, "success_rate": 0.0, "invariant_violation_rate": 0.0}
    by_policy: dict[str, list[RunResult]] = defaultdict(list)
    for result in results:
        by_policy[result.policy].append(result)

    policy_summaries = {}
    for policy, rows in sorted(by_policy.items()):
        count = len(rows)
        policy_summaries[policy] = {
            "runs": count,
            "successes": sum(r.success for r in rows),
            "success_rate": sum(r.success for r in rows) / count,
            "fault_injection_rate": sum(r.fault_injected for r in rows) / count,
            "invariant_violation_rate": sum(bool(r.invariant_violations) for r in rows) / count,
            "mean_tool_calls": sum(r.tool_calls for r in rows) / count,
            "mean_retries": sum(r.retries for r in rows) / count,
            "median_duration_ms": median(r.duration_ms for r in rows),
            "total_invariant_violations": sum(len(r.invariant_violations) for r in rows),
        }
    return {"runs": len(results), "by_policy": policy_summaries}


def wilson_score_interval(successes: int, trials: int, z: float = 1.96) -> tuple[float, float]:
    """Return a Wilson score confidence interval for a binomial proportion."""
    if trials <= 0:
        return (0.0, 0.0)
    p = successes / trials
    denom = 1 + z * z / trials
    center = (p + z * z / (2 * trials)) / denom
    margin = z * ((p * (1 - p) / trials + z * z / (4 * trials * trials)) ** 0.5) / denom
    return (max(0.0, center - margin), min(1.0, center + margin))
