# Global Macro Research Intelligence System

Private, evidence-gated repository for Global Macro Early Warning, morning and
weekly research, structured signal history, and HTML report archives.

## Reading order

1. [`docs/architecture/production-bridge.md`](docs/architecture/production-bridge.md)
   defines the Production bridge modules, interfaces, seams, state model, and
   evidence gates.
2. [`docs/operations/production-bridge-launchd.md`](docs/operations/production-bridge-launchd.md)
   is the install, verification, recovery, and update runbook.
3. [`rules/universal-signal-schema-v1.json`](rules/universal-signal-schema-v1.json)
   is the payload contract.

## Repository structure

- `data/` — environment-separated JSONL signal history and regime history.
- `reports/` — environment-separated HTML reports and metadata.
- `rules/` — payload schema, bridge configuration, and signal rules.
- `scripts/` — validation, ingestion, reconciliation, publishing, and status interfaces.
- `launchd/` — canonical Production LaunchAgent plist and installer.
- `tests/` — public-interface integration and deployment contract tests.
- `runtime/` — ignored local queue state, archives, locks, and logs.

## Public interfaces

```bash
/usr/bin/python3 scripts/validate_payload.py payload.json
/usr/bin/python3 scripts/drive_bridge.py --once --environment test --dry-run
/usr/bin/python3 scripts/production_status.py
launchd/install-production-bridge.sh --verify
```

Production is scheduled; Test is manual only. Do not run the Production publish
interface with synthetic events because it commits and pushes report artifacts.

## Tests

```bash
/usr/bin/python3 -m unittest tests/test_production_status.py -v
tests/test_run_production_bridge.sh scripts/run_production_bridge.sh
tests/test_install_production_bridge.sh launchd/install-production-bridge.sh
```
