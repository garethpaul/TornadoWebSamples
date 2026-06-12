# Offline Native Browser Clients

## Status: Completed

## Context

Both chat templates loaded jQuery 1.7.2 and YUI reset CSS from third-party CDNs
at runtime. This made local tutorial behavior depend on obsolete remote assets
and exposed the browser surface to unnecessary supply-chain risk. The comet
message POST also lacked Tornado XSRF enforcement.

## Objectives

- Make both browser samples fully self-contained at runtime.
- Preserve escaped message rendering and same-origin endpoints.
- Require an XSRF token for comet message submission.
- Keep dependency and CI results independent of ambient environments.

## Work Completed

- Replaced jQuery event, request, and DOM APIs with native browser APIs.
- Replaced the external CSS reset with small local box-model, margin, padding,
  and list-style rules.
- Removed all runtime HTTP and HTTPS asset references from both templates.
- Changed both clients to submit through explicit same-origin `/message`
  forms and continue rendering messages through `textContent`.
- Enabled Tornado `xsrf_cookies`, rendered the comet form token, and submitted
  it through `FormData`.
- Added in-process HTTP tests for accepted token-bearing posts and rejected
  tokenless posts.
- Added static regressions for native APIs, local assets, safe text rendering,
  form endpoints, and XSRF markup.
- Made Makefile paths independent of the caller's directory, added `pip check`,
  and scoped `pip-audit` to the declared runtime requirements.
- Fixed CI to Ubuntu 24.04 with concurrency cancellation and annotated immutable
  action pins with verified release versions.

## Verification

- Fresh isolated dependency installation.
- `python3 -m py_compile comet_chat/application.py socket_chat/application.py`
- `python3 scripts/check_docs_plans.py`
- `python3 -m pytest -q`
- `python3 -m pip check`
- `python3 -m pip_audit -r requirements.txt`
- `make check`
- `make -C /path/to/TornadoWebSamples check`
- Mutations for remote assets, missing XSRF configuration, ambient auditing,
  floating runners, and unsafe HTML rendering
- `git diff --check`

All HTTP coverage uses Tornado's in-process test server. No live service,
credential, browser automation, or external runtime asset is required.
