# Pull Request Procedure

This document is the step-by-step guide for preparing, opening, and merging a pull request in **mima-ai-prompt**. Follow it in order. Repository settings and Actions details live in [GITHUB.md](GITHUB.md). Contribution rules live in [CONTRIBUTING.md](CONTRIBUTING.md).

Package metadata is defined in `pyproject.toml` (`name`, `version`, `description`, README, LICENSE). Version and release notes are updated there and in `CHANGELOG.md`.

## 1. When CI runs

`.github/workflows/ci.yml` does **not** run on every branch you push. It runs when:

- You **push** to `main`, `master`, or a branch whose name matches `v*` (for example `v1.0`), or
- You open or update a **pull request whose base** is `main`, `master`, or `v*`.

Do not name a feature or fix branch `v1.2.3` or `v-anything`. The `v*` pattern is reserved for release stabilization branches.

The **Release** workflow (PyPI) does not run on pull requests. It runs when a maintainer pushes a tag matching `v*.*.*` (for example `v1.1.0`) or starts **Actions → Release → Run workflow**. See section 13 and [GITHUB.md](GITHUB.md).

## 2. Branch naming

Use a prefix, a slash, and a short kebab-case description:

- `feature/` — new capability
- `fix/` — bug fix
- `docs/` — documentation only
- `chore/` — tooling, Dependabot config, lock files
- `ci/` — GitHub Actions
- `release/` — version bump and changelog freeze before a tag

Examples: `feature/yaml-output-format`, `fix/template-render`, `docs/github-guide`, `chore/uv-lock`, `ci/coverage-artifact`, `release/1.1.0`.

## 3. Start from an up-to-date main

```bash
git checkout main
git pull origin main
```

## 4. Create the working branch

```bash
git checkout -b feature/short-description
```

## 5. Make the change

Keep the PR focused. Prefer immutable domain objects. Do not add HTTP clients or vendor chat mappers.

## 6. Changelog

For any user-facing behavior or API change, add an entry under `## [Unreleased]` in `CHANGELOG.md`. Use **Added**, **Changed**, **Fixed**, or **Removed**.

## 7. Version and package metadata

Do **not** bump `version` in `pyproject.toml` on every feature or fix PR. Bump only on a dedicated `release/x.y.z` pull request when you intend to publish that version to PyPI.

On a release pull request:

1. Choose the next SemVer from the Unreleased notes.
2. Set `version` in `pyproject.toml`.
3. Move `[Unreleased]` entries to `## [x.y.z] - YYYY-MM-DD` in `CHANGELOG.md`.

## 8. Verify locally

```bash
uv sync --all-groups
uv run pytest --cov=mima_ai_prompt --cov-fail-under=95
uv build
```

## 9. Commit and push

```bash
git add -A
git commit -m "Short imperative summary"
git push -u origin HEAD
```

Do not add `.venv/`, `dist/`, coverage output, or secrets.

## 10. Open the pull request

Open the PR against **`main`**. Fill `.github/PULL_REQUEST_TEMPLATE.md`.

## 11. Wait for CI

CI must show green **Test** (all Python matrix jobs) and **Pack**.

## 12. Review and merge

Prefer **squash merge**. Delete the branch after merge.

## 13. Publish a PyPI version

Publishing is not part of an ordinary pull request. After a **release** pull request is squash-merged to `main`:

1. Ensure `pyproject.toml` `version` matches the intended release.
2. Tag that commit. The tag must match `v*.*.*` and should match `version`:

```bash
git checkout main
git pull
git tag -a v1.1.0 -m "v1.1.0"
git push origin v1.1.0
```

3. Pushing the tag starts `.github/workflows/release.yml`, which tests, builds, and uploads to PyPI using Trusted Publishing (OIDC). Prerequisites are in [GITHUB.md](GITHUB.md).

You can also rehearse with **Actions → Release → Run workflow** and `dry_run=true` (default). Set `dry_run=false` only to publish without a new tag.

## Quick checklist

1. Update `main`.
2. Branch with `feature/`, `fix/`, `docs/`, `chore/`, `ci/`, or `release/` (never a stray `v*` name).
3. Implement; keep PRs focused.
4. Changelog under `[Unreleased]` when user-facing. Bump `version` only on a release PR.
5. `uv run pytest --cov=mima_ai_prompt --cov-fail-under=95` and `uv build`.
6. Push and open PR into `main`.
7. Wait for CI; squash-merge.
8. For a PyPI release, merge a version bump first, then push tag `vX.Y.Z`.
