# DAO Emergency Pause Justification

An Intelligent Contract that issues a narrow, single-use emergency-pause authorization for a Base protocol only when a registered council's authenticated statement, exact repository evidence, policy and independently observed transaction support it.

## Why this needs GenLayer

The contract combines deterministic identity checks with validator judgment. Validators fetch the exact GitHub commit, verify the Git tree and both blob SHA-1 identities, fetch the referenced Base transaction from Blockscout, enforce a versioned pause policy and classify whether the authenticated council statement describes an active material threat requiring the requested capability pause.

The positive result means only `COUNCIL_ATTESTATION_SUPPORTS_PAUSE`. It does not claim that a successful transaction alone objectively proves an exploit. The registered council is the authority for the incident statement; Blockscout independently proves the exact transaction identity, target, success and timestamp. Statements older than the bounded policy window cannot authorize a current pause.

It does not custody funds and it does not execute a pause. A separately registered execution target must consume the exact authorization tuple once, before expiry.

## Authority and evidence chain

1. The deployer registers a protocol repository, policy path, security council and execution target.
2. Only that security council may request assessment, binding a 40-character commit, incident path, Base transaction hash, affected contract, capability, duration and action SHA-256.
3. Validators derive GitHub API/raw URLs themselves. Contributor-supplied evidence URLs are never accepted.
4. Git blob identities and sizes are recomputed from fetched bytes.
5. The Base transaction is independently fetched from the fixed `base.blockscout.com` API and bound to its hash and destination.
6. Policy failures and scope mismatches fail closed. Source/model failures become `UNRESOLVED` and require an explicit revision-aware retry.
7. A supported authorization is version-bound, exact-scope, revocable, expiring and single-use. Authority rotation or protocol deactivation invalidates it.

The deployer address is exposed by `get_protocol_info`. Only it can register, rotate or deactivate protocol authorities. The registered security council is the authenticated incident-statement authority and may request assessments or revoke an unconsumed authorization. The separately registered execution target is the only account allowed to consume an authorization.

## Local verification

```powershell
python scripts/verify_local.py
```

This single release gate runs the full Direct Mode suite, architecture invariants and GenVM lint/validation. It rejects storage reads inside the nondeterministic evaluator, source truncation, missing byte bounds, unauthenticated Git blobs, raw-string timestamp comparison and unexpected payable surface before deployment.

Constructor arguments: none.

See [SPEC.md](SPEC.md), [test resources](docs/test-resources.md), and [threat model](docs/threat-model.md).
