"""
DepMap dependency module for OncoEvidence Auditor.

This module reads a small OncoEvidence-compatible dependency table.

Priority:
1. Real processed DepMap subset:
   data/depmap/depmap_dependency_subset.csv

2. Mock fallback table:
   data/depmap/mock_depmap_dependency.csv
"""

from pathlib import Path
from typing import Dict
import pandas as pd


REAL_DEPMAP_PATH = Path("data/depmap/depmap_dependency_subset.csv")
MOCK_DEPMAP_PATH = Path("data/depmap/mock_depmap_dependency.csv")


def get_active_depmap_path() -> Path:
    """
    Prefer real processed DepMap data if available.
    Otherwise fall back to the mock table.
    """
    if REAL_DEPMAP_PATH.exists():
        return REAL_DEPMAP_PATH
    return MOCK_DEPMAP_PATH


def load_depmap_table() -> pd.DataFrame:
    """Load active DepMap-style dependency data."""
    path = get_active_depmap_path()
    return pd.read_csv(path)


def get_depmap_data_source_label() -> str:
    """Return a user-facing label describing which data source is active."""
    if REAL_DEPMAP_PATH.exists():
        return "Real processed DepMap subset"
    return "Mock DepMap-style test table"


def get_dependency_result(gene: str, cancer_type: str) -> Dict:
    """
    Return dependency information for a gene/cancer pair.
    """
    df = load_depmap_table()

    match = df[
        (df["gene"].str.upper() == gene.upper())
        & (df["cancer_type"] == cancer_type)
    ]

    if match.empty:
        return {
            "available": False,
            "gene": gene,
            "cancer_type": cancer_type,
            "median_dependency_score": None,
            "dependent_cell_lines": None,
            "total_cell_lines": None,
            "percent_dependent": None,
            "dependency_label": "Not available",
            "dependency_note": "No dependency result found for this gene/cancer pair.",
            "data_source": get_depmap_data_source_label(),
        }

    row = match.iloc[0].to_dict()

    total = int(row["total_cell_lines"]) if pd.notna(row["total_cell_lines"]) else 0
    dependent = int(row["dependent_cell_lines"]) if pd.notna(row["dependent_cell_lines"]) else 0

    if pd.isna(row["median_dependency_score"]):
        score = None
    else:
        score = float(row["median_dependency_score"])

    percent = round((dependent / total) * 100, 1) if total else 0
    label = classify_dependency(score, percent)

    return {
        "available": True,
        "gene": row["gene"],
        "cancer_type": row["cancer_type"],
        "median_dependency_score": score,
        "dependent_cell_lines": dependent,
        "total_cell_lines": total,
        "percent_dependent": percent,
        "dependency_label": label,
        "dependency_note": row.get("dependency_note", row.get("note", "")),
        "note": row.get("note", row.get("dependency_note", "")),
        "data_source": get_depmap_data_source_label(),
    }


def classify_dependency(median_score, percent_dependent: float) -> str:
    """
    Classify dependency strength.

    More negative dependency scores indicate stronger loss of viability
    after gene perturbation in CRISPR-style screens.
    """
    if median_score is None:
        return "Not available"

    if median_score <= -0.75 and percent_dependent >= 60:
        return "Strong dependency"
    if median_score <= -0.50 and percent_dependent >= 40:
        return "Moderate dependency"
    if median_score <= -0.25 and percent_dependent >= 20:
        return "Weak/variable dependency"
    return "Little or no dependency"
