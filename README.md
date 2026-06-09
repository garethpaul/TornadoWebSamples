# TornadoWebSamples

<!-- README-OVERVIEW-IMAGE -->
![Project overview](docs/readme-overview.svg)

## Overview

`garethpaul/TornadoWebSamples` is a static web project. Tornadoweb Web Server Samples

This README is based on the checked-in source, manifests, scripts, and repository metadata on the `master` branch. The project language mix found during review was: JavaScript (2), Python (2).

## Repository Contents

- `README.md` - project overview and local usage notes
- `CHANGES.md` - maintenance history for Tornado chat checks
- `comet_chat` - source or example code
- `Makefile` - local verification entry points
- `docs/plans` - completed maintenance plans for the current baseline
- `plans` - historical implementation notes
- `requirements.txt` - runtime dependency notes
- `scripts` - documentation-plan validators
- `SECURITY.md` - security reporting and disclosure guidance
- `socket_chat` - source or example code
- `test-requirements.txt` - test dependency notes
- `tests` - focused handler and static asset tests
- `VISION.md` - project direction and maintenance guardrails

Additional scan context:

- Source directories: comet_chat, socket_chat
- Dependency and build manifests: Makefile, requirements.txt, test-requirements.txt
- Entry points or build surfaces: comet_chat/application.py, socket_chat/application.py
- Test-looking files: tests/test_chat_handlers.py, tests/test_static_assets.py

## Getting Started

### Prerequisites

- Git
- Python 3

### Setup

```bash
git clone https://github.com/garethpaul/TornadoWebSamples.git
cd TornadoWebSamples
python3 -m pip install -r requirements.txt -r test-requirements.txt
```

The setup commands above are derived from repository files. Legacy mobile, Python, or JavaScript samples may require older SDKs or package versions than a modern workstation uses by default.

## Running or Using the Project

- Run either sample with Python after installing requirements:
  `python3 comet_chat/application.py` or `python3 socket_chat/application.py`.

## Testing and Verification

- `make check` runs Python syntax checks, focused chat-handler tests, message
  validation tests, and static asset checks for browser-side message rendering.
- Static asset checks also keep chat clients on same-origin message endpoints
  and require HTTPS for the shared external reset stylesheet.
- `make check` also requires completed canonical plans under `docs/plans`.

When the required SDK or runtime is unavailable, use static checks and source review first, then verify on a machine that has the matching platform toolchain.

## Configuration and Secrets

- No required secret or credential file was identified in the repository scan. If you add integrations later, keep secrets out of git.

## Security and Privacy Notes

- Review changes touching network requests, sockets, or service endpoints; examples from the scan include comet_chat/application.py, comet_chat/templates/index.html, socket_chat/application.py, socket_chat/static/socketchat.js, and 1 more.
- Review changes touching file, media, JSON, XML, CSV, OCR, or data parsing; examples from the scan include comet_chat/application.py, comet_chat/static/cometchat.js, socket_chat/static/socketchat.js.
- Browser chat clients should use same-origin message endpoints rather than
  hard-coded localhost URLs.

## Maintenance Notes

- See `SECURITY.md` for vulnerability reporting and safe research guidance.
- See `VISION.md` for project direction and contribution guardrails.
- See `docs/plans/2026-06-08-tornado-web-samples-baseline.md` for the
  canonical Tornado chat sample baseline.
- See `docs/plans/2026-06-08-message-validation.md` for chat message input
  validation coverage.
- See `docs/plans/2026-06-09-chat-client-endpoints.md` for client endpoint and
  external asset URL coverage.

## Contributing

Keep changes small and tied to the project that is already present in this repository. For code changes, document the toolchain used, avoid committing generated dependency directories or local configuration, and update this README when setup or verification steps change.
