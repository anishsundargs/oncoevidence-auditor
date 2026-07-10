"""
Gene role annotation module for OncoEvidence Auditor.

This module provides lightweight biological role annotations for curated genes.
It is not intended to replace expert curation; it provides context for interpreting
dependency, alteration, expression, and survival evidence.
"""

from pathlib import Path
from typing import Dict
import pandas as pd


ROLE_PATH = Path("data/config/gene_role_annotations.csv")


def load_gene_roles(path: Path = ROLE_PATH) -> pd.DataFrame:
    """Load gene role annotation table."""
    return pd.read_csv(path)


def get_gene_role(gene: str) -> Dict:
    """Return role annotation for a gene."""
    gene = str(gene).strip().upper()

    if not ROLE_PATH.exists():
        return {
            "available": False,
            "gene": gene,
            "role_category": "Not available",
            "target_class": "Not available",
            "biological_process": "Not available",
            "interpretation_note": "Gene role annotation file not found.",
        }

    df = load_gene_roles()
    df["gene_upper"] = df["gene"].astype(str).str.upper()

    match = df[df["gene_upper"] == gene]

    if match.empty:
        return {
            "available": False,
            "gene": gene,
            "role_category": "Not available",
            "target_class": "Not available",
            "biological_process": "Not available",
            "interpretation_note": "No curated gene role annotation available for this gene.",
        }

    row = match.iloc[0].to_dict()

    return {
        "available": True,
        "gene": row.get("gene"),
        "role_category": row.get("role_category"),
        "target_class": row.get("target_class"),
        "biological_process": row.get("biological_process"),
        "interpretation_note": row.get("interpretation_note"),
    }


def classify_role_risk(gene_role_result: Dict, common_result: Dict = None) -> Dict:
    """
    Classify whether the biological role adds interpretive caution.
    """
    common_result = common_result or {}
    role_category = str(gene_role_result.get("role_category", ""))
    target_class = str(gene_role_result.get("target_class", ""))
    common_label = common_result.get("common_essential_label")

    role_text = f"{role_category} {target_class}".lower()

    if any(term in role_text for term in ["cell-cycle", "proliferation", "mitotic", "core cell-cycle"]):
        if common_label == "High common-essential caution":
            return {
                "role_risk_label": "Proliferation/common-essential caution",
                "role_risk_severity": "High",
                "role_risk_note": (
                    "The gene role is linked to proliferation or cell-cycle biology and the gene also has high "
                    "common-essential caution. Dependency evidence may reflect broad growth essentiality rather "
                    "than selective cancer vulnerability."
                ),
            }

        return {
            "role_risk_label": "Proliferation-linked interpretation caution",
            "role_risk_severity": "Moderate",
            "role_risk_note": (
                "The gene role is linked to proliferation or cell-cycle biology. Dependency and expression signals "
                "should be interpreted carefully because they may reflect tumor growth state."
            ),
        }

    if "tumor suppressor" in role_text:
        return {
            "role_risk_label": "Tumor-suppressor framing caution",
            "role_risk_severity": "Moderate",
            "role_risk_note": (
                "Tumor suppressors are often interpreted through loss-of-function or pathway disruption. "
                "Avoid framing them as simple overexpression or dependency targets without strong support."
            ),
        }

    if "receptor tyrosine kinase" in role_text:
        return {
            "role_risk_label": "Subgroup/actionability context important",
            "role_risk_severity": "Low",
            "role_risk_note": (
                "Receptor tyrosine kinase genes are often most meaningful in alteration- or expression-defined "
                "subgroups. Patient-level alteration/expression evidence should drive interpretation."
            ),
        }

    if any(term in role_text for term in ["secreted", "angiogenesis", "extracellular matrix", "invasion"]):
        return {
            "role_risk_label": "Microenvironment/pathway-context caution",
            "role_risk_severity": "Low",
            "role_risk_note": (
                "This role may involve tumor microenvironment, invasion, angiogenesis, or extracellular signaling. "
                "Tumor-cell dependency alone may not capture the main biology."
            ),
        }

    return {
        "role_risk_label": "No special role-based caution",
        "role_risk_severity": "Low",
        "role_risk_note": "No additional role-based caution was assigned by the current rule set.",
    }


def get_gene_role_summary(gene: str, common_result: Dict = None) -> Dict:
    """Return role annotation plus role-based caution."""
    role = get_gene_role(gene)
    risk = classify_role_risk(role, common_result)

    return {
        **role,
        **risk,
    }
