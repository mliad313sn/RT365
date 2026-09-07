# Infrastructure as Code [Source: 03; Cloud Architect]

Cells: one regional cell per venue cluster (ADR-007). Each cell contains the five namespaces in
`../kubernetes/namespaces.yaml` and the network policies in `../kubernetes/network-policies/`,
checked by `scripts/check_network_policies.py` (TC-NET-001..004).

Provisioning of cloud accounts, vault/KMS, clusters and the egress gateway is a human act
(docs/MISSING_ACTIONS.md H-05) and follows goals/external/infrastructure_provisioning.md.
Terraform/Pulumi modules are added here once the cloud provider is chosen [Open]; the plane
invariants are the acceptance test for whatever tooling is selected.
