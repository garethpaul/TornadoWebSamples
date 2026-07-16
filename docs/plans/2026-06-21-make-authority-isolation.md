# Make Authority Isolation

Status: Completed

## Goal

Keep Tornado sample verification and dependency audits bound to the checked-in
repository under ordinary caller Make roots and shells, later single-colon
recipe replacement, non-executing modes, and Python Make syntax. This is not a
sandbox for arbitrary caller Make programs.

## Changes

- Resolve and export the repository root from the checked-in Makefile alone.
- Freeze the reviewed root, Python value, and recipe shell against ordinary
  later target-specific assignments.
- Use double-colon public aliases so later single-colon recipe replacement
  fails during parsing instead of replacing repository recipes.
- Reject caller-supplied `MAKEFLAGS`, `MAKEFILES`, `MAKEFILE_LIST`, dry-run,
  touch, question, and ignore-error modes.
- Add a self-contained adversarial root harness across every public target.
- Require `/usr/bin/make check` through the existing structural workflow
  validator and mutation suite.

## Caller Boundary

GNU Make `override` directives and caller-added double-colon recipes are
caller programs with the same Make-level authority as this file and remain
outside the checked-in Makefile trust boundary. GNU Make startup files and
earlier extra `-f` files are parsed before repository checks, so their
parse-time code is also outside the no-execution boundary. PATH resolution of the
default `python3` is caller-controlled; callers that require a specific interpreter
must pass a reviewed literal `PYTHON` value.

## Verification

- repository and external-directory pinned `make check` passed
- 35 target/authority combinations passed with quoted and literal-dollar tool
  paths
- 18 unsafe workflow mutations, 5 dependency-audit mutations, and 9 WebSocket
  rate-limit mutations were rejected
- ordinary later target-specific shell assignments could not intercept recipes
- later single-colon replacement of all seven public aliases failed closed
- the target-specific override-shell false-zero was retained as an executable
  boundary control and documented outside repository authority
- 45 tests, `pip check`, and runtime/development `pip-audit` gates passed
