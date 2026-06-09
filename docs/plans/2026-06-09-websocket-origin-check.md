# WebSocket Origin Check

## Status: Completed

## Context

The socket chat browser client now connects to the same-origin `/message`
endpoint, but the server-side WebSocket origin policy was implicit. Making the
origin check explicit keeps the demo behavior clear across Tornado versions and
prevents accidental cross-origin use without adding authentication or
production-only complexity.

## Objectives

- Preserve the simple WebSocket chat sample.
- Accept WebSocket origins only when they match the request host.
- Cover origin behavior without live sockets or network calls.

## Work Completed

- Added `MessageHandler.check_origin` to compare `Origin` with the request
  `Host`.
- Accepted both HTTP and HTTPS same-host origins for local/proxied demos.
- Added no-network tests for same-host, case-normalized, blank, and cross-host
  origins.
- Updated README, VISION, and CHANGES.

## Verification

- `python3 -m pytest -q tests/test_chat_handlers.py`
- `python3 -m py_compile socket_chat/application.py`
- `make check`
- `make verify`
- `git diff --check`

## Follow-Up Candidates

- Add README caveats for deploying the demos behind reverse proxies.
- Document separate production requirements for authentication, rate limits, and
  persistent storage.
