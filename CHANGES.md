# Changes

## 2026-06-08

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
