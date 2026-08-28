#!/usr/bin/env python3

import argparse
import json
import plistlib
import re
import subprocess
from pathlib import Path
from typing import Optional


ROOT = Path(__file__).resolve().parents[1]
EXPECTED_MINUTES = [5, 20, 35, 50]
DEFAULT_LABEL = "com.globalmacro.production-bridge"


def read_text(path: Path):
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return ""


def extract_int(pattern: str, text: str):
    match = re.search(pattern, text)

    if not match:
        return None

    return int(match.group(1))


def load_launchctl_text(snapshot_path: Optional[Path]):
    if snapshot_path is not None:
        return read_text(snapshot_path)

    result = subprocess.run(
        [
            "/bin/launchctl",
            "print",
            f"gui/{subprocess.check_output(['/usr/bin/id', '-u'], text=True).strip()}/{DEFAULT_LABEL}",
        ],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        return result.stderr

    return result.stdout


def collect_scheduler(
    plist_path: Path,
    launchctl_text: str,
    runtime_log: Path,
    stdout_log: Path,
    stderr_log: Path,
):
    try:
        plist = plistlib.loads(plist_path.read_bytes())
    except (OSError, plistlib.InvalidFileException):
        plist = {}

    intervals = plist.get("StartCalendarInterval", [])
    minutes = sorted(
        item.get("Minute")
        for item in intervals
        if isinstance(item, dict) and isinstance(item.get("Minute"), int)
    )
    runs = extract_int(r"\bruns = (\d+)", launchctl_text)
    exit_code = extract_int(r"\blast exit code = (-?\d+)", launchctl_text)
    log_text = read_text(runtime_log)
    log_ok = (
        "production bridge start" in log_text
        and "production bridge end status=0" in log_text
    )
    streams_clean = (
        stdout_log.exists()
        and stderr_log.exists()
        and stdout_log.stat().st_size == 0
        and stderr_log.stat().st_size == 0
    )
    is_healthy = all(
        [
            minutes == EXPECTED_MINUTES,
            "state = not running" in launchctl_text,
            runs is not None and runs >= 1,
            exit_code == 0,
            log_ok,
            streams_clean,
        ]
    )

    return {
        "status": "PASS" if is_healthy else "FAIL",
        "minutes": minutes,
        "runs": runs,
        "last_exit_code": exit_code,
        "log_ok": log_ok,
        "streams_clean": streams_clean,
    }


def collect_queue(production_repo: Path):
    config_path = production_repo / "rules" / "drive-bridge-config.json"

    try:
        config = json.loads(config_path.read_text(encoding="utf-8"))
        drive_root = Path(config["drive_root"])
        inbox_relative = config["environments"]["production"]["inbox"]
        inbox = drive_root / inbox_relative
        payloads = sorted(inbox.glob("*.payload.json"))
        reports = sorted(inbox.glob("*.report.html"))
    except (OSError, KeyError, json.JSONDecodeError):
        return {
            "status": "FAIL",
            "accessible": False,
            "payload_count": None,
            "html_count": None,
        }

    return {
        "status": "PASS",
        "accessible": True,
        "payload_count": len(payloads),
        "html_count": len(reports),
    }


def load_jsonl_event_ids(path: Path, environment: str):
    event_ids = set()

    for line in read_text(path).splitlines():
        if not line.strip():
            continue

        try:
            item = json.loads(line)
        except json.JSONDecodeError:
            continue

        if item.get("environment") == environment and item.get("event_id"):
            event_ids.add(item["event_id"])

    return event_ids


def load_report_event_ids(report_root: Path):
    event_ids = set()

    for metadata_path in report_root.rglob("*.metadata.json"):
        try:
            metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue

        html_name = metadata_path.name.removesuffix(".metadata.json") + ".html"

        if metadata_path.with_name(html_name).is_file() and metadata.get("event_id"):
            event_ids.add(metadata["event_id"])

    return event_ids


def collect_publish(production_repo: Path):
    runtime_root = production_repo / "runtime"
    registry_ids = load_jsonl_event_ids(
        runtime_root / "state" / "processed-events.jsonl",
        "production",
    )
    history_ids = load_jsonl_event_ids(
        production_repo / "data" / "signals" / "production" / "signal-history.jsonl",
        "production",
    )
    report_ids = load_report_event_ids(
        production_repo / "reports" / "production"
    )
    log_ids = set(
        re.findall(
            r"^\[OK\] published: (\S+)$",
            read_text(runtime_root / "logs" / "production-bridge.log"),
            flags=re.MULTILINE,
        )
    )
    verified_ids = sorted(registry_ids & history_ids & report_ids & log_ids)

    return {
        "status": "PASS" if verified_ids else "UNVERIFIED",
        "verified_event_ids": verified_ids,
    }


def collect_report(args):
    production_repo = Path(args.production_repo)
    launchctl_text = load_launchctl_text(
        Path(args.launchctl_snapshot) if args.launchctl_snapshot else None
    )

    return {
        "scheduler": collect_scheduler(
            Path(args.plist),
            launchctl_text,
            production_repo / "runtime" / "logs" / "production-bridge.log",
            Path(args.stdout_log),
            Path(args.stderr_log),
        ),
        "queue": collect_queue(production_repo),
        "publish": collect_publish(production_repo),
    }


def print_human(report):
    print(f"Scheduler: {report['scheduler']['status']}")
    print(f"Queue: {report['queue']['status']}")
    print(f"Publish: {report['publish']['status']}")


def build_parser():
    home = Path.home()
    parser = argparse.ArgumentParser(
        description="Inspect Production bridge scheduler, queue, and publish evidence"
    )
    parser.add_argument("--json", action="store_true")
    parser.add_argument(
        "--plist",
        default=home / "Library" / "LaunchAgents" / f"{DEFAULT_LABEL}.plist",
    )
    parser.add_argument("--source-repo", default=ROOT)
    parser.add_argument(
        "--production-repo",
        default=home / ".local" / "share" / "globalmacro-production",
    )
    parser.add_argument("--launchctl-snapshot")
    parser.add_argument(
        "--stdout-log",
        default="/tmp/globalmacro-production-bridge.stdout.log",
    )
    parser.add_argument(
        "--stderr-log",
        default="/tmp/globalmacro-production-bridge.stderr.log",
    )
    return parser


def main():
    args = build_parser().parse_args()
    report = collect_report(args)

    if args.json:
        print(json.dumps(report, ensure_ascii=False, sort_keys=True))
    else:
        print_human(report)


if __name__ == "__main__":
    main()
