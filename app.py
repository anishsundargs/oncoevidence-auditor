import pandas as pd
import plotly.express as px
import streamlit as st

from src.evidence_scoring import calculate_score, classify_tier, generate_flags, generate_safe_claim


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

df = load_mock_data()

with st.sidebar:
    st.header("Input")
    cancer_type = st.selectbox("Cancer type", sorted(df["cancer_type"].unique()))
    genes = sorted(df.loc[df["cancer_type"] == cancer_type, "gene"].unique())
    gene = st.selectbox("Gene", genes)

    st.divider()
    st.subheader("MVP Status")
    st.write("This starter version uses mock values to test the evidence-card design and scoring logic.")
    st.write("Next step: replace mock values with real TCGA/GDC, cBioPortal, DepMap, GTEx, and GEO data.")

row = df[(df["gene"] == gene) & (df["cancer_type"] == cancer_type)].iloc[0].to_dict()

score, breakdown = calculate_score(row)
flags = generate_flags(row)
tier = classify_tier(score, flags)
safe_claim = generate_safe_claim(row, score, tier)

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
    "flags": flags,
    "safe_claim": safe_claim,
}

st.download_button(
    label="Download evidence summary as JSON",
    data=pd.Series(summary).to_json(indent=2),
    file_name=f"{gene}_{cancer_type}_evidence_summary.json",
    mime="application/json"
)
