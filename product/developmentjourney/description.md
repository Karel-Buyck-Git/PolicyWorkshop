# The EPAC Builder — where this started, and where it's going

## Why this exists

As a Microsoft partner delivering managed services, we were strong across much of Azure — but
**Azure Policy was not one of those areas.** We covered it lightly and inconsistently, and we fell
short in exactly the places that were turning from "good practice" into hard requirements: security
baselines, cost control, operational governance, and regulatory compliance.

Then the ground shifted. **NIS2** moved governance from a nice-to-have to a legal obligation, and
customers increasingly expect their Azure estate to be *provably* under control — for cost, for
security, for regulatory posture. Azure Policy is the mechanism that enforces all of that at scale.
We needed a way to **mass-deploy and configure Azure Policy** as a standard part of what we deliver,
not a bespoke, project-by-project afterthought.

The harder problem was internal. We have **hundreds of engineers working in Azure, each with their
own way** of building and configuring infrastructure. That variety is fine for one-off projects and
fatal for managed services: if every team implements policy differently, we can't operate, audit, or
guarantee any of it consistently.

**The EPAC Builder is our answer: one generalized, repeatable way to produce and deploy Azure Policy,
so every team does it the same way and our managed services are aligned across the board.** A
customer's requirements go in; a deployable, standardized EPAC package comes out — the same shape,
every time, whoever builds it.

## How the approach evolved

The project didn't start where it is now.

**It began as an agentic experiment.** The first sketch — the original version of this very document —
imagined a language model in the loop: Python would fetch Azure's built-in policies, and an LLM would
reason over them at run time, sorting each into our tiers and rendering a Markdown "pitch" table. The
things we worried about were context limits, chunking, and state.

**Then the premise changed.** We found the classification work didn't need a model at run time at all
— it could be expressed as **deterministic rules**. That single realization reshaped everything: the
engine became plain, dependency-free Python that produces identical output every time, with no model,
no API cost, and nothing to babysit. (The earlier LLM-first designs are preserved under `archive/` as
history.) The LLM's real job turned out to be **helping us build the engine**, not running inside it.

**The system then split into two halves that mirror how we actually work:**

- A **producer** turns Microsoft's official built-in policies into a shared, versioned **catalogue** —
  curated once, tiered into **Essential / Professional / Enterprise**, and reused everywhere.
- A **consumer** — the builder proper — takes a customer's manifest plus that shared catalogue and
  renders a **deployable EPAC package**: today in three flavours (native EPAC/JSON, Terraform, Bicep),
  complete with CI/CD pipelines, a package validator, and setup guides shipped inside the package.

What began as "generate a table" now produces **the whole deployable thing** — standardized,
validated, and the same for every team.

## Where it's going

The direction is consistent: make the standardized path the *easy* path, and take the engineer's
local working tree out of the critical line.

- **Self-service, no clone required.** Today a package is built by an engineer driving the tooling.
  Next is a **front end** where an engineer — and eventually a customer — fills in the inputs and gets
  a package out, without ever touching this repo.
- **A read-only catalogue service** so anyone (sales, other internal tools, a future UI) can look up
  what a tier covers, without access to the engine.
- **Hands-off catalogue currency.** Microsoft ships policy changes constantly; a **scheduled cloud
  job** will keep our catalogue current on its own and flag what changed, so every customer stays on a
  fresh baseline.
- **Proven deployability, not just proven determinism.** We've shown a package rebuilds identically
  every time; the next bar is proving it **deploys cleanly into a real tenant**, end to end, through
  the pipeline we generate.
- **Compliance evidence.** Because governance is the whole point, a generated package should be able
  to **show its coverage against public benchmarks** — CIS, ISO 27001, the Microsoft Cloud Security
  Benchmark, NIS2 — so we reassure a customer with a report, not a promise.
- **A durable versioning story** so any package can name exactly which builder and which catalogue
  produced it — the last thing to settle before this leaves alpha.

The thread through all of it is the reason we started: **one aligned, standardized way to deliver
Azure Policy across every team and every customer we manage.**

---

*This is the high-level story. The tracked, itemised work behind "where it's going" lives in
[`actions/backlog.md`](../../actions/backlog.md).*
