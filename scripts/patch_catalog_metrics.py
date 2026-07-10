from pathlib import Path

# 1. Create catalog summary helper
catalog_path = Path("src/catalog_summary.py")
catalog_path.write_text(
'''from pathlib import Path
from typing import Dict

import pandas as pd


MOCK_EVIDENCE_PATH = Path("data/mock_gene_evidence.csv")
CANCER_REGISTRY_PATH = Path("data/config/cancer_registry.csv")


def get_catalog_summary() -> Dict:
    """Return high-level summary metrics for the curated pan-cancer catalog."""

    if not MOCK_EVIDENCE_PATH.exists():
        return {
            "available": False,
            "note": f"Missing catalog file: {MOCK_EVIDENCE_PATH}",
        }

    evidence_df = pd.read_csv(MOCK_EVIDENCE_PATH)

    if evidence_df.empty:
        return {
            "available": False,
            "note": "Catalog file exists but is empty.",
        }

    unique_pairs = evidence_df.drop_duplicates(["gene", "cancer_type"])

    genes_per_cancer = (
        unique_pairs.groupby("cancer_type")["gene"]
        .nunique()
        .sort_values(ascending=False)
    )

    registry_count = None
    if CANCER_REGISTRY_PATH.exists():
        registry_df = pd.read_csv(CANCER_REGISTRY_PATH)
        registry_count = registry_df["cancer_type"].nunique()

    return {
        "available": True,
        "supported_cancer_types": int(registry_count or unique_pairs["cancer_type"].nunique()),
        "catalog_cancer_types": int(unique_pairs["cancer_type"].nunique()),
        "unique_genes": int(unique_pairs["gene"].nunique()),
        "gene_cancer_pairs": int(len(unique_pairs)),
        "median_genes_per_cancer": round(float(genes_per_cancer.median()), 1),
        "largest_cancer_panel": str(genes_per_cancer.index[0]),
        "largest_cancer_gene_count": int(genes_per_cancer.iloc[0]),
        "genes_per_cancer": genes_per_cancer.reset_index(name="gene_count"),
        "note": (
            "Catalog counts reflect curated hypothesis rows available for local triage. "
            "Live evidence coverage still depends on PubMed, cBioPortal, DepMap, and survival data availability."
        ),
    }
'''
)

# 2. Patch app.py import and display block
app_path = Path("app.py")
text = app_path.read_text()

import_line = "from src.catalog_summary import get_catalog_summary\n"
if import_line not in text:
    if "import streamlit as st\n" in text:
        text = text.replace("import streamlit as st\n", "import streamlit as st\n" + import_line)
    else:
        raise SystemExit("Could not find Streamlit import in app.py")

block = '''
catalog_summary = get_catalog_summary()

if catalog_summary.get("available"):
    st.markdown("### Pan-cancer catalog scale")

    cat_col1, cat_col2, cat_col3, cat_col4 = st.columns(4)

    with cat_col1:
        st.metric("Cancer types", catalog_summary["supported_cancer_types"])

    with cat_col2:
        st.metric("Unique genes", catalog_summary["unique_genes"])

    with cat_col3:
        st.metric("Gene-cancer hypotheses", catalog_summary["gene_cancer_pairs"])

    with cat_col4:
        st.metric("Median genes/cancer", catalog_summary["median_genes_per_cancer"])

    st.caption(catalog_summary["note"])

    with st.expander("Show catalog size by cancer type"):
        st.dataframe(
            catalog_summary["genes_per_cancer"],
            use_container_width=True,
            hide_index=True,
        )

    st.divider()
'''

if "Pan-cancer catalog scale" not in text:
    idx = text.find("st.title(")
    if idx == -1:
        raise SystemExit("Could not find st.title call in app.py")

    line_end = text.find("\n", idx)
    if line_end == -1:
        raise SystemExit("Could not find end of st.title line")

    text = text[:line_end + 1] + block + text[line_end + 1:]

app_path.write_text(text)

print("Catalog metrics patch complete.")