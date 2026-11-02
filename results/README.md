# Sample benchmark output

The JSON and JSONL files in this directory are a checked-in example of the default
benchmark configuration in `benchmarks/configs/default.json`.

Reproduce them from the repository root with:

```bash
python benchmarks/run_benchmark.py
```

The run set contains 3 hand-authored scenarios × 3 recovery policies × 5 trials = 45
runs. The simulator is deterministic, so repeating a scenario does not provide
independent evidence about stochastic LLM agents. The output is a reproducibility
artifact for this prototype, not a production reliability claim. Wall-clock timing
fields can vary between machines.
