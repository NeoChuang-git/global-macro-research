#!/usr/bin/env python3

import argparse
import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

CONFIG_PATH = ROOT / "rules" / "drive-bridge-config.json"

RUNTIME_ROOT = ROOT / "runtime"
STAGING_ROOT = RUNTIME_ROOT / "staging"
PROCESSED_ROOT = RUNTIME_ROOT / "processed"
FAILED_ROOT = RUNTIME_ROOT / "failed"
LOG_ROOT = RUNTIME_ROOT / "logs"
STATE_ROOT = RUNTIME_ROOT / "state"

PROCESSED_REGISTRY = (
    STATE_ROOT / "processed-events.jsonl"
)

PUBLISH_SCRIPT = (
    ROOT / "scripts" / "publish_report.sh"
)

VALIDATOR = (
    ROOT / "scripts" / "validate_payload.py"
)


def load_config():
    if not CONFIG_PATH.exists():
        raise RuntimeError(
            f"Missing config: {CONFIG_PATH}"
        )

    try:
        return json.loads(
            CONFIG_PATH.read_text(
                encoding="utf-8"
            )
        )
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            f"Invalid config JSON: {exc}"
        ) from exc


def ensure_runtime():
    for path in (
        STAGING_ROOT,
        PROCESSED_ROOT,
        FAILED_ROOT,
        LOG_ROOT,
        STATE_ROOT,
    ):
        path.mkdir(
            parents=True,
            exist_ok=True,
        )

    if not PROCESSED_REGISTRY.exists():
        PROCESSED_REGISTRY.touch()


def load_payload(path: Path):
    try:
        return json.loads(
            path.read_text(
                encoding="utf-8"
            )
        )
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            f"Invalid payload JSON: {exc}"
        ) from exc


def validate_payload(path: Path):
    result = subprocess.run(
        [
            sys.executable,
            str(VALIDATOR),
            str(path),
        ],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        message = (
            result.stdout
            + "\n"
            + result.stderr
        ).strip()

        raise RuntimeError(
            f"Payload validation failed:\n{message}"
        )


def derive_event_id_from_filename(
    payload_path: Path,
):
    suffix = ".payload.json"

    name = payload_path.name

    if not name.endswith(suffix):
        raise RuntimeError(
            f"Unexpected payload filename: {name}"
        )

    return name[:-len(suffix)]


def expected_html_path(
    payload_path: Path,
    event_id: str,
):
    return (
        payload_path.parent
        / f"{event_id}.report.html"
    )


def check_contract(
    payload,
    event_id: str,
    environment: str,
):
    payload_environment = payload.get(
        "environment"
    )

    if payload_environment != environment:
        raise RuntimeError(
            "Environment mismatch: "
            f"inbox={environment}, "
            f"payload={payload_environment}"
        )

    payload_event_id = payload.get(
        "event_id"
    )

    if (
        payload_event_id is not None
        and payload_event_id != event_id
    ):
        raise RuntimeError(
            "Event ID mismatch: "
            f"filename={event_id}, "
            f"payload={payload_event_id}"
        )

    if not event_id.startswith(
        f"{environment}-"
    ):
        raise RuntimeError(
            "Event ID prefix does not match "
            f"environment: {event_id}"
        )


def registry_contains(
    event_id: str,
    environment: str,
):
    if not PROCESSED_REGISTRY.exists():
        return False

    with PROCESSED_REGISTRY.open(
        "r",
        encoding="utf-8",
    ) as f:
        for line in f:
            if not line.strip():
                continue

            try:
                item = json.loads(line)
            except json.JSONDecodeError:
                continue

            if (
                item.get("event_id") == event_id
                and
                item.get("environment") == environment
            ):
                return True

    return False


def append_registry(
    event_id: str,
    environment: str,
):
    record = {
        "event_id": event_id,
        "environment": environment,
        "processed_at": (
            datetime.now(timezone.utc)
            .isoformat()
        ),
    }

    with PROCESSED_REGISTRY.open(
        "a",
        encoding="utf-8",
    ) as f:
        f.write(
            json.dumps(
                record,
                ensure_ascii=False,
                separators=(",", ":"),
            )
        )
        f.write("\n")


def copy_pair_to_staging(
    payload_path: Path,
    html_path: Path,
    environment: str,
    event_id: str,
):
    target_dir = (
        STAGING_ROOT
        / environment
        / event_id
    )

    if target_dir.exists():
        shutil.rmtree(target_dir)

    target_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    staged_payload = (
        target_dir
        / payload_path.name
    )

    staged_html = (
        target_dir
        / html_path.name
    )

    shutil.copy2(
        payload_path,
        staged_payload,
    )

    shutil.copy2(
        html_path,
        staged_html,
    )

    return (
        staged_payload,
        staged_html,
        target_dir,
    )


def archive_runtime(
    staging_dir: Path,
    environment: str,
    event_id: str,
    success: bool,
):
    root = (
        PROCESSED_ROOT
        if success
        else FAILED_ROOT
    )

    target = (
        root
        / environment
        / event_id
    )

    target.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    if target.exists():
        shutil.rmtree(target)

    shutil.move(
        str(staging_dir),
        str(target),
    )

    return target


def publish(
    staged_payload: Path,
    staged_html: Path,
):
    result = subprocess.run(
        [
            str(PUBLISH_SCRIPT),
            "--payload",
            str(staged_payload),
            "--html",
            str(staged_html),
        ],
        capture_output=True,
        text=True,
    )

    output = (
        result.stdout
        + "\n"
        + result.stderr
    ).strip()

    if result.returncode != 0:
        raise RuntimeError(
            f"Publish failed:\n{output}"
        )

    return output


def scan_environment(
    drive_root: Path,
    config,
    environment: str,
    dry_run: bool,
):
    inbox_relative = (
        config["environments"]
        [environment]["inbox"]
    )

    inbox = (
        drive_root
        / inbox_relative
    )

    if not inbox.exists():
        print(
            f"[WARN] inbox missing: {inbox}"
        )
        return

    payload_files = sorted(
        inbox.glob(
            "*.payload.json"
        )
    )

    if not payload_files:
        print(
            f"[INFO] {environment}: no payloads"
        )
        return

    for payload_path in payload_files:
        event_id = (
            derive_event_id_from_filename(
                payload_path
            )
        )

        html_path = expected_html_path(
            payload_path,
            event_id,
        )

        if not html_path.exists():
            print(
                "[WAIT] incomplete pair: "
                f"{event_id}"
            )
            continue

        if registry_contains(
            event_id,
            environment,
        ):
            print(
                f"[IGNORE] already processed: "
                f"{event_id}"
            )
            continue

        print(
            f"[PAIR] {environment}: "
            f"{event_id}"
        )

        try:
            payload = load_payload(
                payload_path
            )

            check_contract(
                payload,
                event_id,
                environment,
            )

            validate_payload(
                payload_path
            )

            if dry_run:
                print(
                    f"[DRY-RUN] valid pair: "
                    f"{event_id}"
                )
                continue

            (
                staged_payload,
                staged_html,
                staging_dir,
            ) = copy_pair_to_staging(
                payload_path,
                html_path,
                environment,
                event_id,
            )

            try:
                output = publish(
                    staged_payload,
                    staged_html,
                )

                target = archive_runtime(
                    staging_dir,
                    environment,
                    event_id,
                    success=True,
                )

                append_registry(
                    event_id,
                    environment,
                )

                print(
                    f"[OK] published: "
                    f"{event_id}"
                )

                print(
                    f"[OK] runtime archive: "
                    f"{target}"
                )

                if output:
                    print(output)

            except Exception:
                target = archive_runtime(
                    staging_dir,
                    environment,
                    event_id,
                    success=False,
                )

                print(
                    f"[FAILED] runtime archive: "
                    f"{target}"
                )

                raise

        except Exception as exc:
            print(
                f"[ERROR] {event_id}: {exc}"
            )


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Read-only Google Drive inbox "
            "bridge for Research Intelligence System"
        )
    )

    parser.add_argument(
        "--once",
        action="store_true",
        help="Scan once and exit",
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help=(
            "Validate only; do not stage "
            "or publish"
        ),
    )

    parser.add_argument(
        "--environment",
        choices=[
            "production",
            "test",
            "all",
        ],
        default="all",
    )

    args = parser.parse_args()

    config = load_config()

    drive_root = Path(
        config["drive_root"]
    )

    if not drive_root.exists():
        print(
            f"Drive root not found: "
            f"{drive_root}"
        )
        sys.exit(2)

    ensure_runtime()

    if args.environment == "all":
        environments = (
            "test",
            "production",
        )
    else:
        environments = (
            args.environment,
        )

    for environment in environments:
        scan_environment(
            drive_root,
            config,
            environment,
            args.dry_run,
        )


if __name__ == "__main__":
    main()
