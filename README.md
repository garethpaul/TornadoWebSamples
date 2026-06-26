# TornadoWebSamples

<!-- README-OVERVIEW-IMAGE -->
![Project overview](docs/readme-overview.svg)

## Overview

`garethpaul/TornadoWebSamples` contains two local Tornado chat tutorials: an
HTTP long-polling Comet example and a WebSocket example.

Both examples are unauthenticated, process-local, and in-memory. They demonstrate
transport and handler behavior; they are not production chat services.

## Repository Contents

- `comet_chat/application.py` - long-poll handlers, callback admission, XSRF,
  request-body limits, and loopback server entry point
- `socket_chat/application.py` - WebSocket origin, frame, client, message-rate,
  validation, and broadcast behavior
- `comet_chat/static/` and `socket_chat/static/` - dependency-free browser clients
  that render received messages through text nodes
- `tests/` - unit, in-process HTTP/WebSocket, and static asset regressions
- `requirements.txt` and `test-requirements.txt` - exact runtime and verification
  dependency pins
- `Makefile` and `scripts/` - canonical tests, audits, workflow contracts, and
  adversarial Make authority checks
- `docs/plans/` - completed maintenance evidence for the current baseline

## Getting Started

### Supported Runtime

- Git
- CPython 3.10 or newer; CI verifies CPython 3.10, 3.12, and 3.14
- Tornado is pinned to 6.5.7 exactly in `requirements.txt`

### Setup

```bash
git clone https://github.com/garethpaul/TornadoWebSamples.git
cd TornadoWebSamples
python3 -m pip install -r requirements.txt -r test-requirements.txt
```

The two servers cannot bind to port `8000` at the same time. Run one tutorial
per terminal or stop one before starting the other.

## Running or Using the Project

- Run the Comet sample with `python3 comet_chat/application.py` or the WebSocket
  sample with `python3 socket_chat/application.py`.
- Both tutorial servers bind to `127.0.0.1:8000` by default so the
  unauthenticated chat endpoint is not exposed to the local network.
- Template and static asset paths are resolved from
  each sample directory, so either command can be launched from another
  working directory.

### Comet Long-Poll Tutorial

The browser keeps one same-origin `GET /message` request waiting for the next
message. A `POST /message` submits a message, and the in-process message store
broadcasts it to the callbacks currently waiting in that application instance.
Callback queues are snapshot before dispatch, abandoned requests are removed,
and one callback failure does not stop delivery to later callbacks.

#### Comet Input Validation

- Comet request bodies are capped at 4096 bytes by the standalone HTTP server
  before Tornado buffers or parses form data. This 4096-byte request-body limit
  is separate from the semantic message limit.
- Tornado XSRF cookies are enabled, and a Comet post without the rendered XSRF
  token is rejected.
- The `message` form field is trimmed, must be non-empty, and has a
  500-character semantic message limit. The browser `maxlength` is aligned with
  that server rule.
- The browser sends and polls only same-origin `/message` endpoints and renders
  returned text with `textContent`.

#### Comet Operating Caveats

- Comet long polls expire after 25 seconds with `204 No Content`; the browser
  treats that as normal and starts another poll.
- Comet accepts at most 100 pending long polls per process. Temporary overload
  returns `503 Service Unavailable` with `Retry-After: 1`.
- Messages are delivered only to callbacks waiting at dispatch time. There is
  no history, replay, persistence, authentication, user identity, or
  cross-process fanout.
- The callback cap is process-wide, not a per-user or per-IP quota. A production
  service still needs authentication, durable storage, distributed admission,
  observability, and an explicit privacy model.

### WebSocket Tutorial

The browser opens a same-origin `ws://` or `wss://` connection to `/message`,
sends JSON objects with a `body` field, and renders received message text with
`textContent`. The application broadcasts each accepted body to the clients in
that application instance. Tests prove synchronous and asynchronous delivery
failures remove only the failed client and do not stop later deliveries.

#### WebSocket Input Validation

- The upgrade accepts only an `Origin` matching the request host.
- Tornado enforces a 4096-byte frame limit before JSON decoding; oversized
  frames close with code `1009`.
- A frame must decode to an object with a string `body`. The body is trimmed,
  must be non-empty, and uses the same 500-character semantic message limit;
  invalid senders leave the broadcast registry before closing with code `1003`.
- A registered connection may send at most 10 messages per second. Sustained
  overload removes that client and closes it with policy code `1008` before
  JSON parsing or broadcast.

#### WebSocket Operating Caveats

- WebSocket accepts at most 100 connected clients per process. Temporary
  overload closes the rejected connection with code `1013` (`Try Again Later`).
- Client membership and messages are process-local and in-memory. There is no
  history, replay, persistence, authentication, user identity, or
  cross-process fanout.
- The browser logs connection errors but does not implement reconnect, resume,
  acknowledgement, or delivery guarantees.
- The connection and message-rate limits are tutorial resource bounds, not
  authentication, per-IP quotas, distributed rate limiting, or abuse defense.

## Testing and Verification

- `make check` runs Python syntax checks, focused chat-handler tests, a real
  in-process HTTP long-poll and XSRF tests, message validation tests, static
  asset checks, dependency consistency checks, and a vulnerability audit of
  the declared runtime dependency graph.
- The handler suite covers callback and client isolation, abandoned callback
  cleanup, snapshot dispatch ordering, synchronous and asynchronous broadcast
  failures, message normalization, admission limits, close codes, XSRF, origin
  checks, frame bounds, and message-rate enforcement.
- `make check` also requires completed canonical plans under `docs/plans`.
- Runtime dependencies pin Tornado 6.5.7, which fixes
  `GHSA-pw6j-qg29-8w7f`; the audit gate rejects affected dependency states.
- Development dependencies pin msgpack 1.2.1, which fixes
  `GHSA-6v7p-g79w-8964`; `make check` audits runtime and development
  requirement sets separately.
- GitHub Actions installs the pinned runtime and test requirements, then runs
  the same `make check` baseline on Python 3.10, 3.12, and 3.14 for pushes,
  pull requests, and manual runs. The workflow uses Ubuntu 24.04, read-only
  permissions, credential-free checkout, a ten-minute timeout, concurrency
  cancellation, and commit-pinned Node 24 actions. Dependency-free mutation
  tests reject contradictory or relocated credential settings and other
  workflow policy regressions.
- Within the checked-in Makefile boundary, verification ignores ordinary
  caller root and shell assignments, rejects later single-colon replacement of
  all seven public aliases, rejects non-executing/error-ignoring Make modes,
  and rejects Make-syntax Python overrides. Arbitrary caller Make programs are
  outside that boundary: GNU Make `override` directives, caller-added double-colon
  recipes, and startup files can execute with Make-level authority before or
  alongside repository recipes. PATH resolution of the default `python3` is
  also caller-controlled. Hosted verification invokes
  `/usr/bin/make check` without startup or extra `-f` files.

When the required SDK or runtime is unavailable, use static checks and source review first, then verify on a machine that has the matching platform toolchain.

## Configuration and Secrets

- No required secret or credential file was identified in the repository scan. If you add integrations later, keep secrets out of git.

## Security and Privacy Notes

- Review changes touching network requests, sockets, or service endpoints; examples from the scan include comet_chat/application.py, comet_chat/templates/index.html, socket_chat/application.py, socket_chat/static/socketchat.js, and 1 more.
- Review changes touching file, media, JSON, XML, CSV, OCR, or data parsing; examples from the scan include comet_chat/application.py, comet_chat/static/cometchat.js, socket_chat/static/socketchat.js.
- Browser chat clients should use same-origin message endpoints rather than
  hard-coded localhost URLs.
- Browser templates must remain self-contained instead of loading third-party
  CDN scripts or stylesheets.

## Maintenance Notes

- See `SECURITY.md` for vulnerability reporting and safe research guidance.
- See `VISION.md` for project direction and contribution guardrails.
- See `docs/plans/2026-06-08-tornado-web-samples-baseline.md` for the
  canonical Tornado chat sample baseline.
- See `docs/plans/2026-06-08-message-validation.md` for chat message input
  validation coverage.
- See `docs/plans/2026-06-10-offline-browser-clients.md` for native browser
  clients and comet XSRF enforcement.
- See `docs/plans/2026-06-12-websocket-frame-limit.md` for the protocol-level
  WebSocket input bound.
- See `docs/plans/2026-06-12-websocket-async-delivery-failures.md` for delayed
  WebSocket delivery failure cleanup.
- See `docs/plans/2026-06-17-websocket-client-cap.md` for bounded WebSocket
  admission, overload close semantics, and slot-reuse coverage.
- See `docs/plans/2026-06-17-websocket-message-rate-limit.md` for the
  per-connection rolling message-rate boundary.
- See `docs/plans/2026-06-26-websocket-invalid-sender-cleanup.md` for immediate
  registry removal when malformed or invalid messages are policy-closed.
- See `docs/plans/2026-06-20-development-dependency-audit.md` for the
  development dependency pin and dual-scope audit contract.
- See `docs/plans/2026-06-09-chat-client-endpoints.md` for client endpoint and
  external asset URL coverage.
- See `docs/plans/2026-06-09-websocket-origin-check.md` for same-host
  WebSocket origin coverage.
- See `docs/plans/2026-06-09-comet-callback-isolation.md` for long-poll
  callback isolation coverage.
- See `docs/plans/2026-06-09-message-length-hint.md` for browser message
  length hint coverage.
- See `docs/plans/2026-06-09-comet-callback-close-cleanup.md` for abandoned
  long-poll callback cleanup coverage.
- See `docs/plans/2026-06-09-comet-callback-dispatch-snapshot.md` for comet
  callback dispatch ordering coverage.
- See `docs/plans/2026-06-09-comet-callback-exception-isolation.md` for comet
  callback delivery exception isolation.
- See `docs/plans/2026-06-09-websocket-callback-exception-isolation.md` for
  WebSocket callback delivery exception isolation.
- See `docs/plans/2026-06-10-websocket-client-registry.md` for WebSocket client
  registry ownership and application-isolation coverage.
- See `docs/plans/2026-06-10-ci-baseline.md` for the Tornado 6 runtime and CI
  modernization.
- See `docs/plans/2026-06-14-make-root-override-protection.md` for repository-
  anchored Make verification under hostile root assignments.
- See `docs/plans/2026-06-21-make-authority-isolation.md` for executable Make
  startup, flag, shell, tool, and root trust-boundary coverage.
- See `docs/plans/2026-06-26-tornado-transport-guide.md` for the supported
  runtime, transport-specific validation, broadcast, and caveat guide.

## Contributing

Keep changes small and tied to the project that is already present in this repository. For code changes, document the toolchain used, avoid committing generated dependency directories or local configuration, and update this README when setup or verification steps change.
