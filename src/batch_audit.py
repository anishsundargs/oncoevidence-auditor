"""
Batch audit module for OncoEvidence Auditor.

This module creates a batch summary for every curated gene in a selected cancer type.

Default mode:
- fast/local
- uses curated evidence table, DepMap subset, common-essential flags, specificity index

Optional live mode:
- adds cBioPortal patient alteration evidence
- adds cBioPortal patient expression evidence
- slower because it queries cBioPortal for each gene
"""

from pathlib import Path
from typing import Dict, List

import pandas as pd

from src.depmap_dependency import get_dependency_result
from src.common_essential import get_common_essential_result
from src.specificity_index import calculate_specificity_index
from src.auditor_verdict import build_auditor_verdict
from src.cbioportal_alterations import get_cbioportal_alteration_summary
from src.cbioportal_expression import get_cbioportal_expression_summary


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

    priority_terms = [
        "patient-tumor alteration",
        "patient-tumor expression",
        "common-essential",
        "lineage specificity",
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
    patient_support: str = None,
    expression_support: str = None,
) -> str:
    """
    Assign a compact contradiction pattern for batch ranking.
    """
    dependency_label = dependency_label or ""
    common_label = common_label or ""
    specificity_label = specificity_label or ""
    patient_support = patient_support or ""
    expression_support = expression_support or ""

    if (
        dependency_label == "Strong dependency"
        and patient_support == "Little or no patient alteration support"
        and expression_support == "Little or no expression support"
    ):
        return "Strong dependency + weak patient support"

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


def safe_cbio_alteration(gene: str, cancer_type: str) -> Dict:
    """Safely call cBioPortal alteration module."""
    try:
        return get_cbioportal_alteration_summary(gene, cancer_type)
    except Exception as e:
        return {
            "available": False,
            "gene": gene,
            "cancer_type": cancer_type,
            "note": str(e),
        }


def safe_cbio_expression(gene: str, cancer_type: str) -> Dict:
    """Safely call cBioPortal expression module."""
    try:
        return get_cbioportal_expression_summary(gene, cancer_type)
    except Exception as e:
        return {
            "available": False,
            "gene": gene,
            "cancer_type": cancer_type,
            "note": str(e),
        }


def build_batch_audit(cancer_type: str, include_live_cbio: bool = False) -> pd.DataFrame:
    """
    Build a batch audit table for all curated genes in a selected cancer type.

    include_live_cbio=False keeps the batch fast/local.
    include_live_cbio=True adds live cBioPortal alteration/expression columns.
    """
    gene_rows = get_genes_for_cancer(cancer_type)

    results: List[Dict] = []

    for _, row in gene_rows.iterrows():
        gene = str(row["gene"]).strip()

        depmap_result = get_dependency_result(gene, cancer_type)
        common_result = get_common_essential_result(gene)
        specificity_result = calculate_specificity_index(depmap_result, common_result)

        cbio_result = None
        expression_result = None

        if include_live_cbio:
            cbio_result = safe_cbio_alteration(gene, cancer_type)
            expression_result = safe_cbio_expression(gene, cancer_type)

        verdict = build_auditor_verdict(
            gene=gene,
            cancer_type=cancer_type,
            pubmed_count=None,
            saturation_label=None,
            depmap_result=depmap_result,
            common_result=common_result,
            specificity_result=specificity_result,
            cbio_result=cbio_result,
            expression_result=expression_result,
        )

        dependency_label = depmap_result.get("dependency_label")
        common_label = common_result.get("common_essential_label")
        specificity_label = specificity_result.get("specificity_label")

        patient_support = None
        mutation_frequency = None
        amplification_frequency = None
        deep_deletion_frequency = None

        expression_support = None
        median_expression_zscore = None
        percent_high_expression = None

        if cbio_result:
            patient_support = cbio_result.get("patient_alteration_support")
            mutation_frequency = cbio_result.get("mutation_frequency")
            amplification_frequency = cbio_result.get("amplification_frequency")
            deep_deletion_frequency = cbio_result.get("deep_deletion_frequency")

        if expression_result:
            expression_support = expression_result.get("expression_support")
            median_expression_zscore = expression_result.get("median_expression_zscore")
            percent_high_expression = expression_result.get("percent_high_expression")

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
                "patient_alteration_support": patient_support,
                "mutation_frequency": mutation_frequency,
                "amplification_frequency": amplification_frequency,
                "deep_deletion_frequency": deep_deletion_frequency,
                "expression_support": expression_support,
                "median_expression_zscore": median_expression_zscore,
                "percent_high_expression": percent_high_expression,
                "batch_pattern": classify_batch_pattern(
                    dependency_label,
                    common_label,
                    specificity_label,
                    patient_support,
                    expression_support,
                ),
                "auditor_verdict_tier": verdict.get("verdict_tier"),
                "claim_style": verdict.get("claim_style"),
                "main_warning": pick_main_warning(verdict),
                "safe_claim": verdict.get("safe_claim"),
            }
        )

    out = pd.DataFrame(results)

    if not out.empty:
        out["_dependency_sort"] = out["percent_dependent"].fillna(-1)
        out["_specificity_sort"] = out["specificity_delta"].fillna(-999)
        out = out.sort_values(
            by=["_dependency_sort", "_specificity_sort"],
            ascending=[False, False],
        ).drop(columns=["_dependency_sort", "_specificity_sort"])

    return out
