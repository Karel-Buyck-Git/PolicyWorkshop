Here's what exists in the actual policy definitions repo:

policyType field values:

Type Count Meaning
BuiltIn 3,345 Standard Microsoft-authored policies
Static 1,664 Read-only compliance data used by Regulatory Compliance initiatives (e.g. NIST, CIS benchmarks) — not enforceable directly
DisplayName prefix tags:

Tag Count Meaning
[Deprecated] 554 Being phased out; replaced by newer policies
[Preview] 222 Not yet GA; behavior or naming may change
[Mission] 2 Mission-specific (Azure Government/sovereign cloud)
[Image Integrity] 2 Feature-scoped preview label
The script already filters out [Deprecated]. You may want to decide whether to also filter or flag [Preview] policies — they're included in the current output but could be separated into their own tier or marked in the table.
