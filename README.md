# DAO Emergency Pause Justification

An Intelligent Contract that issues a narrow, single-use emergency-pause authorization for a Base protocol only when independently acquired evidence supports it.

## Why this needs GenLayer

The contract combines deterministic identity checks with validator judgment. Validators fetch the exact GitHub commit, verify the Git tree and both blob SHA-1 identities, fetch the referenced Base transaction from Blockscout, enforce a versioned pause policy, and independently classify whether the incident describes an active material threat requiring the requested capability pause.

It does not custody funds and it does not execute a pause. A separately registered execution target must consume the exact authorization tuple once, before expiry.

## Authority and evidence chain

1. The deployer registers a protocol repository, policy path, security council and execution target.
2. Only that security council may request assessment, binding a 40-character commit, incident path, Base transaction hash, affected contract, capability, duration and action SHA-256.
3. Validators derive GitHub API/raw URLs themselves. Contributor-supplied evidence URLs are never accepted.
4. Git blob identities and sizes are recomputed from fetched bytes.
5. The Base transaction is independently fetched from the fixed `base.blockscout.com` API and bound to its hash and destination.
6. Policy failures and scope mismatches fail closed. Source/model failures become `UNRESOLVED` and require an explicit revision-aware retry.
7. A justified authorization is version-bound, exact-scope, expiring and single-use.

## Local verification

```powershell
python scripts/verify_local.py
```

Constructor arguments: none.

See [SPEC.md](SPEC.md), [test resources](docs/test-resources.md), and [threat model](docs/threat-model.md).
