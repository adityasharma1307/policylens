.PHONY: ingest clean warehouse lineage analysis dashboard lint typecheck test

ingest:
	python -m civiclens.ingest.run

clean:
	python -m civiclens.transform.run

warehouse:
	python -m civiclens.warehouse.run

lineage:
	python -m civiclens.lineage.graph

analysis:
	python -m civiclens.analysis.run

dashboard:
	streamlit run dashboard/app.py

lint:
	ruff check .

typecheck:
	mypy src

test:
	pytest
