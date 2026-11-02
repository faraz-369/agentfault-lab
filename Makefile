.PHONY: install test benchmark api format-check clean

install:
	python -m pip install -e ".[dev]"

test:
	pytest

benchmark:
	python benchmarks/run_benchmark.py

api:
	uvicorn agentfault.api.app:app --host 127.0.0.1 --port 8000

format-check:
	ruff check src tests benchmarks examples

clean:
	rm -rf .pytest_cache .ruff_cache build dist *.egg-info
