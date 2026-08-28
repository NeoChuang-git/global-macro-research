# Production Bridge Retirement and Recovery

## Preserved source before migration

The complete pre-migration repository remains untouched at:

```text
/Volumes/VM-Data/Agent/archive/Global-macro-research-20260821
```

Observed source state before recovery:

- branch `main` at `fb42ae7`, aligned with `origin/main`;
- existing uncommitted installer/test hardening;
- existing tracked report deletions;
- existing untracked reports and `retired-local/` operational backups.

The archive was copied, not moved, to
`/Volumes/VM-Data/Agent/Global-macro-research`, and implementation was isolated
on `refactor/zero-token-pages`. No commit, push, merge, reset, or cleanup was
performed by this migration.

## What was retired

The former main path was:

```text
Drive File Provider inbox pair
  → launchd Production Bridge
  → payload validation / ingestion queue
  → Git commit and push publisher
```

Its code, tests, rules, historical data, and runbooks are preserved together at
`legacy/production-bridge/`. They are no longer in `scripts/`, `tests/`,
`launchd/`, or `rules/`, so neither test discovery nor either GitHub workflow can
invoke them. The historical `retired-local/` directory and archived repo remain
additional recovery evidence and are not published by Pages.

Live machine inspection on 2026-08-28 found no loaded
`com.globalmacro.production-bridge` service (launchctl returned service not
found), and no installed plist, launcher, or isolated Production checkout at
the former documented paths. No unload, deletion, or synthetic run was needed.

The old Production Bridge was previously known to have Scheduler PASS and an
accessible empty queue, but Publish remained UNVERIFIED. That evidence is not
carried forward as proof that any report was published.

## Replacement

The replacement has no payload/report pair, Test/Production queue, local
LaunchAgent, ingestion registry, signal-history mutation, or publisher shell
adapter. It reads `.html` directly from the three configured Drive folders and
commits only the report mirror and deterministic index from GitHub Actions.

## Recovery without overwrite

If legacy investigation is required, create a new recovery path from the archive
rather than overwriting the active repository:

```bash
cp -a \
  /Volumes/VM-Data/Agent/archive/Global-macro-research-20260821 \
  /Volumes/VM-Data/Agent/Global-macro-research-legacy-recovery
```

Do not re-enable the old LaunchAgent merely to test recovery. It used a local
Production checkout because macOS privacy controls prevented launchd from
reading `/Volumes/VM-Data`; a scheduler exit code was never sufficient publish
evidence. Re-enablement should be a separate reviewed rollback with an explicit
publisher evidence gate.
