# WebSocket Invalid Sender Cleanup

Status: Completed

## Problem

Malformed JSON and semantically invalid WebSocket messages close with code
`1003`, but the sender remains in `chat_clients` until Tornado later delivers
`on_close`. During that gap the rejected connection remains a broadcast target,
unlike the existing rate-limit path which discards before closing.

## Design

- Remove the invalid sender from the application registry before each `1003`
  policy close.
- Keep `on_close` idempotent through its existing `discard` call.
- Preserve pre-parse rate limiting, validation copy, delivery isolation, client
  capacity, origin checks, and browser behavior.

## Test First

Strengthen the invalid-frame handler regression to require an empty client
registry immediately after rejection. The focused test must fail on the
unchanged handler because it retains the sender.

## Verification

- Focused invalid-frame test red then green
- Full `make check` and external-Makefile gate
- Hostile mutation removing invalid-sender discard
- Python compilation and `git diff --check`

## Scope Boundaries

- No authentication, persistence, distributed fanout, browser reconnect,
  production deployment, or new close code is added.
- Valid senders and recipients keep their current behavior.

The focused invalid-frame test failed first because the sender remained in the
registry, then passed after the shared terminal helper was added. Full `make
check` and external-Makefile gate verification, hostile mutation evidence, and
exact-head review are recorded before merge. Hostile mutation removing
invalid-sender discard is part of the dedicated contract suite.
Checkout and external-path `make check` passed 45 tests, all 36 hostile
contracts, dependency consistency, and both runtime/development audits with no
known vulnerabilities. Python compilation and `git diff --check` also passed.
