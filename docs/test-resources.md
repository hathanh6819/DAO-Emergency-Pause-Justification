# Test resources

The local suite uses deterministic transport and model mocks to exercise the real contract entrypoints. It does not replace the contract with a mock.

Canonical fixture shapes live under `fixtures/canonical/`. Tests calculate real Git blob SHA-1 values from the exact mocked bytes, construct a matching commit tree, and mock the fixed Base Blockscout response. Adversarial cases mutate one authority-bound field at a time.

Before submission, replace the illustrative transaction/address values with a real successful Base transaction whose `to` matches the manifest, commit the fixture files, deploy the exact source, and run the same lifecycle on Studionet. Record finalized transaction hashes and before/after state reads in `docs/deployment-evidence.md`.

Required deployed checks: registration; authorized request; justified assessment; wrong-caller consume; wrong-scope consume; correct consume; replay; unresolved source followed by retry; and state reads proving failed calls do not consume authorization.
