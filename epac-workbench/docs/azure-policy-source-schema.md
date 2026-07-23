# Upstream Azure Policy source — schema notes

Maintainer reference (plane-2) for the fields in Microsoft's built-in policy definitions that the
producer's extraction step depends on. The upstream source is pinned in
[`config/policy-source.json`](../config/policy-source.json); the authoritative filtering/normalisation
logic lives in [`engine/catalogue_builder/extract_policies.py`](../engine/catalogue_builder/extract_policies.py)
— this doc explains the *why*, the code is the *what*. Counts drift with every upstream sync, so none
are pinned here; run the extractor for a current tally.

## `policyType`

Each built-in definition carries a `properties.policyType`. Two values matter:

| Value | Meaning | How the engine treats it |
|---|---|---|
| `BuiltIn` | Standard Microsoft-authored, **enforceable** policy | Extracted; `policyType` retained per record ([extract_policies.py](../engine/catalogue_builder/extract_policies.py)) |
| `Static` | **Read-only** compliance data backing Regulatory Compliance initiatives (NIST, CIS, ISO-style benchmarks) — **not enforceable on its own** | Present in the source; not a directly assignable control. Relevant to the compliance-benchmark work (backlog **#40**) |

Custom definitions the producer generates itself are stamped `policyType: "Custom"`.

## `displayName` bracket tags

Microsoft prefixes some display names with a bracketed lifecycle/scope tag, e.g. `[Preview]: <name>`.
The extractor recognises any `[Tag]:` prefix generically (`_TAG_RE`), strips it from the stored
`name`, and **retains it as a `tag` field** — so downstream consumers can flag or group on it rather
than lose it. Tags seen in the source include:

| Tag | Meaning | Handling |
|---|---|---|
| `[Deprecated]` | Being phased out; superseded by newer policies | **Filtered out** — the record is dropped at extraction ([extract_policies.py](../engine/catalogue_builder/extract_policies.py), the `startswith("[Deprecated]")` guard) |
| `[Preview]` | Not yet GA; naming/behaviour may still change | **Flagged, not filtered** — kept with its `tag` so it's visible in the catalogue rather than silently included |
| `[Mission]` | Mission-specific (Azure Government / sovereign cloud) | Flagged via `tag` |
| `[Image Integrity]` | Feature-scoped preview label | Flagged via `tag` |

**Resolved design decision:** the original open question was whether to also *filter* `[Preview]`
alongside `[Deprecated]`. The engine's answer is to **flag, not filter** — a preview policy stays in
the catalogue carrying its `tag`, so the choice to include or exclude it is visible and deferred to the
consumer, whereas a deprecated policy is removed outright because it's on its way out.

---

*History: this reference was salvaged from an early (May 2026) reconnaissance note formerly at
`product/descriptions/policySchema/`; the point-in-time counts it carried were dropped as stale.*
