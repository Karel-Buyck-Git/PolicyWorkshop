using 'main.bicep'

param namePrefix      = 'polcytax'
param location        = 'westeurope'
param ownerObjectId   = '<your-aad-object-id>'

param tags = {
  workload: 'policy-taxonomy'
  environment: 'dev'
  owner: 'karelbuyck@outlook.com'
}
