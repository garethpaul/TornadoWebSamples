# Message Length Hint

## Status: Completed

## Context

Both Tornado chat handlers trim and reject messages longer than
`MAX_MESSAGE_LENGTH`, currently 500 characters. The browser templates still
presented an unbounded text input, so users could type messages that the server
would reject without any local hint.

## Objectives

- Preserve the existing server-side message validation.
- Add browser-side length hints to both chat templates.
- Keep static asset tests aligned with the server-side 500-character limit.

## Work Completed

- Added `maxlength="500"` to the comet chat message input.
- Added `maxlength="500"` to the WebSocket chat message input.
- Added static template coverage for the message length hint.
- Documented the browser hint guard in README, VISION, and CHANGES.

## Verification

- `python3 -m pytest -q tests/test_static_assets.py`
- `python3 -m pytest -q`
- `make check`
- `make verify`
- `git diff --check`
