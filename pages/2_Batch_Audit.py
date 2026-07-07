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
    "Screen all curated genes for a selected cancer type. Fast mode uses local processed layers; "
    "live mode adds patient-tumor evidence from cBioPortal."
)

st.warning(
    "Research-use only. Batch results are hypothesis-generating and do not imply clinical actionability."
)

cancer_type = st.selectbox("Cancer type", list_supported_cancers())

include_live_cbio = st.checkbox(
    "Include live cBioPortal alteration/expression evidence",
    value=False,
    help="Slower, but adds patient-tumor alteration and expression evidence for each gene.",
)

if st.button("Run batch audit", type="primary"):
    with st.spinner(f"Auditing curated genes for {cancer_type}..."):
        batch_df = build_batch_audit(
            cancer_type=cancer_type,
            include_live_cbio=include_live_cbio,
        )

    if batch_df.empty:
        st.info(f"No curated genes found for {cancer_type}.")
    else:
        mode_label = "live cBioPortal mode" if include_live_cbio else "fast local mode"
        st.success(f"Audited {len(batch_df)} genes for {cancer_type} using {mode_label}.")

        base_cols = [
            "gene",
            "evidence_coverage_label",
            "evidence_coverage_percent",
            "dependency_label",
            "percent_dependent",
            "common_essential_caution",
            "specificity_label",
            "specificity_delta",
            "batch_pattern",
            "auditor_verdict_tier",
            "main_warning",
        ]

        live_cols = [
            "patient_alteration_support",
            "mutation_frequency",
            "amplification_frequency",
            "expression_support",
            "median_expression_zscore",
            "percent_high_expression",
        ]

        summary_cols = base_cols + live_cols if include_live_cbio else base_cols

        st.subheader("Batch Audit Summary")

        display_df = batch_df[summary_cols].copy()

        # Make missing values readable in the app table.
        # Keep the original batch_df unchanged for CSV download.
        text_cols = display_df.select_dtypes(include=["object"]).columns
        display_df[text_cols] = display_df[text_cols].fillna("Not available")

        st.dataframe(display_df, use_container_width=True)

        st.subheader("Pattern Counts")
        pattern_counts = (
            batch_df["batch_pattern"]
            .value_counts()
            .rename_axis("batch_pattern")
            .reset_index(name="gene_count")
        )
        st.dataframe(pattern_counts, use_container_width=True)

        if include_live_cbio:
            st.subheader("Patient-Support Counts")

            patient_counts = (
                batch_df["patient_alteration_support"]
                .fillna("Not available")
                .value_counts()
                .rename_axis("patient_alteration_support")
                .reset_index(name="gene_count")
            )

            expression_counts = (
                batch_df["expression_support"]
                .fillna("Not available")
                .value_counts()
                .rename_axis("expression_support")
                .reset_index(name="gene_count")
            )

            c1, c2 = st.columns(2)
            with c1:
                st.write("Patient alteration support")
                st.dataframe(patient_counts, use_container_width=True)

            with c2:
                st.write("Patient expression support")
                st.dataframe(expression_counts, use_container_width=True)

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

Important patterns:
- **Strong dependency + weak patient support:** strong cell-line dependency but weak patient alteration/expression support.
- **Strong dependency + high common-essential risk:** gene may be broadly essential rather than selectively targetable.
- **Strong dependency + weak lineage specificity:** dependency may not be specific to the selected cancer.
- **Weak dependency signal:** gene may be biologically relevant but not a strong CRISPR dependency in current cell-line models.

For final claims, use the single-gene page and full Markdown evidence report.
"""
        )
else:
    st.info("Choose a cancer type and click **Run batch audit**.")
