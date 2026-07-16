# WebSocket Client Admission Cap

## Status: Completed

## Context

The WebSocket sample bounds inbound frame size and validates message contents,
but every same-origin upgrade is currently inserted into an unbounded
application-owned `chat_clients` set. Each accepted connection can remain open
indefinitely and consumes a socket, Tornado handler, and broadcast target. The
Comet sample already applies a deterministic cap to its equivalent long-lived
poll registry, so leaving WebSocket admission unlimited is now the highest
priority independent resource-control gap.

The prioritized follow-up order is:

1. Bound application-owned WebSocket client admission and prove slot reuse.
2. Evaluate server-side ping/idle policy for abandoned connections.
3. Improve browser reconnect/backoff behavior without hiding terminal policy
   failures.

This plan implements only the first item. The sample remains loopback-bound,
unauthenticated, process-local, and unsuitable for production deployment.

## Goals

- Limit simultaneously registered WebSocket chat clients with one named,
  application-owned default.
- Make admission and registration one synchronous operation on Tornado's event
  loop so capacity cannot be checked separately from insertion.
- Close an upgraded over-capacity client with registered WebSocket close code
  `1013` (`Try Again Later`) without retaining it in the broadcast registry.
- Preserve idempotent close cleanup so a departing client immediately frees a
  slot for the next valid connection.
- Add focused unit, live Tornado runtime, static-contract, and hostile-mutation
  coverage for the boundary and cleanup behavior.

## Non-Goals

- Authentication, per-IP quotas, distributed connection accounting, or a
  reverse-proxy/global rate limit.
- Changing same-origin enforcement, message normalization, frame limits, or
  asynchronous broadcast failure handling.
- Adding heartbeat, idle-timeout, browser retry, persistence, or production
  deployment behavior.
- Replacing the sample's in-memory set with an external broker or registry.

## Design

### Application-Owned Admission

`socket_chat/application.py` will define a default maximum and store the
configured limit on each `Application`. A small synchronous registration method
will return whether the handler was admitted, treating an already registered
handler as an idempotent success and rejecting new handlers once the set reaches
capacity.

`MessageHandler.open` will call that method exactly once. Rejected upgraded
connections will be closed with code `1013` and a short stable reason. They will
never become broadcast recipients. `on_close` will continue using `discard`, so
cleanup remains safe if Tornado invokes it for either an admitted or rejected
handler.

### Runtime Proof

The application constructor will accept a test-only configurable limit while
retaining the existing zero-argument production behavior. A live Tornado test
will connect up to a small limit, observe that the next connection receives
close code `1013`, close an admitted client, and prove that a replacement can be
admitted. Focused unit tests will cover exact-boundary admission, idempotent
registration, rejected-client non-retention, and cleanup.

### Maintained Contract

The canonical checker will require the named limit, atomic registration call,
registered close code, runtime regression names, synchronized operator
guidance, and completed verification evidence. Documentation will distinguish
this local in-process cap from authentication or production-grade abuse
protection.

## Implementation Units

### U1. Bound WebSocket Admission

**Files:** `socket_chat/application.py`

Add the named default, configurable application limit, atomic registration
helper, and overload close path while preserving current cleanup and broadcast
behavior.

### U2. Prove Boundary And Slot Reuse

**Files:** `tests/test_chat_handlers.py`, `tests/test_tornado6_runtime.py`

Cover capacity boundaries and idempotence without a network, then exercise
overload close code and replacement admission through real Tornado WebSocket
connections.

### U3. Enforce And Document The Boundary

**Files:** `scripts/check_docs_plans.py`, `AGENTS.md`, `README.md`,
`SECURITY.md`, `VISION.md`, `CHANGES.md`, and this plan

Require the source/test/documentation contracts and record the maintained
security boundary without implying production readiness.

## Risks And Mitigations

- Closing during `open` still leads to `on_close`. Idempotent `discard` cleanup
  makes rejected and admitted close paths safe.
- A separate capacity check could admit too many clients. The application
  helper combines the check and insertion synchronously on the event-loop
  thread.
- A brittle live test could leak sockets. The runtime test will close every
  client in `finally` cleanup and wait for registry removal before asserting
  replacement admission.
- A low default could surprise sample users. The default matches the existing
  Comet pending-poll cap and remains configurable for focused tests.

## Verification Plan

- Run focused handler and live Tornado WebSocket tests.
- Run the pinned full `make check` from the repository root and an external
  directory with explicit timeouts.
- Reject isolated mutations to the limit, atomic admission, overload code,
  non-retention, slot reuse, runtime tests, guidance, and completed-plan status.
- Audit exact intended paths, generated artifacts, dependency drift,
  whitespace, conflict markers, and credential-shaped additions.
- Capture one bounded exact-head hosted snapshot after push; do not poll pending
  checks.

## Sources

- Tornado `WebSocketHandler` lifecycle and `close(code, reason)` behavior:
  https://www.tornadoweb.org/en/stable/websocket.html
- IANA WebSocket Close Code Number Registry (`1013`, `Try Again Later`):
  https://www.iana.org/assignments/websocket/websocket.xhtml

## Work Completed

- Added a 100-client application-owned WebSocket admission cap with one
  synchronous idempotent registration operation.
- Closed upgraded overload with registered code `1013` and a stable retryable
  reason without retaining rejected handlers in the broadcast registry.
- Preserved idempotent close cleanup so an admitted client's departure
  immediately releases capacity for a replacement connection.
- Added focused unit and live Tornado regressions plus maintained static and
  documentation contracts.

## Verification Completed

- All 39 pinned offline tests passed, including exact-boundary admission,
  overload close code and reason, admitted-client broadcast continuity, and
  slot reuse through live Tornado WebSocket connections.
- repository and external-directory pinned `make check` passed compilation,
  documentation contracts, 17 workflow mutations, all tests, dependency
  consistency, and a runtime vulnerability audit with no known findings.
- Ten hostile WebSocket client-cap mutations were rejected across the limit,
  atomic admission, overload code and reason, non-retention, unit/runtime
  regressions, guidance, and completed-plan status.
- Generated-artifact, dependency-drift, credential-pattern, exact-diff,
  whitespace, conflict-marker, and staged-path audits passed.
- No public listener, live external traffic, credentials, browser session, or
  production deployment was exercised; the sample remains loopback-bound.
