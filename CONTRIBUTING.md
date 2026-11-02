# Contributing

Thanks for considering a contribution to AgentFault Lab. The project is an experimental
reliability harness; changes should preserve deterministic reproduction and make their
assumptions explicit.

## Development setup

```bash
python -m venv .venv
# Activate the environment, then:
python -m pip install -e ".[dev]"
pytest
```

## Adding a scenario

1. Add a JSON file under the appropriate `scenarios/` subdirectory.
2. Give it a unique `scenario_id`, a short task description, initial state, and a bounded
   action sequence.
3. Specify the fault and invariants explicitly.
4. Add a regression test proving the expected failure or recovery behavior.
5. Run `python benchmarks/run_benchmark.py` and inspect the generated trace if the change
   affects runner behavior.

## Pull request expectations

- Add or update automated tests for behavior changes.
- Keep runs reproducible; use seeded randomness if stochastic behavior is introduced.
- Document new fault types, invariants, policies, and limitations.
- Do not add paid APIs or require credentials for the core test suite.
- Do not describe simulator measurements as production reliability results.
