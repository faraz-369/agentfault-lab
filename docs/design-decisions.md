# Design decisions

## Python package before dashboard

The package and CLI are the primary interface. A dashboard would consume time without strengthening the initial experimental contribution.

## Deterministic simulator first

The core benchmark avoids model/API dependence so that infrastructure bugs can be separated from model variability. A local LLM adapter is a later extension.

## Explicit invariant contracts

Where possible, evaluation uses deterministic contracts such as state conditions and unique operation identifiers. This is more reproducible than using an LLM judge for the initial tests.

## JSONL plus SQLite

JSONL is portable and easy to inspect. SQLite supports querying run summaries and event metadata without an external database server.

## Small recovery-policy surface

The initial policies are deliberately limited to no recovery, bounded retry, and state-aware recovery. Additional policies should be added only when a benchmark scenario can distinguish them meaningfully.

## No arbitrary code execution

The first version only executes the simulator's allowlisted tools. Running arbitrary user code would require a separate security architecture.
