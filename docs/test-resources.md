# Test resources

The local suite uses deterministic transport and model mocks to exercise the real contract entrypoints. It does not replace the contract with a mock.

Canonical fixture shapes live under `fixtures/canonical/`. The live fixture replays the FEG Bridge incident reported by CertiK and binds its published Base withdrawal transaction. Blockscout independently reports that transaction as successful at block 24331067 and binds it to the affected contract. Source: https://www.certik.com/blog/feg-bridge-exploit-technical-analysis and transaction: https://base.blockscout.com/tx/0x60fd436dbd0e99c7585b775095048eced56bfc11e18331cfcb0cdad6f9fe7d87

Local tests calculate real Git blob SHA-1 values from the exact mocked bytes, construct a matching commit tree, and mock the fixed Base Blockscout response. Adversarial cases mutate one authority-bound field at a time.

Before submission, commit the fixture files, deploy the exact source, and run the same lifecycle on Studionet. Record finalized transaction hashes and before/after state reads in `docs/deployment-evidence.md`. This fixture is a historical adjudication replay, not a claim that the 2024 incident remains active today.

Required deployed checks: registration; authorized request; justified assessment; wrong-caller consume; wrong-scope consume; correct consume; replay; unresolved source followed by retry; and state reads proving failed calls do not consume authorization.
