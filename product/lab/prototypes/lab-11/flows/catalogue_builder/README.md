# `catalogue_builder/` — the producer pipeline

This package is the **producer** half of lab-11: it turns Microsoft's official built-in policy
definitions into the versioned, shared **catalogue** that the consumer
([`../epac_builder/`](../epac_builder/)) assembles per customer. It runs *occasionally* — only
when the built-ins or the taxonomy change — and is the **only** flow that derives taxonomy
(domain, tier) and stamps the catalogue version.

Run the five steps in order from the `flows/` root; each is idempotent and defaults to this lab
(via [`../shared/paths.py`](../shared/paths.py)), so no flags are needed for a normal run:

```
python flows/catalogue_builder/extract_policies.py
python flows/catalogue_builder/enrich_policies.py
python flows/catalogue_builder/create_initiatives.py
python flows/definition_gen/apply_overlays.py        # custom overlays + register (see definition_gen/)
python flows/catalogue_builder/quality_control.py
```

> The fourth command is the **custom-overlay step** ([`../definition_gen/`](../definition_gen/)):
> it runs the custom-definition generators and registers their output into `index.json` /
> `catalogue.json` *between* create-initiatives and quality-control, so the catalogue contains both
> built-in and custom assets when QC validates it.

## At a glance

| File | Step | Reads | Writes |
| --- | --- | --- | --- |
| [`extract_policies.py`](extract_policies.py) | ① extract | official built-in policy JSON; the hierarchy | one `policies.md` table per category under `catalogue/definitions/` |
| [`enrich_policies.py`](enrich_policies.py) | ② enrich | every `policies.md`; `tier-rules.yaml` | the same files, re-tiered + rationale added |
| [`create_initiatives.py`](create_initiatives.py) | ③ create-initiatives | enriched `policies.md`; the policy repo (params/roles); the abbreviation map | `initiatives/**` artifacts + `index.json` + `catalogue.json` |
| [`../definition_gen/apply_overlays.py`](../definition_gen/apply_overlays.py) | ④ apply-overlays | enabled generators (`config/definition-gens.md`) | custom groups/members + the authoritative `catalogue.json` stamp |
| [`quality_control.py`](quality_control.py) | ⑤ quality-control | the freshly built catalogue | validation report + regenerated naming docs |

## The five steps

### ① [`extract_policies.py`](extract_policies.py)
**Reads** the official built-in policy JSON (`--source`, default the shared *Official Azure Policy*
repo) and **writes** one `policies.md` table per Azure resource category to
`catalogue/definitions/<category>/`. It extracts the key fields (display name, GUID, effect
allowed/soft/hardened, version), drops `[Deprecated]` policies, **deduplicates** by Policy ID
keeping the highest version, looks up each category's **Domain** from the authored hierarchy (via
[`../shared/hierarchy.py`](../shared/hierarchy.py); no match → `undefined`), and assigns a
first-pass **Tier** via [`../shared/tiers.py`](../shared/tiers.py). `--jsonl` emits a flat
extraction instead (no tier, for agent consumption).

### ② [`enrich_policies.py`](enrich_policies.py)
**Re-reads** every `policies.md`, re-applies the authoritative **Tier** from
[`../../config/tier-rules.yaml`](../../config/tier-rules.yaml) (parsed by `shared/tiers.py`, hashed
into `catalogue.json` as `tierRulesHash`), adds a per-resource **`## Tier rationale`** section with
compliance-framework references (NIS2 / ISO 27001 / CIS / NIST), and rewrites the file. Edit the
YAML to change the tiering — no code change. Idempotent: same input ⇒ same output.

### ③ [`create_initiatives.py`](create_initiatives.py)
**Reads** all enriched `policies.md`, joins each policy (on Policy ID) against a parameter index
built from the policy repo, **groups** rows by `(Domain, Tier, Category)` — tiers are *exclusive*
here — and writes up to five EPAC-ready artifacts per group under
`catalogue/initiatives/<domain>/<tier>/<category>/`:

| Artifact | Contents |
| --- | --- |
| `.md` | tier rationale + a `## Usage` deployment guide + the full policy table |
| `.policyset.json` | EPAC `policySetDefinition`; hardened effects baked, required params bubbled up |
| `.assignment.json` | EPAC assignment scaffold with mock tenant references |
| `.exemptions.json` | EPAC exemptions template stub |
| `.roles.json` | *only* for Modify/DeployIfNotExists groups: deduped remediation `roleDefinitionIds` |

All technical names are **brand-neutral and within the Azure hard limits**, built by
[`../shared/naming.py`](../shared/naming.py) from the authored
[`../../config/azure-category-abbreviation.md`](../../config/azure-category-abbreviation.md):
`<domain>-<tier>-<abbr>` (assignment ≤24) with a readable `<Domain> <Tier> — <Category>`
displayName. Finally it writes the two catalogue manifests — **`index.json`** (groups + `domainMap`
+ tiers) and **`catalogue.json`** (the version stamp: `catalogueVersion`, `inputs`, `counts`,
`tools`, `contentHash`) — which, with `initiatives/` + `definitions/`, are the **catalogue
contract** the consumer depends on. At this point `catalogue.json.contentHash` is **`sha256:pending`**
— the catalogue isn't finalized until Phase ④ (apply-overlays) stamps the authoritative hash.

### ④ apply-overlays — [`../definition_gen/apply_overlays.py`](../definition_gen/apply_overlays.py)
The **custom-overlay** step (owned by [`../definition_gen/`](../definition_gen/), run here as a
producer phase): runs the generators enabled in `config/definition-gens.md`, registers their custom
groups/members into `index.json`, and writes the **authoritative** `catalogue.json` stamp (the real
`contentHash` over built-in + custom). Built-in-only? Disable every generator in the registry.

### ⑤ [`quality_control.py`](quality_control.py)
**Reads** the freshly built catalogue, runs a **validation pass**, and regenerates documentation
from live data — the repeatable QC gate at the end of every run. It validates: missing
`displayName`, duplicate technical names, empty initiatives, orphan assignments, members without a
`metadata.policyName`, **and every Azure hard limit** (assignment name ≤24, definition/set/exemption
≤64, displayName ≤128, description ≤512 — see
[`../../docs/epac-arm-hard-limits.md`](../../docs/epac-arm-hard-limits.md)) plus a brand-neutral
guard. It **exits non-zero on any `error`-level finding**. It writes `catalogue/naming-samples.md`,
`docs/epac-naming-convention.md`, and the machine-readable `catalogue/quality-control.json`;
`--check-only` validates without rewriting. Deterministic apart from `generatedAt`.

## Boundaries

This package only *produces* the catalogue. It never deploys, calls Azure, or assembles a customer
scaffold — that is the consumer ([`../epac_builder/`](../epac_builder/)). The custom `dlw-az-naming`
definitions are authored by a **separate** flow ([`../definition_gen/`](../definition_gen/)) and
overlaid into the catalogue; they are not produced here. Shared helpers live in
[`../shared/`](../shared/); the authored inputs in [`../../config/`](../../config/).
