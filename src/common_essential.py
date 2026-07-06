"""
Common-essential / specificity caution module for OncoEvidence Auditor.

This module reads pan-cancer dependency summaries generated from DepMap CRISPRGeneEffect.
It helps distinguish cancer-lineage dependency from broad essentiality.
"""

from pathlib import Path
from typing import Dict
import pandas as pd


COMMON_ESSENTIAL_PATH = Path("data/depmap/common_essential_flags.csv")


def load_common_essential_table() -> pd.DataFrame:
    """Load common-essential flags table."""
    return pd.read_csv(COMMON_ESSENTIAL_PATH)


def get_common_essential_result(gene: str) -> Dict:
    """
    Return pan-cancer dependency/common-essential information for a gene.
    """
    if not COMMON_ESSENTIAL_PATH.exists():
        return {
            "available": False,
            "gene": gene,
            "pan_cancer_median_dependency_score": None,
            "pan_cancer_dependent_cell_lines": None,
            "pan_cancer_total_cell_lines": None,
            "pan_cancer_percent_dependent": None,
            "common_essential_label": "Not available",
            "common_essential_note": "Common-essential table has not been generated yet."
        }

    df = load_common_essential_table()

    match = df[df["gene"].str.upper() == gene.upper()]

    if match.empty:
        return {
            "available": False,
            "gene": gene,
            "pan_cancer_median_dependency_score": None,
            "pan_cancer_dependent_cell_lines": None,
            "pan_cancer_total_cell_lines": None,
            "pan_cancer_percent_dependent": None,
            "common_essential_label": "Not available",
            "common_essential_note": f"No common-essential result found for {gene}."
        }

    row = match.iloc[0].to_dict()

    return {
        "available": True,
        "gene": row["gene"],
        "pan_cancer_median_dependency_score": row["pan_cancer_median_dependency_score"],
        "pan_cancer_dependent_cell_lines": int(row["pan_cancer_dependent_cell_lines"]),
        "pan_cancer_total_cell_lines": int(row["pan_cancer_total_cell_lines"]),
        "pan_cancer_percent_dependent": row["pan_cancer_percent_dependent"],
        "common_essential_label": row["common_essential_label"],
        "common_essential_note": row["common_essential_note"]
    }
