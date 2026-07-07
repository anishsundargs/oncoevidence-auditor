"""
Evidence coverage utilities for OncoEvidence Auditor.

Coverage score answers:
How many major evidence layers are available for this gene/cancer analysis?
"""

from typing import Dict, Optional


def _has_value(value) -> bool:
    """Return True if a value is meaningfully present."""
    if value is None:
        return False

    if value == "":
        return False

    if value == "Not available":
        return False

    return True


def calculate_evidence_coverage(
    pubmed_count: Optional[int] = None,
    depmap_result: Optional[Dict] = None,
    common_result: Optional[Dict] = None,
    specificity_result: Optional[Dict] = None,
    cbio_result: Optional[Dict] = None,
    expression_result: Optional[Dict] = None,
) -> Dict:
    """
    Calculate evidence coverage across the main evidence layers.
    """
    depmap_result = depmap_result or {}
    common_result = common_result or {}
    specificity_result = specificity_result or {}
    cbio_result = cbio_result or {}
    expression_result = expression_result or {}

    layers = {
        "PubMed literature": pubmed_count is not None,
        "DepMap dependency": bool(depmap_result.get("available")) and _has_value(depmap_result.get("dependency_label")),
        "Common-essential caution": _has_value(common_result.get("common_essential_label")),
        "Lineage specificity": _has_value(specificity_result.get("specificity_label")),
        "Patient alteration": bool(cbio_result.get("available")) and _has_value(cbio_result.get("patient_alteration_support")),
        "Patient expression": bool(expression_result.get("available")) and _has_value(expression_result.get("expression_support")),
    }

    available_layers = [name for name, available in layers.items() if available]
    missing_layers = [name for name, available in layers.items() if not available]

    available_count = len(available_layers)
    possible_count = len(layers)
    coverage_percent = round((available_count / possible_count) * 100, 1)

    if coverage_percent >= 90:
        label = "Complete evidence profile"
    elif coverage_percent >= 65:
        label = "Strong evidence coverage"
    elif coverage_percent >= 40:
        label = "Partial evidence coverage"
    else:
        label = "Limited evidence coverage"

    return {
        "available_layers": available_layers,
        "missing_layers": missing_layers,
        "evidence_layers_available": available_count,
        "evidence_layers_possible": possible_count,
        "evidence_coverage_percent": coverage_percent,
        "evidence_coverage_label": label,
    }
