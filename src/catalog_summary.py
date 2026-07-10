from pathlib import Path
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
