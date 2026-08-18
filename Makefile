.PHONY: ingest lint typecheck test

ingest:
	python -m civiclens.ingest.run

lint:
	ruff check .

typecheck:
	mypy src

test:
	pytest
