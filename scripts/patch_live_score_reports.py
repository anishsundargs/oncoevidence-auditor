from pathlib import Path


p = Path("src/report_builder.py")
text = p.read_text()

# 1. Add import.
addition = "from src.live_evidence_score import build_live_evidence_score\n"

if addition not in text:
    lines = text.splitlines(keepends=True)
    insert_at = None

    for i, line in enumerate(lines):
        if line.startswith("from src.") or line.startswith("import src."):
            insert_at = i + 1

    if insert_at is None:
        raise SystemExit("Could not find src imports in src/report_builder.py.")

    lines.insert(insert_at, addition)
    text = "".join(lines)


# 2. Compute live evidence score after contradiction lines are built.
anchor = '''    contradiction_lines = "\\n".join(
        [
            f"- **{item['label']}** ({item['severity']}): {item['explanation']}"
            for item in contradiction_result.get("labels", [])
        ]
    ) or "- None"

    available_layers_text = ", ".join(coverage_result.get("available_layers", [])) or "None"
'''

insert = '''    contradiction_lines = "\\n".join(
        [
            f"- **{item['label']}** ({item['severity']}): {item['explanation']}"
            for item in contradiction_result.get("labels", [])
        ]
    ) or "- None"

    live_score_result = build_live_evidence_score(
        depmap_result=depmap_result,
        common_result=common_result,
        specificity_result=specificity_result,
        cbio_result=cbio_result,
        expression_result=expression_result,
        survival_result=survival_result,
        therapeutic_result=therapeutic_result,
        contradiction_result=contradiction_result,
    )

    live_score_breakdown_lines = "\\n".join(
        [
            f"| {_safe(component)} | {_safe(points)} |"
            for component, points in live_score_result.get("breakdown", {}).items()
        ]
    ) or "| Not available | Not available |"

    available_layers_text = ", ".join(coverage_result.get("available_layers", [])) or "None"
'''

if "live_score_result = build_live_evidence_score(" not in text:
    if anchor not in text:
        raise SystemExit("Could not find contradiction_lines anchor.")
    text = text.replace(anchor, insert, 1)


# 3. Insert report section before Auditor Verdict.
anchor_section = '''---

## Auditor Verdict
'''

insert_section = '''---

## Live Evidence Score

**Live evidence score:** {_safe(live_score_result.get("live_evidence_score"))}/100  
**Live evidence tier:** {_safe(live_score_result.get("live_evidence_tier"))}  

{_safe(live_score_result.get("interpretation_note"))}

| Evidence component | Points |
|---|---|
{live_score_breakdown_lines}

---

## Auditor Verdict
'''

if "## Live Evidence Score" not in text:
    if anchor_section not in text:
        raise SystemExit("Could not find Auditor Verdict section anchor.")
    text = text.replace(anchor_section, insert_section, 1)


p.write_text(text)
print("Added live evidence score to Markdown reports.")