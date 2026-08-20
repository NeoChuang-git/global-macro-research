#!/usr/bin/env python3

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

SIGNAL_HISTORY = (
    ROOT
    / "data"
    / "signals"
    / "signal-history.jsonl"
)

VALIDATOR = (
    ROOT
    / "scripts"
    / "validate_payload.py"
)

REPORT_DIR_MAP = {
    "early_warning": ROOT / "reports" / "early-warning",
    "morning_brief": ROOT / "reports" / "morning",
    "weekly_strategy": ROOT / "reports" / "weekly",
}


def load_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Invalid JSON: {exc}") from exc


def validate_payload(payload_path: Path):
    result = subprocess.run(
        [
            sys.executable,
            str(VALIDATOR),
            str(payload_path),
        ],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        print(result.stdout)
        print(result.stderr)
        raise RuntimeError("Payload validation failed")

    print(result.stdout.strip())


def normalize_generated_at(value: str):
    return datetime.fromisoformat(
        value.replace("Z", "+00:00")
    )


def generate_event_id(payload):
    if payload.get("event_id"):
        return payload["event_id"]

    source = payload["source_system"]
    generated_at = payload["generated_at"]
    thesis = payload["thesis"]

    fingerprint_source = (
        f"{source}|{generated_at}|{thesis}"
    )

    digest = hashlib.sha256(
        fingerprint_source.encode("utf-8")
    ).hexdigest()[:10]

    compact_time = (
        generated_at
        .replace("-", "")
        .replace(":", "")
        .replace("+08:00", "")
        .replace("T", "T")
    )

    return f"{source}-{compact_time}-{digest}"


def event_exists(event_id):
    if not SIGNAL_HISTORY.exists():
        return False

    with SIGNAL_HISTORY.open(
        "r",
        encoding="utf-8",
    ) as file:
        for line in file:
            line = line.strip()

            if not line:
                continue

            try:
                item = json.loads(line)
            except json.JSONDecodeError:
                continue

            if item.get("event_id") == event_id:
                return True

    return False


def append_history(payload):
    SIGNAL_HISTORY.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with SIGNAL_HISTORY.open(
        "a",
        encoding="utf-8",
    ) as file:
        file.write(
            json.dumps(
                payload,
                ensure_ascii=False,
                separators=(",", ":"),
            )
        )
        file.write("\n")


def build_report_directory(payload):
    source = payload["source_system"]

    if source not in REPORT_DIR_MAP:
        raise RuntimeError(
            f"Unsupported source_system: {source}"
        )

    generated = normalize_generated_at(
        payload["generated_at"]
    )

    root = REPORT_DIR_MAP[source]

    if source == "weekly_strategy":
        year, week, _ = generated.isocalendar()

        report_dir = (
            root
            / str(year)
            / f"W{week:02d}"
        )

    else:
        report_dir = (
            root
            / f"{generated.year:04d}"
            / f"{generated.month:02d}"
        )

    report_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    return report_dir


def build_filename(payload, event_id):
    source = payload["source_system"]

    generated = normalize_generated_at(
        payload["generated_at"]
    )

    if source == "early_warning":
        timestamp = generated.strftime(
            "%Y-%m-%dT%H%M%S"
        )

        return (
            f"{timestamp}-"
            f"{event_id[-10:]}.html"
        )

    if source == "morning_brief":
        return generated.strftime(
            "%Y-%m-%d-morning.html"
        )

    if source == "weekly_strategy":
        year, week, _ = generated.isocalendar()

        return (
            f"{year}-W{week:02d}-weekly.html"
        )

    raise RuntimeError(
        f"Unsupported source_system: {source}"
    )


def archive_report(
    html_path: Path,
    payload,
    event_id,
):
    report_dir = build_report_directory(
        payload
    )

    filename = build_filename(
        payload,
        event_id,
    )

    target = report_dir / filename

    shutil.copy2(
        html_path,
        target,
    )

    return target


def write_metadata(
    report_path: Path,
    payload,
):
    metadata_path = report_path.with_suffix(
        ".metadata.json"
    )

    metadata = {
        "event_id": payload["event_id"],
        "schema_version": payload["schema_version"],
        "source_system": payload["source_system"],
        "report_type": payload["report_type"],
        "generated_at": payload["generated_at"],
        "classification": payload["classification"],
        "regime": payload["regime"],
        "thesis": payload["thesis"],
        "risk_lights": payload["risk_lights"],
        "signal_ids": [
            signal.get("id")
            for signal in payload.get(
                "signals",
                []
            )
        ],
        "report_file": report_path.name,
    }

    metadata_path.write_text(
        json.dumps(
            metadata,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    return metadata_path


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Ingest Global Macro Research "
            "Intelligence report"
        )
    )

    parser.add_argument(
        "--payload",
        required=True,
        help="integration_payload JSON file",
    )

    parser.add_argument(
        "--html",
        required=True,
        help="HTML report file",
    )

    parser.add_argument(
        "--force",
        action="store_true",
        help="Allow duplicate event_id",
    )

    args = parser.parse_args()

    payload_path = Path(
        args.payload
    ).expanduser().resolve()

    html_path = Path(
        args.html
    ).expanduser().resolve()

    if not payload_path.exists():
        print(
            f"Payload not found: "
            f"{payload_path}"
        )
        sys.exit(2)

    if not html_path.exists():
        print(
            f"HTML not found: "
            f"{html_path}"
        )
        sys.exit(2)

    validate_payload(
        payload_path
    )

    payload = load_json(
        payload_path
    )

    event_id = generate_event_id(
        payload
    )

    payload["event_id"] = event_id

    if (
        event_exists(event_id)
        and not args.force
    ):
        print(
            "SKIPPED: duplicate event"
        )
        print(
            f"event_id: {event_id}"
        )
        sys.exit(0)

    report_path = archive_report(
        html_path,
        payload,
        event_id,
    )

    payload["report_path"] = str(
        report_path.relative_to(ROOT)
    )

    append_history(
        payload
    )

    metadata_path = write_metadata(
        report_path,
        payload,
    )

    print("INGESTED")
    print(
        f"event_id: {event_id}"
    )
    print(
        f"report: {report_path}"
    )
    print(
        f"metadata: {metadata_path}"
    )
    print(
        f"history: {SIGNAL_HISTORY}"
    )


if __name__ == "__main__":
    main()
