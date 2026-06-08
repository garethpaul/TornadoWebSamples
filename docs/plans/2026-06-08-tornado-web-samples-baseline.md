# Tornado Web Samples Baseline

## Status: Completed

## Context

`TornadoWebSamples` is a small set of legacy Tornado chat examples covering
long-polling comet chat and WebSocket chat. The maintenance baseline should
preserve tutorial clarity while keeping demo-only in-memory state and escaped
browser rendering explicit.

## Objectives

- Preserve both comet and WebSocket chat examples.
- Keep WebSocket close handling idempotent.
- Render browser-side chat messages through text-node APIs.
- Run Python syntax, focused handler tests, static asset checks, and docs-plan
  checks through `make check`.
- Maintain completed maintenance plans under `docs/plans`.

## Work Completed

- Confirmed `make check` runs Python syntax checks and focused pytest coverage.
- Added canonical `docs/plans` coverage for the current chat sample baseline.
- Added a docs-plan checker under `make lint` that requires completed plans
  with `make check` verification.
- Updated README, VISION, and CHANGES to make the baseline discoverable.

## Verification

- `python3 -m py_compile comet_chat/application.py socket_chat/application.py`
- `python3 scripts/check_docs_plans.py`
- `python3 -m pytest -q`
- `make check`
- `make verify`
- `git diff --check`

## Follow-Up Candidates

- Document supported Python and Tornado versions.
- Add separate README caveats for long-polling and WebSocket demos.
