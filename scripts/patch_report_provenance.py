from pathlib import Path


path = Path("src/report_builder.py")
text = path.read_text()

# 1. Add provenance import.
import_line = "from src.evidence_provenance import get_evidence_provenance_table\n"
anchor_import = "from src.therapeutic_relevance import get_therapeutic_relevance_summary\n"

if import_line not in text:
    if anchor_import not in text:
        raise SystemExit("Could not find therapeutic relevance import anchor.")
    text = text.replace(anchor_import, anchor_import + import_line)


# 2. Add provenance table builder after available/missing layer text.
anchor = '''    available_layers_text = ", ".join(coverage_result.get("available_layers", [])) or "None"
    missing_layers_text = ", ".join(coverage_result.get("missing_layers", [])) or "None"

    depmap_note = depmap_result.get("note") or depmap_result.get("dependency_note") or ""
'''

insert = '''    available_layers_text = ", ".join(coverage_result.get("available_layers", [])) or "None"
    missing_layers_text = ", ".join(coverage_result.get("missing_layers", [])) or "None"

    def _md_cell(value):
        value = _safe(value)
        return str(value).replace("|", "/").replace("\\n", " ")

    try:
        provenance_df = get_evidence_provenance_table()
        provenance_rows = [
            "| Evidence layer | Source | Data type | Main limitation |",
            "|---|---|---|---|",
        ]

        for _, provenance_row in provenance_df.iterrows():
            provenance_rows.append(
                "| "
                + _md_cell(provenance_row.get("evidence_layer"))
                + " | "
                + _md_cell(provenance_row.get("source"))
                + " | "
                + _md_cell(provenance_row.get("data_type"))
                + " | "
                + _md_cell(provenance_row.get("main_limitation"))
                + " |"
            )

        provenance_table = "\\n".join(provenance_rows)
    except Exception:
        provenance_table = "Evidence provenance table unavailable for this report."

    depmap_note = depmap_result.get("note") or depmap_result.get("dependency_note") or ""
'''

if "provenance_table =" not in text:
    if anchor not in text:
        raise SystemExit("Could not find available/missing layers anchor.")
    text = text.replace(anchor, insert)


# 3. Insert provenance section before Limitations.
anchor_section = '''---

## Limitations

{_bullet_list(report_limitations)}
'''

insert_section = '''---

## Evidence Source / Provenance

{provenance_table}

**Provenance interpretation note:** Each layer answers a different biological question. Dependency, alteration, expression, survival, role, pathway, and therapeutic context should not be collapsed into a single claim without careful interpretation.

---

## Limitations

{_bullet_list(report_limitations)}
'''

if "## Evidence Source / Provenance" not in text:
    if anchor_section not in text:
        raise SystemExit("Could not find Limitations section anchor.")
    text = text.replace(anchor_section, insert_section, 1)


path.write_text(text)

print("Added evidence provenance table to Markdown reports.")