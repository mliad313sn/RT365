# Key ceremony record — `<key_id>` (template; copy to `<key_id>.md`) [Committee: D-053 §2.3; H-20]

No private material appears in this record or anywhere in the repository. Only the public key, its fingerprint and the
KMS resource name are recorded. Three distinct humans sign; the Product Owner may witness but never holds a sign or
export grant.

| Field | Value |
|---|---|
| key_id | `<purpose>-<yyyy>-<nn>` (one key, one purpose: tool-registry / order-command / risk-policy) |
| purpose | tool-registry \| order-command \| risk-policy |
| algorithm | Ed25519 (or ECDSA P-256 if the KMS lacks Ed25519 [Open: Q-22-1]) |
| public_key (hex) | |
| fingerprint (SHA-256 of the public key) | |
| KMS/HSM resource name | |
| non-exportable | yes / no (must be yes) |
| IAM policy (sign grant) | exactly one workload identity: `<signing job identity>`; no human holds sign or export |
| created_at (UTC) | |
| valid_from | |
| planned rotation | valid_from + 12 months (proposal, D-053); immediately on compromise |
| overlap window | 30 days after the successor's valid_from (proposal, D-053) |
| trust-set entry committed in | `mcp/policies/trust/<purpose>_keys.json` @ commit `<sha>` (2nd-line CODEOWNER review) |
| verification from a clean checkout | test envelope signed and verified with the repository verifier: `<command and output>` |
| DECISION_LOG reference | D-<nnn> |
| AUDIT_EVIDENCE_INDEX row | |

## Participants (three distinct humans)
| Role | Name | Signature | Date |
|---|---|---|---|
| Operator (Security Architect) | | | |
| KMS administrator (Cloud Architect) | | | |
| Witness (Product Owner or named deputy) | | | |

## Retirement (filled at rotation or revocation)
| Field | Value |
|---|---|
| retired_at (UTC) | |
| reason | scheduled rotation \| suspected compromise \| participant departure \| KMS key-material event |
| successor key_id | |
| trust-set commit setting `revoked: true` | |
| re-signed artefact(s) | |
