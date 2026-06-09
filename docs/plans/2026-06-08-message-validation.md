# Chat Message Validation

## Status: Completed

## Context

The chat demos escaped message rendering in the browser, but server handlers
still accepted blank comet messages and assumed every WebSocket frame was valid
JSON containing a `body`. Malformed or oversized inputs could raise through the
sample handler or broadcast low-quality data.

## Objectives

- Preserve the long-polling and WebSocket chat examples.
- Trim and bound user messages before broadcasting.
- Reject blank, non-string, oversized, and malformed message inputs.
- Keep invalid WebSocket frames from raising through the handler.
- Cover the behavior with no-network tests.

## Work Completed

- Added message normalization helpers to both chat samples.
- Rejected invalid comet messages with HTTP 400.
- Closed invalid WebSocket frames with code `1003` and a stable reason.
- Added focused tests for normalization, invalid frames, and trimmed
  broadcasts.
- Updated README, VISION, and CHANGES.

## Verification

- `python3 -m py_compile comet_chat/application.py socket_chat/application.py`
- `python3 scripts/check_docs_plans.py`
- `python3 -m pytest -q`
- `make check`
- `make verify`
- `git diff --check`

## Follow-Up Candidates

- Document separate comet and WebSocket validation caveats in the README.
- Add browser-side message length hints to match the server-side limit.
