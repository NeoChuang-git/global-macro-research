# Global Macro Signal Report

Zero-token maintenance pipeline for publishing Global Macro HTML reports.

Google Drive is the source and archive. Three fixed Drive folders map directly
to three repository mirrors:

| Google Drive folder | Repository mirror |
| --- | --- |
| `early-warning` | `reports/early-warning/` |
| `daily` | `reports/daily/` |
| `weekly` | `reports/weekly/` |

`scripts/sync-drive.py` reads those folders with the Google Drive API, mirrors
new or changed `.html` files, and deterministically rebuilds
`data/reports.json`. GitHub Pages serves the generated static site. None of the
daily Python, GitHub Actions, or Pages paths calls OpenAI or any other LLM, so
the AI-token maintenance cost is **0**.

## Architecture

```text
Google Drive (read only)
  early-warning / daily / weekly
                 │
                 ▼
GitHub Actions: sync-reports.yml
  scripts/sync-drive.py
                 │
                 ├── reports/{early-warning,daily,weekly}/**/*.html
                 └── data/reports.json
                              │
                              ▼
GitHub Actions: deploy-pages.yml → GitHub Pages
  index.html / archive.html / report.html
```

The two workflows are intentionally separate. Drive sync has only
`contents: write` and Google OIDC permissions; Pages deployment has only
`contents: read`, `pages: write`, and Pages OIDC permissions. A sync commit to
`main` triggers a deployment without combining both privilege sets in one job.

## Local verification

The tests do not access Google Drive and require no third-party packages:

```bash
python3 -m unittest discover -s tests -v
node --check assets/js/app.js
node --check assets/js/archive.js
node --check assets/js/report.js
python3 scripts/build_site.py
```

For a real local Drive sync, use Python 3.10+, install
`requirements-sync.txt`, provide Application Default Credentials with
Drive read-only access, and set the three `DRIVE_FOLDER_*` variables documented
in [`docs/operations/enable-automation.md`](docs/operations/enable-automation.md).

## Operational contracts

- Drive access is read-only; the sync never modifies or deletes Drive files.
- A Drive file disappearance does not delete an archived repo report.
- Duplicate HTML filenames in one Drive folder fail closed.
- Report downloads are checksum-verified and atomically replaced.
- `data/reports.json` is the only discovery interface used by the website.
- The Pages artifact contains only website assets, the index, and indexed HTML;
  source scripts, credentials, runtime logs, and legacy material are excluded.
- No workflow, script, dependency, or website code invokes an LLM.

## Documentation

- [Zero-token publishing architecture](docs/architecture/zero-token-publishing.md)
- [One-time Google Cloud, GitHub Actions, and Pages setup](docs/operations/enable-automation.md)
- [Production Bridge retirement and rollback](docs/migration/production-bridge-retirement.md)

The retired inbox/Production Bridge implementation is preserved under
`legacy/production-bridge/` for audit and recovery, but it has no active
workflow or scheduler entrypoint in the main architecture.
