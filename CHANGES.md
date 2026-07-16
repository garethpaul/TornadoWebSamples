# Changes

## 2026-07-09

- Replaced global `pip check` with a project-scoped runtime pin check so shared
  developer environments do not fail the gate on unrelated packages.

## 2026-06-26

- Invalid WebSocket messages remove the sender from the client registry before close code `1003`, preventing rejected handlers from sending or receiving during the close handshake.
- Added failing-first unit coverage for malformed JSON, invalid body shapes,
  and late sends attempted after invalid-message rejection.
- Exact PR head `d19b3db8e5ed7d7a5de5f8046a80166547194421` passed
  Python 3.10/3.12/3.14 `make check` and CodeQL Actions, JavaScript, and Python,
  then merged as `4f4722d00ecd70248012b02e58b4b4ed42ba216e`.
- `$codex-review` stopped before analysis with OpenAI HTTP 401; immutable manual
  review of the exact merged diff found no actionable issue.
- Priority P2 cycle: reconciled the four remaining roadmap items against the
  maintained runtime, existing handler tests, and current browser clients.
- Added separate Comet and WebSocket operating guides covering supported
  CPython/Tornado versions, transport-specific input validation, admission and
  timeout/close behavior, delivery-failure tests, and production limitations.
- Replaced stale generated inventory and the mixed transport verification block
  with source-backed guidance while leaving both tutorial implementations,
  dependencies, workflows, and limits unchanged.
- Added fail-closed documentation contracts for the separate Comet and
  WebSocket operating guides. All 21 hostile documentation mutations were
  rejected, including version, heading, limit, broadcast, caveat, roadmap,
  change-history, and plan-status drift. No delegated threads were needed.
- Verified the exact pinned dependency set in clean CPython 3.12 and 3.14
  containers. Both `make check` runs passed 45 handler tests, 5 dependency
  audit mutations, 18 workflow mutations, 9 WebSocket rate-limit mutations,
  `pip check`, and both dependency audits; the external-path Make invocation
  also passed on CPython 3.12.
- The next recommended action is to keep these sections synchronized with any
  future handler, browser client, dependency, or limit change.

## 2026-06-21

- Bound checked-in verification and dependency auditing against ordinary
  caller root and shell assignments, later single-colon recipe replacement,
  non-executing modes, and tool syntax. Documented GNU Make `override`
  directives, caller-added double-colon recipes, startup parse code, and
  default Python PATH selection as caller-program authority outside the local
  Make boundary.
- Added adversarial Make regression coverage and pinned hosted verification to
  `/usr/bin/make`.

## 2026-06-20

- Pinned development-time msgpack to 1.2.1 for `GHSA-6v7p-g79w-8964` and
  extended `make check` to audit runtime and development requirements
  separately, backed by five hostile dependency-contract mutations.

## 2026-06-19

- Ignored WebSocket messages from handlers that are no longer present in the
  application client registry, preventing rejected or removed connections from
  broadcasting during close races.

## 2026-06-17

- WebSocket accepts at most 10 messages per second per connection and closes
  sustained overload before JSON parsing and broadcast fan-out.
- WebSocket accepts at most 100 connected clients and closes temporary
  overload with registered code `1013` without retaining the rejected client.

## 2026-06-15

- Comet accepts at most 100 pending long polls and returns `503` with
  `Retry-After: 1` when capacity is exhausted.
- Raised Tornado to 6.5.7 to remediate `GHSA-pw6j-qg29-8w7f`.

## 2026-06-13

- Capped standalone comet request bodies at 4096 bytes before Tornado buffers
  or parses form data, complementing the existing 500-character message limit.
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
