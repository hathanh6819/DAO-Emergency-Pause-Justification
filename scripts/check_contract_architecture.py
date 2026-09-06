from __future__ import annotations

import ast
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "contracts" / "dao_emergency_pause_justification.py"


def fail(message: str) -> None:
    raise SystemExit("architecture_check=FAIL: " + message)


body = SOURCE.read_text(encoding="utf-8")
tree = ast.parse(body, str(SOURCE))

contract = next(
    (node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == "DAOEmergencyPauseJustification"),
    None,
)
if contract is None:
    fail("contract class missing")

evaluate = next(
    (
        nested
        for method in contract.body
        if isinstance(method, ast.FunctionDef) and method.name == "assess_pause"
        for nested in method.body
        if isinstance(nested, ast.FunctionDef) and nested.name == "evaluate"
    ),
    None,
)
if evaluate is None:
    fail("strict-equality evaluator missing")

if any(isinstance(node, ast.Name) and node.id == "self" for node in ast.walk(evaluate)):
    fail("storage access found inside nondeterministic evaluator")

if "gl.eq_principle.strict_eq(evaluate)" not in body:
    fail("assessment is not bound by strict_eq")
if "SOURCE_TOO_LARGE" in body or "[:MAX_" in body:
    fail("source truncation pattern found; oversized evidence must be rejected, never sliced")
if "len(body) == 0 or len(body) > MAX_BODY_BYTES" not in body:
    fail("Git evidence lacks explicit empty/oversized rejection")
if "len(tx_body) == 0 or len(tx_body) > MAX_TX_RESPONSE_BYTES" not in body:
    fail("transaction evidence lacks explicit empty/oversized rejection")
if "git_sha != str(item.get(\"sha\"" not in body:
    fail("fetched Git blobs are not authenticated against tree identities")
if "tx_epoch != observed_epoch" not in body:
    fail("timestamps are not compared through canonical epochs")
if "@gl.public.payable" in body or "gl.message.value" in body:
    fail("unexpected value-handling surface")

print("architecture_check=PASS")
print("nondet_storage_reads=0")
print("oversized_sources=fail_closed")
print("timestamp_comparison=canonical_epoch")
print("git_blob_identity=verified")
