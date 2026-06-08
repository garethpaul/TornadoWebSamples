# Client Rendering Gate

## Problem

Both browser chat clients appended received messages by interpolating user input
into HTML strings. That made the demos easier to misuse as unsafe examples. The
WebSocket client also referenced an undefined `message` variable before
appending received data, which could stop message rendering.

## TDD Evidence

1. Added `tests/test_static_assets.py` to check the CoffeeScript sources and
   checked-in JavaScript outputs for text-node rendering.
2. Ran the focused static asset tests before implementation and confirmed they
   failed on the unsafe append patterns and the WebSocket console typo.
3. Updated both client implementations to append `li` elements through
   `.text(...)`, fixed the console error call, and reran the full verification
   gate.

## Verification

- `make lint`
- `python3 -m pytest -q tests/test_static_assets.py`
- `make test`
- `make build`
- `make verify`
- `git diff --check`
