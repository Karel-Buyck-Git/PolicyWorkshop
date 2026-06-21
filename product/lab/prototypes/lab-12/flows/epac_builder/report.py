"""Lineage + coverage report for an assembled scaffold.

``lineage.json`` is the machine-readable provenance (manifest hash, catalogue
version, group→file→policy map); ``report.md`` is the human coverage summary
(groups selected, parameters bound, exemptions, warnings). Both live at the output
root, beside the per-flavour folders.
"""
from pathlib import Path

from epac_builder.writeutil import write_json, write_text


def write_reports(ir, out_root, flavours):
    root = Path(out_root)
    lineage = {
        "customer": ir["identity"]["customer"],
        "pacOwnerId": ir["identity"]["pacOwnerId"],
        "manifestHash": ir["lineage"]["manifestHash"],
        "catalogueVersion": ir["lineage"]["catalogueVersion"],
        "flavours": list(flavours),
        "groups": ir["lineage"]["groups"],
    }
    write_json(root / "lineage.json", lineage)
    write_text(root / "report.md", _report_md(ir, flavours))


def _report_md(ir, flavours):
    n_params = sum(len(a["boundParameters"]) for a in ir["assignments"])
    n_remediation = sum(1 for i in ir["initiatives"] if i["hasRemediation"])
    lines = [
        f"# Assembly report — {ir['identity']['customer']}",
        "",
        f"- Catalogue version: `{ir['catalogueVersion']}`",
        f"- Manifest hash: `{ir['lineage']['manifestHash']}`",
        f"- Flavours: {', '.join(flavours)}",
        f"- Initiatives: {len(ir['initiatives'])} ({n_remediation} remediating)",
        f"- Parameters bound: {n_params}",
        f"- Exemptions: {len(ir['exemptions'])}",
        f"- Role assignments: {len(ir['roleAssignments'])}",
        "",
        "## Groups",
        "",
        "| Group | Initiative | Policies | Remediation |",
        "| --- | --- | --- | --- |",
    ]
    for g in ir["lineage"]["groups"]:
        lines.append(f"| {g['group']} | {g['name']} | {g['policyCount']} | "
                     f"{'yes' if g['hasRemediation'] else 'no'} |")
    if ir["warnings"]:
        lines += ["", "## Warnings", ""]
        lines += [f"- {w}" for w in ir["warnings"]]
    lines.append("")
    return "\n".join(lines)
