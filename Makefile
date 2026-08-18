.PHONY: ingest clean warehouse lineage lint typecheck test

ingest:
	python -m civiclens.ingest.run

clean:
	python -m civiclens.transform.run

warehouse:
	python -m civiclens.warehouse.run

lineage:
	python -m civiclens.lineage.graph

lint:
	ruff check .

typecheck:
	mypy src

test:
	pytest
