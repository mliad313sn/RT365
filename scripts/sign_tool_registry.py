#!/usr/bin/env python3
"""Sign mcp/policies/tool_registry.json -> tool_registry.signed.json (MCP Security Agent's signing job).

Rules (ADR-011, review OBJ-2; D-053, ADR-019 proposed):
* a registry with any pending approval_record cannot be signed as an approved registry; it can only be signed as a
  sim FIXTURE (--sim-fixture) that the loader refuses outside dev/sim;
* --ed25519-key <file> signs with an Ed25519 private seed (32 raw bytes or 64 hex characters) under --key-id; the
  file is never committed (the production key is KMS/HSM-held, H-20, and this path is the sim/ceremony-test path);
* --dev signs with the dev HMAC key (dev/sim only, key_id dev-key-v0). Without one of the two the script refuses:
  there is no silent fallback to the dev key.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "libs" / "core"))
sys.path.insert(0, str(ROOT / "mcp" / "servers"))
from mcp_servers.registry import (  # noqa: E402
    ALGORITHM_ED25519,
    REGISTRY_PURPOSE,
    RegistryUnsigned,
    envelope_message,
    pending_approvals,
    prepare_envelope,
    sign_registry,
    signing_key,
)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--sim-fixture", action="store_true", help="sign as a sim fixture (pending approvals allowed; refused outside dev/sim)")
    ap.add_argument("--ed25519-key", metavar="FILE", help="Ed25519 private seed file (never committed)")
    ap.add_argument("--key-id", help="trust-set key_id for the Ed25519 key")
    ap.add_argument("--dev", action="store_true", help="sign with the dev HMAC key (dev/sim only)")
    ap.add_argument("--src", default=str(ROOT / "mcp" / "policies" / "tool_registry.json"))
    ap.add_argument("--out", default=str(ROOT / "mcp" / "policies" / "tool_registry.signed.json"))
    args = ap.parse_args(argv)
    src, dst = Path(args.src), Path(args.out)
    content = json.loads(src.read_text())
    signed_at = datetime.now(tz=UTC).isoformat()
    try:
        if args.ed25519_key and args.dev:
            raise RegistryUnsigned("choose one of --ed25519-key or --dev")
        if args.ed25519_key:
            if not args.key_id:
                raise RegistryUnsigned("--key-id is required with --ed25519-key (it must match a trust-set entry)")
            from rtcore.signing import Ed25519Signer  # signing capability: this job only, never the MCP servers

            signer = Ed25519Signer.from_file(args.key_id, args.ed25519_key)
            env = prepare_envelope(
                content, key_id=signer.key_id, algorithm=ALGORITHM_ED25519, signed_at=signed_at, fixture=args.sim_fixture
            )
            signed = {**env, "signature": signer.sign(REGISTRY_PURPOSE, envelope_message(env))}
            how = f"Ed25519 key_id={signer.key_id} public={signer.public_key.hex()[:16]}..."
        elif args.dev:
            key, dev = signing_key()
            if not dev:
                raise RegistryUnsigned("--dev requested but RT_MCP_REGISTRY_KEY is set to a non-dev key; unset it or use --ed25519-key")
            signed = sign_registry(content, key, "dev-key-v0", signed_at=signed_at, fixture=args.sim_fixture)
            how = "DEV HMAC KEY (dev/sim only, not for production)"
        else:
            raise RegistryUnsigned(
                "no signing key selected: pass --ed25519-key FILE --key-id ID, or --dev for the dev HMAC key (dev/sim only)"
            )
    except (RegistryUnsigned, OSError, ValueError) as exc:
        print(f"REFUSED: {exc}")
        return 1
    dst.write_text(json.dumps(signed, indent=2, sort_keys=True) + "\n")
    print(f"signed {dst} with {how}; fixture={args.sim_fixture}; pending approvals={pending_approvals(content)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
