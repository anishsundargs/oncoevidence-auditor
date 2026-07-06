"""
DepMap-style dependency module for OncoEvidence Auditor.

This starter version reads a small local dependency table.
Later, this module can be upgraded to use real DepMap public release files.
"""

from typing import Dict, Tuple
import pandas as pd


DEPMAP_MOCK_PATH = "data/depmap/mock_depmap_dependency.csv"


def load_depmap_table(path: str = DEPMAP_MOCK_PATH) -> pd.DataFrame:
    """Load local DepMap-style dependency data."""
    return pd.read_csv(path)


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
            "dependency_note": "No dependency result found for this gene/cancer pair."
        }

    row = match.iloc[0].to_dict()

    dependent = int(row["dependent_cell_lines"])
    total = int(row["total_cell_lines"])
    percent = round((dependent / total) * 100, 1) if total else 0

    score = float(row["median_dependency_score"])
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
        "dependency_note": row["dependency_note"]
    }


def classify_dependency(median_score: float, percent_dependent: float) -> str:
    """
    Classify dependency strength.

    More negative dependency scores indicate stronger loss of viability
    after gene perturbation in CRISPR-style screens.
    """
    if median_score <= -0.75 and percent_dependent >= 60:
        return "Strong dependency"
    if median_score <= -0.50 and percent_dependent >= 40:
        return "Moderate dependency"
    if median_score <= -0.25 and percent_dependent >= 20:
        return "Weak/variable dependency"
    return "Little or no dependency"
