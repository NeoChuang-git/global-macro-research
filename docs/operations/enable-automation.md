# Enable Google Drive Sync and GitHub Pages

This is a one-time setup. The preferred authentication path is GitHub OIDC →
Google Cloud Workload Identity Federation → a Drive-reader service account. It
creates no long-lived service-account JSON key and requires no GitHub secret.

Repository assumed below: `NeoChuang-git/global-macro-research`.

## 1. Prepare Google Drive

Create exactly three folders named:

- `early-warning`
- `morning`
- `weekly`

Copy each folder ID from its Drive URL. Later, share each folder as **Viewer**
with the service-account email created below. Viewer access is sufficient; the
sync uses the `drive.readonly` OAuth scope and never changes Drive.

## 2. Create Google Cloud federation

Choose a Google Cloud project, then run these once in an authenticated Google
Cloud Shell. Replace the uppercase placeholders first.

```bash
gcloud services enable \
  drive.googleapis.com \
  iamcredentials.googleapis.com \
  sts.googleapis.com \
  --project="PROJECT_ID"

gcloud iam service-accounts create global-macro-drive-reader \
  --project="PROJECT_ID" \
  --display-name="Global Macro Drive Reader"

gcloud iam workload-identity-pools create github \
  --project="PROJECT_ID" \
  --location="global" \
  --display-name="GitHub Actions"

gcloud iam workload-identity-pools providers create-oidc global-macro-research \
  --project="PROJECT_ID" \
  --location="global" \
  --workload-identity-pool="github" \
  --display-name="global-macro-research main" \
  --attribute-mapping="google.subject=assertion.sub,attribute.repository=assertion.repository,attribute.ref=assertion.ref" \
  --attribute-condition="assertion.repository == 'NeoChuang-git/global-macro-research' && assertion.ref == 'refs/heads/main'" \
  --issuer-uri="https://token.actions.githubusercontent.com"
```

Obtain the numeric project number:

```bash
gcloud projects describe "PROJECT_ID" --format="value(projectNumber)"
```

Allow only this repository identity to impersonate the reader service account:

```bash
gcloud iam service-accounts add-iam-policy-binding \
  "global-macro-drive-reader@PROJECT_ID.iam.gserviceaccount.com" \
  --project="PROJECT_ID" \
  --role="roles/iam.workloadIdentityUser" \
  --member="principalSet://iam.googleapis.com/projects/PROJECT_NUMBER/locations/global/workloadIdentityPools/github/attribute.repository/NeoChuang-git/global-macro-research"
```

Now share the three Drive folders as Viewer with:

```text
global-macro-drive-reader@PROJECT_ID.iam.gserviceaccount.com
```

Do not create or download a service-account key.

## 3. Add GitHub repository variables

In **Settings → Secrets and variables → Actions → Variables**, add:

| Variable | Value |
| --- | --- |
| `GCP_WORKLOAD_IDENTITY_PROVIDER` | `projects/PROJECT_NUMBER/locations/global/workloadIdentityPools/github/providers/global-macro-research` |
| `GCP_SERVICE_ACCOUNT` | `global-macro-drive-reader@PROJECT_ID.iam.gserviceaccount.com` |
| `DRIVE_FOLDER_EARLY_WARNING` | Drive folder ID for `early-warning` |
| `DRIVE_FOLDER_MORNING` | Drive folder ID for `morning` |
| `DRIVE_FOLDER_WEEKLY` | Drive folder ID for `weekly` |

These are identifiers, not credentials. The preferred configuration has **zero
GitHub Actions secrets**. `google-github-actions/auth@v3` creates a short-lived
credential file during the job and removes it afterward; `.gitignore` also
excludes its `gha-creds-*.json` filename pattern.

## 4. Permit the workflows

In **Settings → Actions → General**:

1. Allow GitHub Actions for the repository.
2. Ensure repository or organization policy permits the workflow's explicit
   `contents: write` request.
3. If `main` is protected, allow `github-actions[bot]` to push this specific
   automated report commit, or adapt the sync to a reviewed pull-request flow.
   Without this, synchronization correctly fails at `git push` rather than
   bypassing protection.

The sync schedule runs at minute 13 of every UTC hour (`13 * * * *`) and can also be
started manually from **Actions → Sync Google Drive reports**. Concurrency is
serialized, and a concurrent source push causes a normal non-fast-forward
failure rather than overwriting remote history.

## 5. Enable GitHub Pages

In **Settings → Pages → Build and deployment**, choose **GitHub Actions** as the
source. The deployment job uses the standard `github-pages` environment and
requests only `contents: read`, `pages: write`, and `id-token: write`.

## 6. First activation and positive evidence

After this local branch is reviewed, committed, and pushed by the repository
owner:

1. Put one valid `.html` file in one of the shared Drive folders.
2. Manually run **Sync Google Drive reports** from the `main` branch.
3. Confirm its log reports `updated=1` (or the expected count), and confirm a bot
   commit changes the matching `reports/<category>/` path plus
   `data/reports.json` and `data/drive-sync-state.json`.
4. Confirm **Deploy GitHub Pages** runs from that commit and its deployment step
   reports the Pages URL.
5. Open the site, the archive filter, and the report reader. Verify the same
   indexed file renders from `reports/.../*.html`.
6. Run sync again without changing Drive. Confirm `updated=0` and no new commit.

A green test job alone is not publication evidence. Publication is verified
only after the Drive file, bot commit, Pages deployment, and rendered local
report path all agree.

## Official references

- [Google GitHub Actions authentication and Workload Identity Federation](https://github.com/google-github-actions/auth/blob/main/README.md)
- [Google Cloud Workload Identity Federation for deployment pipelines](https://cloud.google.com/iam/docs/workload-identity-federation-with-deployment-pipelines)
- [Google Drive `files.list`](https://developers.google.com/workspace/drive/api/reference/rest/v3/files/list)
- [GitHub Pages custom workflows](https://docs.github.com/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages)
