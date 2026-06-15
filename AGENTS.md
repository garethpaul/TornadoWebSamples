# AGENTS.md

## Repository purpose

`garethpaul/TornadoWebSamples` is a static web project. Tornadoweb Web Server Samples

## Project structure

- `Makefile` - repository verification targets
- `scripts` - baseline checks and helper scripts
- `docs` - plans, notes, and generated README assets
- `tests` - tests and fixtures
- `requirements.txt` - Python runtime dependencies
- `comet_chat` - repository source or sample assets
- `plans` - repository source or sample assets
- `socket_chat` - repository source or sample assets

## Development commands

- Install dependencies: `python3 -m pip install -r requirements.txt -r test-requirements.txt`
- Full baseline: `make check`
- Combined verification: `make verify`
- Lint/static checks: `make lint`
- Workflow contract mutations: `make contract-test`
- Tests: `make test`
- Build: `make build`
- If a command above skips because a platform toolchain is missing, verify on a machine with that SDK before claiming platform behavior is tested.

## Coding conventions

- Language mix noted in the README: JavaScript (2), Python (2).
- Prefer dependency-free tests or stdlib checks when optional packages are unavailable.

## Testing guidance

- Test-related files detected: `test-requirements.txt`, `tests/`, `tests/test_chat_handlers.py`, `tests/test_static_assets.py`, `tests/test_tornado6_runtime.py`
- Start with the narrowest relevant test or Make target, then run `make check` before handing off if the change is not documentation-only.
- Keep README verification notes in sync when commands, fixtures, or supported toolchains change.
- Keep hosted verification read-only and credential-free with immutable action
  pins; update the structural workflow mutations with any intentional policy
  change.

## PR / change guidance

- Keep diffs focused on the requested repository and avoid unrelated modernization or formatting churn.
- Preserve public APIs, sample behavior, file formats, and documented environment variables unless the task explicitly changes them.
- Update tests, README notes, or docs/plans when behavior, security posture, or validation commands change.
- Call out skipped platform validation, legacy toolchain assumptions, and any risky files touched in the final summary.

## Safety and gotchas

- No required secret or credential file was identified in the repository scan. If you add integrations later, keep secrets out of git.
- Browser chat clients should use same-origin message endpoints rather than hard-coded localhost URLs.
- Comet accepts at most 100 pending long polls and returns `503` with `Retry-After: 1` when capacity is exhausted.
- See `SECURITY.md` for vulnerability reporting and safe research guidance.
- See `VISION.md` for project direction and contribution guardrails.
- See `docs/plans/2026-06-08-tornado-web-samples-baseline.md` for the canonical Tornado chat sample baseline.
- See `docs/plans/2026-06-08-message-validation.md` for chat message input validation coverage.

## Agent workflow

1. Inspect the README, Makefile, manifests, and the files directly related to the request.
2. Make the smallest source or docs change that satisfies the task; avoid generated, vendored, or local-environment files unless required.
3. Run the narrowest useful validation first, then `make check` or the documented package/platform gate when available.
4. If a required SDK, service credential, or external runtime is unavailable, record the skipped command and why.
5. Summarize changed files, commands run, and remaining risks or follow-up validation.
