# SBOM

| Owner | Reviewer (different line) | Approving body | First gate | Status |
|---|---|---|---|---|
| Security Architect | Cloud Architect | Security & Privacy Board | B | Draft v1.0 |

Policy [Source: 06]: every deployable artefact ships with a generated SBOM (SPDX or CycloneDX), signed; SCA blocks known-critical vulnerabilities; model artefacts and prompts are inventoried alongside code (T-04).
| Artefact | SBOM format | Generated in | Signed by | Last SCA result |
|---|---|---|---|---|
| services/* images | CycloneDX | CI | [Open: O-83 — unsigned; no release key exists, H-30] | pending |
| mcp/servers images | CycloneDX | CI | [Open: O-83 — unsigned; no release key exists, H-30] | pending |
| apps/web bundle | CycloneDX | CI | [Open: O-83 — unsigned; no release key exists, H-30] | pending |
| models/prompts | inventory in MODEL_CARDS/, PROMPT_REGISTRY.md | Model Risk | — | — |
