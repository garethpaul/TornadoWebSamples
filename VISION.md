## Tornado Web Samples Vision

Tornado Web Samples is a small playground for Tornado chat examples, including
long-polling comet chat and WebSocket chat.

The repository is useful as a compact demonstration of Tornado request
handlers, asynchronous callbacks, WebSocket handlers, in-memory message
broadcasting, templates, and static assets.

The goal is to preserve the examples while making their in-memory, unauthenticated
demo nature clear.

The current focus is:

Priority:

- Preserve comet and WebSocket chat examples
- Keep setup and quick-start instructions simple
- Treat in-memory message state as demo-only
- Keep browser message rendering escaped by default
- Keep chat message input bounded and validated before broadcasting
- Keep browser input hints aligned with server-side message limits
- Keep comet long-poll callback queues isolated per message store
- Remove abandoned comet long-poll callbacks when connections close
- Keep idle comet long polls bounded and release their callback state
- Keep comet callback dispatch snapshot-based so new waits survive current sends
- Keep comet callback delivery failures isolated to the failing callback
- Keep WebSocket callback delivery failures isolated to the failing callback
- Observe delayed WebSocket delivery failures and remove failed clients
- Keep connected WebSocket client registries isolated per application
- Keep browser clients self-contained on native, same-origin APIs
- Require XSRF protection for comet message submissions
- Keep WebSocket origin checks restricted to the same host
- Bound WebSocket frames before JSON parsing
- Keep completed maintenance plans under `docs/plans`
- Keep GitHub Actions aligned with the local `make check` baseline
- Keep hosted verification read-only, credential-free, pinned, and structurally
  protected against workflow policy regressions
- Keep the chat tutorials running on maintained Tornado and Python releases
- Keep runtime and verification dependencies pinned and audited
- Keep dependency verification isolated from ambient Python packages
- Keep unauthenticated sample servers bound to loopback by default
- Avoid implying production chat readiness

Next priorities:

- Document supported Python and Tornado versions
- Add small tests for message broadcast behavior
- Add separate input validation notes for comet and WebSocket demos
- Separate long-polling and WebSocket caveats in the README

Contribution rules:

- One PR = one focused example, handler, template, test, or documentation change.
- Keep examples runnable with minimal setup.
- Do not add persistence or auth without clear tutorial framing.
- Explain any Tornado API modernization.

## Security And Responsible Use

Canonical security policy and reporting:

- [`SECURITY.md`](SECURITY.md)

Chat demos can expose user input. These examples should not be deployed as-is
to the public internet without authentication, input handling, rate limits, and
storage decisions.

## What We Will Not Merge (For Now)

- Production deployment claims
- Hidden persistence of chat messages
- Unbounded public chat behavior
- Browser inputs that imply unbounded message size
- Callback delivery failures that stop unrelated chat clients
- Cross-origin WebSocket access without a tutorial note
- Framework rewrites without preserving tutorial clarity

This list is a roadmap guardrail, not a permanent rule.
Strong user demand and strong technical rationale can change it.
