from pathlib import Path


p = Path("app.py")
text = p.read_text()

# 1. Add live evidence score import after the last existing src import.
addition = "from src.live_evidence_score import build_live_evidence_score\n"

if addition not in text:
    lines = text.splitlines(keepends=True)
    insert_at = None

    for i, line in enumerate(lines):
        if line.startswith("from src.") or line.startswith("import src."):
            insert_at = i + 1

    if insert_at is None:
        raise SystemExit("Could not find any src imports in app.py.")

    lines.insert(insert_at, addition)
    text = "".join(lines)


# 2. Insert live evidence score block after first Auditor Verdict heading.
anchor_section = '''st.subheader("Auditor Verdict")
'''

insert_section = '''st.subheader("Auditor Verdict")

try:
    _live_score_contradiction_result = build_contradiction_labels(
        gene=gene,
        cancer_type=cancer_type,
        depmap_result=depmap_result,
        common_result=common_result,
        specificity_result=specificity_result,
        cbio_result=cbio_result,
        expression_result=expr_result,
        survival_result=survival_result if "survival_result" in locals() else {},
        gene_role_result=gene_role_result if "gene_role_result" in locals() else {},
        saturation_label=saturation_label if "saturation_label" in locals() else None,
    )
except Exception:
    _live_score_contradiction_result = {}

try:
    _live_score_therapeutic_result = therapeutic_result
except Exception:
    _live_score_therapeutic_result = {}

live_score_result = build_live_evidence_score(
    depmap_result=depmap_result,
    common_result=common_result,
    specificity_result=specificity_result,
    cbio_result=cbio_result,
    expression_result=expr_result,
    survival_result=survival_result if "survival_result" in locals() else {},
    therapeutic_result=_live_score_therapeutic_result,
    contradiction_result=_live_score_contradiction_result,
)

live_col1, live_col2 = st.columns(2)
with live_col1:
    st.metric("Live evidence score", f"{live_score_result['live_evidence_score']}/100")
with live_col2:
    st.metric("Live evidence tier", live_score_result["live_evidence_tier"])

st.caption(live_score_result["interpretation_note"])

with st.expander("Show live evidence score breakdown"):
    st.dataframe(
        [
            {"Evidence component": key, "Points": value}
            for key, value in live_score_result["breakdown"].items()
        ],
        use_container_width=True,
    )

'''

if "Live evidence score" not in text:
    if anchor_section not in text:
        raise SystemExit("Could not find Auditor Verdict heading.")
    text = text.replace(anchor_section, insert_section, 1)


p.write_text(text)
print("Added live evidence score to app.")