# WebSocket Frame Limit

## Status: Completed

## Context

The WebSocket handler validated decoded chat bodies at 500 characters, but the
Tornado application retained the framework's much larger default frame limit.
An unauthenticated local client could therefore send a multi-megabyte frame
that the server would buffer and decode before rejecting its chat body.

## Objectives

- Bound WebSocket transport input before JSON decoding.
- Keep the existing 500-character semantic message limit unchanged.
- Leave enough byte capacity for JSON syntax and 500 multi-byte characters.
- Protect the transport setting with focused tests and static contracts.

## Work Completed

- Defined a reviewed 4096-byte WebSocket frame limit.
- Applied the limit through Tornado's `websocket_max_message_size` application
  setting so oversized frames are rejected by the protocol layer.
- Added regression coverage for the application setting and the required
  capacity above the semantic character limit.
- Extended the docs checker to require the setting, tests, and completed plan.
- Updated security, maintenance, vision, and change documentation.

## Verification

- Fresh environment with Tornado 6.5.7 and pytest 9.0.3
- `python -m pytest -q tests/test_chat_handlers.py`
- `make check`
- Mutations removing or weakening the frame setting and regression test
- `git diff --check`

The tests are local and in-process; no public service or external network is
used.
