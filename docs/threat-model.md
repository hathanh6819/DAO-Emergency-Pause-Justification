# Threat model

| Threat | Control | Regression coverage |
|---|---|---|
| Contributor supplies a forged URL or JSON | URLs are constructed from the registered repository, exact commit and paths | source-shape and identity tests |
| Mutable branch changes after review | request accepts only a 40-character commit; API response must match | commit mismatch test |
| Raw bytes differ from Git object | validator recomputes Git blob SHA-1 and byte size | corrupt blob test |
| Incident invents an on-chain transaction | fixed Base Blockscout API binds hash, status and `to` contract | transaction matrix |
| Incident is valid but for another capability/contract | manifest and execution consume calls bind the full scope | scope mismatch tests |
| Oversized/truncated source hides unsafe data | 14,000-byte Git bounds, 32,000-byte transaction bound and complete-tree requirement | source failure tests |
| Prompt injection changes output shape | evidence is delimited as data; exact boolean schema and protocol identity | model schema/type tests |
| Stale or parallel decision overwrites state | expected case and policy revisions | stale revision tests |
| Authorization is replayed or broadened | execution-target-only, exact tuple, expiry, single-use flag | replay/scope/expiry tests |
| Historical incident authorizes a current pause | exact Blockscout/statement timestamp plus policy and hard 24-hour age cap | temporal mismatch/stale tests |
| Authority changes after a verdict | consume rechecks active protocol, current policy revision and current council | rotation/deactivation tests |
| Council needs to stop an unconsumed authorization | owner or current council can revision-bump and revoke | revoke authorization tests |
| Temporary acquisition/model failure becomes approval | failures become retryable `UNRESOLVED`, never authorization | recovery test |
