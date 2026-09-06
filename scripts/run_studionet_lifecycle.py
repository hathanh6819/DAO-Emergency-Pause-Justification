#!/usr/bin/env python3
"""Run the live Studionet lifecycle against the already deployed contract. Never deploys."""

import hashlib
import json
import os

from genlayer_py import create_account, create_client, studionet
from genlayer_py.types.transactions import TransactionStatus

CONTRACT = os.environ.get("PAUSE_CONTRACT_ADDRESS", "").strip()
REPOSITORY = "hathanh6819/dao-emergency-pause-justification"
POLICY_PATH = "fixtures/canonical/pause-policy.json"
INCIDENT_PATH = "fixtures/canonical/INC-2026-001.json"
FIXTURE_COMMIT = "999af91c5e8effd7ea0d44e9ebc5967ff6e4ebab"
PROTOCOL = "FEG_BRIDGE_REPLAY"
INCIDENT_TX = "0x60fd436dbd0e99c7585b775095048eced56bfc11e18331cfcb0cdad6f9fe7d87"
AFFECTED = "0xef7bd1543bdacadd7e42822e3f15dd0af0410fda"
CAPABILITY = "BRIDGE_WITHDRAWALS"
DURATION = 3600
ACTION_DIGEST = "sha256:" + hashlib.sha256(b"pause:FEG_BRIDGE_REPLAY:BRIDGE_WITHDRAWALS:3600").hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def checkpoint(condition, message):
    if not condition:
        raise RuntimeError("CHECKPOINT FAILED: " + message)
    print("CHECKPOINT OK: " + message, flush=True)


def read(client, method, args=None):
    value = client.read_contract(address=CONTRACT, function_name=method, args=args or [])
    print("READ " + method + "=" + canonical(value), flush=True)
    return value


def write(client, method, args, timeout=1500):
    tx = client.write_contract(address=CONTRACT, function_name=method, args=args, value=0)
    print("WRITE " + method + " tx=" + str(tx), flush=True)
    receipt = client.wait_for_transaction_receipt(
        tx, status=TransactionStatus.FINALIZED, interval=3000,
        retries=max(1, timeout // 3), full_transaction=False,
    )
    status = str(receipt.get("status_name", receipt.get("status", ""))).upper()
    result = str(receipt.get("result_name", receipt.get("result", ""))).upper()
    checkpoint("ERROR" not in result and "FAILED" not in status, method + " finalized")
    return str(tx)


def main():
    if not CONTRACT:
        raise SystemExit("Set PAUSE_CONTRACT_ADDRESS to the newly deployed, source-verified contract")
    secret = os.environ.get("PAUSE_OWNER_PRIVATE_KEY", "").strip()
    if not secret:
        raise SystemExit("Set PAUSE_OWNER_PRIVATE_KEY to the private key of the deployment owner")
    owner = create_account(secret)
    council = create_account()
    execution = create_account()
    outsider = create_account()
    owner_client = create_client(chain=studionet, account=owner)
    council_client = create_client(chain=studionet, account=council)
    execution_client = create_client(chain=studionet, account=execution)
    outsider_client = create_client(chain=studionet, account=outsider)
    for account, amount in ((owner, 3), (council, 2), (execution, 2), (outsider, 1)):
        owner_client.fund_account(account.address, amount * 10**18)

    print("contract=" + CONTRACT, flush=True)
    print("owner=" + str(owner.address), flush=True)
    print("council=" + str(council.address), flush=True)
    print("execution=" + str(execution.address), flush=True)
    txs = {}
    info = read(owner_client, "get_protocol_info")
    checkpoint(info.get("version") == 3 and info.get("custody") is False, "expected non-custodial contract schema")
    checkpoint(str(info.get("owner", "")).lower() == str(owner.address).lower(), "deployment owner identity matches signer")
    checkpoint(read(owner_client, "get_counts") == {"protocol_count": 0, "case_count": 0}, "fresh deployment")

    before = read(owner_client, "get_counts")
    txs["unauthorized_register"] = write(outsider_client, "register_protocol", [PROTOCOL, REPOSITORY, POLICY_PATH, council.address, execution.address, 8453])
    checkpoint(read(owner_client, "get_counts") == before, "unauthorized registration leaves state unchanged")

    txs["register_protocol"] = write(owner_client, "register_protocol", [PROTOCOL, REPOSITORY, POLICY_PATH, council.address, execution.address, 8453])
    protocol = read(owner_client, "get_protocol", [1])
    checkpoint(protocol.get("repository") == REPOSITORY and protocol.get("security_council", "").lower() == str(council.address).lower(), "authority-controlled source registered")

    txs["unauthorized_request"] = write(outsider_client, "request_pause", [1, FIXTURE_COMMIT, INCIDENT_PATH, INCIDENT_TX, AFFECTED, CAPABILITY, DURATION, ACTION_DIGEST])
    checkpoint(read(owner_client, "get_counts").get("case_count") == 0, "unauthorized request leaves state unchanged")
    txs["request_pause"] = write(council_client, "request_pause", [1, FIXTURE_COMMIT, INCIDENT_PATH, INCIDENT_TX, AFFECTED, CAPABILITY, DURATION, ACTION_DIGEST])
    pending = read(owner_client, "get_case", [1])
    checkpoint(pending.get("status") == "PENDING" and pending.get("commit") == FIXTURE_COMMIT, "request binds canonical commit and incident")

    txs["assess_pause"] = write(owner_client, "assess_pause", [1, 1])
    assessed = read(owner_client, "get_case", [1])
    checkpoint(assessed.get("status") == "POLICY_VIOLATION", "historical incident cannot authorize a current pause")
    checkpoint(assessed.get("reason") == "INCIDENT_OUTSIDE_AUTHORIZATION_WINDOW", "temporal failure is explicit")
    checkpoint(str(assessed.get("evidence_digest", "")).startswith("sha256:"), "non-positive assessment publishes bounded receipt digest")

    txs["wrong_caller_consume"] = write(outsider_client, "consume_pause_authorization", [1, 2, AFFECTED, CAPABILITY, DURATION, ACTION_DIGEST])
    checkpoint(read(owner_client, "get_case", [1]).get("consumed") == 0, "wrong caller cannot consume")
    txs["execution_target_consume_blocked"] = write(execution_client, "consume_pause_authorization", [1, 2, AFFECTED, CAPABILITY, DURATION, ACTION_DIGEST])
    checkpoint(read(owner_client, "get_case", [1]).get("consumed") == 0, "execution target cannot consume a non-positive result")
    print("LIFECYCLE_COMPLETE", flush=True)
    print("transactions=" + canonical(txs), flush=True)


if __name__ == "__main__":
    main()
