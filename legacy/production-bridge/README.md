# Retired Production Bridge

This directory is a migration backup, not an active application surface.

It preserves the former inbox-pair reconciliation, validation, ingestion,
launchd deployment, status, Git publisher, rules, tests, historical data, and
runbooks. Paths are intentionally changed so the root test discovery and active
GitHub workflows cannot call them accidentally.

Do not run `scripts/publish_report.sh`, `scripts/run_production_bridge.sh`, or
`launchd/install-production-bridge.sh` from this directory. The publisher can
commit and push, and the launchd design has a machine-specific deployment
surface. Use the untouched archive identified in
`docs/migration/production-bridge-retirement.md` for a controlled recovery.
