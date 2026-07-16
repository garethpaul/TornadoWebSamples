# Bound Per-Connection WebSocket Message Rates

## Status: Completed

## Context

The WebSocket sample bounds frame size and connected-client count, but an
admitted client can still submit valid messages without a rate bound. Each
accepted message is parsed and broadcast to every connected client, so one
connection can create disproportionate CPU and fan-out work while remaining
inside the existing size and admission limits.

This remains a tutorial control, not production abuse prevention. The narrow
goal is to make one process reject sustained per-connection floods
deterministically without adding accounts, IP reputation, shared storage, or a
distributed quota service.

## Priority

1. Bound valid and invalid incoming message attempts per WebSocket connection
   before JSON parsing and broadcast work.
2. Preserve ordinary chat behavior, the existing frame-size limit, and the
   process-wide connected-client cap.
3. Prove window expiry and overload closure without timing-sensitive sleeps.
4. Keep production authentication, per-IP quotas, and distributed accounting
   explicitly out of scope.

## Requirements

- **R1:** Each admitted WebSocket handler must own an independent message-rate
  window; one client's traffic must not consume another client's allowance.
- **R2:** The default must allow at most 10 incoming messages per rolling
  one-second window per connection.
- **R3:** Attempts above the limit must be rejected before JSON parsing or
  fan-out and close the offending connection with code `1008` and a stable
  reason.
- **R4:** Entries at or beyond the window boundary must expire so a connection
  can send again after the interval elapses.
- **R5:** Tests must use an injected monotonic clock for deterministic boundary
  coverage and exercise a real in-process WebSocket overload close.
- **R6:** Static and hostile-mutation contracts must reject missing,
  unconditional, shared, post-parse, or non-expiring enforcement.
- **R7:** README, security guidance, vision, changelog, agent guidance, and this
  completed plan must describe the control and its process-local limitations.

## Technical Decisions

- Add a small `MessageRateLimiter` value owned by each `MessageHandler`. It
  stores only timestamps within the rolling window and accepts an injectable
  clock for deterministic unit tests.
- Check the limiter at the start of `on_message`, before decoding untrusted
  JSON. Close with policy-violation code `1008`; reserve the existing `1013`
  close for global client-cap overload.
- Allow `Application` to override the per-connection count and window only for
  focused runtime tests. Production defaults remain module constants.
- Do not add delayed queues or retries. Once a connection exceeds the policy,
  closing it bounds further work and keeps the sample behavior understandable.

## Implementation Units

### U1. Enforce a rolling per-connection window

- **Files:** `socket_chat/application.py`
- **Outcome:** Every admitted handler owns an independent limiter and closes
  before parsing when its rolling allowance is exhausted.

### U2. Prove boundaries and mutation sensitivity

- **Files:** `tests/test_chat_handlers.py`, `tests/test_tornado6_runtime.py`,
  `scripts/check_docs_plans.py`,
  `scripts/test_websocket_message_rate_contract.py`, `Makefile`
- **Outcome:** Pure-clock tests cover allowance, overload, expiry, and client
  isolation; the in-process runtime confirms close code and reason; hostile
  mutations prove the enforcement cannot be removed or moved after parsing.

### U3. Document the tutorial boundary

- **Files:** `README.md`, `SECURITY.md`, `VISION.md`, `CHANGES.md`, `AGENTS.md`,
  `docs/plans/2026-06-17-websocket-message-rate-limit.md`
- **Outcome:** Guidance distinguishes the process-local per-connection control
  from authentication, per-IP, and distributed production rate limiting.

## Verification

- Run focused documentation, limiter, handler, runtime, and mutation tests.
- Run the pinned repository and external-directory `make check` gates.
- Audit the exact diff, generated artifacts, bytecode, package outputs, and
  credential patterns.
- Require one bounded exact-head hosted snapshot after push.

## Verification Results

- Pinned Tornado 6.5.7 focused handler and runtime tests passed: 35 passed,
  including deterministic rolling-window expiry, per-connection isolation, and
  an in-process `1008` overload close.
- Nine hostile WebSocket message-rate mutations were rejected across missing,
  unconditional, shared, post-parse, non-expiring, count-disabled, and
  wrong-close-code and retained-client variants.
- repository and external-directory pinned `make check` passed compilation,
  documentation contracts, 17 workflow mutations, the full 43-test suite,
  dependency consistency, and vulnerability auditing.
- No live service, public listener, account, credential, proxy topology, or
  distributed worker deployment was exercised.

## Scope Boundaries

- Do not add authentication, accounts, cookies, IP identity, proxy trust,
  persistence, Redis, shared counters, or distributed coordination.
- Do not change message length, frame size, client admission, Comet behavior,
  browser rendering, dependency versions, or workflow topology.
- Do not claim protection across processes or hosts.
