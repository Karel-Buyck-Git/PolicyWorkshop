# Definition generators — the catalogue overlay registry

> **Authored allowlist** read by `flows/definition_gen/apply_overlays.py`. Only the generators
> listed here with **Enabled = yes** are run and registered into the catalogue (built-in + custom).
> This is the single place that decides *which* custom-definition generators contribute — the
> producer reads this index, not a hard-coded Python list.
>
> **To add a generator:** write `flows/definition_gen/<module>.py` (a `build()` returning an
> `Overlay`) + its `<module>.md`, then add a row here and set Enabled = yes.
> **To disable one:** set Enabled = no (the module stays in the repo but is skipped).
>
> The **Module** column is the Python module name under `flows/definition_gen/` (the file stem,
> no `.py`). Family / Placement are informational. Order is the order generators are applied;
> `Enrich` generators must come after the built-in groups they target already exist (they always
> do — `apply_overlays` runs after `create_initiatives`).

| Module | Family | Placement | Enabled |
|---|---|---|---|
| gen_dlw_naming_definitions | dlw-az-naming | NewGroup · management-esn-naming | yes |
| gen_dlw_tagging_definitions | dlw-az-tagging | NewGroup · management-esn-tagging | yes |
| gen_dlw_az_apim_definitions | dlw-az-apim | Enrich · integration-esn-apim | yes |
