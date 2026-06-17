# Tier 3 — Secure

The CAF **Secure** methodology is end-to-end: security applies across every CAF phase (strategy, plan, ready, adopt, govern, manage), and a gap in any phase weakens the whole posture. This skill carries the governance-relevant security guidance; the actual policy/Defender enforcement is implemented via `epac` and Azure tooling. Confirm specifics against the live source (`source-map.md` → Secure).

## Apply security across every phase, not as a gate

Security is not a single checkpoint. Each phase decision should reinforce protection, detection, and resilience. Align modernization work with the **Microsoft Zero Trust adoption framework**, and validate continuously through policy, IaC, compliance scanning, and **Microsoft Defender for Cloud secure score**.

## The four pillars

1. **Modernize security posture.** Continuous elevation of defenses, detections, and resilience — static controls degrade against evolving threats. Integrate identity strengthening, segmentation, just-in-time / least-privilege access, threat-detection tuning, data protection, and platform-baseline automation into landing zones and operations. Prioritize by measurable risk reduction (exposed privileges, insecure configs, unmonitored assets).
2. **Prepare for and respond to incidents.** A full incident lifecycle — readiness, detection, triage, containment, eradication, recovery, post-incident learning. Codify roles, comms, evidence handling, decision authority; tune telemetry to cut false positives and reduce MTTD; automate containment (isolate hosts, revoke tokens, quarantine storage).
3. **Adopt the CIA triad.** Map controls, telemetry, and metrics to **Confidentiality** (encryption, key management, identity, segmentation, data classification), **Integrity** (hashing, signing, immutable storage, version control, secure update chains), and **Availability** (redundancy, fault isolation, autoscaling, health probes, backup, DR). Gaps in any one principle cascade.
4. **Sustain security posture.** A disciplined cycle of measuring, improving, and validating control efficacy. Track Defender for Cloud secure-score controls, couple with risk-based metrics, automate drift detection via policy and pipelines, and feed incident retrospectives + threat intelligence back into the backlog.

## The security → governance → epac chain

Secure defines *what good looks like*; Govern decides *which security controls become enforced policy*; `epac` *implements* them as Azure Policy (e.g. Defender plans, encryption, private endpoints, baseline initiatives). When a user asks "how do we enforce this security control," give the Secure rationale here, the governance framing in Tier 2, and route the policy implementation to `epac`.

## Useful anchors beyond CAF

- **Zero Trust adoption framework** — the strategic model Secure aligns to.
- **Microsoft Cloud Security Benchmark (MCSB)** and **Defender for Cloud regulatory compliance** — the control catalog and continuous-assessment surface; many map to built-in policy initiatives (implement via `epac`).
- **Microsoft Cybersecurity Reference Architectures (MCRA)** — reference design for security capabilities.

## How to handle Secure questions

1. Identify the pillar (posture, incident, CIA, sustain).
2. Frame the control against Zero Trust and Defender secure score.
3. Separate *strategy/design* (here) from *enforcement* (Govern intent → `epac` implementation).
4. For compliance frameworks (CIS/NIST/ISO/MCSB), note they're delivered as built-in initiatives — design here, assign/deploy via `epac`.
5. Cite the specific Secure pages.

## Source pointers (fetch before asserting specifics)

- Secure overview: `https://learn.microsoft.com/azure/cloud-adoption-framework/secure/overview`
- Teams, roles, functions: `https://learn.microsoft.com/azure/cloud-adoption-framework/secure/teams-roles`
- Secure govern / manage phases: `https://learn.microsoft.com/azure/cloud-adoption-framework/secure/govern` , `.../secure/manage`
- Zero Trust adoption: `https://learn.microsoft.com/security/zero-trust/adopt/zero-trust-adoption-overview`
- Defender for Cloud secure score: `https://learn.microsoft.com/azure/defender-for-cloud/secure-score-security-controls`
- Microsoft Cloud Security Benchmark: `https://learn.microsoft.com/security/benchmark/azure/`
