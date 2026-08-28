#!/usr/bin/env python3

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

VALID_ENVIRONMENTS = {
    "production",
    "test",
}


def get_history_path(environment: str) -> Path:
    if environment not in VALID_ENVIRONMENTS:
        raise ValueError(
            f"Invalid environment: {environment}"
        )

    return (
        ROOT
        / "data"
        / "signals"
        / environment
        / "signal-history.jsonl"
    )


def main():
    if len(sys.argv) != 2:
        print(
            "Usage: append_signal.py payload.json"
        )
        sys.exit(2)

    payload_path = Path(
        sys.argv[1]
    ).expanduser().resolve()

    if not payload_path.exists():
        print(
            f"File not found: {payload_path}"
        )
        sys.exit(2)

    try:
        payload = json.loads(
            payload_path.read_text(
                encoding="utf-8"
            )
        )
    except json.JSONDecodeError as exc:
        print(
            f"INVALID JSON: {exc}"
        )
        sys.exit(1)

    environment = payload.get(
        "environment"
    )

    if environment not in VALID_ENVIRONMENTS:
        print(
            "INVALID environment"
        )
        sys.exit(1)

    history = get_history_path(
        environment
    )

    history.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with history.open(
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

    print(
        f"Appended to: {history}"
    )


if __name__ == "__main__":
    main()
