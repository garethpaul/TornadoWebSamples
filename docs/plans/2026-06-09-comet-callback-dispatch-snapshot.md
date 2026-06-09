# Comet Callback Dispatch Snapshot

## Status: Completed

## Context

The comet chat message store fired callbacks by iterating the live callback
list and clearing it afterward. If a callback registered another long-poll wait
during dispatch, the new wait could be consumed by the current message or wiped
out by the final reset. Long-poll callbacks should represent one pending
message wait and callbacks added during dispatch should wait for the next
message.

## Objectives

- Snapshot the waiting comet callbacks before dispatch.
- Clear the active callback queue before callbacks fire.
- Preserve callbacks registered during dispatch for the next message.
- Add focused no-network coverage for the dispatch ordering.
- Keep the guard part of `make check`.

## Work Completed

- Updated `Messages.add` to snapshot and clear callbacks before invoking them.
- Added a regression test that registers a new callback during dispatch and
  verifies it receives only the next message.
- Extended the docs-plan checker to require the dispatch snapshot behavior.
- Updated README, VISION, and CHANGES.

## Verification

- `python3 -m pytest -q tests/test_chat_handlers.py`
- `python3 scripts/check_docs_plans.py`
- `make check`
- `git diff --check`

## Follow-Up Candidates

- Add explicit tests for callback exception behavior during comet dispatch.
- Document long-polling caveats separately from the WebSocket sample.
