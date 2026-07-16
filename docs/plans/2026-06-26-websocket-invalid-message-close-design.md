# WebSocket Invalid Message Close Design

Status: Completed

## Problem

Invalid WebSocket frames initiate close code `1003`, but the handler remains in
the application client registry until Tornado later calls `on_close`. During
that close-handshake window, the rejected handler can still receive broadcasts
and a subsequent handler callback can still attempt to send.

## Options

1. Rely on `on_close`. This preserves the race window.
2. Add state flags around invalid handlers. This duplicates the registry's
   existing authority and creates another lifecycle state to synchronize.
3. Remove the invalid sender from the registry before initiating close.

## Decision

Use option 3. The registry already defines broadcast and sender authority, and
`on_close` uses idempotent `discard`, so early removal is safe. Centralize the
ordering in one helper used by malformed JSON and invalid body paths.

## Verification

The implementation plan requires focused tests, hostile mutations, and root and
external-directory `make check` before merge.
