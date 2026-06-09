# Comet Callback Exception Isolation

## Status: Completed

## Context

`Messages.add()` snapshots and clears waiting comet callbacks before dispatch.
That protects callbacks registered during dispatch, but an exception from one
waiting callback still stopped delivery to the remaining callbacks in the same
message batch.

## Objectives

- Preserve snapshot-and-clear callback dispatch behavior.
- Keep later waiting callbacks receiving a message when an earlier callback
  raises.
- Log failed callback delivery for debugging without exposing message contents
  in the client response path.
- Add no-network regression and static coverage for the dispatch boundary.

## Work Completed

- Wrapped comet callback delivery in a narrow dispatch loop exception boundary.
- Logged callback delivery failures with `logger.exception`.
- Added no-network handler coverage for a failing callback followed by a
  healthy callback.
- Extended `scripts/check_docs_plans.py` to preserve the exception-isolation
  guard.
- Updated README, VISION, and CHANGES.

## Verification

- Negative: `python3 -m pytest -q tests/test_chat_handlers.py` failed before
  the fix because the first callback exception escaped `Messages.add()`.
- `python3 -m pytest -q tests/test_chat_handlers.py`
- `python3 -m py_compile comet_chat/application.py socket_chat/application.py`
- `python3 scripts/check_docs_plans.py`
- `make check`
- `make verify`
- `git diff --check`

## Follow-Up Candidates

- Add equivalent broadcast exception isolation for the WebSocket sample.
- Document long-poll callback behavior separately from the WebSocket sample.
