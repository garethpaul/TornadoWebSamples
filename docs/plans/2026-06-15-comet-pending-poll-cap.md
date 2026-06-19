---
title: Comet Pending Poll Cap
type: security
status: completed
date: 2026-06-15
---

# Comet Pending Poll Cap

## Status: Completed

## Problem Frame

The comet sample bounds message size, request-body size, and long-poll duration,
but `Messages.register_callback` accepts unlimited concurrent waiters. A burst
of unauthenticated local requests can retain an unbounded number of handlers,
callbacks, and futures for up to 25 seconds before timeout cleanup runs.

## Priorities

1. P0: Reject excess pending long polls before allocating a future or
   registering a callback.
2. P1: Preserve exact callback and future cleanup across delivery, timeout,
   cancellation, and disconnect paths.
3. P2: Return explicit temporary-overload behavior and make the capacity
   contract mutation-sensitive.
4. P0 execution discovery: Raise Tornado from vulnerable 6.5.6 to patched 6.5.7
   after the pinned audit identified `GHSA-pw6j-qg29-8w7f`.

## Requirements

- Define a named maximum of 100 pending comet polls and a one-second overload
  retry hint.
- Make capacity admission an application-owned operation so tests and handlers
  use the same registry boundary.
- Return HTTP 503 with a short retry hint when capacity is exhausted.
- Do not allocate or retain a waiter for rejected requests.
- Preserve the existing message validation, XSRF, body limit, 25-second poll
  timeout, callback snapshot delivery, loopback binding, and browser behavior.
- Cover admission, overload rejection, slot reuse, and all existing cleanup
  paths with deterministic offline tests and static contracts.
- Pin Tornado 6.5.7 and make downgrade to the affected 6.5.6 release fail the
  canonical gate.

## Key Technical Decisions

- **Cap callbacks rather than active TCP connections.** The retained callback
  registry is the resource this application owns and can bound directly.
- **Reject instead of queueing beyond the cap.** A second queue would preserve
  the same unbounded-retention failure under another name.
- **Use HTTP 503 plus `Retry-After: 1`.** The request is structurally valid but
  temporarily cannot be admitted; clients may retry after capacity frees.
- **Check capacity before future allocation.** Rejected requests must not create
  handler-owned asynchronous state that then requires cleanup.

## Scope Boundaries

This change does not add authentication, distributed coordination, persistent
history, per-IP quotas, global rate limiting, reverse-proxy policy, or
WebSocket connection limits. The executable remains loopback-bound and is not
made production-ready by this local resource cap.

The patch-level Tornado update discovered by the required audit is included;
broader dependency modernization remains out of scope.

## Implementation Units

### U1. Bound Application-Owned Poll Admission

**Files:** `comet_chat/application.py`

Add a named pending-poll limit and an atomic main-loop admission helper on the
`Messages` registry. Have `MessageHandler.get` reject overload before creating
its future, while retaining the current cleanup logic for admitted requests.

### U2. Prove Runtime And Cleanup Behavior

**Files:** `tests/test_chat_handlers.py`, `tests/test_tornado6_runtime.py`,
`scripts/check_docs_plans.py`

Cover capacity boundaries, no-allocation rejection, HTTP 503 and retry hints,
slot reuse after removal, and successful admission once a timed-out or
disconnected poll releases capacity. Require production wiring and regression
names from the canonical gate.

### U3. Record The Maintained Boundary

**Files:** `AGENTS.md`, `README.md`, `SECURITY.md`, `VISION.md`, `CHANGES.md`,
and this plan

Document the in-process pending-poll cap and explicitly preserve the sample's
loopback-only, unauthenticated, non-production boundary.

### U4. Remediate The Newly Published Tornado Advisory

**Files:** `requirements.txt`, `scripts/check_docs_plans.py`, `README.md`,
`SECURITY.md`, `VISION.md`, `CHANGES.md`, and this plan

Raise the exact runtime pin to Tornado 6.5.7, require that version from the
canonical gate, rerun the complete pinned suite, and require `pip-audit` to
report no known runtime vulnerabilities.

## Risks And Mitigations

- A count check separated from registration could race in a multithreaded
  implementation. Tornado request handlers and response methods run on the
  event-loop thread; keep admission and insertion in one synchronous registry
  method.
- Cleanup regressions could permanently consume capacity. Existing timeout and
  disconnect tests remain, and new slot-reuse assertions cover every removal
  route.
- Browser clients may retry too aggressively. Return a small integer
  `Retry-After` hint while keeping client retry policy out of scope.

## Verification Plan

- Prove focused overload and slot-reuse tests fail before implementation.
- Run handler and Tornado runtime tests, then the full pinned package gate.
- Run the full gate from the repository root and an external directory with
  explicit timeouts.
- Reject isolated limit, admission, pre-allocation, response, cleanup, test,
  guidance, and completed-plan mutations.
- Audit exact intended paths, generated artifacts, dependency drift,
  whitespace, conflict markers, and credential-shaped additions.

## Sources

- Tornado `RequestHandler` documentation, including asynchronous handlers,
  response status methods, and connection-close cleanup:
  https://www.tornadoweb.org/en/stable/web.html
- Tornado asyncio integration documentation:
  https://www.tornadoweb.org/en/stable/asyncio.html
- GitHub Advisory Database, `GHSA-pw6j-qg29-8w7f` (affected through 6.5.6,
  patched in 6.5.7):
  https://github.com/advisories/GHSA-pw6j-qg29-8w7f
- Tornado 6.5.7 release notes:
  https://www.tornadoweb.org/en/stable/releases/v6.5.7.html

## Work Completed

- Added a 100-callback application-owned admission cap with a one-second retry
  hint and defensive registration enforcement.
- Rejected overload with HTTP 503 before future allocation while preserving
  delivery, timeout, cancellation, disconnect, and slot-reuse cleanup.
- Added deterministic unit/runtime regressions, canonical source contracts,
  synchronized guidance, and completed-plan enforcement.

## Verification Completed

- All 37 pinned offline tests passed, including pending-poll admission,
  overload rejection, retry metadata, and slot-reuse coverage.
- The first repository pinned `make check` passed compilation, documentation
  contracts, 17 workflow mutations, and all tests, then correctly failed when
  `pip-audit` identified Tornado 6.5.6 as affected by
  `GHSA-pw6j-qg29-8w7f`. After upgrading to 6.5.7, the repository and external-directory pinned `make check` passed with no known runtime vulnerabilities.
- Ten isolated hostile pending-poll mutations were rejected across the limit,
  admission, pre-allocation ordering, overload response, cleanup, tests,
  guidance, dependency patch level, and completed-plan status.
- No live network service, credential, browser, or production deployment was
  exercised; the sample remains loopback-bound and non-production.
