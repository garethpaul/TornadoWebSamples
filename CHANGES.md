# Changes

## 2026-06-13

- Bounded comet long polls to 25 seconds, return `204 No Content` on expiry,
  and made the browser repoll without logging an empty-body parse error.

## 2026-06-12

- Observed asynchronous WebSocket write failures and removed only the failed
  client from the application registry.
- Capped WebSocket frames at 4096 bytes before JSON decoding while preserving
  the existing 500-character chat-body validation.

## 2026-06-10

- Scoped connected WebSocket clients to each application instance so separate
  sample applications cannot share broadcasts through handler class state.
- Removed runtime jQuery 1.7.2 and YUI CDN dependencies from both samples,
  replacing them with native DOM, Fetch, FormData, and WebSocket clients plus
  local reset styles.
- Enabled Tornado XSRF cookies for comet posts and added in-process tests for
  accepted token-bearing requests and rejected tokenless requests.
- Scoped dependency auditing to declared runtime requirements, added `pip
  check`, and fixed CI to Ubuntu 24.04 with concurrency cancellation.
- Upgraded the samples from Tornado 4 to Tornado 6.5.6 and replaced removed
  comet async APIs with an awaitable long-poll future.
- Anchored template and static paths to each sample directory and added a real
  in-process HTTP regression test.
- Restricted both unauthenticated tutorial servers to loopback by default.
- Pinned and audited runtime/test dependencies, including pip 26.1.2 for
  `PYSEC-2026-196` remediation.
- Added a least-privilege GitHub Actions matrix for Python 3.10, 3.12, and 3.14
  using commit-pinned Node 24 actions and credential-free checkout.
- Added dependency-free structural workflow tests that reject contradictory or
  relocated credential settings and other CI policy regressions.

## 2026-06-09

- Isolated WebSocket callback delivery exceptions so one failed client does not
  stop later WebSocket clients in the same broadcast.
- Isolated comet callback delivery exceptions so one failed long-poll callback
  does not stop later callbacks in the same dispatch batch.
- Snapshot and clear comet callback queues before dispatching messages so new
  waits registered during dispatch survive for the next message.
- Added no-network callback dispatch ordering coverage.
- Removed abandoned comet long-poll callbacks when client connections close and
  added no-network handler coverage.
- Added browser-side chat input length hints aligned with the server-side
  message limit.
- Moved comet chat callback storage onto each `Messages` instance.
- Added handler coverage so long-poll callbacks cannot leak across
  independent message stores.
- Added an explicit same-host WebSocket origin check to the socket chat sample.
- Added no-network handler coverage for accepted and rejected origins.

## 2026-06-08

- Added server-side chat message validation for blank, non-string, oversized,
  and malformed WebSocket inputs.
- Added `make check` as the shared repository verification alias.
- Escaped browser-side chat rendering by appending messages as text nodes in
  both comet and WebSocket samples.
- Fixed the WebSocket browser error logger to call `console.error`.
- Added focused static asset tests for client-side message rendering.
- Added a Makefile verification gate for Python syntax checks and focused
  chat-handler tests.
- Added dependency metadata for the legacy Tornado 4 sample API.
- Made WebSocket close handling idempotent by discarding absent callbacks.
- Added generated Python artifact ignores and documented verification steps.
- Added canonical `docs/plans` coverage and a docs-plan checker under
  `make check`.
- Kept browser chat clients on same-origin message endpoints and switched the
  shared external reset stylesheet to HTTPS.
