# Audit Runtime and Development Dependencies

## Status: Completed

## Context

The canonical gate audited `requirements.txt` but did not audit
`test-requirements.txt`. A fresh development-requirements audit resolved
msgpack 1.1.2 through pip-audit and reported `GHSA-6v7p-g79w-8964`, fixed in
msgpack 1.2.1. The vulnerable package is development-only, but it still runs
inside CI and contributor environments and therefore belongs inside the
repository security boundary.

## Requirements

- Pin the fixed msgpack release explicitly so dependency resolution cannot
  select the vulnerable transitive version.
- Keep runtime and development audits separate so each declared requirement
  set remains independently reviewable.
- Preserve repository-root-independent Make behavior and the existing Python
  3.10, 3.12, and 3.14 hosted matrix.
- Add a dependency-free hostile-mutation contract for the exact pin and both
  audit commands.
- Document the development dependency boundary without changing chat runtime
  behavior.

## Implementation

- Added `msgpack==1.2.1` to `test-requirements.txt`.
- Extended `make check` to run pip-audit against both requirements files.
- Added `scripts/test_dependency_audit_contract.py` and wired it into
  `make contract-test`.
- Updated repository guidance, changelog, and documentation contracts.

## Verification

- A pre-fix `pip-audit -r test-requirements.txt` reproduced
  `GHSA-6v7p-g79w-8964` against msgpack 1.1.2.
- The fixed repository and external-directory `make check` passed with 45
  tests, clean dependency consistency, and no known vulnerabilities in either
  requirements file.
- All five hostile dependency-audit mutations were rejected, covering a
  vulnerable pin, a floating pin, missing runtime or development audits, and
  a duplicated audit scope.
- Public PyPI supplied msgpack 1.2.1; the local corporate mirror was stale and
  did not yet expose the fixed release.

## Scope Boundaries

- Do not change Tornado runtime behavior, chat limits, workflow topology, or
  the supported Python matrix.
- Do not audit the ambient global environment; audit only the two declared
  requirement sets.
- Do not weaken the fixed pin to accommodate a stale package mirror.
