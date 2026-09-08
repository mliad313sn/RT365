"""TC-SIG — Asymmetric signing [Source: 04, 06; NFR-SEC-01; D-053, ADR-015, ADR-019 proposed]: command authorisation and the
signed tool registry verify with a public trust set; signers hold the private key, verifiers hold none; rotation is
overlap-then-retire and a retired key verifies nothing. Every key pair here is generated in the test process (sim-only).
"""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path
from uuid import uuid4

import pytest
from conftest import ACCOUNT, INSTRUMENT, STRATEGY, TENANT
from execution_gateway.authorisation import (
    CommandAuthoriser,
    CommandVerifier,
    Ed25519CommandAuthoriser,
    PublicKeyCommandVerifier,
)
from mcp_servers.registry import (
    ALGORITHM_ED25519,
    REGISTRY_PURPOSE,
    RegistryUnsigned,
    envelope_message,
    load_registry,
    load_trust_set,
    prepare_envelope,
)
from rtcore.schemas.order import OrderState
from rtcore.signing import Ed25519Signer, ed25519_public_key, ed25519_sign
from rtcore.trust import TrustSet, ed25519_verify
from web_bff.platform import build_sim_platform

ROOT = Path(__file__).resolve().parents[2]
T0 = datetime(2026, 9, 1, 9, 0, tzinfo=UTC)  # before the sim platform base time so a key is valid when the pipeline signs

# RFC 8032 §7.1 TEST 1 (a published, public test vector; not a key of this platform).
RFC8032_SEED = bytes.fromhex("9d61b19deffd5a60ba844af492ec2cc44449c5697b326919703bac031cae7f60")
RFC8032_PUBLIC = bytes.fromhex("d75a980182b10ab7d54bfed3c964073a0ee172f3daa62325af021a68f707511a")
RFC8032_SIG = bytes.fromhex(
    "e5564300c360ac729086e2cc806e828a84877f1eb8e5d974d873e065224901555fb8821590a33bacc61e39701cf9b46bd25bf5f0595bbe24655141438e7a100b"
)


def _sign_registry_file(dst: Path, signer: Ed25519Signer, *, signed_at: datetime = T0, content: dict | None = None) -> Path:
    content = content or json.loads((ROOT / "mcp" / "policies" / "tool_registry.json").read_text())
    env = prepare_envelope(content, key_id=signer.key_id, algorithm=ALGORITHM_ED25519, signed_at=signed_at.isoformat(), fixture=True)
    dst.write_text(json.dumps({**env, "signature": signer.sign(REGISTRY_PURPOSE, envelope_message(env))}, indent=2, sort_keys=True))
    return dst


def _reachable(root: object, *, max_depth: int = 12) -> list[object]:
    """Objects reachable through attributes, bound-method ``__self__`` and containers.

    Function closures are deliberately not followed: the composition root's handler lambdas close over the whole
    SimPlatform (they need account snapshots), which is the in-process limitation R-44 records; the deployment
    boundary is a separate process holding verification material only (ADR-015 addendum, ADR-019 proposed).
    """
    seen: set[int] = set()
    out: list[object] = []
    stack: list[tuple[object, int]] = [(root, 0)]
    while stack:
        obj, depth = stack.pop()
        if id(obj) in seen or depth > max_depth or isinstance(obj, (type, type(sys))):
            continue
        seen.add(id(obj))
        out.append(obj)
        children: list[object] = []
        if hasattr(obj, "__self__") and not isinstance(obj, type):
            children.append(obj.__self__)
        if isinstance(obj, dict):
            children.extend(obj.keys())
            children.extend(obj.values())
        elif isinstance(obj, (list, tuple, set, frozenset)):
            children.extend(obj)
        elif not callable(obj) or hasattr(obj, "__dict__"):
            d = getattr(obj, "__dict__", None)
            if isinstance(d, dict) and not isinstance(obj, type(_reachable)):
                children.extend(d.values())
            for slot in getattr(type(obj), "__slots__", ()):
                if hasattr(obj, slot):
                    children.append(getattr(obj, slot))
        stack.extend((c, depth + 1) for c in children)
    return out


def _private_material_reachable(root: object, seeds: tuple[bytes, ...]) -> list[str]:
    findings: list[str] = []
    hexes = {s.hex() for s in seeds}
    for obj in _reachable(root):
        if isinstance(obj, (Ed25519Signer, Ed25519CommandAuthoriser, CommandAuthoriser, CommandVerifier)):
            findings.append(f"signing/forging handle {type(obj).__name__}")
        if isinstance(obj, (bytes, bytearray)) and bytes(obj) in seeds:
            findings.append("private seed bytes")
        if isinstance(obj, str) and obj in hexes:
            findings.append("private seed hex")
        if callable(getattr(obj, "sign", None)) and not isinstance(obj, type):
            findings.append(f"object with sign(): {type(obj).__name__}")
    return findings


@pytest.mark.tc("TC-SIG-001")
@pytest.mark.req("NFR-SEC-01")
@pytest.mark.quartet("positive")
@pytest.mark.env("sim")
def test_signed_command_and_registry_verify_with_public_trust_set(tmp_path):  # type: ignore[no-untyped-def]
    """Ed25519 matches the RFC 8032 vector; a command signed by the pipeline's signer verifies with a public-key-only verifier at the gateway and the intent executes; a registry signed with Ed25519 loads through the trust set with dev_key_in_use=False; the HMAC dev/sim path is unchanged."""
    assert ed25519_public_key(RFC8032_SEED) == RFC8032_PUBLIC
    assert ed25519_sign(RFC8032_SEED, b"") == RFC8032_SIG
    assert ed25519_verify(RFC8032_PUBLIC, b"", RFC8032_SIG)
    signer = Ed25519CommandAuthoriser.generate("cmd-sim-a")
    trust = TrustSet([signer.trusted_key(valid_from=T0)], purpose="order-command")
    p = build_sim_platform(command_signer=signer, command_trust_set=trust)
    r = p.run_intent(p.make_intent())
    assert r.order.state in (OrderState.ACKNOWLEDGED, OrderState.SUBMITTED, OrderState.FILLED)  # the sim broker fills at once
    assert r.order.command.authorisation.startswith("ed25519:cmd-sim-a:")
    verifier = PublicKeyCommandVerifier(trust)
    assert verifier.verify(r.order.command) is None
    assert p.broker.submissions_received == 1 and not p.audit.by_action("order.command.unauthorised")
    # registry: Ed25519 signature, trust set next to the file, public material only
    reg_signer = Ed25519Signer.generate("reg-sim-a")
    reg_trust = TrustSet([reg_signer.trusted_key(valid_from=T0)], purpose="tool-registry")
    signed = _sign_registry_file(tmp_path / "tool_registry.signed.json", reg_signer)
    reg = load_registry(signed, trust_set=reg_trust, at=T0)
    assert reg.algorithm == ALGORITHM_ED25519 and reg.key_id == "reg-sim-a" and not reg.dev_key_in_use and len(reg.tools) == 6
    (tmp_path / "trust").mkdir()
    reg_trust.save(tmp_path / "trust" / "registry_keys.json")
    assert load_registry(signed, at=T0).key_id == "reg-sim-a"  # default trust set: <dir>/trust/registry_keys.json
    p2 = build_sim_platform(registry_path=signed)
    assert p2.tool_call(p2.issue_agent(), "read_market_snapshot", {"instrument_id": INSTRUMENT}).ok
    # the committed registry still verifies on the HMAC dev path, explicitly and only in dev/sim
    committed = load_registry(ROOT / "mcp" / "policies" / "tool_registry.signed.json")
    assert committed.dev_key_in_use and committed.algorithm == "HMAC-SHA256" and committed.key_id == "dev-key-v0"
    hm = build_sim_platform()  # default: in-process HMAC authoriser, as before
    assert hm.run_intent(hm.make_intent()).order.command.authorisation.count(":") == 0


@pytest.mark.tc("TC-SIG-002")
@pytest.mark.req("NFR-SEC-01")
@pytest.mark.quartet("negative")
@pytest.mark.env("sim")
def test_wrong_key_altered_payload_unknown_and_retired_key_are_refused(tmp_path):  # type: ignore[no-untyped-def]
    """Wrong key, altered payload, unknown key_id and retired key are refused for commands (existing reason prefix, no broker order, audit row with correlation_id) and for the registry (RegistryUnsigned); the gateway fails closed on each."""
    a = Ed25519CommandAuthoriser.generate("cmd-a")
    trust = TrustSet([a.trusted_key(valid_from=T0)], purpose="order-command")
    p = build_sim_platform(command_signer=a, command_trust_set=trust)
    r = p.run_intent(p.make_intent())
    cmd = r.order.command
    verifier = PublicKeyCommandVerifier(trust)
    # wrong key: a signer with a different key pair but the same key_id
    imposter = Ed25519CommandAuthoriser.generate("cmd-a")
    reason = verifier.verify(imposter.sign(cmd))
    assert reason is not None and reason.startswith("command authorisation invalid")
    # altered payload after signing
    altered = cmd.model_copy(update={"quantity": cmd.quantity + 1})
    assert (verifier.verify(altered) or "").startswith("command authorisation invalid")
    # unknown key_id
    unknown = Ed25519CommandAuthoriser.generate("cmd-zzz").sign(cmd)
    assert "unknown key_id" in (verifier.verify(unknown) or "")
    # retired key: still in the trust set, but revoked
    trust.retire("cmd-a", at=T0 + timedelta(days=1))
    assert "retired" in (verifier.verify(cmd) or "")
    # unsigned
    assert verifier.verify(cmd.model_copy(update={"authorisation": ""})) == "command carries no control-plane authorisation"
    # through the gateway: refused before any adapter call, audited with the command's correlation_id
    from execution_gateway.gateway import CommandNotAuthorised
    from rtcore.planes import Plane, enter

    before = p.broker.submissions_received
    late = a.sign(cmd.model_copy(update={"idempotency_key": "k-retired", "command_id": "cmd-retired"}))
    with enter(Plane.CONTROL), pytest.raises(CommandNotAuthorised, match="retired"):
        p.gateway.submit(late, executor_id=p.executor_id, fencing_token=p.leases.current(ACCOUNT).fencing_token, now=p.now)
    assert p.broker.submissions_received == before
    rows = p.audit.by_action("order.command.unauthorised")
    assert rows and rows[-1].correlation_id == cmd.correlation_id and "retired" in str(rows[-1].payload["reason"])
    assert p.alerts.by_name("execution.unauthorised_command")

    # registry: the same four refusals
    reg_a = Ed25519Signer.generate("reg-a")
    reg_trust = TrustSet([reg_a.trusted_key(valid_from=T0)], purpose="tool-registry")
    good = _sign_registry_file(tmp_path / "good.json", reg_a)
    assert load_registry(good, trust_set=reg_trust, at=T0).key_id == "reg-a"
    wrong = _sign_registry_file(tmp_path / "wrong.json", Ed25519Signer.generate("reg-a"))
    with pytest.raises(RegistryUnsigned, match="signature invalid"):
        load_registry(wrong, trust_set=reg_trust, at=T0)
    raw = json.loads(good.read_text())
    raw["registry"]["tools"][0]["quota_per_minute"] = 100000
    (tmp_path / "altered.json").write_text(json.dumps(raw))
    with pytest.raises(RegistryUnsigned, match="signature invalid"):
        load_registry(tmp_path / "altered.json", trust_set=reg_trust, at=T0)
    unknown_file = _sign_registry_file(tmp_path / "unknown.json", Ed25519Signer.generate("reg-nobody"))
    with pytest.raises(RegistryUnsigned, match="unknown key_id"):
        load_registry(unknown_file, trust_set=reg_trust, at=T0)
    with pytest.raises(RegistryUnsigned, match="not yet valid"):
        load_registry(good, trust_set=reg_trust, at=T0 - timedelta(days=1))
    reg_trust.retire("reg-a", at=T0 + timedelta(days=30))
    with pytest.raises(RegistryUnsigned, match="retired"):
        load_registry(good, trust_set=reg_trust, at=T0 + timedelta(days=31))
    with pytest.raises(RegistryUnsigned, match="retired"):  # retired is absolute, even inside the former window
        load_registry(good, trust_set=reg_trust, at=T0)
    with pytest.raises(RegistryUnsigned, match="unknown key_id"):  # empty trust set: nothing asymmetric loads
        load_registry(good, trust_set=TrustSet(purpose="tool-registry"), at=T0)


@pytest.mark.tc("TC-SIG-003")
@pytest.mark.req("NFR-SEC-01")
@pytest.mark.quartet("abuse")
@pytest.mark.env("sim")
def test_verifier_exposes_no_private_key_and_algorithm_or_key_id_confusion_is_refused(tmp_path, monkeypatch):  # type: ignore[no-untyped-def]
    """The public-key verifier at the gateway and the MCP runtime reach no signer, seed or sign(); an HMAC-signed command is refused by an Ed25519-only verifier; a signature from key A under key_id B is refused; an HMAC envelope claiming Ed25519, an Ed25519 envelope claiming HMAC, an unknown algorithm and an HMAC registry outside dev/sim are all refused."""
    a = Ed25519CommandAuthoriser.generate("cmd-a")
    b = Ed25519CommandAuthoriser.generate("cmd-b")
    trust = TrustSet([a.trusted_key(valid_from=T0), b.trusted_key(valid_from=T0)], purpose="order-command")
    p = build_sim_platform(command_signer=a, command_trust_set=trust)
    seeds = (a.private_seed_for_test_only(), b.private_seed_for_test_only())
    verify_handle = p.gateway._verify_command  # the only authorisation object the gateway holds
    assert isinstance(verify_handle.__self__, PublicKeyCommandVerifier) and not hasattr(verify_handle.__self__, "sign")
    assert _private_material_reachable(verify_handle, seeds) == []
    assert _private_material_reachable(p.runtime, seeds) == []
    assert _private_material_reachable(p.registry, seeds) == []
    assert "seed" not in repr(a) and seeds[0].hex() not in repr(a) and seeds[0].hex() not in repr(trust)
    r = p.run_intent(p.make_intent())
    cmd = r.order.command
    verifier = PublicKeyCommandVerifier(trust)
    # HMAC-signed command presented to an Ed25519-only verifier
    hmac_cmd = CommandAuthoriser.generate().sign(cmd)
    assert "algorithm" in (verifier.verify(hmac_cmd) or "")
    # key A's signature replayed under key_id B (both trusted)
    sig_a = cmd.authorisation.split(":", 2)[2]
    replayed = cmd.model_copy(update={"authorisation": f"ed25519:cmd-b:{sig_a}"})
    assert (verifier.verify(replayed) or "").startswith("command authorisation invalid")
    # malformed encodings never reach the curve
    for bad in ("ed25519:cmd-a:zz", "ed25519:cmd-a", "ed25519::" + sig_a, "rsa:cmd-a:" + sig_a):
        assert (verifier.verify(cmd.model_copy(update={"authorisation": bad})) or "").startswith("command authorisation invalid")
    # registry algorithm confusion
    reg_a = Ed25519Signer.generate("reg-a")
    reg_trust = TrustSet([reg_a.trusted_key(valid_from=T0)], purpose="tool-registry")
    good = _sign_registry_file(tmp_path / "good.json", reg_a)
    raw = json.loads(good.read_text())
    hmac_claim = {**raw, "algorithm": "HMAC-SHA256"}
    (tmp_path / "hmac_claim.json").write_text(json.dumps(hmac_claim))
    with pytest.raises(RegistryUnsigned):
        load_registry(tmp_path / "hmac_claim.json", trust_set=reg_trust, at=T0)
    with pytest.raises(RegistryUnsigned):  # the public key offered as an HMAC key
        load_registry(tmp_path / "hmac_claim.json", key=reg_a.public_key.hex(), trust_set=reg_trust, at=T0)
    committed = json.loads((ROOT / "mcp" / "policies" / "tool_registry.signed.json").read_text())
    (tmp_path / "ed_claim.json").write_text(json.dumps({**committed, "algorithm": ALGORITHM_ED25519, "key_id": "reg-a"}))
    with pytest.raises(RegistryUnsigned):
        load_registry(tmp_path / "ed_claim.json", trust_set=reg_trust, at=T0)
    (tmp_path / "alg.json").write_text(json.dumps({**raw, "algorithm": "none"}))
    with pytest.raises(RegistryUnsigned, match="algorithm"):
        load_registry(tmp_path / "alg.json", trust_set=reg_trust, at=T0)
    # outside dev/sim only Ed25519 through the trust set is acceptable: HMAC with any configured key is refused
    monkeypatch.setenv("RT_ENV", "paper")
    monkeypatch.setenv("RT_MCP_REGISTRY_KEY", "configured-symmetric-key-not-allowed")
    with pytest.raises(RegistryUnsigned, match="HMAC"):
        load_registry(ROOT / "mcp" / "policies" / "tool_registry.signed.json", trust_set=reg_trust, at=T0)
    monkeypatch.setenv("RT_ENV", "sim")
    monkeypatch.delenv("RT_MCP_REGISTRY_KEY", raising=False)
    # CI invariant kept: the committed registry is not deployable to production as signed
    prod = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "verify_tool_registry.py"), "--production"], capture_output=True, text=True, cwd=ROOT
    )
    assert prod.returncode == 1 and "FAIL" in prod.stdout
    # the signing script refuses to fall back to the dev key without an explicit --dev
    refused = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "sign_tool_registry.py"), "--sim-fixture", "--out", str(tmp_path / "x.json")],
        capture_output=True,
        text=True,
        cwd=ROOT,
    )
    assert refused.returncode == 1 and "--dev" in refused.stdout
    assert not (tmp_path / "x.json").exists()


@pytest.mark.tc("TC-SIG-004")
@pytest.mark.req("NFR-SEC-01")
@pytest.mark.quartet("recovery")
@pytest.mark.env("sim")
def test_rotation_overlap_then_retire(tmp_path):  # type: ignore[no-untyped-def]
    """Rotation: key B is added to the trust set (overlap), the pipeline signs with B while A-signed commands still verify, A is retired and its commands are refused while B's verify; the registry re-signed with B (via the signing script) loads and the file signed by A is refused after retirement; the trust set round-trips through its JSON file."""
    a = Ed25519CommandAuthoriser.generate("cmd-a")
    trust = TrustSet([a.trusted_key(valid_from=T0)], purpose="order-command")
    p = build_sim_platform(command_signer=a, command_trust_set=trust)
    verifier = PublicKeyCommandVerifier(trust)
    first = p.run_intent(p.make_intent()).order.command
    assert verifier.verify(first) is None
    # overlap: B trusted, A still trusted; the composition root switches the signer to B
    b = Ed25519CommandAuthoriser.generate("cmd-b")
    trust.add(b.trusted_key(valid_from=T0 + timedelta(days=1)))
    p.rotate_command_signer(b)
    by_b = p.run_intent(
        p.make_intent(intent_id=str(uuid4()), quantity="120")
    ).order.command  # different economics: the duplicate control is not under test here
    assert by_b.authorisation.startswith("ed25519:cmd-b:") and verifier.verify(by_b) is None
    assert verifier.verify(first) is None  # A-signed still verifies during the overlap
    assert p.broker.submissions_received == 2
    # retire A: nothing signed by A verifies any more, B is unaffected
    trust.retire("cmd-a", at=T0 + timedelta(days=31))
    assert "retired" in (verifier.verify(first) or "") and verifier.verify(by_b) is None
    after = p.run_intent(p.make_intent(intent_id=str(uuid4()), quantity="140")).order.command
    assert after.authorisation.startswith("ed25519:cmd-b:") and p.broker.submissions_received == 3
    from execution_gateway.gateway import CommandNotAuthorised
    from rtcore.planes import Plane, enter

    stale = a.sign(first.model_copy(update={"idempotency_key": "k-a-after", "command_id": "cmd-a-after"}))
    with enter(Plane.CONTROL), pytest.raises(CommandNotAuthorised, match="retired"):
        p.gateway.submit(stale, executor_id=p.executor_id, fencing_token=p.leases.current(ACCOUNT).fencing_token, now=p.now)
    assert p.broker.submissions_received == 3

    # registry rotation through the signing script (sim-only key material written to tmp_path)
    reg_a = Ed25519Signer.generate("reg-a")
    reg_b = Ed25519Signer.generate("reg-b")
    reg_trust = TrustSet([reg_a.trusted_key(valid_from=T0)], purpose="tool-registry")
    old = _sign_registry_file(tmp_path / "old.json", reg_a)
    assert load_registry(old, trust_set=reg_trust, at=T0).key_id == "reg-a"
    reg_trust.add(reg_b.trusted_key(valid_from=T0 + timedelta(days=1)))
    key_file = tmp_path / "reg-b.ed25519"
    key_file.write_text(reg_b.private_seed_for_test_only().hex())
    new = tmp_path / "new.json"
    res = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "sign_tool_registry.py"),
            "--sim-fixture",
            "--ed25519-key",
            str(key_file),
            "--key-id",
            "reg-b",
            "--out",
            str(new),
        ],
        capture_output=True,
        text=True,
        cwd=ROOT,
    )
    assert res.returncode == 0, res.stdout + res.stderr
    at = T0 + timedelta(days=2)
    assert load_registry(new, trust_set=reg_trust, at=at).key_id == "reg-b"
    assert load_registry(old, trust_set=reg_trust, at=at).key_id == "reg-a"  # overlap
    reg_trust.retire("reg-a", at=T0 + timedelta(days=31))
    with pytest.raises(RegistryUnsigned, match="retired"):
        load_registry(old, trust_set=reg_trust, at=T0 + timedelta(days=32))
    assert load_registry(new, trust_set=reg_trust, at=T0 + timedelta(days=32)).key_id == "reg-b"
    # the trust set persists and reloads with the retirement intact
    reg_trust.save(tmp_path / "registry_keys.json")
    reloaded = TrustSet.load(tmp_path / "registry_keys.json")
    assert reloaded.get("reg-a").revoked and not reloaded.get("reg-b").revoked
    with pytest.raises(RegistryUnsigned, match="retired"):
        load_registry(old, trust_set=reloaded, at=T0 + timedelta(days=32))
    # the shipped trust set holds no ceremony key yet (H-20; the file itself is proposed to the MCP Security Agent,
    # CODEOWNER of mcp/policies): an absent or empty set refuses every Ed25519 registry
    shipped = load_trust_set(ROOT / "mcp" / "policies" / "tool_registry.signed.json")
    assert len(shipped) == 0
    with pytest.raises(RegistryUnsigned, match="unknown key_id"):
        load_registry(new, trust_set=shipped, at=at)
    assert TENANT and STRATEGY  # fixture identifiers unchanged by rotation
