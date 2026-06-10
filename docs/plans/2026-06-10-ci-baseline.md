# Tornado 6 Runtime And CI Modernization

## Status: Completed

## Context

The samples were constrained to Tornado 4 and the comet handler depended on
`@tornado.web.asynchronous` and `RequestHandler.async_callback`, APIs removed
from maintained Tornado releases. The repository also lacked hosted tests and
an audited, reproducible dependency set.

## Objectives

- Preserve comet long-poll and WebSocket tutorial behavior on Tornado 6.
- Keep disconnect and callback-failure isolation guarantees intact.
- Make template and static paths independent of the launch directory.
- Pin and audit runtime and verification dependencies.
- Run the full no-network gate on maintained Python releases.

## Work Completed

- Replaced removed Tornado 4 comet hooks with an `async def` handler backed by
  an asyncio future.
- Cancelled pending long-poll futures and removed callbacks when clients close.
- Anchored template and static paths to each sample's source directory.
- Restricted both unauthenticated tutorial servers to loopback by default.
- Updated startup code to use the current IOLoop and autoreload entry points.
- Pinned Tornado 6.5.6, pytest 9.0.3, pip-audit 2.10.0, and the remediated pip
  26.1.2 release.
- Added a real HTTP long-poll regression test and launch-directory path test.
- Added a least-privilege, commit-pinned GitHub Actions matrix for Python 3.10,
  3.12, and 3.14.
- Extended repository checks and documentation for runtime and workflow drift.

## Verification

- Fresh isolated dependency installation.
- `python3 scripts/check_docs_plans.py`
- `python3 -m pytest -q`
- `python3 -m pip_audit -r requirements.txt`
- `make check`
- `git diff --check`

The tests use Tornado's local in-process HTTP server and do not require live
services, credentials, or external network calls.
