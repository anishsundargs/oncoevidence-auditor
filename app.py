import pandas as pd
import plotly.express as px
import streamlit as st

from src.evidence_scoring import calculate_score, classify_tier, generate_flags, generate_safe_claim
from src.pubmed_saturation import get_pubmed_count, classify_literature_saturation
from src.depmap_dependency import get_dependency_result, get_depmap_data_source_label
from src.common_essential import get_common_essential_result
from src.auditor_verdict import build_auditor_verdict


st.set_page_config(
    page_title="OncoEvidence Auditor",
    page_icon="🧬",
    layout="wide"
)

st.title("OncoEvidence Auditor")
st.caption("Contradiction-aware cancer gene hypothesis triage using public-data evidence layers.")

st.warning(
    "Research/education only. This tool is not a diagnostic, prognostic, or treatment recommendation system.",
    icon="⚠️"
)


@st.cache_data
def load_mock_data():
    return pd.read_csv("data/mock_gene_evidence.csv")


@st.cache_data(show_spinner=False)
def cached_pubmed_count(gene, cancer_type):
    return get_pubmed_count(gene, cancer_type)


df = load_mock_data()

with st.sidebar:
    st.header("Input")
    cancer_type = st.selectbox("Cancer type", sorted(df["cancer_type"].unique()))
    genes = sorted(df.loc[df["cancer_type"] == cancer_type, "gene"].unique())
    gene = st.selectbox("Gene", genes)

    st.divider()
    st.subheader("MVP Status")
    st.write("Main evidence card still uses curated mock values.")
    st.write("PubMed literature saturation is now a live data layer using NCBI ESearch.")

row = df[(df["gene"] == gene) & (df["cancer_type"] == cancer_type)].iloc[0].to_dict()

score, breakdown = calculate_score(row)
flags = generate_flags(row)
tier = classify_tier(score, flags)
safe_claim = generate_safe_claim(row, score, tier)

# Preload PubMed values early so the Auditor Verdict can use them.
pubmed_count = None
pubmed_query = None
saturation_label = None
inferred_novelty = None
saturation_note = None

try:
    pubmed_count, pubmed_query = cached_pubmed_count(gene, cancer_type)
    saturation_label, inferred_novelty, saturation_note = classify_literature_saturation(pubmed_count)
except Exception:
    pass

col1, col2, col3 = st.columns([1, 1, 1])

with col1:
    st.metric("Evidence score", f"{score}/100")

with col2:
    st.metric("Evidence tier", tier)

with col3:
    st.metric("Cancer type", cancer_type)

st.divider()

st.subheader(f"Evidence Card: {gene} in {cancer_type}")

left, right = st.columns([1.1, 1])

with left:
    st.markdown("### Evidence layer summary")
    evidence_table = pd.DataFrame(
        [
            ["Tumor expression", row["tumor_expression"]],
            ["Survival association", row["survival_association"]],
            ["External/GEO validation", row["geo_validation"]],
            ["DepMap dependency", row["depmap_dependency"]],
            ["Normal tissue safety", row["normal_tissue_safety"]],
            ["Mutation/CNA/pathway support", row["mutation_cna_support"]],
            ["Novelty score", row["novelty_score"]],
        ],
        columns=["Evidence layer", "Current result"]
    )
    st.dataframe(evidence_table, use_container_width=True, hide_index=True)

    st.markdown("### Notes")
    st.write(row["notes"])

with right:
    st.markdown("### Score breakdown")
    plot_df = pd.DataFrame(
        {"Component": list(breakdown.keys()), "Points": list(breakdown.values())}
    )
    fig = px.bar(plot_df, x="Points", y="Component", orientation="h", range_x=[0, 20])
    fig.update_layout(height=420, margin=dict(l=10, r=10, t=20, b=10))
    st.plotly_chart(fig, use_container_width=True)

st.divider()

st.subheader("DepMap Dependency Signal")

depmap_result = get_dependency_result(gene, cancer_type)

if depmap_result["available"]:
    d1, d2, d3 = st.columns(3)

    with d1:
        st.metric("Median dependency score", depmap_result["median_dependency_score"])

    with d2:
        st.metric(
            "Dependent cell lines",
            f'{depmap_result["dependent_cell_lines"]}/{depmap_result["total_cell_lines"]}'
        )

    with d3:
        st.metric("Dependency label", depmap_result["dependency_label"])

    st.write(f'Percent dependent: **{depmap_result["percent_dependent"]}%**')
    st.write(depmap_result["dependency_note"])

    st.caption(f"Active dependency data source: {depmap_result['data_source']}")
else:
    st.warning(depmap_result["dependency_note"])

st.subheader("Common-Essential / Specificity Caution")

common_result = get_common_essential_result(gene)

if common_result["available"]:
    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric(
            "Pan-cancer median dependency",
            common_result["pan_cancer_median_dependency_score"]
        )

    with c2:
        st.metric(
            "Pan-cancer dependent models",
            f'{common_result["pan_cancer_dependent_cell_lines"]}/{common_result["pan_cancer_total_cell_lines"]}'
        )

    with c3:
        st.metric(
            "Common-essential label",
            common_result["common_essential_label"]
        )

    st.write(f'Pan-cancer percent dependent: **{common_result["pan_cancer_percent_dependent"]}%**')
    st.warning(common_result["common_essential_note"])
else:
    st.info(common_result["common_essential_note"])

st.subheader("Auditor Verdict")

if pubmed_count is not None and saturation_label is not None:
    verdict = build_auditor_verdict(
        gene=gene,
        cancer_type=cancer_type,
        pubmed_count=pubmed_count,
        saturation_label=saturation_label,
        depmap_result=depmap_result,
        common_result=common_result,
    )

    st.metric("Final hypothesis tier", verdict["verdict_tier"])

    st.markdown("### Evidence strengths")
    if verdict["strengths"]:
        for item in verdict["strengths"]:
            st.success(item)
    else:
        st.info("No major strengths detected by the current auditor logic.")

    st.markdown("### Evidence warnings")
    if verdict["warnings"]:
        for item in verdict["warnings"]:
            st.warning(item)
    else:
        st.success("No major warnings detected by the current auditor logic.")

    st.markdown("### Conservative claim")
    st.info(verdict["safe_claim"])

    with st.expander("Auditor methods note"):
        st.write(verdict["methods_note"])

else:
    st.info("Auditor verdict will appear after PubMed and dependency modules finish loading.")

st.divider()

st.divider()

st.subheader("Live PubMed Literature Saturation")

try:
    with st.spinner("Querying PubMed through NCBI ESearch..."):
        pubmed_count, pubmed_query = cached_pubmed_count(gene, cancer_type)

    saturation_label, inferred_novelty, saturation_note = classify_literature_saturation(pubmed_count)

    p1, p2, p3 = st.columns(3)

    with p1:
        st.metric("PubMed count", pubmed_count)

    with p2:
        st.metric("Literature saturation", saturation_label)

    with p3:
        st.metric("Inferred novelty", inferred_novelty)

    st.write(saturation_note)

    with st.expander("Show PubMed query"):
        st.code(pubmed_query)

except Exception as e:
    st.error("PubMed module failed. Check your internet connection or try again later.")
    st.code(str(e))

st.divider()

st.subheader("Contradiction and caution flags")
for flag in flags:
    st.write(f"- {flag}")

st.subheader("Safe research claim")
st.info(safe_claim)

st.divider()

st.subheader("Exportable summary")

summary = {
    "gene": gene,
    "cancer_type": cancer_type,
    "score": score,
    "tier": tier,
    "pubmed_count": pubmed_count if "pubmed_count" in locals() else None,
    "depmap_dependency_label": depmap_result.get("dependency_label") if "depmap_result" in locals() else None,
    "depmap_median_dependency_score": depmap_result.get("median_dependency_score") if "depmap_result" in locals() else None,
    "depmap_percent_dependent": depmap_result.get("percent_dependent") if "depmap_result" in locals() else None,
    "common_essential_label": common_result.get("common_essential_label") if "common_result" in locals() else None,
    "pan_cancer_percent_dependent": common_result.get("pan_cancer_percent_dependent") if "common_result" in locals() else None,
    "auditor_verdict_tier": verdict.get("verdict_tier") if "verdict" in locals() else None,
    "auditor_safe_claim": verdict.get("safe_claim") if "verdict" in locals() else None,
    "literature_saturation": saturation_label if "saturation_label" in locals() else None,
    "inferred_novelty": inferred_novelty if "inferred_novelty" in locals() else None,
    "flags": flags,
    "safe_claim": safe_claim,
}

st.download_button(
    label="Download evidence summary as JSON",
    data=pd.Series(summary).to_json(indent=2),
    file_name=f"{gene}_{cancer_type}_evidence_summary.json",
    mime="application/json"
)
