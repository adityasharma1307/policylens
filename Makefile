.PHONY: all ingest clean warehouse lineage analysis dashboard brief lint typecheck test

all: ingest clean warehouse analysis brief

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

brief:
	python -m civiclens.report.render_brief

lint:
	ruff check .

typecheck:
	mypy src

test:
	pytest
