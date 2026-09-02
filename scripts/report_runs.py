#!/usr/bin/env python3

"""Idempotency tracking and manifest management for report run IDs."""

import json
import os
import tempfile
from pathlib import Path
from typing import Any, Dict, Optional


RUNS_STATE_PATH = Path("data/report_runs.json")


class ReportRunsError(RuntimeError):
    """Error managing report runs state."""


def load_report_runs(path: Path) -> Dict[str, Any]:
    path = Path(path)
    if not path.exists():
        return {"schema_version": 1, "runs": {}}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ReportRunsError(f"invalid report runs file {path}: {exc}") from exc
    if data.get("schema_version") != 1 or not isinstance(data.get("runs"), dict):
        raise ReportRunsError(f"unsupported report runs schema: {path}")
    return data


def is_run_id_processed(runs_data: Dict[str, Any], run_id: str) -> bool:
    if not run_id or not isinstance(run_id, str):
        return False
    runs = runs_data.get("runs", {})
    return run_id in runs


def get_run_record(runs_data: Dict[str, Any], run_id: str) -> Optional[Dict[str, Any]]:
    if not run_id or not isinstance(run_id, str):
        return None
    return runs_data.get("runs", {}).get(run_id)


def record_report_run(path: Path, run_record: Dict[str, Any]) -> Dict[str, Any]:
    path = Path(path)
    run_id = run_record.get("run_id")
    if not run_id or not isinstance(run_id, str):
        raise ReportRunsError("missing or invalid run_id in run_record")

    data = load_report_runs(path)
    runs = dict(data.get("runs", {}))
    runs[run_id] = dict(run_record)
    next_data = {"schema_version": 1, "runs": dict(sorted(runs.items()))}

    content = (
        json.dumps(next_data, ensure_ascii=False, indent=2, sort_keys=True, default=str)
        + "\n"
    ).encode("utf-8")
    
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.chmod(temporary, 0o644)
        temporary.replace(path)
    finally:
        if temporary.exists():
            temporary.unlink()

    return next_data
