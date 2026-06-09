# Chat Client Endpoint Guard

## Status: Completed

## Context

The sample browser clients still contained hard-coded localhost message
endpoints and an HTTP stylesheet URL. These examples should keep local demo
behavior simple without encouraging protocol-relative, insecure, or
environment-specific client URLs.

## Objectives

- Keep comet AJAX requests on the same-origin `/message` endpoint.
- Build WebSocket URLs from the current page host and choose `ws` or `wss`
  based on the page protocol.
- Load the shared YUI reset stylesheet over HTTPS.
- Cover the client endpoint and external asset contract in static tests.

## Work Completed

- Updated comet CoffeeScript and generated JavaScript to use `/message`.
- Updated WebSocket CoffeeScript and generated JavaScript to use
  `window.location.host`.
- Switched both templates to the HTTPS YUI reset stylesheet URL.
- Added static asset tests and documented the guard in README, VISION, and
  CHANGES.

## Verification

- `python3 -m pytest -q tests/test_static_assets.py`
- `make check`
- `make verify`
- `git diff --check`

## Follow-Up Candidates

- Document separate local deployment notes for comet and WebSocket demos.
- Replace the legacy YUI reset dependency if the sample UI is modernized.
