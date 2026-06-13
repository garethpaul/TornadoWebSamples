---
title: Comet Request Body Limit
date: 2026-06-13
type: implementation-plan
status: completed
---

# Comet Request Body Limit

Status: Completed

## Summary

Bound the standalone comet sample's HTTP request bodies before Tornado buffers
or parses form data. The transport limit will complement, not replace, the
existing 500-character semantic message validation.

## Problem Frame

`comet_chat/application.py` rejects blank and oversized chat messages after
calling `RequestHandler.get_argument`, but its `HTTPServer` still uses
Tornado's substantially larger default request-body allowance. An
unauthenticated local client can therefore make the sample buffer a large form
body before the handler rejects its message.

Tornado exposes `HTTPServer(max_body_size=...)` specifically for applying a
connection-level body limit. The sample already constructs `HTTPServer`
directly, so the narrowest fix is to make that boundary explicit and shared by
the executable path and runtime tests.

## Requirements

- R1. Define a named, positive comet request-body limit that leaves room for a
  valid 500-character multipart form submission.
- R2. Pass the limit to every standalone comet `HTTPServer` construction path
  before request body parsing.
- R3. Preserve the existing message normalization, XSRF protection, long-poll
  timeout, loopback binding, and browser behavior.
- R4. Add deterministic in-process coverage that accepts a valid message and
  rejects an oversized request at the HTTP transport boundary.
- R5. Extend static contracts and maintenance documentation so removal or
  weakening of the limit fails the canonical gate.

## Key Technical Decisions

- **Apply the limit at `HTTPServer`.** Handler-level length checks run after
  request buffering and therefore cannot enforce the intended resource bound.
- **Use one reviewed 4096-byte constant.** This matches the WebSocket frame
  budget, comfortably exceeds the semantic message limit plus multipart
  framing, and keeps the tutorial's limits easy to explain.
- **Share server options with tests.** A small server-options helper avoids a
  test-only configuration that could drift from the executable path.

## Scope Boundaries

This change does not add authentication, deployment proxy configuration,
global rate limiting, streaming request handlers, persistence, or WebSocket
behavior changes. Reverse proxies and hosted deployments remain responsible
for their own outer request limits.

## Implementation Units

### U1. Enforce the transport limit

- **Goal:** Configure the comet HTTP server to reject request bodies above the
  reviewed limit before handler parsing.
- **Files:** `comet_chat/application.py`
- **Approach:** Add a named body-size constant and a shared HTTP-server options
  helper used by the executable server construction.

### U2. Prove configuration and runtime behavior

- **Goal:** Catch both wiring regressions and false confidence from a constant
  that is defined but unused.
- **Files:** `tests/test_chat_handlers.py`, `tests/test_tornado6_runtime.py`,
  `scripts/check_docs_plans.py`
- **Test scenarios:** Verify the configured value, accept a normal XSRF-valid
  form submission, reject an oversized encoded body, and reject mutations that
  remove, bypass, or weaken the transport limit.

### U3. Record the maintained boundary

- **Goal:** Keep contributor and security documentation aligned with runtime
  behavior and completed verification.
- **Files:** `README.md`, `SECURITY.md`, `VISION.md`, `CHANGES.md`,
  `docs/plans/2026-06-13-comet-request-body-limit.md`

## Risks And Mitigations

- Multipart form framing varies with boundary length. Runtime coverage will use
  a comfortably oversized payload and separately prove that a normal browser-
  style submission remains accepted.
- A test-specific server limit could pass while the executable remains
  unbounded. Both paths will consume the same helper, backed by static
  contracts that require the production call site.
- Tornado may close an oversized connection rather than return a handler-level
  response. The runtime assertion will accept the documented transport-level
  rejection shape while requiring that the handler never broadcasts the body.

## Verification

- Focused comet handler and runtime HTTP validation passed 27 tests, including
  a maximum-length multipart browser form and an oversized transport rejection.
- A disposable exact-source snapshot passed the full pinned `make check` gate
  under a 180-second timeout: 35 tests, 17 workflow mutations, `pip check`, and
  `pip-audit` with no known runtime vulnerabilities.
- The same bounded full gate passed from the repository and from an external
  working directory against the completed plan record.
- Eight hostile mutations covering the constant, server option, production
  wiring, configuration and runtime tests, documentation, and completed plan
  status were rejected.
- Python AST, workflow YAML, JavaScript syntax, HTML, and SVG parsing passed;
  exact-path, generated-artifact, whitespace, and changed-line secret audits
  found no unintended files or sensitive material.

## Sources

- Tornado 6.5 `HTTPServer` documentation:
  https://www.tornadoweb.org/en/stable/httpserver.html
- Tornado 4.0 release note introducing separate `max_body_size` enforcement,
  including streaming requests:
  https://www.tornadoweb.org/en/stable/releases/v4.0.0.html
