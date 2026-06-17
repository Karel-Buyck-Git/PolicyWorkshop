# Tier 3 — Networking & Management Guardrails

Common guardrail patterns for landing zones — the controls a team actually assigns. This tier sits between architecture (Tier 2: *where* guardrails go) and deployment (Tier 4: *how* they ship via EPAC). Patterns below are durable; **always confirm the exact built-in name/ID, alias, and current parameters by fetching** (`source-map.md` → Azure Policy repo / AzAdvertizer) before handing someone JSON. Prefer a built-in or the ALZ baseline initiative over a custom policy.

## How to use this tier

When a teammate says "enforce X on the network/platform," do this:
1. Identify the **control** and the **resource type/alias** involved.
2. **Fetch** to find a built-in or ALZ-baseline policy for it (don't assume from memory).
3. Recommend the **altitude** (which MG — see `caf-alz-architecture.md`) and the **effect** (audit-first, then deny).
4. If authoring custom is unavoidable, use `policy-authoring.md`.
5. Note the **Known Issues** caveats for the target type (some network/dataplane types evaluate incompletely).

## Management / platform-wide guardrails

These usually assign at the intermediate root or Platform MG:
- **Allowed locations** — restrict resource and resource-group regions (data residency, cost). Built-in "Allowed locations" / "Allowed locations for resource groups."
- **Required tags** — enforce or append org tags (cost center, owner, environment). Modify effect supports remediation of existing resources.
- **Deny classic / deprecated resources** — block classic VMs, storage, etc.
- **Diagnostic settings** — DINE to route resource logs/metrics to a central Log Analytics workspace (foundational for monitoring landing zones).
- **Microsoft Defender for Cloud** — enable Defender plans and security baselines via the ALZ/regulatory initiatives.

## Networking guardrails

Assign mostly at Connectivity, Corp, or Online MGs depending on intent (see Tier 2 placement):
- **Deny public IP addresses** on NICs/VMs except where explicitly intended — a core Corp guardrail. Target `Microsoft.Network/networkInterfaces` / public IP associations (verify aliases).
- **Subnets must have an NSG** — DINE/audit that every subnet associates a network security group.
- **NSGs must restrict inbound** — audit/deny overly permissive rules (e.g. RDP/SSH from Internet, `0.0.0.0/0`).
- **Route tables / forced tunneling** — require UDRs that send egress through the hub firewall.
- **Private endpoints / deny public network access** — enforce private connectivity on PaaS (Storage, SQL, Key Vault): "should disable public network access" built-ins.
- **DDoS protection** — audit/enforce DDoS plan on virtual networks (Online MG).

### Application Gateway / WAF (internet-facing — Online MG)

- **WAF enabled** — Application Gateway should use the **WAF SKU** and have a Web Application Firewall policy associated; audit/deny non-WAF gateways. Target `Microsoft.Network/applicationGateways`.
- **WAF in Prevention mode** — the associated `Microsoft.Network/ApplicationGatewayWebApplicationFirewallPolicies` should run in Prevention (not just Detection).
- **TLS / HTTPS only** — listeners should require HTTPS and a minimum TLS version; deny plain HTTP listeners.
- **Front Door / WAF parity** — if Azure Front Door is used at the edge, apply equivalent WAF-policy guardrails there.

These pair naturally with the network-topology and governance CAF design areas — fetch the ALZ policy list to see which the baseline already covers before writing custom.

## Effect & rollout guidance specific to network guardrails

- Network guardrails frequently hit **existing non-compliant resources** in brownfield zones. Start with `Audit`/`AuditIfNotExists` or `enforcementMode: DoNotEnforce`, review compliance, communicate, remediate, then promote to `Deny`.
- Some networking/dataplane types appear in the **Known Issues** list (e.g. certain subnet properties populate differently on GET vs PUT). Deny may work while compliance reporting is imperfect — call this out so the team doesn't trust a green dashboard blindly.
- DINE network remediations (e.g. attach NSG, enable diagnostics) need the managed identity + roles and a remediation task for existing resources.

## Source pointers (fetch before asserting specifics)

- Built-in network policies: `https://github.com/Azure/azure-policy/tree/master/built-in-policies/policyDefinitions/Network`
- ALZ policy baseline: `https://aka.ms/alz/policies`
- Live built-in/alias lookup: `https://www.azadvertizer.net/`
- Known Issues (network/dataplane caveats): README at `https://github.com/Azure/azure-policy`
- App Gateway WAF concepts: `https://learn.microsoft.com/azure/web-application-firewall/ag/ag-overview`
