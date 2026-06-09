# Changes

## 2026-06-09

- Moved comet chat callback storage onto each `Messages` instance.
- Added handler coverage so long-poll callbacks cannot leak across
  independent message stores.
- Added an explicit same-host WebSocket origin check to the socket chat sample.
- Added no-network handler coverage for accepted and rejected origins.

## 2026-06-08

- Added server-side chat message validation for blank, non-string, oversized,
  and malformed WebSocket inputs.
- Added `make check` as the shared repository verification alias.
- Escaped browser-side chat rendering by appending messages as text nodes in
  both comet and WebSocket samples.
- Fixed the WebSocket browser error logger to call `console.error`.
- Added focused static asset tests for client-side message rendering.
- Added a Makefile verification gate for Python syntax checks and focused
  chat-handler tests.
- Added dependency metadata for the legacy Tornado 4 sample API.
- Made WebSocket close handling idempotent by discarding absent callbacks.
- Added generated Python artifact ignores and documented verification steps.
- Added canonical `docs/plans` coverage and a docs-plan checker under
  `make check`.
- Kept browser chat clients on same-origin message endpoints and switched the
  shared external reset stylesheet to HTTPS.
