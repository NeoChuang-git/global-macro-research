# Production Bridge LaunchAgent Runbook

## Installed layout

| Purpose | Default path |
| --- | --- |
| Development source | `/Volumes/VM-Data/Agent/Global-macro-research` |
| Production checkout | `~/.local/share/globalmacro-production` |
| Production launcher | `~/.local/bin/globalmacro-production-bridge` |
| LaunchAgent | `~/Library/LaunchAgents/com.globalmacro.production-bridge.plist` |
| Production runtime log | `~/.local/share/globalmacro-production/runtime/logs/production-bridge.log` |

The source-repository log path is a convenience symlink to the Production log.

## Install or update

Commit the source changes first. Push before Production publication is expected,
then run:

```bash
launchd/install-production-bridge.sh --install
```

The installer:

1. creates or fast-forwards the isolated Production checkout;
2. refuses a dirty or divergent Production checkout;
3. installs the launcher and renders absolute plist paths;
4. saves the previous installed plist as `.bak`;
5. reloads the LaunchAgent, whose `RunAtLoad` performs one reconciliation.

Use `--no-load` only for fixture tests or offline staging.

## Verify deployment and health

```bash
launchd/install-production-bridge.sh --verify
/usr/bin/python3 scripts/production_status.py
```

For machine-readable monitoring:

```bash
/usr/bin/python3 scripts/production_status.py --json
```

Interpret the three gates independently:

- `Scheduler: PASS` means launchd and the reconciliation runner are healthy.
- `Queue: PASS` means the configured inbox was actually readable, including when
  the observed counts are zero.
- `Publish: UNVERIFIED` means no event has all required publish evidence. It is
  not a failure when the Production inbox has never contained a legitimate pair.

## Schedule and wake behavior

`StartCalendarInterval` runs at minute 05, 20, 35, and 50 of every hour. macOS
launchd coalesces calendar intervals missed during sleep into one event on wake.
The wrapper then waits 20 seconds and performs one scan of all complete pairs, so
sleep-time bursts are reconciled as one batch.

## Test environment

Test remains manual and must never be added to the Production plist:

```bash
/usr/bin/python3 scripts/drive_bridge.py --once --environment test --dry-run
```

Remove `--dry-run` only when a Test pair is intentionally ready for ingestion.

## Failure handling

1. Run `production_status.py --json`; do not infer an empty queue from an access
   failure.
2. Read `runtime/logs/production-bridge.log` and the launchd stderr file.
3. If deployment verification fails, inspect both Git worktrees before updating;
   do not reset the Production checkout.
4. If a pair is under `runtime/failed`, preserve the Drive source pair and failure
   archive until the validator or publisher error is understood.
5. Do not append the processed registry manually. A receipt is valid only after
   the publish path completes.

## Rollback

The installer preserves the previous installed plist as
`com.globalmacro.production-bridge.plist.bak`. The initial 2026-08-20 migration
also has a recoverable backup at
`/private/tmp/globalmacro-production-bridge-backup-20260820`.

Before rollback, unload the current LaunchAgent and inspect both versions. A
rollback to a wrapper that reads `/Volumes/VM-Data` will restore macOS privacy
failures and exit 127, so prefer fixing the local deployment.
