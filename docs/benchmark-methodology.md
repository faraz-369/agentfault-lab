# Benchmark methodology

## Purpose

Evaluate the local simulator's ability to reproduce configured faults, record execution, detect explicitly defined invariant violations, and compare simple recovery policies.

## Included scenarios

1. `order_malformed_response`: a status update takes effect but returns malformed output.
2. `notification_timeout`: the first notification call fails before executing.
3. `malformed_transform`: a transformation response is malformed.

## Policies

- `none`: do not retry.
- `retry`: retry tool errors up to two times.
- `state_aware`: before retrying a supported order update, inspect state and resume if the intended status is already visible; other errors use bounded retries.

## Metrics

The report includes run count, task success rate, fault injection rate, invariant violation rate, mean tool calls, mean retries, median local duration, and total invariant violations.

## Limitations

- The scenario suite is small and hand-authored.
- The simulator's state transitions are simplified.
- Duration measurements are affected by machine load and are not production performance benchmarks.
- Repeated trials of deterministic scenarios do not create independent evidence about real-world stochastic agent behavior.
- The current report aggregates by policy, not by every scenario-policy pair.
- A detected invariant violation is not equivalent to a proven hidden causal explanation.

## Reproduction

From the repository root:

```bash
python -m pip install -e ".[dev]"
python benchmarks/run_benchmark.py
```

The default configuration is in `benchmarks/configs/default.json`. Generated results are written under `results/`.

## Baseline observation (default configuration)

A fresh run of the shipped 45-run configuration produced:

| Policy | Task successes | Success rate | Runs with invariant violations | Violation rate | Mean tool calls |
|---|---:|---:|---:|---:|---:|
| `none` | 0/15 | 0% | 0/15 | 0% | 1.67 |
| `retry` | 15/15 | 100% | 5/15 | 33.3% | 4.00 |
| `state_aware` | 15/15 | 100% | 0/15 | 0% | 3.67 |

Interpretation: in this hand-authored simulator suite, blind retry completes all tasks but duplicates the order update in the malformed-response scenario. State-aware recovery completes the same task set without that configured invariant violation. The `none` policy stops before the duplicated operation occurs, which is why its invariant-violation rate is zero despite its task-success rate being zero.

Task success and invariant correctness are intentionally separate metrics. A run can complete its task and still violate a safety invariant. These figures are deterministic outcomes of the supplied test cases, not estimates of real-world agent performance. The accompanying `results/agentfault-baseline-v1_summary.json` and `results/agentfault-baseline-v1_runs.jsonl` contain the generated report and run records.
