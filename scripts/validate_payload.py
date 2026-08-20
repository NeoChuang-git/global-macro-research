#!/usr/bin/env python3

import json
import sys
from pathlib import Path

REQUIRED = {
    "schema_version",
    "source_system",
    "report_type",
    "generated_at",
    "window",
    "triggered",
    "thesis",
    "classification",
    "regime",
    "risk_lights",
    "signals",
    "watchlist",
}

VALID_SOURCES = {
    "early_warning",
    "morning_brief",
    "weekly_strategy",
}

VALID_CLASSIFICATIONS = {
    "noise",
    "tactical",
    "trend",
    "regime_shift",
}

VALID_STATUS = {
    "on",
    "off",
    "watch",
}

VALID_DIRECTION = {
    "positive",
    "negative",
    "mixed",
}


def validate(payload):
    errors = []

    missing = REQUIRED - set(payload)
    if missing:
        errors.append(f"missing fields: {sorted(missing)}")

    if payload.get("schema_version") != "1.0":
        errors.append("schema_version must be 1.0")

    if payload.get("source_system") not in VALID_SOURCES:
        errors.append("invalid source_system")

    if payload.get("classification") not in VALID_CLASSIFICATIONS:
        errors.append("invalid classification")

    signals = payload.get("signals", [])

    if not isinstance(signals, list):
        errors.append("signals must be an array")
        return errors

    for index, signal in enumerate(signals):
        severity = signal.get("severity")
        confidence = signal.get("confidence")
        status = signal.get("status")
        direction = signal.get("direction")

        if severity is not None and not 1 <= severity <= 5:
            errors.append(
                f"signals[{index}].severity must be between 1 and 5"
            )

        if confidence is not None and not 0 <= confidence <= 1:
            errors.append(
                f"signals[{index}].confidence must be between 0 and 1"
            )

        if status is not None and status not in VALID_STATUS:
            errors.append(
                f"signals[{index}].status invalid"
            )

        if direction is not None and direction not in VALID_DIRECTION:
            errors.append(
                f"signals[{index}].direction invalid"
            )

    return errors


def main():
    if len(sys.argv) != 2:
        print("Usage: validate_payload.py payload.json")
        sys.exit(2)

    path = Path(sys.argv[1])

    if not path.exists():
        print(f"File not found: {path}")
        sys.exit(2)

    try:
        payload = json.loads(
            path.read_text(encoding="utf-8")
        )
    except json.JSONDecodeError as exc:
        print(f"INVALID JSON: {exc}")
        sys.exit(1)

    errors = validate(payload)

    if errors:
        print("INVALID")
        for error in errors:
            print(f"- {error}")
        sys.exit(1)

    print("VALID")


if __name__ == "__main__":
    main()
