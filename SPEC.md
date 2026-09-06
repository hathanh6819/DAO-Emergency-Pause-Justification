# Contract specification

## States

`PENDING` can become one immutable substantive result (`COUNCIL_ATTESTATION_SUPPORTS_PAUSE`, `INSUFFICIENT_EVIDENCE`, `SCOPE_MISMATCH`, or `POLICY_VIOLATION`) or `UNRESOLVED`. Only `UNRESOLVED` can return to `PENDING`, using the current case revision and unchanged policy revision.

## Authorization tuple

Consumption must match: case revision, current policy revision, current council, active protocol, execution target, affected contract, capability, pause duration and action digest. It must occur before expiry, remain unrevoked and can succeed once.

## Fail-closed rules

- Only Base chain ID 8453 is accepted.
- Git commit/tree/blob identity or response-bound failure never authorizes.
- The incident manifest must exactly match protocol, chain, transaction, affected contract and capability.
- Blockscout must confirm the exact transaction hash, destination, successful status and timestamp. Its complete response has a separate 32,000-byte bound.
- The transaction timestamp must exactly match the statement and remain within the contract-capped 24-hour policy window.
- The committed policy revision, duration range and severity must match.
- Validator output uses an exact schema and strict equality consensus.
- Only a complete `COUNCIL_ATTESTATION_SUPPORTS_PAUSE` result creates a consumable authorization.
