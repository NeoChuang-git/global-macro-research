#!/bin/zsh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
DEFAULT_SOURCE_REPO="$(cd "$SCRIPT_DIR/.." && pwd)"
SOURCE_REPO="${GLOBALMACRO_SOURCE_REPO:-$DEFAULT_SOURCE_REPO}"
HOME_ROOT="${GLOBALMACRO_HOME:-$HOME}"
PRODUCTION_REPO="${GLOBALMACRO_PRODUCTION_REPO:-$HOME_ROOT/.local/share/globalmacro-production}"
LAUNCHER="${GLOBALMACRO_LAUNCHER:-$HOME_ROOT/.local/bin/globalmacro-production-bridge}"
PLIST_DEST="${GLOBALMACRO_PLIST_DEST:-$HOME_ROOT/Library/LaunchAgents/com.globalmacro.production-bridge.plist}"
SOURCE_WRAPPER="$SOURCE_REPO/scripts/run_production_bridge.sh"
SOURCE_PLIST="$SOURCE_REPO/launchd/com.globalmacro.production-bridge.plist"
LABEL="com.globalmacro.production-bridge"

MODE=""
SHOULD_LOAD=1

usage() {
  echo "Usage: $0 --install|--verify [--no-load]" >&2
  exit 2
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --install|--verify)
      [[ -z "$MODE" ]] || usage
      MODE="$1"
      ;;
    --no-load)
      SHOULD_LOAD=0
      ;;
    *)
      usage
      ;;
  esac
  shift
done

[[ -n "$MODE" ]] || usage

require_source_artifacts() {
  [[ -x "$SOURCE_WRAPPER" ]] || {
    echo "Missing executable wrapper: $SOURCE_WRAPPER" >&2
    exit 2
  }
  /usr/bin/plutil -lint "$SOURCE_PLIST" >/dev/null
}

ensure_clean_checkout() {
  if [[ -n "$(/usr/bin/git -C "$PRODUCTION_REPO" status --porcelain)" ]]; then
    echo "Production checkout is not clean: $PRODUCTION_REPO" >&2
    exit 1
  fi
}

sync_checkout() {
  if [[ ! -d "$PRODUCTION_REPO/.git" ]]; then
    /bin/mkdir -p "$(dirname "$PRODUCTION_REPO")"
    /usr/bin/git clone --no-hardlinks --branch main --single-branch \
      "$SOURCE_REPO" "$PRODUCTION_REPO"

    local remote_url=""
    remote_url="$(/usr/bin/git -C "$SOURCE_REPO" remote get-url origin 2>/dev/null || true)"

    if [[ -n "$remote_url" ]]; then
      /usr/bin/git -C "$PRODUCTION_REPO" remote set-url origin "$remote_url"
    fi
    return
  fi

  ensure_clean_checkout

  local source_head="$(/usr/bin/git -C "$SOURCE_REPO" rev-parse HEAD)"
  local production_head="$(/usr/bin/git -C "$PRODUCTION_REPO" rev-parse HEAD)"

  if [[ "$source_head" == "$production_head" ]]; then
    return
  fi

  /usr/bin/git -C "$PRODUCTION_REPO" fetch "$SOURCE_REPO" "$source_head"
  /usr/bin/git -C "$PRODUCTION_REPO" merge --ff-only FETCH_HEAD

  production_head="$(/usr/bin/git -C "$PRODUCTION_REPO" rev-parse HEAD)"

  if [[ "$source_head" != "$production_head" ]]; then
    echo "Production checkout did not converge to source HEAD" >&2
    exit 1
  fi
}

render_plist() {
  /usr/bin/install -d -m 755 "$(dirname "$PLIST_DEST")"

  if [[ -f "$PLIST_DEST" ]]; then
    /bin/cp -p "$PLIST_DEST" "$PLIST_DEST.bak"
  fi

  /usr/bin/install -m 644 "$SOURCE_PLIST" "$PLIST_DEST"
  /usr/bin/plutil -remove ProgramArguments "$PLIST_DEST"
  /usr/bin/plutil -insert ProgramArguments -json '[]' "$PLIST_DEST"
  /usr/bin/plutil -insert ProgramArguments.0 -string "$LAUNCHER" "$PLIST_DEST"
  /usr/bin/plutil -replace WorkingDirectory -string "$PRODUCTION_REPO" "$PLIST_DEST"
  /usr/bin/plutil -replace EnvironmentVariables.GLOBALMACRO_REPO_ROOT \
    -string "$PRODUCTION_REPO" "$PLIST_DEST"
  /usr/bin/plutil -replace EnvironmentVariables.HOME -string "$HOME_ROOT" "$PLIST_DEST"
  /usr/bin/plutil -lint "$PLIST_DEST" >/dev/null
}

install_artifacts() {
  sync_checkout
  /usr/bin/install -d -m 755 "$(dirname "$LAUNCHER")"
  /usr/bin/install -m 755 "$SOURCE_WRAPPER" "$LAUNCHER"
  render_plist

  if [[ "$SHOULD_LOAD" -eq 1 ]]; then
    local domain="gui/$(/usr/bin/id -u)"
    /bin/launchctl bootout "$domain" "$PLIST_DEST" 2>/dev/null || true
    /bin/launchctl bootstrap "$domain" "$PLIST_DEST"
  fi
}

verify_artifacts() {
  [[ -d "$PRODUCTION_REPO/.git" ]] || {
    echo "Missing Production checkout: $PRODUCTION_REPO" >&2
    exit 1
  }
  ensure_clean_checkout
  /usr/bin/cmp -s "$SOURCE_WRAPPER" "$LAUNCHER"
  /usr/bin/plutil -lint "$PLIST_DEST" >/dev/null

  local program="$(/usr/bin/plutil -extract ProgramArguments.0 raw -o - "$PLIST_DEST")"
  local program_count="$(/usr/bin/plutil -extract ProgramArguments json -o - "$PLIST_DEST" | /usr/bin/python3 -c 'import json, sys; print(len(json.load(sys.stdin)))')"
  local working_dir="$(/usr/bin/plutil -extract WorkingDirectory raw -o - "$PLIST_DEST")"
  local configured_repo="$(/usr/bin/plutil -extract EnvironmentVariables.GLOBALMACRO_REPO_ROOT raw -o - "$PLIST_DEST")"
  local source_head="$(/usr/bin/git -C "$SOURCE_REPO" rev-parse HEAD)"
  local production_head="$(/usr/bin/git -C "$PRODUCTION_REPO" rev-parse HEAD)"

  [[ "$program" == "$LAUNCHER" ]]
  [[ "$program_count" == "1" ]]
  [[ "$working_dir" == "$PRODUCTION_REPO" ]]
  [[ "$configured_repo" == "$PRODUCTION_REPO" ]]
  [[ "$source_head" == "$production_head" ]]

  if [[ "$SHOULD_LOAD" -eq 1 ]]; then
    /bin/launchctl print "gui/$(/usr/bin/id -u)/$LABEL" >/dev/null
  fi

  echo "PASS: Production deployment matches source HEAD $source_head"
}

require_source_artifacts

case "$MODE" in
  --install)
    install_artifacts
    ;;
  --verify)
    verify_artifacts
    ;;
esac
