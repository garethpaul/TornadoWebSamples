# Effective Bound Pinning For Reviewed Limits

## Status: Completed

## Context

Every reviewed limit in this repository is guarded by a static contract in
`scripts/check_docs_plans.py` (and, for the message-rate limiter, by
`scripts/test_websocket_message_rate_contract.py`). Three of those guards
compared source text with a bare substring:

- `"MAX_WEBSOCKET_CLIENTS = 100"`
- `"MAX_WEBSOCKET_MESSAGES_PER_WINDOW = 10"`
- `"COMET_LONG_POLL_TIMEOUT_SECONDS = 25"`

A bare substring is a prefix match. `"MAX_WEBSOCKET_CLIENTS = 100"` is contained
in `MAX_WEBSOCKET_CLIENTS = 100000`, so a 1000x widening of the client cap
satisfied the contract, while the value-preserving refactor
`MAX_WEBSOCKET_CLIENTS = 10 * 10` did not contain the pinned text and was
rejected. The guard therefore inverted: it accepted a widening and rejected an
honest restatement of the same number, which is the signature of a check that
reads text and has no access to meaning.

No other layer closed the gap for these three bounds, because each bound's own
runtime coverage injected an explicit value and so could not observe the shipped
default:

- `tests/test_chat_handlers.py` constructed `Application(max_chat_clients=1)`
  and `MessageRateLimiter(2, 1, ...)`.
- `tests/test_tornado6_runtime.py` constructed the socket application with
  `max_chat_clients=1, max_messages_per_window=1, message_rate_window_seconds=60`.
- `test_comet_handler_times_out_and_cleans_up_long_poll` asserted
  `timeout == comet.COMET_LONG_POLL_TIMEOUT_SECONDS`, comparing the value to
  itself, which holds for any value.
- `test_long_poll_timeout_returns_no_content_and_cleans_up` overwrote
  `COMET_LONG_POLL_TIMEOUT_SECONDS = 0.01` before exercising the handler.

The documentation contracts assert the strings "100 connected clients",
"10 messages per second", and "25 seconds with `204 No Content`" in
`README.md`/`SECURITY.md`/`AGENTS.md`, but those are document text and cannot
observe the module constants, so the docs and the code could disagree silently.

The correct mechanism already existed in-repo and simply stopped one line short.
`MAX_PENDING_COMET_POLLS` and `COMET_OVERLOAD_RETRY_SECONDS` were already pinned
with an anchored whole-line regex (`^NAME = VALUE$`), and
`MAX_WEBSOCKET_FRAME_SIZE`/`MAX_COMET_REQUEST_BODY_SIZE` already had fixtures
asserting the effective value against literals. Both of those mechanisms reject
the same widening that the three substring-pinned bounds accepted.

## Goals

- Pin every reviewed numeric bound in both samples to a whole source line so a
  widening cannot prefix-match the reviewed literal.
- Assert each bound's *effective* default value at runtime against a literal, in
  a fixture that constructs the application with no injected limit.
- Prove the message-rate guards reject widening and fixture removal through the
  existing executed mutation harness.

## Non-Goals

- Changing any shipped limit, close code, or sample behavior. The values 100,
  10, 1, 25, 500, 4096, 1013, and 1008 are unchanged.
- Adding authentication, distributed accounting, or production abuse protection.
- Reworking the Make authority, workflow, or dependency-audit contracts, which
  were probed and left unchanged.

## Design

### Anchored Whole-Line Source Pins

`scripts/check_docs_plans.py` gains one `(name, value)` table per sample,
checked with `re.search(rf"^{name} = {value}$", source, re.MULTILINE)`, reusing
the idiom already used for `MAX_PENDING_COMET_POLLS`. The redundant bare
substring pins for those same constants are removed so the weaker mechanism
cannot be mistaken for coverage. `scripts/test_websocket_message_rate_contract.py`
pins its three rate constants the same way.

### Effective-Value Fixtures

An anchored source pin proves what the reviewed line *says*, not what the module
*exports*: appending a second `MAX_WEBSOCKET_CLIENTS = 100000` later in the file
leaves the pinned line byte-identical while the last assignment wins. Three
fixtures in `tests/test_chat_handlers.py` therefore load each module, construct
`Application()` with no arguments, and assert the effective value against
literals, including a behavioral assertion (admit exactly 100 clients and reject
the 101st; allow exactly 10 messages and reject the 11th; observe the literal
`25` handed to `asyncio.wait_for`).

### Executed Mutation Controls

`test_websocket_message_rate_contract.py` gains three source mutations (widened
limit, appended multiplier, shortened window) and two coverage mutations
(deleting and self-referencing the new default-rate fixture), so the contract
proves it rejects both the widening and the removal of the only observer of the
shipped default.

## Implementation Units

### U1. Anchor The Source Pins

**Files:** `scripts/check_docs_plans.py`,
`scripts/test_websocket_message_rate_contract.py`

### U2. Observe The Effective Defaults

**Files:** `tests/test_chat_handlers.py`

### U3. Prove Rejection

**Files:** `scripts/test_websocket_message_rate_contract.py`, this plan

## Risks And Mitigations

- An anchored pin also rejects a value-preserving refactor such as `10 * 10`.
  This matches the pre-existing repository convention for
  `MAX_PENDING_COMET_POLLS` ("must be declared exactly as"), and the runtime
  fixtures independently assert meaning, so a deliberate restatement is a
  one-line contract update rather than a silent change.
- A source pin cannot see an appended redefinition. The runtime fixtures cover
  that case and were verified to catch it.
- A fixture could be deleted. Its name and distinctive assertions are pinned in
  `check_docs_plans.py`, and the rate fixture's removal is additionally rejected
  by an executed mutation control.

## Verification Plan

- Re-baseline `make verify` on a clean tree before and after the change.
- Probe each bound in both directions: same value in a different spelling, and a
  wider value in the pinned spelling.
- Probe the fix itself: append-redefinition, default-argument rebind, fixture
  deletion, and defeating each layer separately.

## Work Completed

- Anchored ten reviewed numeric bounds across both samples to whole source
  lines and removed seven redundant prefix-matchable substring pins.
- Added three fixtures asserting the effective default client cap, message rate,
  and long-poll timeout against literals with no injected limit.
- Extended the message-rate contract to 12 source and 2 coverage mutations.
- Changed no shipped limit or sample behavior.

## Verification Completed

- `make verify` passed on a clean tree before the change (45 tests) and after
  it (48 tests), including the 35-case Makefile root/authority control, the
  documentation contracts, 5 dependency-audit mutations, 18 workflow mutations,
  and 12 source plus 2 coverage message-rate mutations.
- Before the change, measured with `make verify`: `MAX_WEBSOCKET_CLIENTS = 100000`
  (effective 100000), `MAX_WEBSOCKET_CLIENTS = 100 * 10**12` (effective 10^14),
  `MAX_WEBSOCKET_MESSAGES_PER_WINDOW = 10000`, and
  `COMET_LONG_POLL_TIMEOUT_SECONDS = 2500` each exited 0, while the
  value-preserving `10 * 10`, `5 * 2`, and `5 * 5` restatements each exited 2.
  After the change, all four widenings exit 2.
- After the change, an appended `MAX_WEBSOCKET_CLIENTS = 100000` that leaves the
  anchored line byte-identical (effective value 100000) is rejected by the
  runtime fixture, and a `max_chat_clients=MAX_WEBSOCKET_CLIENTS * 1000` default
  rebind that leaves every constant pin byte-identical is also rejected.
  Widening the source with the anchored pin repaired is caught by the fixture;
  widening it with the fixture literals repaired is caught by the anchored pin
  and by the fixture's behavioral assertion.
- `MAX_MESSAGE_LENGTH`, `MAX_WEBSOCKET_FRAME_SIZE`, `MAX_COMET_REQUEST_BODY_SIZE`,
  `MAX_PENDING_COMET_POLLS`, and `COMET_OVERLOAD_RETRY_SECONDS` were probed and
  already rejected the same widening; they are unchanged.
- Not run in this environment: the `pip check` and `pip_audit` steps of the full
  `make check` target. `pip_audit` requires network access and `ensurepip`, both
  unavailable in the offline verification sandbox, so the audit steps were not
  exercised and no claim is made about them. Every probe above was run through
  `make verify`, which contains all source, contract, and test layers touched by
  this change. Hosted CI runs the full `make check` on Python 3.10, 3.12, 3.14.
- No public listener, live external traffic, credentials, browser session, or
  production deployment was exercised; the samples remain loopback-bound.
