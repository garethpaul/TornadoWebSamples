# Comet Callback Isolation

## Status: Completed

## Context

The comet chat `Messages` helper kept its callback queue as a class-level list.
The application normally creates one `Messages` instance, but class-level
storage means independent message stores can share waiting long-poll callbacks
in tests or future demos.

## Objectives

- Keep each `Messages` instance's waiting callback queue isolated.
- Preserve the existing behavior where adding a message notifies callbacks and
  clears the queue.
- Cover the behavior with focused no-network handler tests.

## Work Completed

- Moved `callbacks` initialization into `Messages.__init__`.
- Added a regression test proving two `Messages` instances do not share
  callbacks.
- Updated README, VISION, and CHANGES with the new lifecycle guard.

## Verification

- `python3 -m pytest -q tests/test_chat_handlers.py`
- `make lint`
- `make test`
- `make build`
- `make check`
- `make verify`
- `git diff --check`

## Follow-Up Candidates

- Document long-polling callback behavior separately from the WebSocket sample.
- Add a small test for callback cleanup when a waiting request is abandoned.
