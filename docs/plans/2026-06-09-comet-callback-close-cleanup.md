# Comet Callback Close Cleanup

## Status: Completed

## Context

The comet chat sample stores waiting long-poll callbacks until the next message
arrives. If a waiting client disconnects before a message is posted, its
callback should be removed so the in-memory queue does not keep abandoned
request callbacks.

## Objectives

- Preserve the simple long-polling comet chat flow.
- Remove abandoned waiting callbacks when a connection closes.
- Cover cleanup behavior without live network calls.

## Work Completed

- Added `Messages.remove_callback()` for idempotent callback removal.
- Stored the active message callback on `MessageHandler` while a long-poll
  request waits.
- Added `MessageHandler.on_connection_close()` to remove the waiting callback
  when the client disconnects.
- Added no-network tests for callback removal and connection-close cleanup.
- Extended the docs-plan checker with source guards for the cleanup API.
- Updated README, VISION, and CHANGES.

## Verification

- Negative check before implementation:
  `python3 -m pytest -q tests/test_chat_handlers.py` failed because
  `Messages.remove_callback()` was missing and `on_connection_close()` did not
  remove the waiting callback.
- `python3 -m pytest -q tests/test_chat_handlers.py`
- `python3 scripts/check_docs_plans.py`
- `python3 -m py_compile comet_chat/application.py socket_chat/application.py`
- `make check`
- `make verify`
- `git diff --check`
