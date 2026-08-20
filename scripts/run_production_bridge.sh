#!/bin/zsh

set -euo pipefail

export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"

REPO_ROOT="${GLOBALMACRO_REPO_ROOT:-/Users/neochuang/.local/share/globalmacro-production}"
PYTHON="${GLOBALMACRO_PYTHON:-/usr/bin/python3}"
SETTLE_SECONDS="${GLOBALMACRO_SETTLE_SECONDS:-20}"

if [[ ! -d "$REPO_ROOT" ]]; then
  echo "Production repository unavailable: $REPO_ROOT" >&2
  exit 2
fi

if [[ ! -x "$PYTHON" ]]; then
  echo "Python executable unavailable: $PYTHON" >&2
  exit 2
fi

BRIDGE_SCRIPT="$REPO_ROOT/scripts/drive_bridge.py"

if [[ ! -f "$BRIDGE_SCRIPT" ]]; then
  echo "Production bridge unavailable: $BRIDGE_SCRIPT" >&2
  exit 2
fi

case "$SETTLE_SECONDS" in
  ''|*[!0-9]*)
    echo "GLOBALMACRO_SETTLE_SECONDS must be a non-negative integer" >&2
    exit 2
    ;;
esac

RUNTIME_ROOT="$REPO_ROOT/runtime"
LOG_DIR="$RUNTIME_ROOT/logs"
LOCK_DIR="$RUNTIME_ROOT/locks/production-bridge.lock"
LOCK_PID="$LOCK_DIR/pid"

/bin/mkdir -p "$LOG_DIR" "$RUNTIME_ROOT/locks"

LOG_FILE="$LOG_DIR/production-bridge.log"

log() {
  echo "$(/bin/date '+%Y-%m-%d %H:%M:%S') $*" >> "$LOG_FILE"
}

release_lock() {
  /bin/rm -f "$LOCK_PID" 2>/dev/null || true
  /bin/rmdir "$LOCK_DIR" 2>/dev/null || true
}

acquire_lock() {
  if /bin/mkdir "$LOCK_DIR" 2>/dev/null; then
    echo $$ > "$LOCK_PID"
    return 0
  fi

  local existing_pid=""

  if [[ -f "$LOCK_PID" ]]; then
    existing_pid="$(/bin/cat "$LOCK_PID" 2>/dev/null || true)"

    if [[ "$existing_pid" == <-> ]] && kill -0 "$existing_pid" 2>/dev/null; then
      log "[LOCK] bridge already running pid=$existing_pid"
      return 1
    fi
  fi

  log "[LOCK] removing stale lock"
  /bin/rm -f "$LOCK_PID" 2>/dev/null || true

  if ! /bin/rmdir "$LOCK_DIR" 2>/dev/null; then
    log "[LOCK] stale lock contains unexpected files"
    return 1
  fi

  if /bin/mkdir "$LOCK_DIR" 2>/dev/null; then
    echo $$ > "$LOCK_PID"
    return 0
  fi

  log "[LOCK] unable to acquire lock"
  return 1
}

if ! acquire_lock; then
  exit 0
fi

trap release_lock EXIT INT TERM

cd "$REPO_ROOT"

log "===== production bridge start pid=$$ ====="

# Google Drive File Provider may deliver payload/html a few seconds apart.
# Waiting once per reconciliation also collapses wake-time bursts into one scan.
/bin/sleep "$SETTLE_SECONDS"

set +e
"$PYTHON" "$BRIDGE_SCRIPT" \
  --once \
  --environment production \
  >> "$LOG_FILE" 2>&1
bridge_status=$?
set -e

log "===== production bridge end status=$bridge_status ====="

exit "$bridge_status"
