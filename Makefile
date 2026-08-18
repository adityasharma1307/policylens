.PHONY: all ingest clean warehouse lineage analysis dashboard brief lint typecheck test

all: ingest clean warehouse analysis brief

ingest:
	python -m policylens.ingest.run

clean:
	python -m policylens.transform.run

warehouse:
	python -m policylens.warehouse.run

lineage:
	python -m policylens.lineage.graph

analysis:
	python -m policylens.analysis.run

dashboard:
	streamlit run dashboard/app.py

brief:
	python -m policylens.report.render_brief

lint:
	ruff check .

typecheck:
	mypy src

test:
	pytest
