import json

from policylens.lineage.graph import _collapse_raw_inputs, build_mermaid, load_jobs


def test_collapse_raw_inputs_groups_zips():
    names = ["data/raw/19929- Dataful.zip", "data/raw/19930- Dataful.zip", "other.parquet"]
    result = _collapse_raw_inputs(names)
    assert "other.parquet" in result
    assert "data/raw/*.zip (2 commodity files)" in result
    assert len(result) == 2


def test_collapse_raw_inputs_no_zips_unchanged():
    names = ["a.parquet", "b.parquet"]
    assert _collapse_raw_inputs(names) == names


def test_build_mermaid_contains_flowchart_block():
    jobs = {"ingest": {"inputs": ["a.zip"], "outputs": ["b.parquet"]}}
    result = build_mermaid(jobs)
    assert result.startswith("```mermaid")
    assert result.endswith("```")
    assert "flowchart LR" in result
    assert "-->|ingest|" in result


def test_build_mermaid_creates_edge_per_input_output_pair():
    jobs = {"transform": {"inputs": ["x.parquet"], "outputs": ["y.parquet", "z.parquet"]}}
    result = build_mermaid(jobs)
    assert result.count("-->|transform|") == 2


def test_load_jobs_reads_only_complete_events(tmp_path, monkeypatch):
    log_path = tmp_path / "lineage_events.jsonl"
    start_event = {
        "eventType": "START",
        "job": {"name": "ingest"},
        "inputs": [{"name": "a.zip"}],
        "outputs": [{"name": "b.parquet"}],
    }
    complete_event = {
        "eventType": "COMPLETE",
        "job": {"name": "ingest"},
        "inputs": [{"name": "a.zip"}],
        "outputs": [{"name": "b.parquet"}],
    }
    log_path.write_text(json.dumps(start_event) + "\n" + json.dumps(complete_event) + "\n")

    import policylens.lineage.graph as graph_module

    monkeypatch.setattr(graph_module, "LINEAGE_LOG_PATH", log_path)
    jobs = load_jobs()
    assert jobs == {"ingest": {"inputs": ["a.zip"], "outputs": ["b.parquet"]}}
