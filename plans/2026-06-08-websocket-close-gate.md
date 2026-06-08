# WebSocket Close Gate

## Problem

The repository had no local verification command or dependency metadata. The
WebSocket sample used `callbacks.remove(self)` during close, so a duplicate
close or close without a matching open raised `KeyError`.

## TDD Evidence

1. Added pytest coverage for comet message dispatch and WebSocket close/message
   behavior.
2. Ran `make test` before implementation changes and confirmed the close test
   failed with `KeyError`.
3. Switched close handling to `discard`, added dependency metadata, and reran
   the full verification gate.

## Verification

- `make lint`
- `make test`
- `make build`
- `make verify`
- `git diff --check`
