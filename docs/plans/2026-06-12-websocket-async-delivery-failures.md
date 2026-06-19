---
title: "fix: Observe asynchronous WebSocket delivery failures"
type: fix
date: 2026-06-12
---

# Observe Asynchronous WebSocket Delivery Failures

## Status: Completed

## Context

Tornado 6.5.6 returns a future from `WebSocketHandler.write_message`. The
socket chat currently handles only failures raised before that future is
returned. A later stream failure can therefore go unobserved and leave a dead
client in the application registry.

## Requirements

- R1. Observe every future returned by a successful WebSocket write.
- R2. Log asynchronous delivery failures and discard only the failed client.
- R3. Preserve synchronous exception isolation and delivery to later clients.
- R4. Keep compatibility with simple test doubles that return no future.
- R5. Protect the behavior with focused runtime tests and a static contract.

## Scope Boundaries

In scope are the socket chat broadcast path, its focused tests, the plan
checker, and concise maintenance documentation. Authentication, rate limiting,
message persistence, protocol acknowledgements, and backpressure policy remain
outside this change.

## Implementation Units

### U1. Observe Delivery Futures

- **Goal:** Attach completion handling to each returned delivery future and
  remove a client only when its asynchronous write fails.
- **Files:** `socket_chat/application.py`
- **Approach:** Keep the existing per-client synchronous `try` boundary. When a
  write returns a future-like object, register a completion callback that calls
  `result()`, logs failures, and discards the associated client.
- **Patterns to follow:** Preserve the existing registry ownership and
  exception logging conventions in `socket_chat/application.py`.
- **Test scenarios:** A successful delayed completion keeps the client; a
  failed delayed completion removes it; a synchronous write failure still
  allows the next client to receive the message; a write returning `None`
  remains supported.
- **Verification:** Every delivery failure path is observed without interrupting
  the broadcast loop.

### U2. Add Regression and Static Contracts

- **Goal:** Make future observation and failed-client cleanup durable.
- **Files:** `tests/test_chat_handlers.py`, `scripts/check_docs_plans.py`
- **Approach:** Use no-network future doubles to deterministically complete or
  fail writes after broadcast dispatch. Extend the checker to require future
  callback registration, result observation, cleanup, focused tests, and this
  completed plan.
- **Test scenarios:** The checker rejects removal of callback registration,
  result observation, cleanup, or the failed-future regression test.
- **Verification:** Focused tests and mutation checks fail for each weakened
  contract.

### U3. Record the Reliability Contract

- **Goal:** Document the completed behavior and verification evidence.
- **Files:** `CHANGES.md`, `README.md`, `SECURITY.md`,
  `docs/plans/2026-06-12-websocket-async-delivery-failures.md`
- **Approach:** Describe asynchronous delivery cleanup without presenting the
  tutorial sample as production-ready.
- **Test expectation:** Documentation is enforced by the plan checker; no
  separate runtime behavior is introduced.
- **Verification:** Documentation matches the implementation and actual test
  commands run.

## Risks

- Completion callbacks run later than the broadcast loop, so they must capture
  the intended client rather than the loop variable.
- Calling `result()` is required to consume the future exception; omitting it
  would leave the failure unobserved despite registering a callback.
- The callback must not remove healthy clients on successful completion.

## Assumptions

- Tornado 6.5.6 remains the pinned runtime and its documented future-returning
  `write_message` contract is authoritative for this sample.
- Supporting a `None` return keeps existing lightweight test doubles and older
  sample integrations compatible.

## Work Completed

- Added completion handling for every future returned by a successful
  WebSocket write.
- Consumed delayed delivery results, logged failures, and removed only the
  client associated with the failed or cancelled delivery.
- Preserved synchronous exception isolation and clients whose test doubles
  return no future.
- Added deterministic delayed-success and delayed-failure regression tests.
- Extended the static checker with independent async-delivery contracts.
- Updated maintenance, security, vision, and change documentation.

## Verification

- Python 3.14.0 with Tornado 6.5.6 and pytest 9.0.3
- `python -m pytest -q tests/test_chat_handlers.py` (18 passed)
- Six hostile mutations covering callback registration, result consumption,
  cancellation handling, client binding, async cleanup, and failed-future
  coverage
- `make check`
- `git diff --check`

All tests are local and in-process; no public service or external network is
used beyond the dependency audit performed by `make check`.
