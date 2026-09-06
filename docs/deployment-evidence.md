# Deployment evidence

Status: v2 live probe completed and exposed two defects; corrected v3 source requires deployment.

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
