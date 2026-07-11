import pandas as pd
import plotly.express as px
import streamlit as st

from src.cancer_registry import list_supported_cancers
from src.batch_audit import build_batch_audit
from src.ui_style import apply_global_style, render_theme_selector
from src.plotly_theme import apply_plotly_theme


st.set_page_config(
    page_title="Batch Audit | OncoEvidence Auditor",
    page_icon="📊",
    layout="wide",
)
_theme_mode = render_theme_selector()
apply_global_style(_theme_mode)


st.title("Batch Audit Mode")
st.caption(
    "Screen curated genes for a selected cancer type and identify contradiction-heavy hypotheses."
)

st.warning(
    "Research-use only. Batch results are hypothesis-generating and do not imply clinical actionability."
)

if "batch_audit_df" not in st.session_state:
    st.session_state["batch_audit_df"] = None
if "batch_audit_cancer" not in st.session_state:
    st.session_state["batch_audit_cancer"] = None
if "batch_audit_mode" not in st.session_state:
    st.session_state["batch_audit_mode"] = None

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

run_col, clear_col = st.columns([1, 1])

with run_col:
    run_batch = st.button("Run batch audit", type="primary")

with clear_col:
    clear_results = st.button("Clear batch results")

if clear_results:
    st.session_state["batch_audit_df"] = None
    st.session_state["batch_audit_cancer"] = None
    st.session_state["batch_audit_mode"] = None
    st.success("Cleared batch results.")

if run_batch:
    with st.spinner(f"Auditing curated genes for {cancer_type}..."):
        batch_df = build_batch_audit(
            cancer_type=cancer_type,
            include_live_cbio=include_live_cbio,
            include_live_pubmed=include_live_pubmed,
        )

    enabled_layers = []
    if include_live_pubmed:
        enabled_layers.append("live PubMed")
    if include_live_cbio:
        enabled_layers.append("live cBioPortal")

    mode_label = "fast local mode" if not enabled_layers else " + ".join(enabled_layers)

    st.session_state["batch_audit_df"] = batch_df
    st.session_state["batch_audit_cancer"] = cancer_type
    st.session_state["batch_audit_mode"] = mode_label

batch_df = st.session_state.get("batch_audit_df")

if batch_df is None:
    st.info("Choose a cancer type and click Run batch audit.")
    st.stop()

if batch_df.empty:
    selected_cancer_for_message = st.session_state.get("batch_audit_cancer_type", "the selected cancer")
    st.info(f"No curated genes found for {selected_cancer_for_message}.")
    st.stop()

active_cancer = st.session_state.get("batch_audit_cancer") or cancer_type
mode_label = st.session_state.get("batch_audit_mode") or "stored results"

st.success(f"Audited {len(batch_df)} genes for {active_cancer} using {mode_label}.")
st.caption("Changing filters below will not rerun external APIs. Click Run batch audit again to refresh results.")

st.info(
    "Coverage note: local curated coverage measures fast-mode layers such as DepMap, common-essential caution, "
    "specificity, gene role, pathway, and therapeutic annotation. Full evidence coverage includes live layers "
    "such as PubMed, cBioPortal alteration/expression, and survival/prognosis evidence."
)

base_cols = [
    "gene",
    "local_curated_coverage_label",
    "local_curated_coverage_percent",
    "evidence_coverage_label",
    "evidence_coverage_percent",
    "primary_contradiction_label",
    "primary_contradiction_severity",
    "gene_role_category",
    "target_class",
    "role_risk_label",
    "pathway_category",
    "function_group",
    "pathway_caution_label",
    "therapeutic_relevance",
    "biomarker_type",
    "therapeutic_alignment_label",
    "dependency_label",
    "percent_dependent",
    "common_essential_caution",
    "specificity_label",
    "specificity_delta",
    "batch_pattern",
    "auditor_verdict_tier",
    "main_warning",
    "safe_claim",
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

summary_cols = [c for c in base_cols + pubmed_cols + cbio_cols if c in batch_df.columns]


def options_for(df, column):
    if column not in df.columns:
        return []
    values = df[column].fillna("Not available").astype(str).unique().tolist()
    return sorted(values)


def apply_multiselect_filter(df, column, selected):
    if column not in df.columns or not selected:
        return df
    return df[df[column].fillna("Not available").astype(str).isin(selected)]


def count_chart(df, column, title):
    if column not in df.columns or df.empty:
        return None

    chart_df = (
        df[column]
        .fillna("Not available")
        .astype(str)
        .value_counts()
        .rename_axis(column)
        .reset_index(name="gene_count")
    )

    if chart_df.empty:
        return None

    fig = px.bar(
        chart_df,
        x="gene_count",
        y=column,
        orientation="h",
        title=title,
    )
    fig.update_layout(
        height=max(320, min(650, 80 + 35 * len(chart_df))),
        margin=dict(l=20, r=20, t=60, b=20),
        yaxis=dict(autorange="reversed"),
    )
    return fig


st.subheader("Filters and sorting")

f1, f2, f3 = st.columns(3)

with f1:
    severity_options = options_for(batch_df, "primary_contradiction_severity")
    selected_severity = st.multiselect(
        "Contradiction severity",
        severity_options,
        default=severity_options,
    )

with f2:
    contradiction_options = options_for(batch_df, "primary_contradiction_label")
    selected_contradictions = st.multiselect(
        "Primary contradiction label",
        contradiction_options,
        default=contradiction_options,
    )

with f3:
    dependency_options = options_for(batch_df, "dependency_label")
    selected_dependency = st.multiselect(
        "Dependency label",
        dependency_options,
        default=dependency_options,
    )

f4, f5, f6 = st.columns(3)

with f4:
    therapeutic_options = options_for(batch_df, "therapeutic_relevance")
    selected_therapeutic = st.multiselect(
        "Therapeutic relevance",
        therapeutic_options,
        default=therapeutic_options,
    )

with f5:
    role_options = options_for(batch_df, "gene_role_category")
    selected_roles = st.multiselect(
        "Gene role category",
        role_options,
        default=role_options,
    )

with f6:
    pathway_options = options_for(batch_df, "pathway_category")
    selected_pathways = st.multiselect(
        "Pathway category",
        pathway_options,
        default=pathway_options,
    )

sort_options = [
    "evidence_coverage_percent",
    "percent_dependent",
    "specificity_delta",
    "primary_contradiction_severity",
    "therapeutic_relevance",
    "gene",
]
sort_options = [c for c in sort_options if c in batch_df.columns]

sort_col, sort_dir_col = st.columns([1, 1])

with sort_col:
    sort_by = st.selectbox("Sort by", sort_options, index=0 if sort_options else None)

with sort_dir_col:
    sort_direction = st.selectbox("Sort direction", ["Descending", "Ascending"])


filtered_df = batch_df.copy()
filtered_df = apply_multiselect_filter(filtered_df, "primary_contradiction_severity", selected_severity)
filtered_df = apply_multiselect_filter(filtered_df, "primary_contradiction_label", selected_contradictions)
filtered_df = apply_multiselect_filter(filtered_df, "dependency_label", selected_dependency)
filtered_df = apply_multiselect_filter(filtered_df, "therapeutic_relevance", selected_therapeutic)
filtered_df = apply_multiselect_filter(filtered_df, "gene_role_category", selected_roles)
filtered_df = apply_multiselect_filter(filtered_df, "pathway_category", selected_pathways)

ascending = sort_direction == "Ascending"

if sort_by:
    if sort_by == "primary_contradiction_severity":
        severity_rank = {
            "High": 3,
            "Moderate": 2,
            "Low": 1,
            "Not available": 0,
            "None": 0,
        }
        filtered_df = filtered_df.copy()
        filtered_df["_severity_sort"] = (
            filtered_df["primary_contradiction_severity"]
            .fillna("Not available")
            .astype(str)
            .map(severity_rank)
            .fillna(0)
        )
        filtered_df = filtered_df.sort_values("_severity_sort", ascending=ascending).drop(columns=["_severity_sort"])
    else:
        filtered_df = filtered_df.sort_values(sort_by, ascending=ascending, na_position="last")

st.subheader("Dashboard summary")

m1, m2, m3, m4 = st.columns(4)

with m1:
    st.metric("Genes shown", f"{len(filtered_df)}/{len(batch_df)}")

with m2:
    high_count = 0
    if "primary_contradiction_severity" in filtered_df.columns:
        high_count = int((filtered_df["primary_contradiction_severity"].fillna("") == "High").sum())
    st.metric("High-severity contradictions", high_count)

with m3:
    if "local_curated_coverage_percent" in filtered_df.columns and not filtered_df.empty:
        avg_local_coverage = round(float(pd.to_numeric(filtered_df["local_curated_coverage_percent"], errors="coerce").mean()), 1)
        st.metric("Mean local curated coverage", f"{avg_local_coverage}%")
    elif "evidence_coverage_percent" in filtered_df.columns and not filtered_df.empty:
        avg_coverage = round(float(pd.to_numeric(filtered_df["evidence_coverage_percent"], errors="coerce").mean()), 1)
        st.metric("Mean evidence coverage", f"{avg_coverage}%")
    else:
        st.metric("Mean local curated coverage", "Not available")

with m4:
    therapeutic_count = 0
    if "therapeutic_relevance" in filtered_df.columns:
        therapeutic_count = int(filtered_df["therapeutic_relevance"].fillna("").astype(str).str.contains("High", case=False).sum())
    st.metric("High therapeutic relevance", therapeutic_count)

st.subheader("Batch Audit Visual Dashboard")

chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    fig = count_chart(filtered_df, "primary_contradiction_severity", "Contradiction severity distribution")
    if fig is not None:
        st.plotly_chart(apply_plotly_theme(fig), use_container_width=True)

local_cov_fig = count_chart(filtered_df, "local_curated_coverage_label", "Local curated coverage distribution")
if local_cov_fig is not None:
    st.plotly_chart(apply_plotly_theme(local_cov_fig), use_container_width=True)

with chart_col2:
    fig = count_chart(filtered_df, "therapeutic_relevance", "Therapeutic relevance distribution")
    if fig is not None:
        st.plotly_chart(apply_plotly_theme(fig), use_container_width=True)

chart_col3, chart_col4 = st.columns(2)

with chart_col3:
    fig = count_chart(filtered_df, "gene_role_category", "Gene role distribution")
    if fig is not None:
        st.plotly_chart(apply_plotly_theme(fig), use_container_width=True)

with chart_col4:
    fig = count_chart(filtered_df, "pathway_category", "Pathway category distribution")
    if fig is not None:
        st.plotly_chart(apply_plotly_theme(fig), use_container_width=True)

st.markdown("### Dependency versus specificity map")

scatter_df = filtered_df.copy()

if "percent_dependent" in scatter_df.columns and "specificity_delta" in scatter_df.columns:
    scatter_df["percent_dependent_numeric"] = pd.to_numeric(scatter_df["percent_dependent"], errors="coerce")
    scatter_df["specificity_delta_numeric"] = pd.to_numeric(scatter_df["specificity_delta"], errors="coerce")

    scatter_df = scatter_df.dropna(subset=["percent_dependent_numeric", "specificity_delta_numeric"])

    if not scatter_df.empty:
        hover_cols = [
            c for c in [
                "dependency_label",
                "primary_contradiction_label",
                "therapeutic_relevance",
                "gene_role_category",
                "pathway_category",
            ] if c in scatter_df.columns
        ]

        fig = px.scatter(
            scatter_df,
            x="percent_dependent_numeric",
            y="specificity_delta_numeric",
            color="primary_contradiction_severity" if "primary_contradiction_severity" in scatter_df.columns else None,
            hover_name="gene",
            hover_data=hover_cols,
            title="Dependency strength versus lineage specificity",
        )
        fig.update_layout(
            xaxis_title="Percent dependent cell lines",
            yaxis_title="Specificity delta",
            height=460,
            margin=dict(l=20, r=20, t=60, b=20),
        )
        st.plotly_chart(apply_plotly_theme(fig), use_container_width=True)
    else:
        st.info("Dependency-specificity map unavailable because numeric values are missing.")
else:
    st.info("Dependency-specificity map unavailable because required columns are missing.")

st.subheader("Filtered Batch Audit Table")

display_df = filtered_df[summary_cols].copy()
display_df = display_df.astype(object).where(pd.notna(display_df), "Not available")

st.dataframe(display_df, use_container_width=True, hide_index=True)

st.subheader("Count Tables")

count_col1, count_col2 = st.columns(2)

with count_col1:
    coverage_counts = (
        filtered_df["evidence_coverage_label"]
        .fillna("Not available")
        .value_counts()
        .rename_axis("evidence_coverage_label")
        .reset_index(name="gene_count")
    ) if "evidence_coverage_label" in filtered_df.columns else pd.DataFrame()
    st.write("Coverage counts")
    st.dataframe(coverage_counts, use_container_width=True, hide_index=True)

with count_col2:
    pattern_counts = (
        filtered_df["batch_pattern"]
        .fillna("Not available")
        .value_counts()
        .rename_axis("batch_pattern")
        .reset_index(name="gene_count")
    ) if "batch_pattern" in filtered_df.columns else pd.DataFrame()
    st.write("Pattern counts")
    st.dataframe(pattern_counts, use_container_width=True, hide_index=True)

st.subheader("Download Batch Results")

full_csv = batch_df.to_csv(index=False)
filtered_csv = filtered_df.to_csv(index=False)

dl1, dl2 = st.columns(2)

with dl1:
    st.download_button(
        label="Download full batch audit CSV",
        data=full_csv,
        file_name=f"{active_cancer}_full_batch_audit.csv".replace(" ", "_"),
        mime="text/csv",
    )

with dl2:
    st.download_button(
        label="Download filtered batch audit CSV",
        data=filtered_csv,
        file_name=f"{active_cancer}_filtered_batch_audit.csv".replace(" ", "_"),
        mime="text/csv",
    )

st.subheader("Interpretation Guide")

st.write(
    "Use this page to identify genes that look promising in one layer but risky in another. "
    "Strong dependency with weak patient support may indicate a cell-line-only signal. "
    "Strong dependency with high common-essential caution may indicate broad essentiality rather than selective targetability. "
    "Therapeutic relevance without strong dependency may still support a biomarker or subgroup hypothesis. "
    "For final claims, use the single-gene page and full Markdown evidence report."
)
