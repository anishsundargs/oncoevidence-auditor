"""
Therapeutic relevance annotation module for OncoEvidence Auditor.

This module does not provide clinical recommendations. It flags whether a gene/cancer
pair has curated therapeutic or biomarker relevance and explains how that should be
kept separate from dependency evidence.
"""

from pathlib import Path
from typing import Dict
import pandas as pd


THERAPEUTIC_PATH = Path("data/config/therapeutic_relevance_annotations.csv")


def load_therapeutic_annotations(path: Path = THERAPEUTIC_PATH) -> pd.DataFrame:
    """Load curated therapeutic relevance annotations."""
    return pd.read_csv(path)


def get_therapeutic_relevance(gene: str, cancer_type: str) -> Dict:
    """Return therapeutic relevance annotation for one gene/cancer pair."""
    gene = str(gene).strip().upper()
    cancer_type = str(cancer_type).strip()

    if not THERAPEUTIC_PATH.exists():
        return {
            "available": False,
            "gene": gene,
            "cancer_type": cancer_type,
            "therapeutic_relevance": "Not available",
            "therapeutic_context": "Therapeutic relevance annotation file not found.",
            "biomarker_type": "Not available",
            "dependency_interpretation": "Not available",
            "therapeutic_caution": "Not available",
            "validation_suggestions": "Not available",
        }

    df = load_therapeutic_annotations()
    df["gene_upper"] = df["gene"].astype(str).str.upper()
    df["cancer_lower"] = df["cancer_type"].astype(str).str.lower()

    match = df[
        (df["gene_upper"] == gene)
        & (df["cancer_lower"] == cancer_type.lower())
    ]

    if match.empty:
        gene_only = df[df["gene_upper"] == gene]
        if not gene_only.empty:
            row = gene_only.iloc[0].to_dict()
            return {
                "available": False,
                "gene": gene,
                "cancer_type": cancer_type,
                "therapeutic_relevance": "Gene-level context only",
                "therapeutic_context": (
                    f"No curated {cancer_type}-specific therapeutic annotation is available for {gene}. "
                    f"Gene-level context from {row.get('cancer_type')}: {row.get('therapeutic_context')}"
                ),
                "biomarker_type": row.get("biomarker_type"),
                "dependency_interpretation": row.get("dependency_interpretation"),
                "therapeutic_caution": (
                    "Treat this as gene-level context only, not disease-specific therapeutic evidence."
                ),
                "validation_suggestions": row.get("validation_suggestions"),
            }

        return {
            "available": False,
            "gene": gene,
            "cancer_type": cancer_type,
            "therapeutic_relevance": "Not available",
            "therapeutic_context": "No curated therapeutic relevance annotation available for this gene/cancer pair.",
            "biomarker_type": "Not available",
            "dependency_interpretation": "Not available",
            "therapeutic_caution": "Do not make therapeutic relevance claims without external disease-specific evidence.",
            "validation_suggestions": "Add this gene/cancer pair to data/config/therapeutic_relevance_annotations.csv after curation.",
        }

    row = match.iloc[0].to_dict()

    return {
        "available": True,
        "gene": row.get("gene"),
        "cancer_type": row.get("cancer_type"),
        "therapeutic_relevance": row.get("therapeutic_relevance"),
        "therapeutic_context": row.get("therapeutic_context"),
        "biomarker_type": row.get("biomarker_type"),
        "dependency_interpretation": row.get("dependency_interpretation"),
        "therapeutic_caution": row.get("therapeutic_caution"),
        "validation_suggestions": row.get("validation_suggestions"),
    }


def classify_therapeutic_dependency_alignment(
    therapeutic_result: Dict,
    depmap_result: Dict = None,
    cbio_result: Dict = None,
    expression_result: Dict = None,
) -> Dict:
    """
    Classify whether therapeutic relevance aligns or conflicts with dependency evidence.
    """
    depmap_result = depmap_result or {}
    cbio_result = cbio_result or {}
    expression_result = expression_result or {}

    relevance = therapeutic_result.get("therapeutic_relevance")
    dep_label = depmap_result.get("dependency_label")
    patient_support = cbio_result.get("patient_alteration_support")
    expression_support = expression_result.get("expression_support")

    if relevance in {"High therapeutic relevance", "High therapeutic biomarker relevance", "High predictive biomarker relevance"}:
        if dep_label in {"Little or no dependency", "Moderate dependency"}:
            return {
                "therapeutic_alignment_label": "Therapeutic relevance without strong dependency",
                "therapeutic_alignment_severity": "Moderate",
                "therapeutic_alignment_note": (
                    "This gene/cancer pair has curated therapeutic or biomarker relevance, but the current DepMap "
                    "dependency signal is not strong. This should be framed as biomarker/subgroup relevance rather "
                    "than cell-autonomous dependency evidence."
                ),
            }

        if dep_label == "Strong dependency":
            return {
                "therapeutic_alignment_label": "Therapeutic relevance with dependency support",
                "therapeutic_alignment_severity": "Low",
                "therapeutic_alignment_note": (
                    "This gene/cancer pair has curated therapeutic or biomarker relevance and also shows dependency "
                    "support. Interpret carefully using specificity, common-essential, and patient evidence layers."
                ),
            }

        return {
            "therapeutic_alignment_label": "Therapeutic relevance with missing dependency context",
            "therapeutic_alignment_severity": "Moderate",
            "therapeutic_alignment_note": (
                "Therapeutic or biomarker relevance is curated, but dependency context is missing or unavailable."
            ),
        }

    if relevance in {"Moderate therapeutic relevance", "Exploratory therapeutic relevance"}:
        if patient_support in {"High patient alteration support", "Moderate patient alteration support"} or expression_support in {
            "Subgroup high-expression support",
            "Moderate expression support",
            "High broad expression support",
        }:
            return {
                "therapeutic_alignment_label": "Exploratory therapeutic subgroup signal",
                "therapeutic_alignment_severity": "Low",
                "therapeutic_alignment_note": (
                    "Therapeutic relevance is exploratory or moderate, but patient alteration/expression evidence may support "
                    "a subgroup hypothesis."
                ),
            }

        return {
            "therapeutic_alignment_label": "Exploratory therapeutic context",
            "therapeutic_alignment_severity": "Low",
            "therapeutic_alignment_note": (
                "Therapeutic relevance is exploratory or pathway-contextual and should not be treated as actionability."
            ),
        }

    if relevance in {"Low direct therapeutic relevance", "Low/uncertain therapeutic relevance"}:
        if dep_label == "Strong dependency":
            return {
                "therapeutic_alignment_label": "Dependency without therapeutic actionability",
                "therapeutic_alignment_severity": "High",
                "therapeutic_alignment_note": (
                    "The gene shows dependency evidence but has low or uncertain curated therapeutic relevance. "
                    "Do not equate dependency with druggability or clinical actionability."
                ),
            }

        return {
            "therapeutic_alignment_label": "Low therapeutic relevance",
            "therapeutic_alignment_severity": "Low",
            "therapeutic_alignment_note": (
                "No strong curated therapeutic relevance is available in the current annotation layer."
            ),
        }

    return {
        "therapeutic_alignment_label": "Therapeutic relevance not curated",
        "therapeutic_alignment_severity": "Low",
        "therapeutic_alignment_note": (
            "No curated therapeutic relevance alignment was assigned by the current rule set."
        ),
    }


def get_therapeutic_relevance_summary(
    gene: str,
    cancer_type: str,
    depmap_result: Dict = None,
    cbio_result: Dict = None,
    expression_result: Dict = None,
) -> Dict:
    """Return therapeutic annotation plus dependency-alignment interpretation."""
    therapeutic = get_therapeutic_relevance(gene, cancer_type)
    alignment = classify_therapeutic_dependency_alignment(
        therapeutic,
        depmap_result=depmap_result,
        cbio_result=cbio_result,
        expression_result=expression_result,
    )

    return {
        **therapeutic,
        **alignment,
    }
