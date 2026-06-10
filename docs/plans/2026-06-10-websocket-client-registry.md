# WebSocket Client Registry Isolation

Status: Completed

## Goal

Keep connected WebSocket clients owned by the `Application` that accepted
them, preventing separate application instances in the same process from
sharing broadcasts through handler class state.

## Implementation

- Initialize a fresh `chat_clients` set on every socket chat `Application`.
- Register, remove, broadcast to, and discard failed clients through the
  handler's owning application.
- Add a regression test proving two application instances have independent
  client registries.
- Extend the static documentation gate to reject a class-level callback set.

## Verification

- `python -m pytest -q`
- `make check`
- Mutation check: restoring `callbacks = set()` on `MessageHandler` must fail
  the static registry-ownership contract.
