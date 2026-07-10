"""
Pathway/function annotation module for OncoEvidence Auditor.

This module provides curated pathway/function context for interpreting cancer-gene
evidence layers. It is intentionally lightweight and transparent: annotations are
stored in a local CSV so they can be reviewed, edited, and expanded.
"""

from pathlib import Path
from typing import Dict
import pandas as pd


PATHWAY_PATH = Path("data/config/pathway_function_annotations.csv")


def load_pathway_annotations(path: Path = PATHWAY_PATH) -> pd.DataFrame:
    """Load curated pathway/function annotations."""
    return pd.read_csv(path)


def get_pathway_function(gene: str) -> Dict:
    """Return pathway/function annotation for one gene."""
    gene = str(gene).strip().upper()

    if not PATHWAY_PATH.exists():
        return {
            "available": False,
            "gene": gene,
            "pathway_category": "Not available",
            "function_group": "Not available",
            "pathway_process": "Not available",
            "interpretive_use": "Pathway/function annotation file not found.",
            "validation_suggestions": "Not available",
        }

    df = load_pathway_annotations()
    df["gene_upper"] = df["gene"].astype(str).str.upper()

    match = df[df["gene_upper"] == gene]

    if match.empty:
        return {
            "available": False,
            "gene": gene,
            "pathway_category": "Not available",
            "function_group": "Not available",
            "pathway_process": "Not available",
            "interpretive_use": "No curated pathway/function annotation available for this gene.",
            "validation_suggestions": "Add this gene to data/config/pathway_function_annotations.csv for pathway-aware interpretation.",
        }

    row = match.iloc[0].to_dict()

    return {
        "available": True,
        "gene": row.get("gene"),
        "pathway_category": row.get("pathway_category"),
        "function_group": row.get("function_group"),
        "pathway_process": row.get("pathway_process"),
        "interpretive_use": row.get("interpretive_use"),
        "validation_suggestions": row.get("validation_suggestions"),
    }


def classify_pathway_caution(pathway_result: Dict, common_result: Dict = None) -> Dict:
    """
    Add a pathway-level caution label based on pathway category and common-essential evidence.
    """
    common_result = common_result or {}

    pathway_category = str(pathway_result.get("pathway_category", ""))
    function_group = str(pathway_result.get("function_group", ""))
    process = str(pathway_result.get("pathway_process", ""))
    common_label = common_result.get("common_essential_label")

    text = f"{pathway_category} {function_group} {process}".lower()

    if any(term in text for term in ["cell cycle", "mitosis", "proliferation", "dna replication"]):
        if common_label == "High common-essential caution":
            return {
                "pathway_caution_label": "Pathway-supported common-essential caution",
                "pathway_caution_severity": "High",
                "pathway_caution_note": (
                    "The gene is annotated to a proliferation, replication, or mitotic pathway and also has high "
                    "common-essential caution. This strengthens the interpretation that dependency may reflect broad "
                    "growth biology rather than a selective cancer vulnerability."
                ),
            }

        return {
            "pathway_caution_label": "Proliferation-pathway interpretation caution",
            "pathway_caution_severity": "Moderate",
            "pathway_caution_note": (
                "The gene is annotated to a proliferation, replication, or mitotic pathway. Dependency and expression "
                "signals should be interpreted against tumor growth state and pan-essential controls."
            ),
        }

    if any(term in text for term in ["rtk", "growth factor receptor", "mapk", "pi3k", "ras"]):
        return {
            "pathway_caution_label": "Signaling-subgroup interpretation",
            "pathway_caution_severity": "Low",
            "pathway_caution_note": (
                "The gene is annotated to oncogenic signaling. Interpretation should emphasize alteration/expression "
                "subgroups, downstream pathway activation, and drug-response context."
            ),
        }

    if any(term in text for term in ["p53", "tumor suppressor"]):
        return {
            "pathway_caution_label": "Tumor-suppressor pathway framing caution",
            "pathway_caution_severity": "Moderate",
            "pathway_caution_note": (
                "The gene is annotated to tumor-suppressor or p53 pathway biology. Interpretation should emphasize "
                "loss-of-function, pathway disruption, and context rather than simple target dependency."
            ),
        }

    if any(term in text for term in ["dna repair", "dna damage"]):
        return {
            "pathway_caution_label": "DNA-repair/pathway-context interpretation",
            "pathway_caution_severity": "Low",
            "pathway_caution_note": (
                "The gene is annotated to DNA repair or DNA damage biology. Interpretation should include pathway state, "
                "therapy-response context, and mutation/expression mechanisms."
            ),
        }

    if any(term in text for term in ["angiogenesis", "ecm", "invasion", "microenvironment", "extracellular"]):
        return {
            "pathway_caution_label": "Microenvironment/pathway-context interpretation",
            "pathway_caution_severity": "Low",
            "pathway_caution_note": (
                "The gene is annotated to angiogenesis, invasion, ECM remodeling, or microenvironmental biology. "
                "Tumor-cell dependency alone may not capture the main mechanism."
            ),
        }

    if any(term in text for term in ["lineage", "epithelial", "differentiation"]):
        return {
            "pathway_caution_label": "Lineage/subtype interpretation",
            "pathway_caution_severity": "Low",
            "pathway_caution_note": (
                "The gene is annotated to lineage, epithelial, or differentiation biology. Interpretation should focus "
                "on subtype enrichment and patient-tumor expression/protein evidence."
            ),
        }

    return {
        "pathway_caution_label": "No special pathway caution",
        "pathway_caution_severity": "Low",
        "pathway_caution_note": "No additional pathway-based caution was assigned by the current rule set.",
    }


def get_pathway_function_summary(gene: str, common_result: Dict = None) -> Dict:
    """Return pathway annotation plus pathway-level caution."""
    pathway = get_pathway_function(gene)
    caution = classify_pathway_caution(pathway, common_result)

    return {
        **pathway,
        **caution,
    }
