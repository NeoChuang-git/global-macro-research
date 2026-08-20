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

EVENT_ID="$(
  echo "$OUTPUT" |
  awk -F': ' '/^event_id:/ {print $2}'
)"

if [[ -z "$EVENT_ID" ]]; then
  echo "Unable to determine event_id."
  exit 1
fi

echo
echo "=== 2. Git status ==="

git status --short

if git diff --quiet && git diff --cached --quiet && \
   [[ -z "$(git ls-files --others --exclude-standard)" ]]; then
  echo "No Git changes detected."
  exit 0
fi

echo
echo "=== 3. Git add ==="

git add \
  data/signals/signal-history.jsonl \
  reports/

echo
echo "=== 4. Commit ==="

git commit -m "Ingest research event: ${EVENT_ID}"

echo
echo "=== 5. Push ==="

git push origin main

echo
echo "PUBLISHED"
echo "event_id: ${EVENT_ID}"
