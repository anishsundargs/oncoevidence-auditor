import streamlit as st

from src.cancer_registry import list_supported_cancers
from src.batch_audit import build_batch_audit


st.set_page_config(
    page_title="Batch Audit | OncoEvidence Auditor",
    page_icon="📊",
    layout="wide",
)

st.title("Batch Audit Mode")
st.caption(
    "Fast local screening of all curated genes for a selected cancer type. "
    "This page ranks genes by dependency, specificity, common-essential caution, and auditor interpretation."
)

st.warning(
    "Research-use only. Batch results are hypothesis-generating and do not imply clinical actionability."
)

cancer_type = st.selectbox("Cancer type", list_supported_cancers())

if st.button("Run batch audit", type="primary"):
    with st.spinner(f"Auditing curated genes for {cancer_type}..."):
        batch_df = build_batch_audit(cancer_type)

    if batch_df.empty:
        st.info(f"No curated genes found for {cancer_type}.")
    else:
        st.success(f"Audited {len(batch_df)} genes for {cancer_type}.")

        summary_cols = [
            "gene",
            "dependency_label",
            "percent_dependent",
            "common_essential_caution",
            "specificity_label",
            "specificity_delta",
            "batch_pattern",
            "auditor_verdict_tier",
            "main_warning",
        ]

        st.subheader("Batch Audit Summary")
        st.dataframe(batch_df[summary_cols], use_container_width=True)

        st.subheader("Pattern Counts")
        pattern_counts = (
            batch_df["batch_pattern"]
            .value_counts()
            .rename_axis("batch_pattern")
            .reset_index(name="gene_count")
        )
        st.dataframe(pattern_counts, use_container_width=True)

        st.subheader("Download Batch Results")
        csv_data = batch_df.to_csv(index=False)

        st.download_button(
            label="Download batch audit CSV",
            data=csv_data,
            file_name=f"{cancer_type}_batch_audit.csv".replace(" ", "_"),
            mime="text/csv",
        )

        st.subheader("Interpretation Guide")
        st.write(
            """
Use this page to identify genes that look promising in one layer but risky in another.
The most important patterns are:

- **Strong dependency + high common-essential risk:** gene may be broadly essential rather than selectively targetable.
- **Strong dependency + weak lineage specificity:** dependency may not be specific to the selected cancer.
- **Weak dependency signal:** the gene may be biologically relevant but not a strong CRISPR dependency in current cell-line models.

For final claims, use the single-gene page and full Markdown report.
"""
        )
else:
    st.info("Choose a cancer type and click **Run batch audit**.")
