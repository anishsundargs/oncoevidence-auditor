"""
Batch audit module for OncoEvidence Auditor.

This module creates a fast, local batch summary for every gene in a selected
cancer type using currently processed/curated evidence layers.
"""

from pathlib import Path
from typing import Dict, List

import pandas as pd

from src.depmap_dependency import get_dependency_result
from src.common_essential import get_common_essential_result
from src.specificity_index import calculate_specificity_index
from src.auditor_verdict import build_auditor_verdict


EVIDENCE_PATH = Path("data/mock_gene_evidence.csv")


def load_gene_table() -> pd.DataFrame:
    """Load the app's curated gene/cancer evidence table."""
    if not EVIDENCE_PATH.exists():
        raise FileNotFoundError(f"Missing evidence table: {EVIDENCE_PATH}")

    return pd.read_csv(EVIDENCE_PATH)


def get_genes_for_cancer(cancer_type: str) -> pd.DataFrame:
    """Return curated gene rows for one cancer type."""
    df = load_gene_table()

    required = {"gene", "cancer_type"}
    missing = required - set(df.columns)

    if missing:
        raise ValueError(f"{EVIDENCE_PATH} missing required columns: {sorted(missing)}")

    out = df[df["cancer_type"] == cancer_type].copy()
    out = out.drop_duplicates(subset=["gene", "cancer_type"])

    return out


def pick_main_warning(verdict: Dict) -> str:
    """Return the first/highest-priority warning from a verdict."""
    warnings = verdict.get("warnings", [])

    if not warnings:
        return "No major warning reported."

    # Prioritize the most project-relevant warnings.
    priority_terms = [
        "common-essential",
        "lineage specificity",
        "patient-tumor alteration",
        "patient-tumor expression",
        "literature",
    ]

    for term in priority_terms:
        for warning in warnings:
            if term.lower() in warning.lower():
                return warning

    return warnings[0]


def classify_batch_pattern(
    dependency_label: str,
    common_label: str,
    specificity_label: str,
) -> str:
    """
    Assign a compact contradiction pattern for batch ranking.
    """
    dependency_label = dependency_label or ""
    common_label = common_label or ""
    specificity_label = specificity_label or ""

    if (
        dependency_label == "Strong dependency"
        and common_label == "High common-essential caution"
    ):
        return "Strong dependency + high common-essential risk"

    if (
        dependency_label == "Strong dependency"
        and specificity_label in {"Low lineage specificity", "Lower-than-background dependency"}
    ):
        return "Strong dependency + weak lineage specificity"

    if dependency_label == "Strong dependency":
        return "Strong dependency signal"

    if dependency_label == "Moderate dependency":
        return "Moderate dependency signal"

    if dependency_label == "Little or no dependency":
        return "Weak dependency signal"

    return "Data-limited"


def build_batch_audit(cancer_type: str) -> pd.DataFrame:
    """
    Build a batch audit table for all curated genes in a selected cancer type.
    """
    gene_rows = get_genes_for_cancer(cancer_type)

    results: List[Dict] = []

    for _, row in gene_rows.iterrows():
        gene = str(row["gene"]).strip()

        depmap_result = get_dependency_result(gene, cancer_type)
        common_result = get_common_essential_result(gene)
        specificity_result = calculate_specificity_index(depmap_result, common_result)

        # Fast/local batch mode does not call live PubMed or cBioPortal.
        verdict = build_auditor_verdict(
            gene=gene,
            cancer_type=cancer_type,
            pubmed_count=None,
            saturation_label=None,
            depmap_result=depmap_result,
            common_result=common_result,
            specificity_result=specificity_result,
            cbio_result=None,
            expression_result=None,
        )

        dependency_label = depmap_result.get("dependency_label")
        common_label = common_result.get("common_essential_label")
        specificity_label = specificity_result.get("specificity_label")

        results.append(
            {
                "gene": gene,
                "cancer_type": cancer_type,
                "curated_score": row.get("score"),
                "curated_tier": row.get("tier"),
                "dependency_label": dependency_label,
                "median_dependency_score": depmap_result.get("median_dependency_score"),
                "percent_dependent": depmap_result.get("percent_dependent"),
                "common_essential_caution": common_label,
                "pan_cancer_percent_dependent": common_result.get("pan_cancer_percent_dependent"),
                "specificity_label": specificity_label,
                "specificity_delta": specificity_result.get("specificity_delta"),
                "batch_pattern": classify_batch_pattern(
                    dependency_label,
                    common_label,
                    specificity_label,
                ),
                "auditor_verdict_tier": verdict.get("verdict_tier"),
                "claim_style": verdict.get("claim_style"),
                "main_warning": pick_main_warning(verdict),
                "safe_claim": verdict.get("safe_claim"),
            }
        )

    out = pd.DataFrame(results)

    # Useful sort: strongest dependency first, then highest contradiction risk.
    if not out.empty:
        out["_dependency_sort"] = out["percent_dependent"].fillna(-1)
        out["_specificity_sort"] = out["specificity_delta"].fillna(-999)
        out = out.sort_values(
            by=["_dependency_sort", "_specificity_sort"],
            ascending=[False, False],
        ).drop(columns=["_dependency_sort", "_specificity_sort"])

    return out
