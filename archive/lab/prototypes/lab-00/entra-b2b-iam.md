# Microsoft Entra B2B IAM — Request for Proposal

## 1. Introduction and purpose
This Request for Proposal (RFP) invites qualified system integrators and identity platform specialists to submit proposals for the design, implementation, and operationalisation of a Business-to-Business (B2B) Identity and Access Management (IAM) solution based on Microsoft Entra ID.

The organisation requires a structured, secure, and governed approach to managing external identities — including partners, suppliers, contractors, and auditors — across its Microsoft 365 and Azure environments. The selected partner will be responsible for translating the access principles described in this document into a production-ready, policy-driven platform.

## 2. Background and business context
The organisation currently grants external parties access to internal resources through a combination of shared accounts, manually managed guest invitations, and application-specific credentials. This approach has resulted in:

- Insufficient visibility into who has access to what, and for how long
- No consistent enforcement of authentication strength for external users
- Privileged roles assigned permanently to third-party accounts with no review cycle
- Devices used by external users that are outside the organisation's compliance boundary

The organisation has standardised on Microsoft 365 and Azure as its primary platforms. Microsoft Entra ID is already in use for internal identity management. The scope of this RFP is to extend that platform to govern external identities with the same rigour applied to internal staff.

## 3. Scope of work

The selected vendor shall deliver the following workstreams:

### 3.1 Discovery and current-state assessment
Conduct a structured assessment of the existing B2B access landscape, including an inventory of all active guest accounts, current role assignments, authentication policies in force, and any cross-tenant trust configurations. Findings shall be documented in a written report with a prioritised risk register.

### 3.2 Conditional Access design and implementation
Design and deploy a Conditional Access policy framework governing all external user sign-ins. The framework must address the following requirements:

- Multi-factor authentication shall be enforced for all guest and external users without exception. The implementation shall not rely on inbound MFA claims from partner tenants unless a formal trust assessment has been completed and approved.
- Legacy authentication protocols shall be blocked for all external identities. No exceptions are permitted.
- Sign-in risk and user risk signals from Microsoft Entra ID Protection shall be incorporated into policy decisions. High-risk sign-ins shall trigger automatic blocking or step-up authentication.
- Named location policies shall restrict access from geographies outside the organisation's defined operating regions, with a documented exception process for approved deviations.
- Session controls shall enforce re-authentication intervals, disable persistent browser sessions, and — for unmanaged devices — restrict functionality to browser-based access with download prevention.
- All policies shall be implemented in report-only mode first, with a validation period of no less than ten business days before enforcement is enabled.

### 3.3 Privileged Identity Management implementation
Remove all standing privileged role assignments from external user accounts and replace them with eligible assignments governed by Privileged Identity Management. Requirements include:

- No external user shall hold a permanently active Azure AD directory role or Azure RBAC role. All privileged access shall be time-bound and activated on demand.
- Activation requests shall require a written justification and, for roles classified as high-impact, approval from a designated internal role owner.
- Maximum activation duration shall be defined per role, not to exceed four hours for directory roles and eight hours for Azure resource roles, unless a specific exception is approved in writing.
- PIM alerts shall be configured and integrated with the organisation's SIEM or notification platform.
- An access review schedule shall be established for all eligible role assignments. Reviews shall occur no less than quarterly and shall be assigned to an internal sponsor for each external user or third-party organisation.

### 3.4 Device compliance framework
Define and implement a device compliance strategy that accounts for the three categories of device used by external parties: partner-managed devices enrolled in the partner's MDM platform, unmanaged bring-your-own devices, and organisation-issued devices. Requirements include:

- For partner-managed devices: assess the feasibility of cross-tenant compliance trust via Entra External Identities cross-tenant access settings. Where trust is established, document the partner's compliance baseline and the approval process for that trust relationship.
- For unmanaged devices: implement a Conditional Access App Control policy enforcing browser-only sessions with download blocking and session watermarking for designated sensitive applications.
- For organisation-issued devices: confirm that existing Intune compliance policies extend correctly to guest user sessions and that the compliant device grant control is enforced.
- Compliance policy minimum requirements shall include: disk encryption, minimum OS version, active antivirus, screen lock enforcement, and — for mobile devices — jailbreak and root detection.

### 3.5 Guest lifecycle governance
Implement an automated guest lifecycle process including:

- A maximum account validity period of twelve months, with automated notification to the account sponsor thirty days before expiry.
- An Entra Entitlement Management access package configuration for at least two use cases, enabling self-service access requests with policy-driven approval and automatic expiry.
- A documented off-boarding procedure ensuring that guest accounts are disabled and access is revoked within 24 hours of a termination trigger.

### 3.6 Monitoring and alerting
Configure logging, alerting, and reporting to provide ongoing visibility into the B2B access environment:

- All Entra sign-in and audit logs shall be forwarded to the organisation's Log Analytics workspace or SIEM platform.
- Detection rules shall be implemented for: impossible travel sign-ins by guest users, PIM activations outside defined business hours, bulk download events by external users, and guest accounts approaching or exceeding their validity period.
- A monthly B2B access report shall be defined, covering active guest count, MFA compliance rate, devices without compliance status, and open access reviews.