# WebSocket Invalid Message Close

Status: Completed

## Goal

Remove invalid WebSocket senders from broadcast authority before close code
`1003` starts its asynchronous handshake.

## Work

- Added one invalid-message close helper that discards the sender before close.
- Routed malformed JSON and invalid body validation through the helper.
- Added failing-first coverage for registry removal and a late send attempt.
- Updated maintained security, operating, vision, agent, and change guidance.
- Extended the structural checker for implementation, ordering, test, guidance,
  and completed-plan contracts.

## Verification

- Run focused and complete handler tests.
- Run repository and external-directory `make check` with pinned dependencies.
- Reject hostile invalid-message close mutations.
- Audit syntax, whitespace, generated artifacts, and secret-shaped additions.

## Completion Evidence

- Before implementation, the invalid-frame regression found the rejected
  handler still present in `chat_clients` after close code `1003` was requested.
- After implementation, the focused regression passed and late sends from the
  removed handler were ignored.
- The repository and external-directory `make check` gates passed in a clean
  Python 3.11 environment with the pinned runtime and test dependencies.
- All 45 tests, 35 Make target/authority cases, 5 dependency-audit mutations,
  18 workflow mutations, and 9 WebSocket rate-limit mutations passed.
- Both pinned dependency audits reported no known vulnerabilities, and
  `pip check` reported no broken requirements.
- Six hostile invalid-message close mutations were rejected across behavior,
  ordering, call-site, test, guidance, and plan-status contracts.
- Python syntax, whitespace, generated-artifact, and likely-secret audits
  passed. Hosted checks must pass on the exact pull request head before merge.

## Scope Boundaries

- Do not change accepted message semantics, rate limits, frame limits, origin
  policy, client caps, broadcast payloads, or close codes.
