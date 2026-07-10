import pandas as pd
import plotly.express as px
import streamlit as st

from src.evidence_provenance import get_evidence_provenance_table


st.set_page_config(
    page_title="Evidence Provenance | OncoEvidence Auditor",
    page_icon="🧾",
    layout="wide",
)

st.title("Evidence Source / Provenance")

st.caption(
    "A transparent map of where each evidence layer comes from, what it supports, and what it cannot prove."
)

st.warning(
    "Research-use only. Provenance information is meant to prevent overclaiming and does not provide clinical guidance."
)

df = get_evidence_provenance_table()

st.markdown("### Evidence provenance table")

st.dataframe(df, use_container_width=True, hide_index=True)

st.download_button(
    label="Download evidence provenance CSV",
    data=df.to_csv(index=False),
    file_name="oncoevidence_evidence_provenance.csv",
    mime="text/csv",
)

st.divider()

st.markdown("### Source composition")

col1, col2 = st.columns(2)

with col1:
    source_counts = (
        df["live_or_local"]
        .value_counts()
        .rename_axis("source_type")
        .reset_index(name="layer_count")
    )

    fig = px.bar(
        source_counts,
        x="layer_count",
        y="source_type",
        orientation="h",
        title="Live vs local evidence layers",
    )
    fig.update_layout(height=340, margin=dict(l=20, r=20, t=60, b=20))
    st.plotly_chart(fig, use_container_width=True)

with col2:
    data_type_counts = (
        df["data_type"]
        .value_counts()
        .rename_axis("data_type")
        .reset_index(name="layer_count")
    )

    fig = px.bar(
        data_type_counts,
        x="layer_count",
        y="data_type",
        orientation="h",
        title="Evidence layer data types",
    )
    fig.update_layout(
        height=max(340, 80 + 35 * len(data_type_counts)),
        margin=dict(l=20, r=20, t=60, b=20),
        yaxis=dict(autorange="reversed"),
    )
    st.plotly_chart(fig, use_container_width=True)

st.divider()

st.markdown("### Why provenance matters")

st.write(
    "The central point of OncoEvidence Auditor is that different evidence layers answer different questions. "
    "A CRISPR dependency signal is not the same as patient alteration support. A therapeutic biomarker can matter even "
    "when DepMap dependency is weak. A high expression subgroup does not automatically prove protein-level antigen expression. "
    "This page makes those boundaries explicit."
)

st.markdown("### Layer-by-layer limitation summary")

for _, row in df.iterrows():
    with st.expander(row["evidence_layer"]):
        st.markdown("**Source**")
        st.write(row["source"])

        st.markdown("**What this layer supports**")
        st.write(row["supports"])

        st.markdown("**Main limitation**")
        st.warning(row["main_limitation"])

        st.markdown("**Used for**")
        st.write(row["used_for"])
