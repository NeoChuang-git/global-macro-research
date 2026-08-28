#!/bin/zsh

set -euo pipefail

INSTALLER_UNDER_TEST="${1:?usage: $0 /path/to/install-production-bridge.sh}"
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TEST_ROOT="$(/usr/bin/mktemp -d /tmp/globalmacro-installer-test.XXXXXX)"

cleanup() {
  /bin/rm -rf "$TEST_ROOT"
}

trap cleanup EXIT INT TERM

FAKE_SOURCE="$TEST_ROOT/source"
FAKE_HOME="$TEST_ROOT/home"
FAKE_PRODUCTION="$FAKE_HOME/.local/share/globalmacro-production"
FAKE_LAUNCHER="$FAKE_HOME/.local/bin/globalmacro-production-bridge"
FAKE_PLIST="$FAKE_HOME/Library/LaunchAgents/com.globalmacro.production-bridge.plist"

/bin/mkdir -p "$FAKE_SOURCE/scripts" "$FAKE_SOURCE/launchd" "$FAKE_HOME"
/bin/cp "$REPO_ROOT/scripts/run_production_bridge.sh" "$FAKE_SOURCE/scripts/"
/bin/cp "$REPO_ROOT/launchd/com.globalmacro.production-bridge.plist" "$FAKE_SOURCE/launchd/"

/usr/bin/git -C "$FAKE_SOURCE" init -q -b main
/usr/bin/git -C "$FAKE_SOURCE" add scripts launchd
/usr/bin/git -C "$FAKE_SOURCE" \
  -c user.name='Global Macro Test' \
  -c user.email='global-macro-test@example.invalid' \
  commit -q -m 'test fixture'

GLOBALMACRO_SOURCE_REPO="$FAKE_SOURCE" \
GLOBALMACRO_HOME="$FAKE_HOME" \
  "$INSTALLER_UNDER_TEST" --install --no-load

/usr/bin/cmp -s "$FAKE_SOURCE/scripts/run_production_bridge.sh" "$FAKE_LAUNCHER"
/usr/bin/plutil -lint "$FAKE_PLIST" >/dev/null

PROGRAM="$(/usr/bin/plutil -extract ProgramArguments.0 raw -o - "$FAKE_PLIST")"
PROGRAM_COUNT="$(/usr/bin/plutil -extract ProgramArguments json -o - "$FAKE_PLIST" | /usr/bin/python3 -c 'import json, sys; print(len(json.load(sys.stdin)))')"
WORKING_DIRECTORY="$(/usr/bin/plutil -extract WorkingDirectory raw -o - "$FAKE_PLIST")"
SOURCE_HEAD="$(/usr/bin/git -C "$FAKE_SOURCE" rev-parse HEAD)"
PRODUCTION_HEAD="$(/usr/bin/git -C "$FAKE_PRODUCTION" rev-parse HEAD)"

[[ "$PROGRAM" == "$FAKE_LAUNCHER" ]]
[[ "$PROGRAM_COUNT" == "1" ]]
[[ "$WORKING_DIRECTORY" == "$FAKE_PRODUCTION" ]]
[[ "$SOURCE_HEAD" == "$PRODUCTION_HEAD" ]]

GLOBALMACRO_SOURCE_REPO="$FAKE_SOURCE" \
GLOBALMACRO_HOME="$FAKE_HOME" \
  "$INSTALLER_UNDER_TEST" --verify --no-load

/usr/bin/plutil -insert ProgramArguments.1 -string unexpected-argument "$FAKE_PLIST"

if GLOBALMACRO_SOURCE_REPO="$FAKE_SOURCE" \
  GLOBALMACRO_HOME="$FAKE_HOME" \
  "$INSTALLER_UNDER_TEST" --verify --no-load >/dev/null 2>&1; then
  echo 'Verifier accepted an unexpected launcher argument' >&2
  exit 1
fi

echo 'PASS: installer creates and verifies an isolated Production deployment'
