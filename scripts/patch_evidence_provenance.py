from pathlib import Path


src_path = Path("src/evidence_provenance.py")
src_path.write_text(
'''from typing import List, Dict
import pandas as pd


EVIDENCE_PROVENANCE: List[Dict] = [
    {
        "evidence_layer": "PubMed literature saturation",
        "source": "NCBI PubMed / ESearch",
        "data_type": "Literature count",
        "supports": "How heavily studied a gene-cancer pair is.",
        "main_limitation": "High publication count does not prove biological importance; low count may reflect under-study rather than novelty.",
        "used_for": "Literature saturation, inferred novelty caution, claim framing.",
        "live_or_local": "Live API",
    },
    {
        "evidence_layer": "DepMap dependency",
        "source": "DepMap CRISPRGeneEffect subset",
        "data_type": "Cancer cell-line gene dependency",
        "supports": "Whether cancer models appear dependent on a gene after CRISPR perturbation.",
        "main_limitation": "Cell-line dependency does not prove patient-tumor relevance, clinical actionability, or immune/antigen relevance.",
        "used_for": "Dependency label, percent dependent, target-like signal.",
        "live_or_local": "Local processed data",
    },
    {
        "evidence_layer": "Common-essential caution",
        "source": "DepMap pan-cancer dependency summary",
        "data_type": "Pan-cancer dependency background",
        "supports": "Whether a gene may be broadly essential across many cancer models.",
        "main_limitation": "Broad dependency can indicate general viability/proliferation effects rather than selective cancer targeting.",
        "used_for": "Common-essential warning, broad-essentiality contradiction labels.",
        "live_or_local": "Local processed data",
    },
    {
        "evidence_layer": "Lineage specificity",
        "source": "Selected-cancer DepMap dependency compared with pan-cancer background",
        "data_type": "Relative dependency enrichment",
        "supports": "Whether dependency is stronger in the selected cancer type than across broader cancer models.",
        "main_limitation": "Specificity depends on available cell-line representation and OncoTree mapping.",
        "used_for": "Specificity delta, lineage specificity label.",
        "live_or_local": "Local computed layer",
    },
    {
        "evidence_layer": "Patient alteration evidence",
        "source": "cBioPortal TCGA / PanCancer Atlas studies",
        "data_type": "Mutation, amplification, deletion frequencies",
        "supports": "Whether patient tumors show genomic support for the gene-cancer hypothesis.",
        "main_limitation": "Alteration frequency does not prove functional dependency or therapeutic actionability.",
        "used_for": "Patient alteration support and alteration-driven contradiction labels.",
        "live_or_local": "Live API",
    },
    {
        "evidence_layer": "Patient expression evidence",
        "source": "cBioPortal mRNA expression z-score profiles",
        "data_type": "Patient tumor expression distribution",
        "supports": "Whether tumors show broad expression or a high-expression subgroup.",
        "main_limitation": "mRNA expression does not prove protein expression, surface localization, or functional dependency.",
        "used_for": "Expression support, subgroup expression flag, expression-defined subgroup labels.",
        "live_or_local": "Live API",
    },
    {
        "evidence_layer": "Survival/prognosis evidence",
        "source": "cBioPortal clinical survival records matched to expression groups",
        "data_type": "Descriptive survival comparison",
        "supports": "Whether high-expression tumors show a descriptive survival separation from other tumors.",
        "main_limitation": "Current analysis is descriptive and not a full Kaplan-Meier/log-rank/Cox clinical model.",
        "used_for": "Survival signal, Kaplan-Meier-style visualization, survival caution labels.",
        "live_or_local": "Live API",
    },
    {
        "evidence_layer": "Gene role classification",
        "source": "Local curated annotation table",
        "data_type": "Biological role category",
        "supports": "Whether the gene is an oncogene, tumor suppressor, DNA repair gene, surface antigen, lineage factor, etc.",
        "main_limitation": "Curated role labels simplify context-dependent biology and require manual review.",
        "used_for": "Role-based interpretation, role-supported caution labels.",
        "live_or_local": "Local curated data",
    },
    {
        "evidence_layer": "Pathway/function annotation",
        "source": "Local curated annotation table",
        "data_type": "Pathway and functional context",
        "supports": "Which biological pathway gives context to the gene-cancer hypothesis.",
        "main_limitation": "Pathway membership does not prove causality or selective targetability.",
        "used_for": "Pathway caution, validation suggestions, pathway-level framing.",
        "live_or_local": "Local curated data",
    },
    {
        "evidence_layer": "Therapeutic relevance annotation",
        "source": "Local curated therapeutic/context table",
        "data_type": "Biomarker or therapeutic-context annotation",
        "supports": "Whether a gene has known therapeutic, biomarker, antigen, pathway, or research-use context.",
        "main_limitation": "This is not a clinical recommendation and must not be interpreted as treatment guidance.",
        "used_for": "Therapeutic relevance, biomarker type, therapeutic-alignment contradiction labels.",
        "live_or_local": "Local curated data",
    },
]


def get_evidence_provenance_table() -> pd.DataFrame:
    """Return evidence provenance as a dataframe."""
    return pd.DataFrame(EVIDENCE_PROVENANCE)


def get_layer_limitations() -> Dict[str, str]:
    """Return a mapping from evidence layer to major limitation."""
    return {
        row["evidence_layer"]: row["main_limitation"]
        for row in EVIDENCE_PROVENANCE
    }
'''
)


page_path = Path("pages/5_Evidence_Provenance.py")
page_path.write_text(
'''import pandas as pd
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
'''
)


readiness_path = Path("scripts/project_readiness_check.py")
if readiness_path.exists():
    text = readiness_path.read_text()
    entry = '    "pages/5_Evidence_Provenance.py",\n'
    if entry not in text:
        anchor = '    "pages/4_Catalog_Explorer.py",\n'
        if anchor in text:
            text = text.replace(anchor, anchor + entry)
        else:
            anchor = '    "pages/3_Examples_and_Interpretation_Guide.py",\n'
            text = text.replace(anchor, anchor + entry)
        readiness_path.write_text(text)


readme_path = Path("README.md")
if readme_path.exists():
    readme = readme_path.read_text()
    section = """
## Evidence provenance

The app includes an Evidence Provenance page that documents every evidence layer, its source, data type, interpretation purpose, and main limitation. This is intended to make the tool's claims more transparent and prevent overinterpretation of any single evidence layer.
"""
    if "## Evidence provenance" not in readme:
        readme_path.write_text(readme.rstrip() + "\\n\\n" + section.strip() + "\\n")


print("Added Evidence Provenance page and helper module.")