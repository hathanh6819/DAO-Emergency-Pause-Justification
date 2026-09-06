# Deployment evidence

Status: corrected v3 exact source deployed; historical fail-closed lifecycle verified.

Verified v3 deployment:

- Contract: `0x6F5e72cEd396f3D07F4523320fd6a7CB1cC10415`
- Explorer: https://explorer-studio.genlayer.com/address/0x6F5e72cEd396f3D07F4523320fd6a7CB1cC10415
- Deployment: https://explorer-studio.genlayer.com/tx/0x06011e9b1a96396eccd3e54b09821104ffef0f47855912c89d6fe0ad7bb4701d
- Deployed/local source: exact byte-for-byte match, 27,664 bytes, SHA-256 `414d78b9d346e005fc1b455337e9cbc3b3681e730c2493789ffd58dbf1380c3a`
- Readback: version `3`, owner `0xa365f55a3bf352767bc5c5739ffddaee8fcf3a19`, non-custodial, initial counts `0/0`

| Scenario | Transaction | Final result and authoritative readback |
|---|---|---|
| Register canonical authority | `0x71b3f110730730ce8c6d70230e00db9490db04c10fd9c85d29be8becc29dfed5` | FINALIZED, 3 AGREE/2 IDLE; protocol 1 binds exact repo, policy, council, execution target, Base chain and revision 1 |
| Council requests historical assessment | `0x9fdc036f358d85f7193ea778a1d2670e96f17848836b0e0973946601262f65a1` | FINALIZED/MAJORITY_AGREE, leader SUCCESS returns case 1; exact source identities stored, PENDING revision 1 |
| Assess canonical sources | `0x1e4d3a4306dbddfb09e54b7e2a2ee857eec13e7ad3bed91d33b08da67633d1c5` | FINALIZED/MAJORITY_AGREE, leader SUCCESS, empty stderr; `POLICY_VIOLATION / INCIDENT_OUTSIDE_AUTHORIZATION_WINDOW`, revision 2, evidence digest `sha256:b4850d0d7dea7dbfc5bbb6ef04d76391541af18d87091f96a4e635183e6bcba1` |
| Outsider cannot consume negative result | `0x63e129f0186b1682f01f861b93ee6b62b646dfec21f8e2fc882dedeb7faa1a47` | FINALIZED/MAJORITY_AGREE, leader SUCCESS returns `PAUSE_NOT_AUTHORIZED`; state unchanged |
| Registered execution target cannot consume negative result | `0x379c65454eccbeaa7a5bbfa71e752aa1956684912aa3e80984ca88936e00cf9d` | FINALIZED/MAJORITY_AGREE, 5/5 AGREE, leader SUCCESS returns `PAUSE_NOT_AUTHORIZED`; final consumed remains 0 |

Two diagnostic transactions, `0xca1735acae87bd4fee2e7b7d3e248b9eab04f27a47924a08f5ce5d8b9e90800a` and `0x3ff78d4862199324fcd327aa0a115dec66aa37c1df5bf4a10c5cf112533315dc`, intentionally are not counted as contract-path evidence: PowerShell collapsed six CLI arguments into one and GenVM returned a missing-arguments contract error. Readback before the corrected calls proved no state mutation. The active CLI account was restored to `dbl-owner`; the temporary encrypted `lifecycle-a` export was deleted in `finally` (`temporary_keystore_exists=False`).

Final authoritative state: protocol count 1, case count 1; case 1 is `POLICY_VIOLATION`, revision 2, expiry 0, revoked 0, consumed 0. This fixture proves historical evidence cannot authorize a current pause; it is not presented as a positive pause authorization.

Replacement v2 deployment:

- Address: `0x8FB121E391c03E115Bed9b283C9233aAAdaC113f`
- Owner readback: `0xa365f55a3bf352767bc5c5739ffddaee8fcf3a19`
- Source parity: exact after LF newline normalization
- Normalized deployed/local SHA-256: `0a1bff77f2187e4ff9d98800a1c246cdabf45114887125666efb875d78e7a2c5`
- Initial readback: `protocol_count=0`, `case_count=0`
- Schema: 12 methods (4 view, 8 write), no payable methods
- Registration transaction: `0x9244f71eea31a231b2693603e4fdc637292db1e71b7185743ec52b2954efa71a` — finalized, `MAJORITY_AGREE`, 5/5 agree, protocol ID `1`
- Pause request transaction: `0xb191d94891d5131f780286cb8cce0a08d411adf72940705cd68383c59559f7ba` — finalized, `MAJORITY_AGREE`, case ID `1`
- Assessment transaction: `0x82cc3ae66b957d98831ce4806b370662d0a6905a2d0e81f18b9f6ec261ad039b` — finalized, safely denied with `SCOPE_MISMATCH / TRANSACTION_TIME_MISMATCH`
- Assessment exposed equivalent ISO timestamp representations (`...21Z` and `...21.000000Z`) being compared as raw strings, plus a GenVM warning from storage reads inside nondeterministic mode. The v3 source compares parsed epochs and snapshots all required storage/time before entering `strict_eq`.
- No authorization was issued or consumed on this superseded deployment.

- Historical/superseded contract: `0xA31872DF1E62A84230a73F7204E1BC21c340dC2c`
- Explorer: https://explorer-studio.genlayer.com/address/0xA31872DF1E62A84230a73F7204E1BC21c340dC2c
- Superseded source SHA-256: `b2169ac0d285602ee6457a2aaf4e3f7a6d4d8c21f0bb0183fad5589ed87454c1`
- Replacement v2 source SHA-256: `132989841bdcbfce19a902be360ddbc591dc9d0a178e850ca4a50dbea4482e8f`
- Live lifecycle: invalidated by the v3 source change; must be regenerated on a replacement address.

Canonical lifecycle inputs:

- Repository: `hathanh6819/dao-emergency-pause-justification`
- Fixture commit: `999af91c5e8effd7ea0d44e9ebc5967ff6e4ebab`
- Incident transaction: `0x60fd436dbd0e99c7585b775095048eced56bfc11e18331cfcb0cdad6f9fe7d87`
- Blockscout result: `ok`, block `24331067`, target `0xEf7Bd1543bDAcAdD7e42822e3F15Dd0af0410fDa`

The first registration transaction `0xe77904ad981fc74f59ea8877a258e0d1d777987a73dbbd062afe28c41db972c8` finalized but returned `INVALID_AUTHORITIES`. The receipt proves both intended addresses were encoded correctly. This exposed a GenVM runtime representation mismatch (`str(Address)` versus canonical `Address.as_hex`); state remained at zero and the source was patched with a dedicated regression test.

Corrected v3 source SHA-256: `414d78b9d346e005fc1b455337e9cbc3b3681e730c2493789ffd58dbf1380c3a`. Local verification: 40 Direct Mode tests passed; architecture release gate passed; GenVM lint and validation passed (12 methods, 4 view, 8 write).

Record the fixture commit, finalized transaction hashes, and matching before/after `get_case` reads here after the lifecycle. Do not claim a live result until the explorer shows finalized status.
