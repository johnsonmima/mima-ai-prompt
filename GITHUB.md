# GitHub repository setup — mima-ai-prompt

Maintainer guide for Actions, CI, PyPI Trusted Publishing, and branch protection.

First-publish account steps live in local `TEMP.md` (gitignored; not on GitHub).

Workflow files: `.github/workflows/ci.yml` and `.github/workflows/release.yml`

## Contents

- [1. Default branch](#1-default-branch)
- [2. Branch protection](#2-branch-protection)
- [3. CI workflow](#3-ci-workflow)
- [4. Release workflow](#4-release-workflow)
- [5. PyPI Trusted Publishing](#5-pypi-trusted-publishing)
- [6. Dependabot](#6-dependabot)
- [7. Troubleshooting](#7-troubleshooting)

## 1. Default branch

Use **`main`** as the default branch. Keep release lines such as `v1.0` only for hotfixes if needed.

Confirm that `.github/workflows/ci.yml` and `.github/workflows/release.yml` exist on `main`. Workflows listed under **Actions → Run workflow** are taken from the **default branch**.

## 2. Branch protection

Protect `main` (and any `v*` release branch):

- Require a pull request before merging
- Require status checks: **Test** (all Python matrix jobs) and **Pack**
- Prefer squash merging
- Optionally require CODEOWNERS review

## 3. CI workflow

`.github/workflows/ci.yml` runs on push/PR to `main` / `master` / `v*`.

| Job | What it does |
| --- | --- |
| **Test** | `uv sync --locked`, `pytest` with coverage fail-under **95%**, matrix Python 3.10–3.13 |
| **Pack** | `uv build` and upload wheel/sdist artifacts |

CI never publishes to PyPI.

## 4. Release workflow

`.github/workflows/release.yml` starts when:

- A git tag matching `v*.*.*` is pushed (for example `v1.0.0`), or
- A maintainer uses **Actions → Release → Run workflow**

`dry_run` (manual only, default `true`): build/test/pack only — skip PyPI upload.  
Set `dry_run=false` to publish. A **tag push always attempts publish**.

## 5. PyPI Trusted Publishing

This project uses [PyPI Trusted Publishers](https://docs.pypi.org/trusted-publishers/) (OIDC). No long-lived PyPI API token is stored in GitHub.

### 5.1 Register a publisher on PyPI

1. Sign in at [https://pypi.org/](https://pypi.org/).
2. Create the project `mima-ai-prompt` (or claim it on first publish).
3. Open **Publishing** → **Add a new pending publisher** (or manage publishers on the project):
   - **PyPI Project Name:** `mima-ai-prompt`
   - **Owner:** `johnsonmima` (GitHub user/org)
   - **Repository name:** `mima-ai-prompt`
   - **Workflow name:** `release.yml`
   - **Environment name:** leave empty (this workflow does not set `environment:`)

### 5.2 Permissions

The Release job needs:

```yaml
permissions:
  contents: read
  id-token: write
```

`pypa/gh-action-pypi-publish` exchanges the OIDC token for a short-lived upload credential.

### 5.3 Verify a release

1. **Actions → Release → Run workflow**, leave `dry_run=true`. Confirm test + build.
2. To publish: push tag `v1.0.0`, or run with `dry_run=false`.
3. Package appears at [https://pypi.org/project/mima-ai-prompt/](https://pypi.org/project/mima-ai-prompt/).

## 6. Dependabot

`.github/dependabot.yml`:

- Ecosystems: **uv** (root) and **github-actions**
- Schedule: **semiannually**
- NuGet-style majors: **ignore** `semver-major` for Python deps
- Security alerts can still open independently

Close unwanted major PRs; the ignore only stops **new** major version PRs after it lands on `main`.

## 7. Troubleshooting

| Symptom | Likely cause |
| --- | --- |
| Release not listed under Actions | Workflow not on default branch (`main`) |
| Tag push did not publish | Tag not `v*.*.*`, or dry-run confusion (tags always publish) |
| OIDC / publisher 403 | PyPI Trusted Publisher owner/repo/workflow mismatch |
| CI restore fails | `uv.lock` out of date — run `uv sync` and commit the lock file |
| Coverage fail | Line coverage &lt; 95% — add tests |

## Checklist for a new public repo

The full open-source **GitHub UI** checklist (About, merge, rulesets, Actions, security, Community standards) is in local `TEMP.md` (gitignored).

Short form:

1. Push this folder as the repository root.
2. Set default branch to `main`.
3. Enable Actions; protect `main` with all Test matrix jobs + Pack required.
4. Register PyPI Trusted Publisher for `mima-ai-prompt` / `release.yml`.
5. Enable Dependabot alerts + version updates, secret scanning, private vulnerability reporting.
6. First publish: follow local `TEMP.md`, then merge, tag `v1.0.0`, push the tag.
