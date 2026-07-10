from pathlib import Path


batch_path = Path("src/batch_audit.py")
text = batch_path.read_text()

helper = '''

def is_layer_available(result: Dict) -> bool:
    """Return whether a local batch evidence layer is available."""
    if not isinstance(result, dict):
        return False
    if result.get("available") is False:
        return False
    return True


def summarize_local_curated_coverage(
    depmap_result: Dict,
    common_result: Dict,
    specificity_result: Dict,
    gene_role_result: Dict,
    pathway_result: Dict,
    therapeutic_result: Dict,
) -> Dict:
    """
    Summarize local/non-live evidence layers used in fast batch mode.

    This is separate from full 10-layer coverage because PubMed, cBioPortal,
    expression, and survival require live external data calls.
    """
    layers = {
        "DepMap dependency": is_layer_available(depmap_result),
        "Common-essential caution": is_layer_available(common_result),
        "Lineage specificity": is_layer_available(specificity_result),
        "Gene role classification": is_layer_available(gene_role_result),
        "Pathway/function annotation": is_layer_available(pathway_result),
        "Therapeutic relevance": is_layer_available(therapeutic_result),
    }

    available_layers = [name for name, available in layers.items() if available]
    missing_layers = [name for name, available in layers.items() if not available]

    possible = len(layers)
    available = len(available_layers)
    percent = round((available / possible) * 100, 1) if possible else 0

    if percent == 100:
        label = "Complete local curated profile"
    elif percent >= 70:
        label = "Mostly complete local curated profile"
    elif percent >= 40:
        label = "Partial local curated profile"
    else:
        label = "Sparse local curated profile"

    return {
        "local_curated_layers_available": available,
        "local_curated_layers_possible": possible,
        "local_curated_coverage_percent": percent,
        "local_curated_coverage_label": label,
        "local_curated_available_layers": available_layers,
        "local_curated_missing_layers": missing_layers,
    }
'''

if "def summarize_local_curated_coverage(" not in text:
    anchor = "def build_batch_audit("
    idx = text.find(anchor)
    if idx == -1:
        raise SystemExit("Could not find build_batch_audit in src/batch_audit.py")
    text = text[:idx] + helper + "\n" + text[idx:]


insert_after = '''        coverage_result = calculate_evidence_coverage(
            pubmed_count=pubmed_count,
            depmap_result=depmap_result,
            common_result=common_result,
            specificity_result=specificity_result,
            cbio_result=cbio_result,
            expression_result=expression_result,
            gene_role_result=gene_role_result,
            pathway_result=pathway_result,
            therapeutic_result=therapeutic_result,
        )
'''

local_block = '''        coverage_result = calculate_evidence_coverage(
            pubmed_count=pubmed_count,
            depmap_result=depmap_result,
            common_result=common_result,
            specificity_result=specificity_result,
            cbio_result=cbio_result,
            expression_result=expression_result,
            gene_role_result=gene_role_result,
            pathway_result=pathway_result,
            therapeutic_result=therapeutic_result,
        )

        local_coverage_result = summarize_local_curated_coverage(
            depmap_result=depmap_result,
            common_result=common_result,
            specificity_result=specificity_result,
            gene_role_result=gene_role_result,
            pathway_result=pathway_result,
            therapeutic_result=therapeutic_result,
        )
'''

if "local_coverage_result = summarize_local_curated_coverage(" not in text:
    if insert_after not in text:
        raise SystemExit("Could not find coverage_result block in src/batch_audit.py")
    text = text.replace(insert_after, local_block)


row_anchor = '''                "evidence_coverage_label": coverage_result.get("evidence_coverage_label"),
                "primary_contradiction_label": contradiction_result.get("primary_label"),
'''

row_replacement = '''                "evidence_coverage_label": coverage_result.get("evidence_coverage_label"),
                "local_curated_layers_available": local_coverage_result.get("local_curated_layers_available"),
                "local_curated_layers_possible": local_coverage_result.get("local_curated_layers_possible"),
                "local_curated_coverage_percent": local_coverage_result.get("local_curated_coverage_percent"),
                "local_curated_coverage_label": local_coverage_result.get("local_curated_coverage_label"),
                "primary_contradiction_label": contradiction_result.get("primary_label"),
'''

if '"local_curated_coverage_percent": local_coverage_result.get("local_curated_coverage_percent")' not in text:
    if row_anchor not in text:
        raise SystemExit("Could not find row coverage anchor in src/batch_audit.py")
    text = text.replace(row_anchor, row_replacement)

batch_path.write_text(text)


page_path = Path("pages/2_Batch_Audit.py")
page = page_path.read_text()

# Add local coverage columns to the visible table.
old_cols = '''    "evidence_coverage_label",
    "evidence_coverage_percent",
    "primary_contradiction_label",
'''

new_cols = '''    "local_curated_coverage_label",
    "local_curated_coverage_percent",
    "evidence_coverage_label",
    "evidence_coverage_percent",
    "primary_contradiction_label",
'''

if '"local_curated_coverage_label",' not in page:
    if old_cols not in page:
        raise SystemExit("Could not find base_cols coverage area in pages/2_Batch_Audit.py")
    page = page.replace(old_cols, new_cols)


# Add explanatory note after success/caption.
old_note = '''st.caption("Changing filters below will not rerun external APIs. Click Run batch audit again to refresh results.")
'''

new_note = '''st.caption("Changing filters below will not rerun external APIs. Click Run batch audit again to refresh results.")

st.info(
    "Coverage note: local curated coverage measures fast-mode layers such as DepMap, common-essential caution, "
    "specificity, gene role, pathway, and therapeutic annotation. Full evidence coverage includes live layers "
    "such as PubMed, cBioPortal alteration/expression, and survival/prognosis evidence."
)
'''

if "Coverage note: local curated coverage" not in page:
    if old_note not in page:
        raise SystemExit("Could not find Batch Audit caption block.")
    page = page.replace(old_note, new_note)


# Add local coverage metric to dashboard summary if possible.
old_metric = '''with m3:
    if "evidence_coverage_percent" in filtered_df.columns and not filtered_df.empty:
        avg_coverage = round(float(pd.to_numeric(filtered_df["evidence_coverage_percent"], errors="coerce").mean()), 1)
        st.metric("Mean evidence coverage", f"{avg_coverage}%")
    else:
        st.metric("Mean evidence coverage", "Not available")
'''

new_metric = '''with m3:
    if "local_curated_coverage_percent" in filtered_df.columns and not filtered_df.empty:
        avg_local_coverage = round(float(pd.to_numeric(filtered_df["local_curated_coverage_percent"], errors="coerce").mean()), 1)
        st.metric("Mean local curated coverage", f"{avg_local_coverage}%")
    elif "evidence_coverage_percent" in filtered_df.columns and not filtered_df.empty:
        avg_coverage = round(float(pd.to_numeric(filtered_df["evidence_coverage_percent"], errors="coerce").mean()), 1)
        st.metric("Mean evidence coverage", f"{avg_coverage}%")
    else:
        st.metric("Mean local curated coverage", "Not available")
'''

if "Mean local curated coverage" not in page:
    if old_metric not in page:
        raise SystemExit("Could not find dashboard coverage metric block.")
    page = page.replace(old_metric, new_metric)


# Add chart for local curated coverage if the chart section exists.
chart_anchor = '''with chart_col1:
    fig = count_chart(filtered_df, "primary_contradiction_severity", "Contradiction severity distribution")
    if fig is not None:
        st.plotly_chart(fig, use_container_width=True)
'''

chart_replacement = '''with chart_col1:
    fig = count_chart(filtered_df, "primary_contradiction_severity", "Contradiction severity distribution")
    if fig is not None:
        st.plotly_chart(fig, use_container_width=True)

local_cov_fig = count_chart(filtered_df, "local_curated_coverage_label", "Local curated coverage distribution")
if local_cov_fig is not None:
    st.plotly_chart(local_cov_fig, use_container_width=True)
'''

if "Local curated coverage distribution" not in page:
    if chart_anchor not in page:
        raise SystemExit("Could not find first chart block in Batch Audit page.")
    page = page.replace(chart_anchor, chart_replacement)

page_path.write_text(page)

print("Patched Batch Audit with local curated coverage.")