"""Generate the dlw-az-naming Azure Policy definitions from the customer naming
convention defined in getResourceName.bicep (v1.5).

PRODUCT: DLW Azure naming governance as code. This tool generates the custom policy
definitions (one per resource type) plus the 'naming' initiative that bundles them, so
the platform can verify resource names against the dlw MSPE convention.

EFFECT DEFAULT = 'Audit' (definitions AND the initiative's top-level effect parameter).
The set ships safe: it reports, it does not block. Enforcement is a per-customer decision
made AT THE CUSTOMER — override the initiative's 'effect' parameter to 'Deny' on the EPAC
assignment in the customer tenant. Do NOT bake 'Deny' into the generated artifacts here.

Convention (default): {customerAbbreviation}-{abbr}-{service}-{environmentName}-{locationAbbreviation}-{instanceNumber}
Some resource types are special-cased (compact, parent-prefixed, peering, subnet, VM).

Validation strategy (Azure Policy limits: 'like' allows ONE '*', 'match' is fixed-width):
  - Anchor the deterministic head/token of each name; flag names that don't match.
  - customerAbbreviation is a parameter (default 'dlw'); the resource abbreviation is baked.

Base resource list + categories come from the CAF abbreviation page; the customer
MODULE map overrides abbreviation + template kind for the ~70 types it defines.

Output: one EPAC policyDefinition JSON per ARM type under
        catalogue/definitions/custom/dlw-az-naming/ (existing naming-*.json are replaced).

Usage:  python flows/definition_gen/gen_dlw_naming_definitions.py
See gen-dlw-naming-definitions.md for the full narrative.
"""
import glob, json, os, re, sys
from collections import OrderedDict

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # flows/ root
from shared.paths import CATALOGUE_DIR  # noqa: E402  the ONE catalogue path

LAB = CATALOGUE_DIR.parent
OUT = CATALOGUE_DIR / "definitions" / "custom" / "dlw-az-naming"
_EPAC_BASE = "https://raw.githubusercontent.com/Azure/enterprise-azure-policy-as-code/main/Schemas"
SCHEMA_DEF = f"{_EPAC_BASE}/policy-definition-schema.json"
SCHEMA_POLICYSET = f"{_EPAC_BASE}/policy-set-definition-schema.json"
SCHEMA_ASSIGNMENT = f"{_EPAC_BASE}/policy-assignment-schema.json"
SCHEMA_EXEMPTIONS = f"{_EPAC_BASE}/policy-exemption-schema.json"
CUST_DEFAULT = "dlw"
SOURCE = "getResourceName.bicep v1.5"

# ---- 'naming' initiative (placed alongside the built-in producer's output) ----
PREFIX = "company"
INIT_DOMAIN = "Management"
INIT_TIER = "Essential"
INIT_CATEGORY = "Naming"          # leaf category (folder slug = 'naming')
INIT_NAME = f"{PREFIX}-management-essential-naming"
INIT_DISPLAY = "Company Management Essential — Naming"
INIT_DIR = LAB / "catalogue" / "initiatives" / "management" / "essential" / "naming"
INIT_RATIONALE = (
    "**Essential** — Naming-convention guardrails for every Azure resource type: audits "
    "(or denies) resources whose names do not follow the DLW landing-zone convention defined "
    "in getResourceName.bicep. Consistent, decodable names are baseline hygiene — they "
    "underpin cost allocation, automation, access scoping and incident response. Effects "
    "default to Audit and are tuned from a single initiative parameter."
)

# ---- CAF base rows (category, resource, namespace_raw, abbr) + 2 module-only adds ----
ROWS = [
    ("AI + machine learning", "AI Search", "Microsoft.Search/searchServices", "srch"),
    ("AI + machine learning", "Foundry Tools (multi-service account)", "Microsoft.CognitiveServices/accounts", "ais"),
    ("AI + machine learning", "Foundry account", "Microsoft.CognitiveServices/accounts", "aif"),
    ("AI + machine learning", "Foundry account project", "Microsoft.CognitiveServices/accounts/projects", "proj"),
    ("AI + machine learning", "Foundry hub", "Microsoft.MachineLearningServices/workspaces", "hub"),
    ("AI + machine learning", "Foundry hub project", "Microsoft.MachineLearningServices/workspaces", "proj"),
    ("AI + machine learning", "Azure AI Video Indexer", "Microsoft.VideoIndexer/accounts", "avi"),
    ("AI + machine learning", "Azure Machine Learning workspace", "Microsoft.MachineLearningServices/workspaces", "mlw"),
    ("AI + machine learning", "Azure OpenAI Service", "Microsoft.CognitiveServices/accounts", "oai"),
    ("AI + machine learning", "Bot service", "Microsoft.BotService/botServices", "bot"),
    ("AI + machine learning", "Computer vision", "Microsoft.CognitiveServices/accounts", "cv"),
    ("AI + machine learning", "Content moderator", "Microsoft.CognitiveServices/accounts", "cm"),
    ("AI + machine learning", "Content safety", "Microsoft.CognitiveServices/accounts", "cs"),
    ("AI + machine learning", "Custom vision (prediction)", "Microsoft.CognitiveServices/accounts", "cstv"),
    ("AI + machine learning", "Custom vision (training)", "Microsoft.CognitiveServices/accounts", "cstvt"),
    ("AI + machine learning", "Document intelligence", "Microsoft.CognitiveServices/accounts", "di"),
    ("AI + machine learning", "Face API", "Microsoft.CognitiveServices/accounts", "face"),
    ("AI + machine learning", "Health Insights", "Microsoft.CognitiveServices/accounts", "hi"),
    ("AI + machine learning", "Immersive reader", "Microsoft.CognitiveServices/accounts", "ir"),
    ("AI + machine learning", "Language service", "Microsoft.CognitiveServices/accounts", "lang"),
    ("AI + machine learning", "Speech service", "Microsoft.CognitiveServices/accounts", "spch"),
    ("AI + machine learning", "Translator", "Microsoft.CognitiveServices/accounts", "trsl"),
    ("Analytics and IoT", "Azure Analysis Services server", "Microsoft.AnalysisServices/servers", "as"),
    ("Analytics and IoT", "Azure Databricks Access Connector", "Microsoft.Databricks/workspaces/accessConnectors", "dbac"),
    ("Analytics and IoT", "Azure Databricks workspace", "Microsoft.Databricks/workspaces", "dbw"),
    ("Analytics and IoT", "Azure Data Explorer cluster", "Microsoft.Kusto/clusters", "dec"),
    ("Analytics and IoT", "Azure Data Explorer cluster database", "Microsoft.Kusto/clusters/databases", "dedb"),
    ("Analytics and IoT", "Azure Data Factory", "Microsoft.DataFactory/factories", "adf"),
    ("Analytics and IoT", "Azure Digital Twin instance", "Microsoft.DigitalTwins/digitalTwinsInstances", "dt"),
    ("Analytics and IoT", "Azure Stream Analytics", "Microsoft.StreamAnalytics/cluster", "asa"),
    ("Analytics and IoT", "Azure Synapse Analytics private link hub", "Microsoft.Synapse/privateLinkHubs", "synplh"),
    ("Analytics and IoT", "Azure Synapse Analytics SQL Dedicated Pool", "Microsoft.Synapse/workspaces/sqlPools", "syndp"),
    ("Analytics and IoT", "Azure Synapse Analytics Spark Pool", "Microsoft.Synapse/workspaces/bigDataPools", "synsp"),
    ("Analytics and IoT", "Azure Synapse Analytics workspaces", "Microsoft.Synapse/workspaces", "synw"),
    ("Analytics and IoT", "Data Lake Store account", "Microsoft.DataLakeStore/accounts", "dls"),
    ("Analytics and IoT", "Event Hubs namespace", "Microsoft.EventHub/namespaces", "evhns"),
    ("Analytics and IoT", "Event hub", "Microsoft.EventHub/namespaces/eventHubs", "evh"),
    ("Analytics and IoT", "Event Grid domain", "Microsoft.EventGrid/domains", "evgd"),
    ("Analytics and IoT", "Event Grid namespace", "Microsoft.EventGrid/namespaces", "evgns"),
    ("Analytics and IoT", "Event Grid subscriptions", "Microsoft.EventGrid/eventSubscriptions", "evgs"),
    ("Analytics and IoT", "Event Grid topic", "Microsoft.EventGrid/domains/topics", "evgt"),
    ("Analytics and IoT", "Event Grid system topic", "Microsoft.EventGrid/systemTopics", "egst"),
    ("Analytics and IoT", "Fabric Capacity", "Microsoft.Fabric/capacities", "fc"),
    ("Analytics and IoT", "HDInsight - Hadoop cluster", "Microsoft.HDInsight/clusters", "hadoop"),
    ("Analytics and IoT", "HDInsight - HBase cluster", "Microsoft.HDInsight/clusters", "hbase"),
    ("Analytics and IoT", "HDInsight - Kafka cluster", "Microsoft.HDInsight/clusters", "kafka"),
    ("Analytics and IoT", "HDInsight - Spark cluster", "Microsoft.HDInsight/clusters", "spark"),
    ("Analytics and IoT", "HDInsight - Storm cluster", "Microsoft.HDInsight/clusters", "storm"),
    ("Analytics and IoT", "HDInsight - ML Services cluster", "Microsoft.HDInsight/clusters", "mls"),
    ("Analytics and IoT", "IoT hub", "Microsoft.Devices/IotHubs", "iot"),
    ("Analytics and IoT", "Provisioning services", "Microsoft.Devices/provisioningServices", "provs"),
    ("Analytics and IoT", "Provisioning services certificate", "Microsoft.Devices/provisioningServices/certificates", "pcert"),
    ("Analytics and IoT", "Power BI Embedded", "Microsoft.PowerBIDedicated/capacities", "pbi"),
    ("Analytics and IoT", "Time Series Insights environment", "Microsoft.TimeSeriesInsights/environments", "tsi"),
    ("Compute and web", "App Service environment", "Microsoft.Web/hostingEnvironments", "ase"),
    ("Compute and web", "App Service plan", "Microsoft.Web/serverFarms", "asp"),
    ("Compute and web", "Azure Load Testing instance", "Microsoft.LoadTestService/loadTests", "lt"),
    ("Compute and web", "Availability set", "Microsoft.Compute/availabilitySets", "avail"),
    ("Compute and web", "Azure Arc enabled server", "Microsoft.HybridCompute/machines", "arcs"),
    ("Compute and web", "Azure Arc enabled Kubernetes cluster", "Microsoft.Kubernetes/connectedClusters", "arck"),
    ("Compute and web", "Azure Arc private link scope", "Microsoft.HybridCompute/privateLinkScopes", "pls"),
    ("Compute and web", "Azure Arc gateway", "Microsoft.HybridCompute/gateways", "arcgw"),
    ("Compute and web", "Batch accounts", "Microsoft.Batch/batchAccounts", "ba"),
    ("Compute and web", "Cloud service", "Microsoft.Compute/cloudServices", "cld"),
    ("Compute and web", "Communication Services", "Microsoft.Communication/communicationServices", "acs"),
    ("Compute and web", "Disk encryption set", "Microsoft.Compute/diskEncryptionSets", "des"),
    ("Compute and web", "Function app", "Microsoft.Web/sites", "func"),
    ("Compute and web", "Gallery", "Microsoft.Compute/galleries", "gal"),
    ("Compute and web", "Hosting environment", "Microsoft.Web/hostingEnvironments", "host"),
    ("Compute and web", "Image template", "Microsoft.VirtualMachineImages/imageTemplates", "it"),
    ("Compute and web", "Managed disk (OS)", "Microsoft.Compute/disks", "osdisk"),
    ("Compute and web", "Managed disk (data)", "Microsoft.Compute/disks", "disk"),
    ("Compute and web", "Notification Hubs", "Microsoft.NotificationHubs/namespaces/notificationHubs", "ntf"),
    ("Compute and web", "Notification Hubs namespace", "Microsoft.NotificationHubs/namespaces", "ntfns"),
    ("Compute and web", "Proximity placement group", "Microsoft.Compute/proximityPlacementGroups", "ppg"),
    ("Compute and web", "Restore point collection", "Microsoft.Compute/restorePointCollections", "rpc"),
    ("Compute and web", "Snapshot", "Microsoft.Compute/snapshots", "snap"),
    ("Compute and web", "Static web app", "Microsoft.Web/staticSites", "stapp"),
    ("Compute and web", "Virtual machine", "Microsoft.Compute/virtualMachines", "vm"),
    ("Compute and web", "Virtual machine scale set", "Microsoft.Compute/virtualMachineScaleSets", "vmss"),
    ("Compute and web", "Virtual machine maintenance configuration", "Microsoft.Maintenance/maintenanceConfigurations", "mc"),
    ("Compute and web", "VM storage account", "Microsoft.Storage/storageAccounts", "stvm"),
    ("Compute and web", "Web app", "Microsoft.Web/sites", "app"),
    ("Containers", "AKS cluster", "Microsoft.ContainerService/managedClusters", "aks"),
    ("Containers", "AKS system node pool", "Microsoft.ContainerService/managedClusters/agentPools", "npsystem"),
    ("Containers", "AKS user node pool", "Microsoft.ContainerService/managedClusters/agentPools", "np"),
    ("Containers", "Container apps", "Microsoft.App/containerApps", "ca"),
    ("Containers", "Container apps environment", "Microsoft.App/managedEnvironments", "cae"),
    ("Containers", "Container apps job", "Microsoft.App/jobs", "caj"),
    ("Containers", "Container registry", "Microsoft.ContainerRegistry/registries", "cr"),
    ("Containers", "Container instance", "Microsoft.ContainerInstance/containerGroups", "ci"),
    ("Containers", "Service Fabric cluster", "Microsoft.ServiceFabric/clusters", "sf"),
    ("Containers", "Service Fabric managed cluster", "Microsoft.ServiceFabric/managedClusters", "sfmc"),
    ("Databases", "Azure Cosmos DB database", "Microsoft.DocumentDB/databaseAccounts/sqlDatabases", "cosmos"),
    ("Databases", "Azure Cosmos DB for Apache Cassandra account", "Microsoft.DocumentDB/databaseAccounts", "coscas"),
    ("Databases", "Azure Cosmos DB for MongoDB account", "Microsoft.DocumentDB/databaseAccounts", "cosmon"),
    ("Databases", "Azure Cosmos DB for NoSQL account", "Microsoft.DocumentDb/databaseAccounts", "cosno"),
    ("Databases", "Azure Cosmos DB for Table account", "Microsoft.DocumentDb/databaseAccounts", "costab"),
    ("Databases", "Azure Cosmos DB for Apache Gremlin account", "Microsoft.DocumentDb/databaseAccounts", "cosgrm"),
    ("Databases", "Azure Cosmos DB PostgreSQL cluster", "Microsoft.DBforPostgreSQL/serverGroupsv2", "cospos"),
    ("Databases", "Azure Managed Redis", "Microsoft.Cache/RedisEnterprise", "amr"),
    ("Databases", "Azure SQL Database server", "Microsoft.Sql/servers", "sql"),
    ("Databases", "Azure SQL database", "Microsoft.Sql/servers/databases", "sqldb"),
    ("Databases", "Azure SQL Elastic Job agent", "Microsoft.Sql/servers/jobAgents", "sqlja"),
    ("Databases", "Azure SQL Elastic Pool", "Microsoft.Sql/servers/elasticpool", "sqlep"),
    ("Databases", "MySQL database", "Microsoft.DBforMySQL/servers", "mysql"),
    ("Databases", "PostgreSQL database", "Microsoft.DBforPostgreSQL/servers", "psql"),
    ("Databases", "SQL Managed Instance", "Microsoft.Sql/managedInstances", "sqlmi"),
    ("Developer tools", "App Configuration store", "Microsoft.AppConfiguration/configurationStores", "appcs"),
    ("Developer tools", "Maps account", "Microsoft.Maps/accounts", "map"),
    ("Developer tools", "SignalR", "Microsoft.SignalRService/SignalR", "sigr"),
    ("Developer tools", "WebPubSub", "Microsoft.SignalRService/webPubSub", "wps"),
    ("DevOps", "Azure Managed Grafana", "Microsoft.Dashboard/grafana", "amg"),
    ("DevOps", "Managed DevOps Pools", "Microsoft.DevOpsInfrastructure/pools", "mdp"),
    ("Integration", "API management service instance", "Microsoft.ApiManagement/service", "apim"),
    ("Integration", "Integration account", "Microsoft.Logic/integrationAccounts", "ia"),
    ("Integration", "Logic app", "Microsoft.Logic/workflows", "logic"),
    ("Integration", "Service Bus namespace", "Microsoft.ServiceBus/namespaces", "sbns"),
    ("Integration", "Service Bus queue", "Microsoft.ServiceBus/namespaces/queues", "sbq"),
    ("Integration", "Service Bus topic", "Microsoft.ServiceBus/namespaces/topics", "sbt"),
    ("Integration", "Service Bus topic subscription", "Microsoft.ServiceBus/namespaces/topics/subscriptions", "sbts"),
    ("Management and governance", "Automation account", "Microsoft.Automation/automationAccounts", "aa"),
    ("Management and governance", "Application Insights", "Microsoft.Insights/components", "appi"),
    ("Management and governance", "Azure Monitor action group", "Microsoft.Insights/actionGroups", "ag"),
    ("Management and governance", "Azure Monitor data collection rule", "Microsoft.Insights/dataCollectionRules", "dcr"),
    ("Management and governance", "Azure Monitor alert processing rule", "Microsoft.AlertsManagement/actionRules", "apr"),
    ("Management and governance", "Data collection endpoint", "Microsoft.Insights/dataCollectionEndpoints", "dce"),
    ("Management and governance", "Deployment scripts", "Microsoft.Resources/deploymentScripts", "script"),
    ("Management and governance", "Log Analytics workspace", "Microsoft.OperationalInsights/workspaces", "log"),
    ("Management and governance", "Log Analytics query packs", "Microsoft.OperationalInsights/querypacks", "pack"),
    ("Management and governance", "Microsoft Purview instance", "Microsoft.Purview/accounts", "pview"),
    ("Management and governance", "Resource group", "Microsoft.Resources/subscriptions/resourceGroups", "rg"),
    ("Management and governance", "Template specs name", "Microsoft.Resources/templateSpecs", "ts"),
    ("Migration", "Azure Migrate project", "Microsoft.Migrate/assessmentProjects", "migr"),
    ("Migration", "Database Migration Service instance", "Microsoft.DataMigration/services", "dms"),
    ("Migration", "Recovery Services vault", "Microsoft.RecoveryServices/vaults", "rsv"),
    ("Networking", "Application gateway", "Microsoft.Network/applicationGateways", "agw"),
    ("Networking", "Application security group (ASG)", "Microsoft.Network/applicationSecurityGroups", "asg"),
    ("Networking", "CDN profile", "Microsoft.Cdn/profiles", "cdnp"),
    ("Networking", "CDN endpoint", "Microsoft.Cdn/profiles/endpoints", "cdne"),
    ("Networking", "Connections", "Microsoft.Network/connections", "con"),
    ("Networking", "DNS forwarding ruleset", "Microsoft.Network/dnsForwardingRulesets", "dnsfrs"),
    ("Networking", "DNS private resolver", "Microsoft.Network/dnsResolvers", "dnspr"),
    ("Networking", "DNS private resolver inbound endpoint", "Microsoft.Network/dnsResolvers/inboundEndpoints", "in"),
    ("Networking", "DNS private resolver outbound endpoint", "Microsoft.Network/dnsResolvers/outboundEndpoints", "out"),
    ("Networking", "Firewall", "Microsoft.Network/azureFirewalls", "afw"),
    ("Networking", "Firewall policy", "Microsoft.Network/firewallPolicies", "afwp"),
    ("Networking", "ExpressRoute circuit", "Microsoft.Network/expressRouteCircuits", "erc"),
    ("Networking", "ExpressRoute direct", "Microsoft.Network/expressRoutePorts", "erd"),
    ("Networking", "ExpressRoute gateway", "Microsoft.Network/virtualNetworkGateways", "ergw"),
    ("Networking", "Front Door (Standard/Premium) profile", "Microsoft.Cdn/profiles", "afd"),
    ("Networking", "Front Door (Standard/Premium) endpoint", "Microsoft.Cdn/profiles/afdEndpoints", "fde"),
    ("Networking", "Front Door firewall policy", "Microsoft.Network/frontdoorWebApplicationFirewallPolicies", "fdfp"),
    ("Networking", "Front Door (classic)", "Microsoft.Network/frontDoors", "afd"),
    ("Networking", "IP group", "Microsoft.Network/ipGroups", "ipg"),
    ("Networking", "Load balancer (internal)", "Microsoft.Network/loadBalancers", "lbi"),
    ("Networking", "Load balancer (external)", "Microsoft.Network/loadBalancers", "lbe"),
    ("Networking", "Load balancer rule", "Microsoft.Network/loadBalancers/inboundNatRules", "rule"),
    ("Networking", "Local network gateway", "Microsoft.Network/localNetworkGateways", "lgw"),
    ("Networking", "NAT gateway", "Microsoft.Network/natGateways", "ng"),
    ("Networking", "Network interface (NIC)", "Microsoft.Network/networkInterfaces", "nic"),
    ("Networking", "Network security perimeter", "Microsoft.Network/networkSecurityPerimeters", "nsp"),
    ("Networking", "Network security group (NSG)", "Microsoft.Network/networkSecurityGroups", "nsg"),
    ("Networking", "Network security group (NSG) security rules", "Microsoft.Network/networkSecurityGroups/securityRules", "nsgsr"),
    ("Networking", "Network Watcher", "Microsoft.Network/networkWatchers", "nw"),
    ("Networking", "Private Link", "Microsoft.Network/privateLinkServices", "pl"),
    ("Networking", "Private endpoint", "Microsoft.Network/privateEndpoints", "pep"),
    ("Networking", "Public IP address", "Microsoft.Network/publicIPAddresses", "pip"),
    ("Networking", "Public IP address prefix", "Microsoft.Network/publicIPPrefixes", "ippre"),
    ("Networking", "Route filter", "Microsoft.Network/routeFilters", "rf"),
    ("Networking", "Route server", "Microsoft.Network/virtualHubs", "rtserv"),
    ("Networking", "Route table", "Microsoft.Network/routeTables", "rt"),
    ("Networking", "Service endpoint policy", "Microsoft.Network/serviceEndPointPolicies", "se"),
    ("Networking", "Traffic Manager profile", "Microsoft.Network/trafficManagerProfiles", "traf"),
    ("Networking", "User defined route (UDR)", "Microsoft.Network/routeTables/routes", "udr"),
    ("Networking", "Virtual network", "Microsoft.Network/virtualNetworks", "vnet"),
    ("Networking", "Virtual network gateway", "Microsoft.Network/virtualNetworkGateways", "vgw"),
    ("Networking", "Virtual network manager", "Microsoft.Network/networkManagers", "vnm"),
    ("Networking", "Virtual network peering", "Microsoft.Network/virtualNetworks/virtualNetworkPeerings", "peer"),
    ("Networking", "Virtual network subnet", "Microsoft.Network/virtualNetworks/subnets", "snet"),
    ("Networking", "Virtual WAN", "Microsoft.Network/virtualWans", "vwan"),
    ("Networking", "Virtual WAN Hub", "Microsoft.Network/virtualHubs", "vhub"),
    ("Security", "Azure Bastion", "Microsoft.Network/bastionHosts", "bas"),
    ("Security", "Key vault", "Microsoft.KeyVault/vaults", "kv"),
    ("Security", "Key Vault Managed HSM", "Microsoft.KeyVault/managedHSMs", "kvmhsm"),
    ("Security", "Managed identity", "Microsoft.ManagedIdentity/userAssignedIdentities", "id"),
    ("Security", "SSH key", "Microsoft.Compute/sshPublicKeys", "sshkey"),
    ("Security", "VPN Gateway", "Microsoft.Network/vpnGateways", "vpng"),
    ("Security", "VPN connection", "Microsoft.Network/vpnGateways/vpnConnections", "vcn"),
    ("Security", "VPN site", "Microsoft.Network/vpnGateways/vpnSites", "vst"),
    ("Security", "Web Application Firewall (WAF) policy", "Microsoft.Network/firewallPolicies", "waf"),
    ("Security", "Web Application Firewall (WAF) policy rule group", "Microsoft.Network/firewallPolicies/ruleGroups", "wafrg"),
    ("Storage", "Azure Backup Resource Guard", "Microsoft.DataProtection/resourceGuards", "rgd"),
    ("Storage", "Backup Vault name", "Microsoft.DataProtection/backupVaults", "bvault"),
    ("Storage", "Backup Vault policy", "Microsoft.DataProtection/backupVaults/backupPolicies", "bkpol"),
    ("Storage", "File share", "Microsoft.Storage/storageAccounts/fileServices/shares", "share"),
    ("Storage", "Storage account", "Microsoft.Storage/storageAccounts", "st"),
    ("Storage", "Storage Sync Service name", "Microsoft.StorageSync/storageSyncServices", "sss"),
    ("Virtual desktop infrastructure", "Virtual desktop host pool", "Microsoft.DesktopVirtualization/hostPools", "vdpool"),
    ("Virtual desktop infrastructure", "Virtual desktop application group", "Microsoft.DesktopVirtualization/applicationGroups", "vdag"),
    ("Virtual desktop infrastructure", "Virtual desktop workspace", "Microsoft.DesktopVirtualization/workspaces", "vdws"),
    ("Virtual desktop infrastructure", "Virtual desktop scaling plan", "Microsoft.DesktopVirtualization/scalingPlans", "vdscaling"),
    # module-only resources (not on the CAF page)
    ("Integration", "API connection", "Microsoft.Web/connections", "apic"),
    ("Management and governance", "Operations Management solution", "Microsoft.OperationsManagement/solutions", "oms"),
]

# ---- customer MODULE overrides: ARM type -> (abbrs, templateKind) ----
# These REPLACE the CAF abbreviations for the type (module is source of truth).
MODULE = {
    "Microsoft.Insights/actionGroups": (["ag"], "default"),
    "Microsoft.Web/connections": (["apic"], "default"),
    "Microsoft.ApiManagement/service": (["apim"], "default"),
    "Microsoft.Insights/components": (["appi"], "default"),
    "Microsoft.Web/serverFarms": (["asp"], "default"),
    "Microsoft.Automation/automationAccounts": (["aa"], "default"),
    "Microsoft.Network/azureFirewalls": (["afw"], "default"),
    "Microsoft.Network/bastionHosts": (["bas"], "default"),
    "Microsoft.App/containerApps": (["ca"], "default"),
    "Microsoft.App/managedEnvironments": (["cae"], "default"),
    "Microsoft.App/jobs": (["caj"], "default"),
    "Microsoft.ContainerRegistry/registries": (["cr"], "compact"),
    "Microsoft.Network/connections": (["vcn"], "default"),
    "Microsoft.Insights/dataCollectionRules": (["dcr"], "default"),
    "Microsoft.DataLakeStore/accounts": (["dl"], "default"),
    "Microsoft.DataFactory/factories": (["adf"], "default"),
    "Microsoft.Databricks/workspaces/accessConnectors": (["dbrcon"], "default"),
    "Microsoft.Databricks/workspaces": (["dbw"], "default"),
    "Microsoft.EventGrid/domains": (["evgd"], "default"),
    "Microsoft.EventGrid/namespaces": (["evgns"], "default"),
    "Microsoft.EventGrid/eventSubscriptions": (["evgs"], "default"),
    "Microsoft.EventGrid/systemTopics": (["egst"], "default"),
    "Microsoft.EventGrid/domains/topics": (["evgt"], "default"),
    "Microsoft.EventHub/namespaces/eventHubs": (["evh"], "default"),
    "Microsoft.EventHub/namespaces": (["evhns"], "default"),
    "Microsoft.Network/virtualNetworkGateways": (["ergw"], "default"),
    "Microsoft.Fabric/capacities": (["fc"], "compact"),
    "Microsoft.Network/firewallPolicies": (["afwp"], "default"),
    "Microsoft.CognitiveServices/accounts": (["aif"], "default"),
    "Microsoft.Web/sites": (["func", "app"], "default"),
    "Microsoft.KeyVault/vaults": (["kv"], "default"),
    "Microsoft.Network/loadBalancers": (["lbi", "lbe"], "default"),
    "Microsoft.Network/loadBalancers/inboundNatRules": (["rule"], "default"),
    "Microsoft.OperationalInsights/workspaces": (["log"], "default"),
    "Microsoft.OperationalInsights/querypacks": (["pack"], "default"),
    "Microsoft.Logic/workflows": (["logic"], "default"),
    "Microsoft.ManagedIdentity/userAssignedIdentities": (["id"], "default"),
    "Microsoft.Network/natGateways": (["ng"], "default"),
    "Microsoft.Network/networkSecurityGroups": (["nsg"], "default"),
    "Microsoft.OperationsManagement/solutions": (["oms"], "default"),
    "Microsoft.Network/dnsResolvers": (["dnspr"], "default"),
    "Microsoft.Network/dnsResolvers/inboundEndpoints": (["in"], "default"),
    "Microsoft.Network/dnsResolvers/outboundEndpoints": (["out"], "default"),
    "Microsoft.Network/privateEndpoints": (["pep"], "privateEndpoint"),
    "Microsoft.Network/publicIPAddresses": (["pip"], "default"),
    "Microsoft.RecoveryServices/vaults": (["rsv"], "default"),
    "Microsoft.Resources/subscriptions/resourceGroups": (["rg"], "default"),
    "Microsoft.Network/routeTables": (["rt"], "default"),
    "Microsoft.Network/dnsForwardingRulesets": (["dnsfr"], "default"),
    "Microsoft.ServiceBus/namespaces": (["sbns"], "default"),
    "Microsoft.ServiceBus/namespaces/queues": (["sbq"], "default"),
    "Microsoft.ServiceBus/namespaces/topics": (["sbt"], "default"),
    "Microsoft.ServiceBus/namespaces/topics/subscriptions": (["sbts"], "default"),
    "Microsoft.Compute/snapshots": (["snap"], "parentToken"),
    "Microsoft.Sql/servers/databases": (["sqldb"], "default"),
    "Microsoft.Sql/servers": (["sql"], "default"),
    "Microsoft.Storage/storageAccounts": (["st"], "compact"),
    "Microsoft.Network/virtualNetworks/subnets": (["subnet"], "subnet"),
    "Microsoft.Network/virtualNetworks": (["vnet"], "default"),
    "Microsoft.Compute/virtualMachines": (["vm"], "vmCompact"),
    "Microsoft.Compute/disks": (["osdisk", "disk"], "parentToken"),
    "Microsoft.Network/networkInterfaces": (["nic"], "parentToken"),
    "Microsoft.Network/virtualHubs": (["vhub"], "default"),
    "Microsoft.Network/vpnGateways": (["vpng"], "default"),
    "Microsoft.Network/virtualNetworks/virtualNetworkPeerings": (["peer"], "peering"),
    "Microsoft.Network/virtualWans": (["vwan"], "default"),
}

RG_TYPE = "Microsoft.Resources/subscriptions/resourceGroups"
RG_EXCLUDED = ["AzureBackupRG_*", "NetworkWatcherRG", "synapseworkspace-managedrg-*", "mrg-cisco-meraki-*"]


def norm_type(ns):
    t = re.split(r"\s*\(", ns.strip().strip("`"))[0].strip().strip("`")
    return t.replace("Microsoft.DocumentDb/", "Microsoft.DocumentDB/")


def slug(t):
    s = t[len("Microsoft."):] if t.startswith("Microsoft.") else t
    return "naming-" + re.sub(r"[^A-Za-z0-9]+", "-", s).lower().strip("-")


def friendly(resource):
    return re.sub(r"\s+name$", "", re.sub(r"\s*\(.*?\)", "", resource).strip(), flags=re.I)


def mode_for(t):
    return "All" if (t == RG_TYPE or t.count("/") >= 2) else "Indexed"


def count_none(patterns):
    return {"count": {"value": patterns, "name": "pattern",
                      "where": {"field": "name", "like": "[current('pattern')]"}}, "equals": 0}


def build_check(kind, abbrs):
    """Return (noncompliant_condition, uses_customer_param, example, check_desc)."""
    a0 = abbrs[0]
    if kind == "default":
        pats = [f"[concat(parameters('customerAbbreviation'), '-{a}-*')]" for a in abbrs]
        return (count_none(pats), True,
                f"dlw-{a0}-<service>-<env>-<loc>-<instance>",
                f"name begins with the '{{customerAbbreviation}}-{a0}-' anchor (customer + resource abbreviation)")
    if kind == "compact":
        pats = [f"[concat(parameters('customerAbbreviation'), '{a}*')]" for a in abbrs]
        return (count_none(pats), True,
                f"dlw{a0}<service><env><loc><instance>",
                f"name begins with the compact '{{customerAbbreviation}}{a0}' anchor (no hyphens)")
    if kind == "peering":
        return (count_none(["peer-*"]), False,
                "peer-<sourceVnet>-with-<destVnet>", "name begins with 'peer-'")
    if kind == "subnet":
        return (count_none(["*Subnet"]), False,
                "<subnetFunction>Subnet", "name ends with 'Subnet'")
    if kind == "parentToken":
        anyof = [{"field": "name", "contains": f"-{a}-"} for a in abbrs]
        toks = " or ".join(f"'-{a}-'" for a in abbrs)
        return ({"not": {"anyOf": anyof}}, False,
                f"<parentResourceName>-{a0}-<instance>", f"name contains the {toks} token")
    if kind == "privateEndpoint":
        return ({"not": {"field": "name", "contains": "-pep-"}}, False,
                "<attachedResourceName>-pep-<loc>-<subResource>-<instance>", "name contains the '-pep-' token")
    if kind == "vmCompact":
        return ({"field": "name", "contains": "-"}, False,
                "<service><env><loc><role><instance>",
                "name is compact (contains no hyphens). NOTE: the Windows computer-name 15-char limit applies to the computerName, not the resource name, so length is not enforced here")
    raise ValueError(kind)


def md_escape(value):
    return (value or "").replace("|", "\\|").replace("\n", " ")


def catalogue_version():
    """Reuse the producer's catalogue version when present, else today's UTC date."""
    cat = LAB / "catalogue" / "catalogue.json"
    if cat.exists():
        try:
            return json.loads(cat.read_text(encoding="utf-8")).get("catalogueVersion") or ""
        except (json.JSONDecodeError, OSError):
            pass
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).strftime("%Y.%m.%d")


def member_params(src_params):
    """Mirror the producer: bubble 'effect' to the initiative parameter; emit every
    other parameter inline with its definition default."""
    mp = {}
    for pname, pdef in src_params.items():
        if pname == "effect":
            mp["effect"] = {"value": "[parameters('effect')]"}
        elif "defaultValue" in pdef:
            mp[pname] = {"value": pdef["defaultValue"]}
    return mp


def build_policyset(members, version):
    policy_defs = []
    for m in members:
        entry = {
            "policyDefinitionReferenceId": m["ref"],
            "policyDefinitionName": m["ref"],  # custom in-repo definition -> referenced by name
            "groupNames": [INIT_TIER],
            "metadata": {"policyName": m["displayName"]},
        }
        mp = member_params(m["src_params"])
        if mp:
            entry["parameters"] = mp
        policy_defs.append(entry)
    return {
        "$schema": SCHEMA_POLICYSET,
        "name": INIT_NAME,
        "properties": {
            "displayName": INIT_DISPLAY,
            "description": INIT_RATIONALE,
            "policyType": "Custom",
            "metadata": {
                "category": "Naming convention",
                "domain": INIT_DOMAIN,
                "tier": INIT_TIER,
                "catalogueVersion": version,
                "source": SOURCE,
                "hasRemediation": False,
            },
            "policyDefinitionGroups": [{"name": INIT_TIER}],
            "parameters": {
                "effect": {
                    "type": "String",
                    "allowedValues": ["Audit", "Deny", "Disabled"],
                    "defaultValue": "Audit",
                    "metadata": {"displayName": "Effect",
                                 "description": "Effect applied to every naming-convention policy in this initiative."},
                }
            },
            "policyDefinitions": policy_defs,
        },
    }


def build_assignment(members):
    return {
        "$schema": SCHEMA_ASSIGNMENT,
        "nodeName": f"/{PREFIX}/management/essential/naming/",
        "assignment": {
            "name": INIT_NAME,
            "displayName": INIT_DISPLAY,
            "description": (
                f"Deployment scaffold for {len(members)} naming-convention policies. Effects default to "
                f"Audit via the initiative's 'effect' parameter — set it to Deny to enforce. No managed "
                f"identity is required (no Modify/DeployIfNotExists policies). Replace all mock references "
                f"(<root-mg-id>, <pac-environment-selector>, <sub-id>) before deploying."
            ),
        },
        "policySetDefinitionName": INIT_NAME,
        "parameters": {},  # 'effect' has a default; override here to deny
        "scope": {"<pac-environment-selector>": ["/providers/Microsoft.Management/managementGroups/<root-mg-id>"]},
        "notScopes": [],
    }


def build_exemptions():
    return {
        "$schema": SCHEMA_EXEMPTIONS,
        "nodeName": f"/{PREFIX}/management/essential/naming/exemptions/",
        "exemptions": [
            {
                "name": f"{INIT_NAME}-example-exemption",
                "displayName": "Example exemption — replace or remove",
                "description": "Template stub. Set the scope/assignment id and the policyDefinitionReferenceIds "
                               "(e.g. 'naming-storage-storageaccounts') for resource types that should not be governed here.",
                "exemptionCategory": "Waiver",
                "policyAssignmentId": f"/providers/Microsoft.Management/managementGroups/<root-mg-id>"
                                      f"/providers/Microsoft.Authorization/policyAssignments/{INIT_NAME}",
                "policyDefinitionReferenceIds": ["<policy-reference-id>"],
                "scope": "/subscriptions/<sub-id>",
            }
        ],
    }


_MD_HEADER = (
    "| # | Policy | Policy ID | Tag | Description | Requires Parameters | Requires Managed Identity | "
    "Allowed Values | Default Value | Soft Value | Hardened Value | Category | Domain | Version | Type | Tier |"
)
_MD_SEP = "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"


def build_markdown(members):
    product = [
        "## Product, purpose & deployment", "",
        "**Product.** Part of DLW's Azure naming governance as code — generated by "
        "`flows/definition_gen/gen_dlw_naming_definitions.py` from the dlw MSPE `getResourceName.bicep` convention. "
        "This initiative bundles the custom `naming-*` definitions into one assignable set.", "",
        "**Purpose.** Where `getResourceName.bicep` *builds* compliant names at deploy time, these "
        "policies *verify* them at the platform — catching resources created outside the module "
        "(portal, scripts, other IaC).", "",
        "> ⚠️ **Ships as `Audit`. Enforcement is a decision made at the customer.**",
        "> The initiative's top-level `effect` parameter (and every member definition) defaults to "
        "**`Audit`** — non-compliant names are reported, nothing is blocked. To enforce the convention "
        "in a customer tenant, set `effect` to **`Deny`** (or `Disabled` to switch a control off) "
        "**at assignment time in the customer environment** by overriding the `effect` parameter on the "
        "EPAC assignment. Do not bake `Deny` into the artifacts.", "",
        "**Parameter values** (safe defaults; override per assignment / per customer):", "",
        "| Parameter | Allowed values | Default | Notes |",
        "|---|---|---|---|",
        "| `effect` | `Audit`, `Deny`, `Disabled` | **`Audit`** | One top-level initiative parameter, "
        "wired to every member. Set to `Deny` at the customer to enforce. |",
        "| `customerAbbreviation` | string | `dlw` | Org prefix that anchors the name check (on the definitions). |",
        "| `excludedNamePattern` | array (wildcards) | `[]` | Carve-outs; resource groups ship with "
        "platform-managed exclusions. |", "",
        "**Deployment.** Deploy the `naming-*` definitions and this initiative together via EPAC "
        "(members are referenced by `policyDefinitionName`). Assign at a management-group scope; leave "
        "`effect` at `Audit` to observe, flip to `Deny` per customer to enforce.", "",
    ]
    lines = [f"# {INIT_DISPLAY}", "", "## Tier rationale", "", INIT_RATIONALE, "", *product, "## Usage", "",
             "These artifacts are [EPAC](https://azure.github.io/enterprise-azure-policy-as-code/) "
             "(Enterprise Azure Policy as Code) definition files — deploy them via the EPAC pipeline "
             "(`Build-DeploymentPlans` → `Deploy-PolicyPlan`) or translate them to Terraform / Bicep. "
             "The member policies are the custom `naming-*` definitions under "
             "`catalogue/definitions/custom/dlw-az-naming/` (referenced by `policyDefinitionName`), so deploy "
             "those alongside this set. Each carries a `$schema` reference for editor validation.", "",
             "| Artifact | EPAC type | What to do with it |", "|---|---|---|",
             f"| `{INIT_NAME}.policyset.json` | `policySetDefinition` (initiative) | The naming-convention set. "
             "Effect is bubbled to a single top-level `effect` parameter (default Audit). Place under your EPAC "
             "`policyDefinitions/` folder. |",
             f"| `{INIT_NAME}.assignment.json` | `policyAssignment` | Binds the initiative to a scope. Replace "
             "`<root-mg-id>`, `<pac-environment-selector>`, `<sub-id>`; set `effect` to Deny to enforce. |",
             f"| `{INIT_NAME}.exemptions.json` | `policyExemption` | One `Waiver` stub. Set the scope and "
             "`policyDefinitionReferenceIds` for resource types that do not apply, or remove the file. |",
             f"| `{INIT_NAME}.roles.json` | role assignments (lab helper) | Not present for this group (no "
             "Modify/DeployIfNotExists policy). |", "",
             "**Deployment order:** deploy the `naming-*` definitions → assign the initiative.", "",
             "## Policies", "", _MD_HEADER, _MD_SEP]
    for i, m in enumerate(sorted(members, key=lambda x: x["displayName"].lower()), start=1):
        lines.append(
            f"| {i} | {md_escape(m['displayName'])} | {m['ref']} |  | {md_escape(m['description'])} | "
            f"No | No | Audit, Deny, Disabled | Audit | Audit | Audit | "
            f"Naming convention | {INIT_DOMAIN} | {m['version']} | Custom | {INIT_TIER} |"
        )
    return "\n".join(lines) + "\n"


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    types = OrderedDict()
    for category, resource, ns, abbr in ROWS:
        t = norm_type(ns)
        e = types.setdefault(t, {"abbrs": [], "category": category, "resources": []})
        if abbr not in e["abbrs"]:
            e["abbrs"].append(abbr)
        e["resources"].append(resource)

    for f in glob.glob(str(OUT / "naming-*.json")):
        os.remove(f)

    written = 0
    members = []
    for t, e in types.items():
        if t in MODULE:
            abbrs, kind = MODULE[t]
            abbr_source = "module (getResourceName.bicep)"
        else:
            abbrs, kind = sorted(e["abbrs"]), "default"
            abbr_source = "CAF abbreviation page"
        cond, uses_cust, example, check_desc = build_check(kind, abbrs)
        prim = friendly(e["resources"][0])
        name = slug(t)

        params = {}
        if uses_cust:
            params["customerAbbreviation"] = {
                "type": "String", "defaultValue": CUST_DEFAULT,
                "metadata": {"displayName": "Customer abbreviation",
                             "description": "Organization/customer abbreviation that prefixes the name (e.g. 'dlw')."},
            }
        params["excludedNamePattern"] = {
            "type": "Array", "defaultValue": RG_EXCLUDED if t == RG_TYPE else [],
            "metadata": {"displayName": "Excluded name patterns",
                         "description": "Names matching any of these wildcard patterns are exempt. Example: 'rg-*, NetworkWatcherRG'."},
        }
        params["effect"] = {
            "type": "String", "allowedValues": ["Audit", "Deny", "Disabled"], "defaultValue": "Audit",
            "metadata": {"displayName": "Effect", "description": "The effect of the policy (Audit, Deny or Disabled)."},
        }

        desc = (f"Audits or denies {prim} ({t}) that do not follow the organisation's naming "
                f"convention from getResourceName.bicep. Accepted abbreviation(s): {', '.join(abbrs)}. "
                f"Example: '{example}'. Check: {check_desc}. "
                f"Note: Azure Policy 'like' allows a single wildcard, so only the deterministic anchor is "
                f"validated, not every segment.")
        if len(desc) > 512:                      # Azure description hard limit
            desc = desc[:511].rstrip() + "…"

        d = {
            "$schema": SCHEMA_DEF,
            "name": name,
            "properties": {
                "displayName": f"Require naming convention for {prim}",
                "description": desc,
                "policyType": "Custom",
                "mode": mode_for(t),
                "metadata": {
                    "category": "Naming convention",
                    "version": "2.0.0",
                    "source": SOURCE,
                    "cafCategory": e["category"],
                    "resourceType": t,
                    "abbreviations": abbrs,
                    "abbreviationSource": abbr_source,
                    "checkKind": kind,
                    "conventionExample": example,
                },
                "parameters": params,
                "policyRule": {
                    "if": {"allOf": [
                        {"field": "type", "equals": t},
                        {"count": {"value": "[parameters('excludedNamePattern')]", "name": "excluded",
                                   "where": {"field": "name", "like": "[current('excluded')]"}}, "equals": 0},
                        cond,
                    ]},
                    "then": {"effect": "[parameters('effect')]"},
                },
            },
        }
        (OUT / f"{name}.json").write_text(json.dumps(d, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        written += 1
        members.append({"ref": name, "displayName": d["properties"]["displayName"],
                        "description": desc, "version": "2.0.0", "src_params": params})

    # ---- 'naming' initiative: same artifact set as the built-in producer ----
    version = catalogue_version()
    INIT_DIR.mkdir(parents=True, exist_ok=True)
    (INIT_DIR / f"{INIT_NAME}.policyset.json").write_text(
        json.dumps(build_policyset(members, version), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (INIT_DIR / f"{INIT_NAME}.assignment.json").write_text(
        json.dumps(build_assignment(members), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (INIT_DIR / f"{INIT_NAME}.exemptions.json").write_text(
        json.dumps(build_exemptions(), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (INIT_DIR / f"{INIT_NAME}.md").write_text(build_markdown(members), encoding="utf-8")

    module_types = sum(1 for t in types if t in MODULE)
    print(f"types: {len(types)} | files: {written} | module-aligned: {module_types} | caf-default: {len(types)-module_types}")
    kinds = {}
    for t in types:
        k = MODULE[t][1] if t in MODULE else "default"
        kinds[k] = kinds.get(k, 0) + 1
    print("by checkKind:", kinds)
    print(f"initiative: {INIT_NAME} ({len(members)} members, catalogueVersion {version}) -> {INIT_DIR}")


if __name__ == "__main__":
    main()
