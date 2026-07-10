"""
Evidence coverage scoring for OncoEvidence Auditor.

This module tracks which evidence layers are available for a gene/cancer audit.
It measures evidence completeness, not evidence quality.
"""


def _is_available_dict(result):
    """Generic availability check for result dictionaries."""
    if not result:
        return False

    if result.get("available") is False:
        return False

    return True


def _pubmed_available(pubmed_count):
    return pubmed_count is not None


def _depmap_available(depmap_result):
    if not _is_available_dict(depmap_result):
        return False
    return depmap_result.get("dependency_label") not in {None, "Not available"}


def _common_essential_available(common_result):
    if not _is_available_dict(common_result):
        return False
    return common_result.get("common_essential_label") not in {None, "Not available"}


def _specificity_available(specificity_result):
    if not _is_available_dict(specificity_result):
        return False
    return specificity_result.get("specificity_label") not in {None, "Not available"}


def _patient_alteration_available(cbio_result):
    if not _is_available_dict(cbio_result):
        return False
    return cbio_result.get("patient_alteration_support") not in {None, "Not available"}


def _patient_expression_available(expression_result):
    if not _is_available_dict(expression_result):
        return False
    return expression_result.get("expression_support") not in {None, "Not available"}


def _survival_available(survival_result):
    if not _is_available_dict(survival_result):
        return False
    return survival_result.get("survival_signal") not in {None, "Not available"}


def _gene_role_available(gene_role_result):
    if not gene_role_result:
        return False
    return gene_role_result.get("role_category") not in {None, "Not available"}


def _pathway_available(pathway_result):
    if not pathway_result:
        return False
    return pathway_result.get("pathway_category") not in {None, "Not available"}


def _therapeutic_available(therapeutic_result):
    if not therapeutic_result:
        return False
    return therapeutic_result.get("therapeutic_relevance") not in {None, "Not available"}


def calculate_evidence_coverage(
    pubmed_count=None,
    depmap_result=None,
    common_result=None,
    specificity_result=None,
    cbio_result=None,
    expression_result=None,
    survival_result=None,
    gene_role_result=None,
    pathway_result=None,
    therapeutic_result=None,
):
    """
    Calculate evidence coverage across all current OncoEvidence layers.

    Coverage measures whether the layer is available, not whether the evidence is strong.
    """
    layers = [
        ("PubMed literature", _pubmed_available(pubmed_count)),
        ("DepMap dependency", _depmap_available(depmap_result)),
        ("Common-essential caution", _common_essential_available(common_result)),
        ("Lineage specificity", _specificity_available(specificity_result)),
        ("Patient alteration", _patient_alteration_available(cbio_result)),
        ("Patient expression", _patient_expression_available(expression_result)),
        ("Survival/prognosis", _survival_available(survival_result)),
        ("Gene role classification", _gene_role_available(gene_role_result)),
        ("Pathway/function annotation", _pathway_available(pathway_result)),
        ("Therapeutic relevance", _therapeutic_available(therapeutic_result)),
    ]

    available_layers = [name for name, available in layers if available]
    missing_layers = [name for name, available in layers if not available]

    available_count = len(available_layers)
    total_count = len(layers)
    coverage_percent = round((available_count / total_count) * 100, 1)

    if available_count == total_count:
        label = "Complete evidence profile"
    elif coverage_percent >= 80:
        label = "High evidence coverage"
    elif coverage_percent >= 50:
        label = "Moderate evidence coverage"
    else:
        label = "Limited evidence coverage"

    return {
        "evidence_coverage_label": label,
        "evidence_coverage_percent": coverage_percent,

        # Current key names
        "layers_available": available_count,
        "total_layers": total_count,
        "available_layer_count": available_count,
        "total_layer_count": total_count,

        # Backward-compatible key names used by older app/report code
        "evidence_layers_available": available_count,
        "evidence_layers_possible": total_count,

        "available_layers": available_layers,
        "missing_layers": missing_layers,
    }
