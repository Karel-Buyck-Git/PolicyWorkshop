# Azure Category Abbreviations

> **Authored map** — the single source of truth for catalogue *category* short codes.
> Used to build brand-neutral, within-limit technical names of the form
> `<domain>-<tier>-<abbreviation>` (e.g. `integration-esn-apim`). Read by both the
> producer (catalogue-builder) and the consumer (epac-builder) via
> `flows/shared/naming.py`. Edit here, then re-run the catalogue-builder.
>
> **Basis** — `CAF`: aligned to the official Cloud Adoption Framework resource
> abbreviation; `shortname`: a simple readable code (the category is not an Azure
> resource type, e.g. Tags / Regulatory Compliance / Security Center).
>
> **Rules** — codes must be unique within a domain and keep the assignment name
> (`<domain>-<tier>-<abbr>`) at or under **24** characters. QC enforces both.

| Domain | Category | Abbreviation | Basis |
|---|---|---|---|
| ai-foundry | azure-ai-services | ais | shortname |
| ai-foundry | bot-service | bot | CAF |
| ai-foundry | cognitive-services | cog | CAF |
| ai-foundry | health-bot | hbot | shortname |
| ai-foundry | machine-learning | mlw | CAF |
| ai-foundry | search | srch | CAF |
| compute | azure-local | azl | shortname |
| compute | batch | ba | CAF |
| compute | compute | cmp | shortname |
| compute | desktop-virtualization | avd | CAF |
| compute | lab-services | labs | shortname |
| compute | service-fabric | sf | CAF |
| compute | stack-hci | hci | shortname |
| compute | trusted-launch | tl | shortname |
| compute | vm-image-builder | aib | CAF |
| containers | container-apps | ca | CAF |
| containers | container-instance | ci | CAF |
| containers | container-instances | cis | shortname |
| containers | container-registry | cr | CAF |
| containers | kubernetes | aks | CAF |
| data | azure-data-explorer | adx | CAF |
| data | azure-databricks | dbw | CAF |
| data | azure-purview | pvw | CAF |
| data | cache | redis | CAF |
| data | cosmos-db | cosmos | CAF |
| data | data-factory | adf | CAF |
| data | data-lake | dls | CAF |
| data | hdinsight | hdi | CAF |
| data | postgresql | psql | CAF |
| data | sql | sql | CAF |
| data | sql-managed-instance | sqlmi | CAF |
| data | sql-server | sqls | shortname |
| data | stream-analytics | asa | CAF |
| data | synapse | syn | CAF |
| devops | azure-load-testing | lt | CAF |
| devops | custom-provider | cp | shortname |
| devops | devcenter | dc | shortname |
| devops | devopsinfrastructure | doi | shortname |
| integration | api-management | apim | CAF |
| integration | communication | acs | CAF |
| integration | durable-task | dtk | shortname |
| integration | event-grid | evg | CAF |
| integration | event-hub | evh | CAF |
| integration | fluid-relay | fr | shortname |
| integration | logic-apps | logic | CAF |
| integration | service-bus | sb | CAF |
| integration | signalr | sigr | CAF |
| integration | web-pubsub | wps | CAF |
| management | automanage | amng | shortname |
| management | automatic-update | au | shortname |
| management | automation | aa | CAF |
| management | azure-arc | arc | CAF |
| management | azure-update-manager | aum | shortname |
| management | general | gen | shortname |
| management | guest-configuration | gc | shortname |
| management | lighthouse | lh | shortname |
| management | managed-application | mapp | shortname |
| management | migrate | migr | shortname |
| management | portal | prtl | shortname |
| management | regulatory-compliance | reg | shortname |
| management | tags | tags | shortname |
| monitoring | changetrackingandinventory | cti | shortname |
| monitoring | managed-grafana | amg | CAF |
| monitoring | monitoring | mon | shortname |
| networking | cdn | cdn | CAF |
| networking | network | net | shortname |
| security | attestation | att | shortname |
| security | azure-active-directory | aad | shortname |
| security | key-vault | kv | CAF |
| security | managed-identity | id | CAF |
| security | security-center | asc | shortname |
| security | security-center-granular-pricing | ascg | shortname |
| storage | backup | bkp | shortname |
| storage | data-box | dbox | shortname |
| storage | elasticsan | esan | CAF |
| storage | resilience | resl | shortname |
| storage | site-recovery | asr | CAF |
| storage | storage | st | CAF |
| undefined | api-for-fhir | fhir | shortname |
| undefined | azure-edge-hardware-center | ehc | shortname |
| undefined | azure-stack-edge | ase | shortname |
| undefined | builtinpolicytest | test | shortname |
| undefined | health-data-services-workspace | hds | shortname |
| undefined | health-deidentification-service | hdid | shortname |
| undefined | healthcare-apis | hapi | shortname |
| undefined | internet-of-things | iot | shortname |
| undefined | maps | map | shortname |
| undefined | mission | msn | shortname |
| undefined | missionplatforms | msnp | shortname |
| undefined | planetary-computer | plc | shortname |
| undefined | privileged-identity-management | pim | shortname |
| undefined | virtualenclaves | ve | shortname |
| web | app-configuration | appcs | CAF |
| web | app-platform | spr | shortname |
| web | app-service | app | CAF |
