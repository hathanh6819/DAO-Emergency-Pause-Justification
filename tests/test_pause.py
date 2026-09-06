import hashlib, json
from pathlib import Path
import pytest

CONTRACT = "contracts/dao_emergency_pause_justification.py"
REPO = "example/bridge-protocol"
COMMIT = "1" * 40
TREE = "2" * 40
POLICY_PATH = ".security/pause-policy.json"
INCIDENT_PATH = ".security/incidents/INC-2026-001.json"
COUNCIL = "0x2222222222222222222222222222222222222222"
TARGET = "0x3333333333333333333333333333333333333333"
AFFECTED = "0x4444444444444444444444444444444444444444"
TX = "0x" + "5" * 64
DIGEST = "sha256:" + "6" * 64

def deploy(d): return d(CONTRACT)
def setup(c): return c.register_protocol("BRIDGE_ALPHA", REPO, POLICY_PATH, COUNCIL, TARGET, 8453)
def request(c, vm, **kw):
    args = [1, kw.get("commit", COMMIT), kw.get("path", INCIDENT_PATH), kw.get("tx", TX), kw.get("affected", AFFECTED), kw.get("capability", "BRIDGE_WITHDRAWALS"), kw.get("duration", 3600), kw.get("digest", DIGEST)]
    with vm.prank(COUNCIL): return c.request_pause(*args)
def policy(**kw):
    v={"allowed_severities":["CRITICAL","HIGH"],"max_incident_age_seconds":86400,"max_pause_seconds":86400,"min_pause_seconds":900,"policy_revision":1,"protocol_code":"BRIDGE_ALPHA"};v.update(kw);return json.dumps(v,sort_keys=True)
def incident(**kw):
    v={"affected_contract":AFFECTED,"attesting_council":COUNCIL,"capability":"BRIDGE_WITHDRAWALS","chain_id":8453,"incident_summary":"An active withdrawal proof bypass permits immediate unauthorized release of escrowed user assets and remains unpatched.","incident_tx_hash":TX,"observed_at":"2026-09-06T00:00:00Z","protocol_code":"BRIDGE_ALPHA","severity":"CRITICAL"};v.update(kw);return json.dumps(v,sort_keys=True)
def git_blob(body): return hashlib.sha1(b"blob "+str(len(body)).encode()+b"\x00"+body).hexdigest()
def mock_sources(vm, inc=None, pol=None, status=200, commit=COMMIT, truncated=False, corrupt=False, tx_status=200, tx_hash=TX, tx_to=AFFECTED, tx_result="ok", tx_time="2026-09-06T00:00:00Z"):
    ib=(inc if inc is not None else incident()).encode();pb=(pol if pol is not None else policy()).encode()
    entries=[{"path":INCIDENT_PATH,"mode":"100644","type":"blob","sha":"f"*40 if corrupt else git_blob(ib),"size":len(ib)},{"path":POLICY_PATH,"mode":"100644","type":"blob","sha":git_blob(pb),"size":len(pb)}]
    vm.mock_web(r"/git/commits/",{"status":status,"body":json.dumps({"sha":commit,"tree":{"sha":TREE}})})
    vm.mock_web(r"/git/trees/",{"status":status,"body":json.dumps({"sha":TREE,"truncated":truncated,"tree":entries})})
    vm.mock_web(r"INC-2026-001\.json",{"status":status,"body":ib.decode()})
    vm.mock_web(r"pause-policy\.json",{"status":status,"body":pb.decode()})
    vm.mock_web(r"base\.blockscout\.com/api/v2/transactions/",{"status":tx_status,"body":json.dumps({"hash":tx_hash,"to":{"hash":tx_to},"status":tx_result,"timestamp":tx_time})})
def mock_model(vm, active=True, material=True, matches=True, **kw):
    v={"active_threat":active,"capability_matches":matches,"material_risk":material,"protocol_code":"BRIDGE_ALPHA"};v.update(kw)
    vm.mock_llm(r"Assess whether one emergency pause is justified",json.dumps(v))
def prepared(d,vm):
    vm.warp("2026-09-06T00:30:00Z");c=deploy(d);setup(c);request(c,vm);return c

def test_shape_is_distinct_and_nonpayable():
    s=Path(CONTRACT).read_text(); assert "maintainer_handoff" not in s and "payable" not in s
    assert "pause-policy" not in s and "/git/trees/" in s and "hashlib.sha1" in s and "strict_eq" in s and "base.blockscout.com" in s
    assert 'hasattr(value, "as_hex")' in s and "_address_text(security_council)" in s and "_address_text(affected_contract)" in s
    compile(s,CONTRACT,"exec")

def test_contract_identity_is_v3(direct_deploy):
    info=deploy(direct_deploy).get_protocol_info();assert info["version"]==3 and info["custody"] is False

def test_owner_registry_and_rotation(direct_deploy,direct_vm,direct_bob):
    c=deploy(direct_deploy)
    with direct_vm.prank(direct_bob): assert setup(c)=="ONLY_OWNER"
    assert setup(c)==1 and c.get_protocol(1)["policy_revision"]==1
    with direct_vm.prank(direct_bob): assert c.rotate_protocol_authority(1,COUNCIL,TARGET)=="ONLY_OWNER"
    assert c.rotate_protocol_authority(1,"0x7777777777777777777777777777777777777777",TARGET)=="AUTHORITY_ROTATED"
    assert c.get_protocol(1)["policy_revision"]==2

@pytest.mark.parametrize("field,value",[("commit","f"*39),("path","../x"),("tx","0x12"),("capability","bad lower"),("duration",10),("digest","bad")])
def test_invalid_request_no_mutation(direct_deploy,direct_vm,field,value):
    c=deploy(direct_deploy);setup(c);before=c.get_counts(); assert isinstance(request(c,direct_vm,**{field:value}),str);assert c.get_counts()==before

def test_only_council_and_duplicate_blocked(direct_deploy,direct_vm):
    c=deploy(direct_deploy);setup(c)
    assert c.request_pause(1,COMMIT,INCIDENT_PATH,TX,AFFECTED,"BRIDGE_WITHDRAWALS",3600,DIGEST)=="ONLY_SECURITY_COUNCIL"
    assert request(c,direct_vm)==1; before=c.get_counts(); assert request(c,direct_vm)=="INCIDENT_SCOPE_ALREADY_REGISTERED"; assert c.get_counts()==before

def test_justified_consume_scope_and_replay(direct_deploy,direct_vm):
    c=prepared(direct_deploy,direct_vm);mock_sources(direct_vm);mock_model(direct_vm)
    assert c.assess_pause(1,1)=="COUNCIL_ATTESTATION_SUPPORTS_PAUSE";r=c.get_case(1);assert r["revision"]==2 and r["evidence_digest"].startswith("sha256:")
    assert c.consume_pause_authorization(1,2,AFFECTED,"BRIDGE_WITHDRAWALS",3600,DIGEST)=="ONLY_EXECUTION_TARGET"
    with direct_vm.prank(TARGET):
        assert c.consume_pause_authorization(1,2,AFFECTED,"BRIDGE_WITHDRAWALS",3600,"sha256:"+"a"*64)=="AUTHORIZATION_SCOPE_MISMATCH"
        assert c.consume_pause_authorization(1,2,AFFECTED,"BRIDGE_WITHDRAWALS",3600,DIGEST)=="PAUSE_AUTHORIZATION_CONSUMED"
        assert c.consume_pause_authorization(1,2,AFFECTED,"BRIDGE_WITHDRAWALS",3600,DIGEST)=="AUTHORIZATION_ALREADY_CONSUMED"
    assert c.get_case(1)["consumed"]==1

@pytest.mark.parametrize("active,material,matches,status",[(False,True,True,"INSUFFICIENT_EVIDENCE"),(True,False,True,"INSUFFICIENT_EVIDENCE"),(True,True,False,"SCOPE_MISMATCH")])
def test_semantic_negative_never_authorizes(direct_deploy,direct_vm,active,material,matches,status):
    c=prepared(direct_deploy,direct_vm);mock_sources(direct_vm);mock_model(direct_vm,active,material,matches);assert c.assess_pause(1,1)==status;assert c.get_case(1)["consumed"]==0

def test_equivalent_timestamp_precision_is_canonicalized(direct_deploy,direct_vm):
    c=prepared(direct_deploy,direct_vm);mock_sources(direct_vm,tx_time="2026-09-06T00:00:00.000000Z");mock_model(direct_vm)
    assert c.assess_pause(1,1)=="COUNCIL_ATTESTATION_SUPPORTS_PAUSE"

@pytest.mark.parametrize("kwargs,expected",[
    ({"inc":incident(chain_id=1)},"BOUND_SCOPE_MISMATCH"),({"inc":incident(affected_contract=TARGET)},"BOUND_SCOPE_MISMATCH"),
    ({"inc":incident(incident_tx_hash="0x"+"9"*64)},"BOUND_SCOPE_MISMATCH"),({"pol":policy(max_pause_seconds=1000)},"DURATION_OR_SEVERITY_NOT_ALLOWED"),
    ({"pol":policy(policy_revision=2)},"POLICY_DOCUMENT_REVISION_MISMATCH"),({"status":503},"COMMIT_UNAVAILABLE"),
    ({"commit":"f"*40},"COMMIT_IDENTITY_MISMATCH"),({"truncated":True},"TREE_INCOMPLETE"),({"corrupt":True},"BLOB_DIGEST_MISMATCH"),
    ({"tx_status":503},"TRANSACTION_UNAVAILABLE_OR_OVERSIZED"),({"tx_hash":"0x"+"8"*64},"TRANSACTION_IDENTITY_MISMATCH"),
    ({"tx_to":TARGET},"TRANSACTION_TARGET_MISMATCH"),({"tx_result":"error"},"TRANSACTION_NOT_CONFIRMED"),
    ({"tx_time":"2026-09-05T00:00:00Z"},"TRANSACTION_TIME_MISMATCH"),
    ({"inc":incident(attesting_council=TARGET)},"ATTESTING_COUNCIL_MISMATCH"),
    ({"pol":policy(max_incident_age_seconds=60),"inc":incident(observed_at="2026-09-05T00:00:00Z"),"tx_time":"2026-09-05T00:00:00Z"},"INCIDENT_OUTSIDE_AUTHORIZATION_WINDOW"),
])
def test_authoritative_failures_fail_closed(direct_deploy,direct_vm,kwargs,expected):
    c=prepared(direct_deploy,direct_vm);mock_sources(direct_vm,**kwargs);assert c.assess_pause(1,1) in ("UNRESOLVED","SCOPE_MISMATCH","POLICY_VIOLATION","INSUFFICIENT_EVIDENCE");r=c.get_case(1);assert r["reason"]==expected and r["consumed"]==0
    assert (r["evidence_digest"]=="") == (r["status"]=="UNRESOLVED")

@pytest.mark.parametrize("bad",[{"extra":1},{"active_threat":"true"},{"protocol_code":"OTHER"}])
def test_model_schema_identity_and_types(direct_deploy,direct_vm,bad):
    c=prepared(direct_deploy,direct_vm);mock_sources(direct_vm);mock_model(direct_vm,**bad);assert c.assess_pause(1,1)=="UNRESOLVED";assert c.get_case(1)["evidence_digest"]==""

def test_unresolved_revision_recovery(direct_deploy,direct_vm):
    c=prepared(direct_deploy,direct_vm);mock_sources(direct_vm,status=503);assert c.assess_pause(1,1)=="UNRESOLVED"
    assert c.retry_unresolved(1,1)=="STALE_CASE_REVISION";assert c.retry_unresolved(1,2)=="PENDING"
    direct_vm.clear_mocks();mock_sources(direct_vm);mock_model(direct_vm);assert c.assess_pause(1,2)=="COUNCIL_ATTESTATION_SUPPORTS_PAUSE";assert c.get_case(1)["revision"]==3

def test_policy_rotation_stales_pending_case(direct_deploy,direct_vm):
    c=prepared(direct_deploy,direct_vm);c.rotate_protocol_authority(1,"0x7777777777777777777777777777777777777777",TARGET)
    assert c.assess_pause(1,1)=="STALE_POLICY_REVISION";assert c.get_case(1)["status"]=="PENDING"

def test_expired_authorization(direct_deploy,direct_vm):
    c=prepared(direct_deploy,direct_vm);mock_sources(direct_vm);mock_model(direct_vm);c.assess_pause(1,1)
    direct_vm.warp("2026-09-07T00:00:01Z")
    with direct_vm.prank(TARGET): assert c.consume_pause_authorization(1,2,AFFECTED,"BRIDGE_WITHDRAWALS",3600,DIGEST)=="AUTHORIZATION_EXPIRED"
    assert c.get_case(1)["consumed"]==0

def test_rotation_invalidates_issued_authorization(direct_deploy,direct_vm):
    c=prepared(direct_deploy,direct_vm);mock_sources(direct_vm);mock_model(direct_vm);c.assess_pause(1,1)
    c.rotate_protocol_authority(1,"0x7777777777777777777777777777777777777777",TARGET)
    with direct_vm.prank(TARGET): assert c.consume_pause_authorization(1,2,AFFECTED,"BRIDGE_WITHDRAWALS",3600,DIGEST)=="STALE_POLICY_REVISION"
    assert c.get_case(1)["consumed"]==0

def test_revoke_is_authorized_revisioned_and_terminal(direct_deploy,direct_vm,direct_bob):
    c=prepared(direct_deploy,direct_vm);mock_sources(direct_vm);mock_model(direct_vm);c.assess_pause(1,1);before=c.get_case(1)
    with direct_vm.prank(direct_bob): assert c.revoke_pause_authorization(1,2)=="ONLY_OWNER_OR_SECURITY_COUNCIL"
    assert c.get_case(1)==before
    with direct_vm.prank(COUNCIL): assert c.revoke_pause_authorization(1,2)=="PAUSE_AUTHORIZATION_REVOKED"
    assert c.get_case(1)["revoked"]==1 and c.get_case(1)["revision"]==3
    with direct_vm.prank(TARGET): assert c.consume_pause_authorization(1,3,AFFECTED,"BRIDGE_WITHDRAWALS",3600,DIGEST)=="AUTHORIZATION_REVOKED"

def test_deactivation_invalidates_authorization(direct_deploy,direct_vm):
    c=prepared(direct_deploy,direct_vm);mock_sources(direct_vm);mock_model(direct_vm);c.assess_pause(1,1)
    assert c.deactivate_protocol(1)=="PROTOCOL_DEACTIVATED"
    with direct_vm.prank(TARGET): assert c.consume_pause_authorization(1,2,AFFECTED,"BRIDGE_WITHDRAWALS",3600,DIGEST)=="PROTOCOL_INACTIVE"
    assert c.get_case(1)["consumed"]==0
