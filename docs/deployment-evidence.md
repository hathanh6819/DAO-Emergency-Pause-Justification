# Deployment evidence

Status: v2 local verification complete; replacement Studionet deployment required.

- Historical/superseded contract: `0xA31872DF1E62A84230a73F7204E1BC21c340dC2c`
- Explorer: https://explorer-studio.genlayer.com/address/0xA31872DF1E62A84230a73F7204E1BC21c340dC2c
- Superseded source SHA-256: `b2169ac0d285602ee6457a2aaf4e3f7a6d4d8c21f0bb0183fad5589ed87454c1`
- Replacement v2 source SHA-256: `132989841bdcbfce19a902be360ddbc591dc9d0a178e850ca4a50dbea4482e8f`
- Live lifecycle: invalidated by source change; must be regenerated on the replacement address.

Canonical lifecycle inputs:

- Repository: `hathanh6819/dao-emergency-pause-justification`
- Fixture commit: `999af91c5e8effd7ea0d44e9ebc5967ff6e4ebab`
- Incident transaction: `0x60fd436dbd0e99c7585b775095048eced56bfc11e18331cfcb0cdad6f9fe7d87`
- Blockscout result: `ok`, block `24331067`, target `0xEf7Bd1543bDAcAdD7e42822e3F15Dd0af0410fDa`

The first registration transaction `0xe77904ad981fc74f59ea8877a258e0d1d777987a73dbbd062afe28c41db972c8` finalized but returned `INVALID_AUTHORITIES`. The receipt proves both intended addresses were encoded correctly. This exposed a GenVM runtime representation mismatch (`str(Address)` versus canonical `Address.as_hex`); state remained at zero and the source was patched with a dedicated regression test. A new deployment is required.

Record the fixture commit, finalized transaction hashes, and matching before/after `get_case` reads here after the lifecycle. Do not claim a live result until the explorer shows finalized status.
