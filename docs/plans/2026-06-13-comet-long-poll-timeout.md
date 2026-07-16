# Comet Long-Poll Timeout

Status: Completed

## Problem

Each comet `GET /message` registers a callback and waits indefinitely for a
message or client disconnect. Quiet or abandoned connections can therefore
retain request futures and callbacks without a server-side lifetime bound.

## Requirements

- Bound each long poll with a named positive timeout constant.
- Return HTTP `204 No Content` when the wait expires so the browser can issue a
  fresh poll without treating the timeout as an application error.
- Remove the callback and clear handler-owned future state on delivery,
  timeout, cancellation, and connection close.
- Preserve message delivery, XSRF-protected posting, validation, and loopback
  binding behavior.
- Add deterministic no-network handler tests for timeout status and cleanup.
- Extend static contracts and documentation for the bounded resource lifetime.

## Non-Goals

- Do not add authentication, global rate limiting, persistence, or production
  deployment configuration.
- Do not change WebSocket behavior or message limits.
- Do not wait for the real timeout duration in tests.

## Implementation

1. Wrap the per-request message future with `asyncio.wait_for` using a named
   timeout constant.
2. Handle `asyncio.TimeoutError` with status 204 while retaining `finally`
   cleanup for every exit path.
3. Add focused async tests, checker contracts, and user/security documentation.

## Verification

- Focused handler and browser-client tests passed 27 cases.
- A disposable Python 3.12.8 environment installed the exact pinned runtime and
  test requirements and passed all 32 tests with Tornado 6.5.6 and pytest 9.0.3.
- The full pinned `make check` gate and external-working-directory invocation
  passed 32 tests, 17 workflow mutations, `pip check`, and `pip-audit` with no
  known vulnerabilities.
- Eleven hostile mutations for the timeout constant, wait wrapper, timeout
  handling/status, completion cleanup, browser behavior, tests, documentation,
  and completed plan evidence were rejected.
- Python AST, workflow YAML, JavaScript syntax, HTML, and SVG XML parsing passed.
- Secret-pattern, generated-cache, exact-diff, and worktree audits passed; only
  ignored bytecode and pytest caches were preserved and excluded from commit.
