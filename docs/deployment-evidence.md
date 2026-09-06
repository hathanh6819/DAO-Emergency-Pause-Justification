# Deployment evidence

Status: local verification complete; Studionet contract deployed.

- Contract: `0xA31872DF1E62A84230a73F7204E1BC21c340dC2c`
- Explorer: https://explorer-studio.genlayer.com/address/0xA31872DF1E62A84230a73F7204E1BC21c340dC2c
- Local source SHA-256: `b2169ac0d285602ee6457a2aaf4e3f7a6d4d8c21f0bb0183fad5589ed87454c1`
- CLI source retrieval: successful on 2026-09-06; deployed source contains the verdict fix and fixed Base Blockscout acquisition path.
- Live lifecycle: canonical inputs locked; execution pending deployment-owner signing authority.

Canonical lifecycle inputs:

- Repository: `hathanh6819/dao-emergency-pause-justification`
- Fixture commit: `13bd11f1e499cf9a7d02427f5aadbe4a158ef3be`
- Incident transaction: `0x60fd436dbd0e99c7585b775095048eced56bfc11e18331cfcb0cdad6f9fe7d87`
- Blockscout result: `ok`, block `24331067`, target `0xEf7Bd1543bDAcAdD7e42822e3F15Dd0af0410fDa`

The first registration transaction `0xe77904ad981fc74f59ea8877a258e0d1d777987a73dbbd062afe28c41db972c8` finalized but returned `INVALID_AUTHORITIES`. The receipt proves both intended addresses were encoded correctly. This exposed a GenVM runtime representation mismatch (`str(Address)` versus canonical `Address.as_hex`); state remained at zero and the source was patched with a dedicated regression test. A new deployment is required.

Record the fixture commit, finalized transaction hashes, and matching before/after `get_case` reads here after the lifecycle. Do not claim a live result until the explorer shows finalized status.
