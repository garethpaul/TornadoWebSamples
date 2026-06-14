# Make Root Override Protection

## Status: Planned

## Context

The Makefile derives an absolute repository root so every public verification
alias can be invoked from outside the checkout. GNU Make still permits an
environment or command-line `ROOT` assignment to replace that ordinary
declaration. A caller can therefore redirect repository-owned checker, source,
test, workflow, dependency, and documentation paths while receiving a
successful command result from a different tree.

The Python interpreter is intentionally configurable. The repository path is
not: verification must always inspect the checkout containing the invoked
Makefile while `PYTHON` remains available for explicit toolchain selection.

## Requirements

- Protect the derived repository root from environment and command-line
  reassignment.
- Preserve explicit `PYTHON` overrides and all existing public aliases.
- Prove every alias remains rooted in this checkout from repository and
  external working directories under hostile root assignments.
- Add fail-closed static contracts for the exact declaration, declaration
  count and order, aliases, checker paths, README index, and completed plan.
- Preserve all Tornado runtime, chat protocol, client, dependency, workflow,
  security-documentation, and test behavior.

## Approach

Use GNU Make's `override` directive on the existing immediate root assignment.
Keep the protected root before the configurable Python declaration. Extend the
existing repository checker rather than adding another validation entry point,
and exercise environment and command-line precedence through bounded shell
cases plus mutation-sensitive source checks.

## Implementation Units

### Protect repository path ownership

- Update `Makefile` so exactly one root declaration is protected.
- Retain the current absolute path expression, alias graph, and `PYTHON`
  configurability.

### Add static and adversarial contracts

- Extend `scripts/check_docs_plans.py` with exact declaration, assignment-count,
  ordering, alias, checker-path, README, and plan-presence requirements.
- Verify all six public aliases from repository and external directories with
  hostile environment and command-line `ROOT` values.
- Reject mutations that weaken, duplicate, relocate, bypass, or stop
  documenting the protected declaration.

### Record completed evidence

- Index this plan from `README.md`.
- Mark the plan completed only after focused, mutation, full `make check`,
  artifact, secret, and diff verification succeeds.

## Risks And Mitigations

- An overly broad override could prevent legitimate interpreter selection.
  Only `ROOT` becomes protected; `PYTHON ?=` remains unchanged and receives an
  explicit override check.
- A declaration-only assertion could miss a later assignment or alias bypass.
  Count all root assignments and require repository-owned command paths and the
  complete public alias graph.
- Repository-local testing alone could hide working-directory assumptions.
  Run every alias from both repository and external directories.

## Scope Boundaries

This change does not modify Python application behavior, message validation,
XSRF handling, HTTP or WebSocket limits, long-poll lifecycle, browser assets,
dependency pins, CI policy, or deployment behavior.

## Verification Plan

- Run focused static checker and Make dry-run validation.
- Run all public aliases from repository and external directories under hostile
  environment and command-line root assignments while preserving `PYTHON`.
- Run mutation cases for declaration protection, duplicate assignments,
  ordering, aliases, checker paths, README indexing, and plan status.
- Run the pinned full `make check` gate with an explicit timeout.
- Audit the exact diff, generated artifacts, changed-line secrets, whitespace,
  and protected application/workflow/dependency paths before committing.
