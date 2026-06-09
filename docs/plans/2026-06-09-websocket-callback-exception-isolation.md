# WebSocket Callback Exception Isolation

## Status: Completed

## Context

The WebSocket chat sample broadcast each accepted message to every registered
callback. A single stale or failing client could raise from `write_message()`
and stop delivery to later clients in the same broadcast.

## Objectives

- Keep broadcasting valid messages to remaining WebSocket clients when one
  callback fails.
- Log failed WebSocket deliveries for debugging.
- Remove failed callbacks so stale clients do not fail every future broadcast.
- Add no-network regression coverage and a docs-plan guard.

## Work Completed

- Wrapped each WebSocket `write_message()` call in an exception boundary.
- Logged delivery failures and discarded the failing callback.
- Added a focused no-network test proving later clients still receive a
  message after an earlier callback fails.
- Extended `scripts/check_docs_plans.py` to require the WebSocket callback
  exception-isolation guard.
- Updated README, VISION, and CHANGES.

## Verification

- Negative: source review showed an uncaught `write_message()` exception would
  exit the broadcast loop before later callbacks ran.
- `python3 -m py_compile comet_chat/application.py socket_chat/application.py`
- `python3 scripts/check_docs_plans.py`
- `python3 -m pytest -q tests/test_chat_handlers.py`
- `make check`
- `make verify`
- `git diff --check`

## Follow-Up Candidates

- Add websocket-level integration coverage when a Tornado test server is
  available.
- Consider documenting explicit demo limits for stale client cleanup and
  in-memory callback storage.
