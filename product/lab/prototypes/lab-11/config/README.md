# `config/` — authored inputs

This folder holds the **human-authored** sources that drive the producer pipeline
in [`../flows/`](../flows/). They are edited by hand; the pipeline reads them and
generates the catalogue. Each source has exactly one parser, so there is no
second copy to drift (see each file's note in [`../flows/README.md`](../flows/README.md)).

| File | What it defines | Parser |
|---|---|---|
| [`azure-domain-hierachy.md`](azure-domain-hierachy.md) | Domain → resource-category taxonomy | [`../flows/shared/hierarchy.py`](../flows/shared/hierarchy.py) |
| [`tier-rules.yaml`](tier-rules.yaml) | Essential / Professional / Enterprise classification | [`../flows/shared/tiers.py`](../flows/shared/tiers.py) |

The rest of this document explains the **tier-rules design** — the priority order
and the override model — because both have non-obvious effects.

---

## How a policy gets a tier

A policy's `name + description` text is scanned, case-insensitively, against the
keyword lists in `tier-rules.yaml`. Two things decide the outcome:

1. **Overrides** are checked first (see below).
2. Otherwise the **keyword scan** runs, trying tiers in a fixed priority order.

If nothing matches, the policy defaults to **Essential**.

### Why the priority is Enterprise → Professional → Essential

The keyword scan tries tiers **most-specific-first**, and that order is not
interchangeable — reversing it would break classification.

The reason is keyword breadth. Essential keywords are **common** (they appear in
a large share of all policies); Enterprise keywords are **rare and specific**.
From the current built-in catalogue:

| Keyword | Tier | Policies it appears in |
|---|---|---|
| `https` | Essential | ~605 |
| `encrypt*` | Essential | ~115 |
| `customer-managed key*` | Enterprise | ~36 |
| `availability zone*` | Enterprise | ~5 |

Most policies match **several** tiers at once. A typical Enterprise policy
("Configure X with **customer-managed keys**, encrypted at rest, over **https**")
hits Enterprise *and* Essential keywords. The classifier must pick one tier, so
it picks the **most demanding control present** — the CMK is what makes it
Enterprise-grade, even though it is also "encryption".

This mirrors the commercial model where the tiers are cumulative
(Enterprise ⊃ Professional ⊃ Essential): check the narrowest, highest tier first
and fall through to the broad baseline last. If the order were reversed, the
common baseline words (`https`, `encrypt`, `key`) would **capture almost every
policy as Essential** before the specific Enterprise/Professional signals were
ever examined — nothing would ever reach Enterprise.

> Changing keyword **membership** (moving a keyword between the tier lists) is
> safe and expected. Changing the **priority order** itself is a code change in
> `tiers.py` (`TIER_PRIORITY`) and would re-tier large parts of the catalogue.

---

## Overrides

Overrides force a tier *before* the keyword scan, for cases the per-keyword rules
cannot judge fairly. They are declared **per-tier** under `overrides:` in
`tier-rules.yaml`, so you can target any tier — not only Enterprise. The shape
(any tier may appear under either kind):

```yaml
overrides:
  name_only:           # force a tier from the policy NAME
    professional:
      - some name keyword*
  category_only:       # force a tier for whole resource categories
    enterprise:
      - regulatory-compliance
```

| Override | Effect |
|---|---|
| `name_only[tier]` | If the policy **name** matches one of the keywords, force `tier`. The **description is ignored**. |
| `category_only[tier]` | Every policy in the listed **resource categories** is forced to `tier`, regardless of its text. |

### Current overrides

- **`category_only.enterprise: [regulatory-compliance]`** — every row in the
  *Regulatory Compliance* category is an attestation control with a terse,
  near-identical description, so per-keyword rules can't separate them; the
  category as a whole is Enterprise. *(This is the only active override.)*
- **`name_only`** has no entries right now. It is the right tool when a tier is
  decided by the policy **name** alone. For example, private-connectivity
  policies were once pinned to Enterprise this way — a policy named "… should use
  a private endpoint / private link" was forced to Enterprise while a policy named
  "… should disable public network access" stayed Professional (matching the name
  only avoids the description's private-endpoint mention promoting it). That rule
  has since been removed: private connectivity is now classified by keyword in the
  **Professional** tier instead.

### Precedence rule

When **more than one override matches** a policy, the **highest tier wins** —
the same `Enterprise > Professional > Essential` order used by the keyword scan —
regardless of whether it matched by name or by category.

Worked example: suppose you add `name_only.professional: [guest account*]` and a
policy is named *"Guest accounts in a regulatory-compliance resource …"* whose
category is also in `category_only.enterprise`. It matches a **Professional**
name-override and an **Enterprise** category-override. The result is
**Enterprise**, because Enterprise outranks Professional. Name-vs-category does
not matter; only the tier rank does.

This rule keeps overrides predictable as you add them: an override can only ever
*raise* a policy toward the tier you target, and the strongest (highest) signal
present is the one that takes effect.

---

## Editing & applying

- Edit `tier-rules.yaml` by hand (keyword conventions are documented at the top
  of that file: whole-word match, space vs. hyphen, trailing `*` stem, `...` gap).
- Re-run the pipeline to apply: `python flows/catalogue_builder/enrich_policies.py` re-classifies
  every `policies.md`. The file's SHA is recorded in `catalogue.json` as
  `tierRulesHash`, so a rules change is visible in catalogue provenance and in
  [`../flows/tools/catalogue_diff.py`](../flows/tools/catalogue_diff.py).
