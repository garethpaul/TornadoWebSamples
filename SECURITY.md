# Security Policy

## Supported Versions

The supported security scope for `TornadoWebSamples` is the current default branch, `master`. Older commits, tags, branches, forks, demos, and generated artifacts are not actively supported unless the repository explicitly marks them as maintained.

Project summary: Tornadoweb Web Server Samples

## Reporting a Vulnerability

Please report suspected vulnerabilities through GitHub's private vulnerability reporting or by opening a draft GitHub Security Advisory for `garethpaul/TornadoWebSamples` when that option is available. If GitHub does not show a private reporting option for this repository, contact the repository owner through GitHub and avoid posting exploit details publicly until the issue can be assessed.

Do not open a public issue that includes exploit code, secrets, personal data, or detailed reproduction steps for an unpatched vulnerability.

## What to Include

Helpful reports include:

- the affected file, endpoint, permission, dependency, or workflow
- a concise impact statement explaining what an attacker could do
- reproduction steps using test data and accounts you control
- the branch, commit SHA, platform version, device, runtime, or dependency versions used
- logs, screenshots, or proof-of-concept snippets that demonstrate impact without exposing private data

## Project Security Posture

- This repository appears to be a public sample, documentation, or utility project. The active security scope is the code and documentation on the default branch.
- Review found network clients, sockets, web APIs, or service endpoints; changes in those areas should receive security-focused review before merge.
- Review found file, document, data, or media parsing flows; changes in those areas should receive security-focused review before merge.
- Runtime and verification dependencies are pinned in `requirements.txt` and
  `test-requirements.txt`; review version changes together with audit results.
- Both unauthenticated sample servers bind to `127.0.0.1` by default. Any
  change that exposes them to other interfaces requires an explicit threat
  model and deployment warning.
- Browser templates are self-contained and do not load third-party CDN code.
  The comet POST requires Tornado's same-origin XSRF token, while the WebSocket
  endpoint enforces a same-host Origin check. Connected WebSocket clients are
  scoped to their owning application instance rather than shared globally, and
  clients whose asynchronous message delivery fails are removed from that
  registry.
  WebSocket frames are capped at 4096 bytes before JSON parsing, in addition
  to the 500-character validated chat-body limit.
- Comet long polls have a 25-second server-side lifetime and release their
  callback/future state on delivery, timeout, cancellation, or disconnect.
- GitHub Actions runs the same `make check` baseline as local development with
  Ubuntu 24.04, read-only permissions, credential-free checkout, a ten-minute
  timeout, concurrency cancellation, and commit-pinned Node 24 actions.
  Structural mutation tests reject contradictory credential settings, write
  permissions, unreviewed actions, and weakened verification commands. Keep
  the workflow limited to local in-process HTTP tests and static checks unless
  a separate review documents a need for live services.

## Service and API Notes

For web services, APIs, sockets, or scraping workflows, prioritize reports involving authentication bypass, authorization errors, injection, server-side request forgery, unsafe deserialization, credential leakage, data exposure, or denial-of-service conditions. Use test accounts and minimal proof-of-concept traffic only.

## Dependency and Supply Chain Security

Dependency updates should come from trusted package managers and should keep lockfiles in sync when lockfiles exist. Do not commit credentials, private keys, tokens, generated secrets, or machine-local configuration. If a vulnerability depends on a compromised package, typosquatting risk, insecure transitive dependency, or unsafe build step, include the package name, affected version, and the path through which it is used.

## Safe Research Guidelines

Good-faith research is welcome when it stays within these boundaries:

- use only accounts, devices, data, and infrastructure that you own or have explicit permission to test
- avoid destructive actions, persistence, spam, phishing, social engineering, or denial-of-service testing
- minimize access to personal data and stop testing immediately if private data is exposed
- do not exfiltrate secrets or third-party data; report the minimum evidence needed to verify impact
- keep vulnerability details confidential until the maintainer has assessed the report

## Maintainer Response

The maintainer will review complete reports as availability allows, prioritize issues by exploitability and impact, and coordinate a fix or mitigation when the affected code is still maintained. For sample, archived, or educational repositories, the likely remediation may be documentation, dependency updates, or clearly marking unsupported code rather than a production-style patch release.
