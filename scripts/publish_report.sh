#!/bin/zsh

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

usage() {
  echo "Usage:"
  echo "  $0 --payload <payload.json> --html <report.html>"
  exit 2
}

PAYLOAD=""
HTML=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --payload)
      PAYLOAD="$2"
      shift 2
      ;;
    --html)
      HTML="$2"
      shift 2
      ;;
    *)
      usage
      ;;
  esac
done

[[ -n "$PAYLOAD" ]] || usage
[[ -n "$HTML" ]] || usage

[[ -f "$PAYLOAD" ]] || {
  echo "Payload not found: $PAYLOAD"
  exit 2
}

[[ -f "$HTML" ]] || {
  echo "HTML not found: $HTML"
  exit 2
}

echo "=== 1. Ingest ==="

OUTPUT="$(
  python3 scripts/ingest_report.py \
    --payload "$PAYLOAD" \
    --html "$HTML"
)"

echo "$OUTPUT"

if echo "$OUTPUT" | grep -q "SKIPPED: duplicate event"; then
  echo
  echo "Duplicate event. Nothing to publish."
  exit 0
fi

if ! echo "$OUTPUT" | grep -q "^INGESTED"; then
  echo "Ingest failed."
  exit 1
fi

ENVIRONMENT="$(
  echo "$OUTPUT" |
  awk -F': ' '/^environment:/ {print $2}'
)"

EVENT_ID="$(
  echo "$OUTPUT" |
  awk -F': ' '/^event_id:/ {print $2}'
)"

if [[ "$ENVIRONMENT" != "production" &&
      "$ENVIRONMENT" != "test" ]]; then
  echo "Invalid environment returned by ingest: $ENVIRONMENT"
  exit 1
fi

if [[ -z "$EVENT_ID" ]]; then
  echo "Unable to determine event_id."
  exit 1
fi

HISTORY_PATH="data/signals/${ENVIRONMENT}/signal-history.jsonl"
REPORT_PATH="reports/${ENVIRONMENT}"

echo
echo "=== 2. Environment ==="
echo "$ENVIRONMENT"

echo
echo "=== 3. Git status ==="

git status --short \
  "$HISTORY_PATH" \
  "$REPORT_PATH"

echo
echo "=== 4. Git add ==="

git add \
  "$HISTORY_PATH" \
  "$REPORT_PATH"

if git diff --cached --quiet; then
  echo "No staged changes detected."
  exit 0
fi

echo
echo "=== 5. Commit ==="

git commit \
  -m "Ingest ${ENVIRONMENT} research event: ${EVENT_ID}"

echo
echo "=== 6. Push ==="

git push origin main

echo
echo "PUBLISHED"
echo "environment: ${ENVIRONMENT}"
echo "event_id: ${EVENT_ID}"
