# Architecture

## Goals

- Local-first, zero-paid-service core.
- Deterministic fault injection.
- Observable execution state.
- Explicit invariants instead of opaque judge-only evaluation.
- Reproducible experiment outputs.
- Keep the simulator, recorder, analyzer, and API separate.

## Run lifecycle

1. Load and validate a `ScenarioSpec`.
2. Initialize a fresh run ID, state copy, event recorder, and fault injector.
3. Execute the scenario's ordered actions.
4. Record tool calls and state-changing events.
5. Inject the configured fault when the matching tool call count is reached.
6. Apply the selected bounded recovery policy.
7. Check invariants against the event trace and final state.
8. Persist run metadata, events, and aggregated report.

## State and event semantics

The simulator records state-changing events after the simulated operation mutates state. This matters for the malformed-response scenario: the operation may have taken effect even though the response is unusable. A retry may therefore duplicate the effect.

The `unique_operation` invariant compares operation identifiers in state-change events. It is a deliberately narrow invariant and should not be treated as a general transaction verifier.

## Storage

- SQLite: run metadata, serialized result, event metadata, and event details.
- JSONL: portable event traces and run summaries.
- JSON: experiment summary.

The SQLite database is a local artifact. It is not a multi-user service database and has not been optimized for high concurrency.

## Failure localization

The current analyzer reports the earliest event sequence attached to a detected invariant violation. It does not infer hidden model reasoning and does not claim causal root-cause analysis. More sophisticated diagnosis would require hypothesis testing or interventions.

## Boundaries

The current runner is a deterministic simulator, not an arbitrary code execution engine. An adapter for a real agent should use a controlled interface and preserve event semantics without pretending every framework exposes the same internal state.
