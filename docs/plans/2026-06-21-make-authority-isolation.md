# Make Authority Isolation

Status: Completed

## Goal

Keep Tornado sample verification and dependency audits bound to the checked-in
repository under hostile Make roots, shells, startup files, modes, and Python
executable values.

## Changes

- Resolve and export the repository root from the checked-in Makefile alone.
- Freeze the trusted Python override as a literal value and fix the recipe
  shell.
- Reject caller-supplied `MAKEFLAGS`, `MAKEFILES`, `MAKEFILE_LIST`, dry-run,
  touch, question, and ignore-error modes.
- Add a self-contained adversarial root harness across every public target.
- Require `/usr/bin/make check` through the existing structural workflow
  validator and mutation suite.

## Verification

- repository and external-directory pinned `make check` passed
- 35 target/authority combinations passed with quoted and literal-dollar tool
  paths
- 18 unsafe workflow mutations, 5 dependency-audit mutations, and 9 WebSocket
  rate-limit mutations were rejected
- 45 tests, `pip check`, and runtime/development `pip-audit` gates passed
