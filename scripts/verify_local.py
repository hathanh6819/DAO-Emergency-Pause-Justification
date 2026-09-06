from __future__ import annotations

import hashlib
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "contracts" / "dao_emergency_pause_justification.py"


def run(command: list[str]) -> None:
    result = subprocess.run(command, cwd=ROOT)
    if result.returncode:
        raise SystemExit(result.returncode)


run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider"])
run([sys.executable, "scripts/check_contract_architecture.py"])
run(["genvm-lint", "check", str(SOURCE)])
body = SOURCE.read_bytes()
compile(body, str(SOURCE), "exec")
print(f"contract_bytes={len(body)}")
print(f"contract_sha256={hashlib.sha256(body).hexdigest()}")
print("verification=PASS")
