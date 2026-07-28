# Identity checklist — what to create, in what order

**This is the first step that writes to the tenant.** Everything in
[`tenant-intake.md`](tenant-intake.md) is read-only; from here on you are changing Entra
and Azure RBAC, so have the change approval in hand.

## Don't duplicate — this is the running order

The authoritative reference is the guide **shipped inside every json package**, and it
stays authoritative because the customer receives it:

- **`engine/epac_builder/azure_requirements.md` §4–§5** — the three app registrations and
  the exact least-privilege Azure roles (Reader / Resource Policy Contributor / Role Based
  Access Control Administrator), plus what *you* need to create them.
- **`engine/epac_builder/github_setup.md` §4** — the federated-credential subjects, which
  are what make this secretless.

This page is the **order of operations and the traps**, not a second copy of those tables.
If the two ever disagree, the shipped guides win — they are what the customer holds.

## Order

1. **Confirm you can register applications in Entra.** The *Application Developer* role, or
   an Entra admin who will do it. If neither, stop here — steps 2–4 are blocked and it is
   better to find that out now than halfway through.
2. **Create the three app registrations** (plan / policy / roles). Three, not one: the roles
   identity holds RBAC-granting power and must stay isolated from the one that writes
   policy. A dev-only setup may collapse policy+roles, but then say so out loud — it is a
   deliberate reduction, not a simplification.
3. **Add a federated credential to each**, per `github_setup.md §4`. **No client secrets.**
   If you find yourself creating a secret, the OIDC subject is wrong — fix the subject
   rather than falling back to a secret you will have to rotate and store.
4. **Assign the Azure roles at (or above) `deploymentRootScope`** so they cover every child
   scope. Requires *Owner* or *User Access Administrator* at that MG.
5. **Record the three client ids** into §5 of the intake sheet.

## Traps

- **The federated-credential subject must match exactly** how the workflow runs —
  `repo:<org>/<repo>:environment:<name>` for an environment-gated job is *not*
  `repo:<org>/<repo>:ref:refs/heads/main`. A mismatch fails at login with a generic
  "no matching federated identity record", which reads like a permissions problem and is
  not.
- **Assign roles at the MG, not at a subscription.** Subscription-scoped assignments leave
  the plan blind above them, and the failure looks like missing policy rather than missing
  permission.
- **Reader really is enough for plan.** If plan appears to need more, something is running
  a deploy step, not a plan step.
- **The roles identity is the dangerous one.** Consider an RBAC condition preventing it
  from granting `Owner` / `User Access Administrator`.
- **User-assigned remediation identities** additionally need *Managed Identity Operator*
  where those identities live.

## Before running the workflow

- [ ] Three app registrations exist; each has a federated credential and **no secret**
- [ ] Roles assigned at or above `deploymentRootScope`, verified with
      `az role assignment list --scope <root-mg-scope> -o table`
- [ ] Repository secrets set: `AZURE_TENANT_ID`, `AZURE_SUBSCRIPTION_ID`, `PLAN_CLIENT_ID`
      (plus `POLICY_CLIENT_ID` / `ROLES_CLIENT_ID` before any deploy)
- [ ] The first run is **plan only**. Read the plan before anything is allowed to deploy.
