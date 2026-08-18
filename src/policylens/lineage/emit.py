import uuid
from datetime import UTC, datetime
from typing import TypeVar

from openlineage.client import OpenLineageClient
from openlineage.client.event_v2 import (
    Dataset,
    InputDataset,
    Job,
    OutputDataset,
    Run,
    RunEvent,
    RunState,
)
from openlineage.client.facet_v2 import schema_dataset
from openlineage.client.transport.file import FileConfig, FileTransport

from policylens.config import INTERIM_DIR

NAMESPACE = "policylens"
LINEAGE_LOG_PATH = INTERIM_DIR / "lineage_events.jsonl"


def _client() -> OpenLineageClient:
    INTERIM_DIR.mkdir(parents=True, exist_ok=True)
    transport = FileTransport(FileConfig(log_file_path=str(LINEAGE_LOG_PATH), append=True))
    return OpenLineageClient(transport=transport)


DatasetT = TypeVar("DatasetT", bound=Dataset)


def _with_schema(name: str, columns: dict[str, str], cls: type[DatasetT]) -> DatasetT:
    fields = [schema_dataset.SchemaDatasetFacetFields(name=n, type=t) for n, t in columns.items()]
    facet = schema_dataset.SchemaDatasetFacet(fields=fields)
    return cls(namespace=NAMESPACE, name=name, facets={"schema": facet})


def emit_job(
    job_name: str,
    inputs: dict[str, dict[str, str]],
    outputs: dict[str, dict[str, str]],
) -> None:
    """Emit a START+COMPLETE OpenLineage run event for one pipeline stage.

    inputs/outputs map dataset name -> {column_name: column_type}, giving column-level
    lineage for each stage. Events are appended as JSON Lines to
    data/interim/lineage_events.jsonl (no Marquez/backend server required).
    """
    client = _client()
    run = Run(runId=str(uuid.uuid4()))
    job = Job(namespace=NAMESPACE, name=job_name)
    now = datetime.now(UTC).isoformat()

    input_datasets = [_with_schema(n, cols, InputDataset) for n, cols in inputs.items()]
    output_datasets = [_with_schema(n, cols, OutputDataset) for n, cols in outputs.items()]

    for state in (RunState.START, RunState.COMPLETE):
        client.emit(
            RunEvent(
                eventType=state,
                eventTime=now,
                producer="policylens",
                run=run,
                job=job,
                inputs=input_datasets,
                outputs=output_datasets,
            )
        )
