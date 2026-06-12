# Tornado Web Samples CI Baseline

Status: Completed

## Context

The Tornado chat samples already have `make check` coverage for syntax,
handler behavior, static assets, and completed plan documents. The missing
guard was a hosted workflow that repeats that gate before changes merge.

## Changes

- Added `.github/workflows/check.yml` for GitHub Actions.
- Installed `requirements.txt` and `test-requirements.txt` on Python 3.9 to
  preserve the legacy Tornado 4 runtime boundary.
- Ran `make check` in the hosted workflow.
- Extended the docs-plan checker and docs so the CI gate remains visible.

## Verification

- `make check`
- `git diff --check`
