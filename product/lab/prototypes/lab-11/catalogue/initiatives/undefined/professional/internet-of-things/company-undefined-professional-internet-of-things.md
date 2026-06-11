# Company undefined Professional — Internet of Things

## Tier rationale

**Professional** — Active security posture for Internet of Things: controls that produce signals an operations team must act on. This tier delivers network hardening (public access disabled, VNet integration, firewall rules). Together these policies protect against unauthorized network exposure, exploitable vulnerabilities, and undetected privilege misuse. Maps to NIS2 Article 21 (detection & response), ISO 27001 A.12.4 (logging) and A.13 (network security).

## Policies

| # | Policy | Policy ID | Tag | Description | Allowed Values | Default Value | Soft Value | Hardened Value | Category | Domain | Version | Type | Tier | Requires Parameters | Requires Managed Identity |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Configure IoT Hub device provisioning service instances to disable public network access | 859dfc91-ea35-43a6-8256-31271c363794 |  | Disable public network access for your IoT Hub device provisioning instance so that it's not accessible over the public internet. This can reduce data leakage risks. Learn more at: https://aka.ms/iotdpsvnet. | Modify, Disabled | Modify | Modify | Modify | Internet of Things | undefined | 1.0.0 | BuiltIn | Professional | No | Yes |
| 2 | IoT Hub device provisioning service instances should disable public network access | d82101f3-f3ce-4fc5-8708-4c09f4009546 |  | Disabling public network access improves security by ensuring that IoT Hub device provisioning service instance isn't exposed on the public internet. Creating private endpoints can limit exposure of the IoT Hub device provisioning instances. Learn more at: https://aka.ms/iotdpsvnet. | Audit, Deny, Disabled | Audit | Audit | Deny | Internet of Things | undefined | 1.0.0 | BuiltIn | Professional | No | No |
