import pandas as pd
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
    "live modes add PubMed and/or cBioPortal evidence."
)

st.warning(
    "Research-use only. Batch results are hypothesis-generating and do not imply clinical actionability."
)

cancer_type = st.selectbox("Cancer type", list_supported_cancers())

include_live_pubmed = st.checkbox(
    "Include live PubMed literature saturation",
    value=False,
    help="Adds PubMed count, literature saturation, and inferred novelty. Slower because it queries PubMed for each gene.",
)

include_live_cbio = st.checkbox(
    "Include live cBioPortal alteration/expression evidence",
    value=False,
    help="Adds patient-tumor alteration and expression evidence. Slower because it queries cBioPortal for each gene.",
)

if st.button("Run batch audit", type="primary"):
    with st.spinner(f"Auditing curated genes for {cancer_type}..."):
        batch_df = build_batch_audit(
            cancer_type=cancer_type,
            include_live_cbio=include_live_cbio,
            include_live_pubmed=include_live_pubmed,
        )

    if batch_df.empty:
        st.info(f"No curated genes found for {cancer_type}.")
    else:
        enabled_layers = []
        if include_live_pubmed:
            enabled_layers.append("live PubMed")
        if include_live_cbio:
            enabled_layers.append("live cBioPortal")

        mode_label = "fast local mode" if not enabled_layers else " + ".join(enabled_layers)
        st.success(f"Audited {len(batch_df)} genes for {cancer_type} using {mode_label}.")

        base_cols = [
            "gene",
            "evidence_coverage_label",
            "evidence_coverage_percent",
            "primary_contradiction_label",
            "primary_contradiction_severity",
            "gene_role_category",
            "target_class",
            "role_risk_label",
            "dependency_label",
            "percent_dependent",
            "common_essential_caution",
            "specificity_label",
            "specificity_delta",
            "batch_pattern",
            "auditor_verdict_tier",
            "main_warning",
        ]

        pubmed_cols = [
            "pubmed_count",
            "literature_saturation",
            "inferred_novelty",
        ]

        cbio_cols = [
            "patient_alteration_support",
            "mutation_frequency",
            "amplification_frequency",
            "expression_support",
            "median_expression_zscore",
            "percent_high_expression",
        ]

        summary_cols = base_cols.copy()

        if include_live_pubmed:
            summary_cols += pubmed_cols

        if include_live_cbio:
            summary_cols += cbio_cols

        st.subheader("Batch Audit Summary")

        display_df = batch_df[summary_cols].copy()

        # Make missing values readable in the app table.
        # Keep the original batch_df unchanged for CSV download.
        display_df = display_df.astype(object).where(pd.notna(display_df), "Not available")

        st.dataframe(display_df, use_container_width=True)

        st.subheader("Coverage Counts")
        coverage_counts = (
            batch_df["evidence_coverage_label"]
            .fillna("Not available")
            .value_counts()
            .rename_axis("evidence_coverage_label")
            .reset_index(name="gene_count")
        )
        st.dataframe(coverage_counts, use_container_width=True)

        st.subheader("Pattern Counts")
        pattern_counts = (
            batch_df["batch_pattern"]
            .value_counts()
            .rename_axis("batch_pattern")
            .reset_index(name="gene_count")
        )
        st.dataframe(pattern_counts, use_container_width=True)

        if include_live_pubmed:
            st.subheader("Literature Saturation Counts")
            pubmed_counts = (
                batch_df["literature_saturation"]
                .fillna("Not available")
                .value_counts()
                .rename_axis("literature_saturation")
                .reset_index(name="gene_count")
            )
            st.dataframe(pubmed_counts, use_container_width=True)

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
- **Literature-saturated hypothesis:** the gene/cancer pair is heavily studied, so novelty requires a sharper angle.
- **Weak dependency signal:** gene may be biologically relevant but not a strong CRISPR dependency in current cell-line models.

For final claims, use the single-gene page and full Markdown evidence report.
"""
        )
else:
    st.info("Choose a cancer type and click **Run batch audit**.")
