import pandas as pd
import plotly.express as px
import streamlit as st


MOCK_PATH = "data/mock_gene_evidence.csv"
ROLE_PATH = "data/config/gene_role_annotations.csv"
PATHWAY_PATH = "data/config/pathway_function_annotations.csv"
THER_PATH = "data/config/therapeutic_relevance_annotations.csv"


st.set_page_config(
    page_title="Catalog Explorer | OncoEvidence Auditor",
    page_icon="🧭",
    layout="wide",
)

st.title("Pan-Cancer Catalog Explorer")

st.caption(
    "Browse the curated gene-cancer hypothesis catalog without running live evidence queries."
)

st.warning(
    "Research-use only. Catalog inclusion means a gene-cancer pair is available for hypothesis triage; "
    "it does not imply clinical actionability or experimental validation."
)


@st.cache_data(show_spinner=False)
def load_catalog():
    mock_df = pd.read_csv(MOCK_PATH)
    role_df = pd.read_csv(ROLE_PATH)
    pathway_df = pd.read_csv(PATHWAY_PATH)
    therapeutic_df = pd.read_csv(THER_PATH)

    catalog = mock_df.drop_duplicates(["gene", "cancer_type"]).copy()

    role_cols = [
        "gene",
        "role_category",
        "target_class",
        "biological_process",
        "interpretation_note",
    ]

    pathway_cols = [
        "gene",
        "pathway_category",
        "function_group",
        "pathway_process",
        "interpretive_use",
        "validation_suggestions",
    ]

    therapeutic_cols = [
        "gene",
        "cancer_type",
        "therapeutic_relevance",
        "therapeutic_context",
        "biomarker_type",
        "dependency_interpretation",
        "therapeutic_caution",
    ]

    catalog = catalog.merge(
        role_df[[c for c in role_cols if c in role_df.columns]].drop_duplicates("gene"),
        on="gene",
        how="left",
    )

    catalog = catalog.merge(
        pathway_df[[c for c in pathway_cols if c in pathway_df.columns]].drop_duplicates("gene"),
        on="gene",
        how="left",
    )

    catalog = catalog.merge(
        therapeutic_df[[c for c in therapeutic_cols if c in therapeutic_df.columns]].drop_duplicates(["gene", "cancer_type"]),
        on=["gene", "cancer_type"],
        how="left",
    )

    return catalog


def options_for(df, column):
    if column not in df.columns:
        return []
    return sorted(df[column].fillna("Not available").astype(str).unique().tolist())


def apply_multiselect_filter(df, column, selected):
    if column not in df.columns or not selected:
        return df
    return df[df[column].fillna("Not available").astype(str).isin(selected)]


def count_chart(df, column, title, height_base=320):
    if column not in df.columns or df.empty:
        return None

    chart_df = (
        df[column]
        .fillna("Not available")
        .astype(str)
        .value_counts()
        .rename_axis(column)
        .reset_index(name="count")
    )

    if chart_df.empty:
        return None

    fig = px.bar(
        chart_df,
        x="count",
        y=column,
        orientation="h",
        title=title,
    )

    fig.update_layout(
        height=max(height_base, min(800, 90 + 32 * len(chart_df))),
        margin=dict(l=20, r=20, t=60, b=20),
        yaxis=dict(autorange="reversed"),
    )

    return fig


catalog = load_catalog()

if catalog.empty:
    st.error("Catalog is empty or unavailable.")
    st.stop()

unique_pairs = catalog.drop_duplicates(["gene", "cancer_type"])

st.markdown("### Catalog scale")

m1, m2, m3, m4 = st.columns(4)

with m1:
    st.metric("Cancer types", unique_pairs["cancer_type"].nunique())

with m2:
    st.metric("Unique genes", unique_pairs["gene"].nunique())

with m3:
    st.metric("Gene-cancer hypotheses", len(unique_pairs))

with m4:
    genes_per_cancer = unique_pairs.groupby("cancer_type")["gene"].nunique()
    st.metric("Median genes/cancer", round(float(genes_per_cancer.median()), 1))

st.divider()

st.subheader("Search and filters")

search_query = st.text_input(
    "Search gene, cancer, role, pathway, therapeutic context, or notes",
    value="",
)

f1, f2, f3 = st.columns(3)

with f1:
    selected_cancers = st.multiselect(
        "Cancer type",
        options_for(catalog, "cancer_type"),
        default=[],
        help="Leave empty to include all cancers.",
    )

with f2:
    selected_roles = st.multiselect(
        "Gene role category",
        options_for(catalog, "role_category"),
        default=[],
        help="Leave empty to include all roles.",
    )

with f3:
    selected_pathways = st.multiselect(
        "Pathway category",
        options_for(catalog, "pathway_category"),
        default=[],
        help="Leave empty to include all pathways.",
    )

f4, f5, f6 = st.columns(3)

with f4:
    selected_therapeutic = st.multiselect(
        "Therapeutic relevance",
        options_for(catalog, "therapeutic_relevance"),
        default=[],
        help="Leave empty to include all therapeutic relevance categories.",
    )

with f5:
    selected_dependency = st.multiselect(
        "Curated dependency context",
        options_for(catalog, "depmap_dependency"),
        default=[],
        help="Leave empty to include all dependency contexts.",
    )

with f6:
    selected_safety = st.multiselect(
        "Curated safety context",
        options_for(catalog, "normal_tissue_safety"),
        default=[],
        help="Leave empty to include all safety contexts.",
    )

filtered = catalog.copy()

filtered = apply_multiselect_filter(filtered, "cancer_type", selected_cancers)
filtered = apply_multiselect_filter(filtered, "role_category", selected_roles)
filtered = apply_multiselect_filter(filtered, "pathway_category", selected_pathways)
filtered = apply_multiselect_filter(filtered, "therapeutic_relevance", selected_therapeutic)
filtered = apply_multiselect_filter(filtered, "depmap_dependency", selected_dependency)
filtered = apply_multiselect_filter(filtered, "normal_tissue_safety", selected_safety)

if search_query.strip():
    q = search_query.strip().lower()
    search_cols = [
        "gene",
        "cancer_type",
        "role_category",
        "target_class",
        "biological_process",
        "pathway_category",
        "function_group",
        "therapeutic_relevance",
        "therapeutic_context",
        "biomarker_type",
        "notes",
    ]
    search_cols = [c for c in search_cols if c in filtered.columns]

    mask = pd.Series(False, index=filtered.index)

    for col in search_cols:
        mask = mask | filtered[col].fillna("").astype(str).str.lower().str.contains(q, regex=False)

    filtered = filtered[mask]

st.markdown("### Filtered catalog summary")

s1, s2, s3, s4 = st.columns(4)

with s1:
    st.metric("Rows shown", f"{len(filtered)}/{len(catalog)}")

with s2:
    st.metric("Filtered cancers", filtered["cancer_type"].nunique() if not filtered.empty else 0)

with s3:
    st.metric("Filtered genes", filtered["gene"].nunique() if not filtered.empty else 0)

with s4:
    high_ther_count = 0
    if "therapeutic_relevance" in filtered.columns and not filtered.empty:
        high_ther_count = int(
            filtered["therapeutic_relevance"]
            .fillna("")
            .astype(str)
            .str.contains("High", case=False)
            .sum()
        )
    st.metric("High therapeutic rows", high_ther_count)

st.divider()

st.subheader("Catalog visualizations")

chart1, chart2 = st.columns(2)

with chart1:
    fig = count_chart(filtered, "cancer_type", "Gene-cancer rows by cancer type", height_base=420)
    if fig is not None:
        st.plotly_chart(fig, use_container_width=True)

with chart2:
    fig = count_chart(filtered, "role_category", "Gene role distribution", height_base=420)
    if fig is not None:
        st.plotly_chart(fig, use_container_width=True)

chart3, chart4 = st.columns(2)

with chart3:
    fig = count_chart(filtered, "pathway_category", "Pathway category distribution", height_base=420)
    if fig is not None:
        st.plotly_chart(fig, use_container_width=True)

with chart4:
    fig = count_chart(filtered, "therapeutic_relevance", "Therapeutic relevance distribution", height_base=420)
    if fig is not None:
        st.plotly_chart(fig, use_container_width=True)

st.divider()

st.subheader("Catalog table")

display_cols = [
    "gene",
    "cancer_type",
    "role_category",
    "target_class",
    "pathway_category",
    "function_group",
    "therapeutic_relevance",
    "biomarker_type",
    "depmap_dependency",
    "normal_tissue_safety",
    "mutation_cna_support",
    "novelty_score",
    "notes",
]

display_cols = [c for c in display_cols if c in filtered.columns]

display_df = filtered[display_cols].copy()
display_df = display_df.astype(object).where(pd.notna(display_df), "Not available")

st.dataframe(display_df, use_container_width=True, hide_index=True)

st.download_button(
    label="Download filtered catalog CSV",
    data=filtered.to_csv(index=False),
    file_name="filtered_oncoevidence_catalog.csv",
    mime="text/csv",
)

st.divider()

st.subheader("How to use this page")

st.write(
    "Use the Catalog Explorer to find gene-cancer hypotheses worth auditing. "
    "After selecting an interesting pair, go to the main OncoEvidence Auditor page for a single-gene report "
    "or use Batch Audit to triage a full cancer panel."
)
