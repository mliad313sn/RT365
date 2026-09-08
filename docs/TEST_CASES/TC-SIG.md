# TC-SIG — Asymmetric signing: command authorisation and tool-registry trust set with rotation

Control: Asymmetric signing: command authorisation and tool-registry trust set with rotation — Requirement: NFR-SEC-01 — RTM row: NFR-SEC-01 — Owner: Security Architect — Reviewer (≠ owner): MCP Security Agent — **signature pending** (generated evidence is never self-certified [Source: 00, 11])

Environment tag: dev/sim — Data version: `sim-policy-v0.1 | sim-feed seed=7 | tool_registry 0.1.0` — Generated 2026-09-08T14:42:56.660963+00:00 at `3f155b0340953e9e2786ce25162cbd46461cbfea` (tree clean, tested tree `97be9c67b74e`)

| Quartet | Test ID | Given/When/Then (docstring) | Expected | Actual | Evidence link |
|---|---|---|---|---|---|
| positive | TC-SIG-001 | Ed25519 matches the RFC 8032 vector; a command signed by the pipeline's signer verifies with a public-key-only verifier at the gateway and the intent executes; a registry signed with Ed25519 loads through the trust set with dev_key_in_use=False; the HMAC dev/sim path is unchanged. | pass | passed | `test/quartets/test_tc_sig_signing.py::test_signed_command_and_registry_verify_with_public_trust_set` |
| negative | TC-SIG-002 | Wrong key, altered payload, unknown key_id and retired key are refused for commands (existing reason prefix, no broker order, audit row with correlation_id) and for the registry (RegistryUnsigned); the gateway fails closed on each. | pass | passed | `test/quartets/test_tc_sig_signing.py::test_wrong_key_altered_payload_unknown_and_retired_key_are_refused` |
| abuse | TC-SIG-003 | The public-key verifier at the gateway and the MCP runtime reach no signer, seed or sign(); an HMAC-signed command is refused by an Ed25519-only verifier; a signature from key A under key_id B is refused; an HMAC envelope claiming Ed25519, an Ed25519 envelope claiming HMAC, an unknown algorithm and an HMAC registry outside dev/sim are all refused. | pass | passed | `test/quartets/test_tc_sig_signing.py::test_verifier_exposes_no_private_key_and_algorithm_or_key_id_confusion_is_refused` |
| recovery | TC-SIG-004 | Rotation: key B is added to the trust set (overlap), the pipeline signs with B while A-signed commands still verify, A is retired and its commands are refused while B's verify; the registry re-signed with B (via the signing script) loads and the file signed by A is refused after retirement; the trust set round-trips through its JSON file. | pass | passed | `test/quartets/test_tc_sig_signing.py::test_rotation_overlap_then_retire` |

Quartet complete: yes. Records: 4.
