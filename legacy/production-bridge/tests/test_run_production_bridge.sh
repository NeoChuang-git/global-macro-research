#!/bin/zsh

set -euo pipefail

SCRIPT_UNDER_TEST="${1:?usage: $0 /path/to/run_production_bridge.sh}"
TEST_ROOT="$(/usr/bin/mktemp -d /tmp/globalmacro-wrapper-test.XXXXXX)"

cleanup() {
  /bin/rm -rf "$TEST_ROOT"
}

trap cleanup EXIT INT TERM

FAKE_REPO="$TEST_ROOT/repo"
FAKE_PYTHON="$TEST_ROOT/fake-python"
FAKE_CALLS="$TEST_ROOT/python-calls.txt"

/bin/mkdir -p "$FAKE_REPO/scripts"
: > "$FAKE_REPO/scripts/drive_bridge.py"

/usr/bin/printf '%s\n' \
  '#!/bin/zsh' \
  'echo "[INFO] production: no payloads"' \
  '/usr/bin/printf "%s\\n" "$@" > "$FAKE_CALLS"' \
  > "$FAKE_PYTHON"

/bin/chmod 755 "$FAKE_PYTHON"

export FAKE_CALLS
export GLOBALMACRO_REPO_ROOT="$FAKE_REPO"
export GLOBALMACRO_PYTHON="$FAKE_PYTHON"
export GLOBALMACRO_SETTLE_SECONDS=0

"$SCRIPT_UNDER_TEST"

LOG_FILE="$FAKE_REPO/runtime/logs/production-bridge.log"

/usr/bin/grep -q 'production bridge start' "$LOG_FILE"
/usr/bin/grep -q '\[INFO\] production: no payloads' "$LOG_FILE"
/usr/bin/grep -q 'production bridge end status=0' "$LOG_FILE"
/usr/bin/grep -qx "$FAKE_REPO/scripts/drive_bridge.py" "$FAKE_CALLS"
/usr/bin/grep -qx -- '--once' "$FAKE_CALLS"
/usr/bin/grep -qx -- '--environment' "$FAKE_CALLS"
/usr/bin/grep -qx -- 'production' "$FAKE_CALLS"

echo 'PASS: production wrapper uses the configured local checkout and production-only scan'
