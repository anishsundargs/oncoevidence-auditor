"""
Auditor verdict module for OncoEvidence Auditor.

This module synthesizes literature saturation, lineage dependency,
and pan-cancer common-essential risk into a cautious research interpretation.
"""


def build_auditor_verdict(
    gene: str,
    cancer_type: str,
    pubmed_count,
    saturation_label,
    depmap_result,
    common_result,
):
    """
    Return a final evidence-auditor verdict.

    The verdict is intentionally conservative. It does not claim clinical utility.
    """
    dependency_label = depmap_result.get("dependency_label", "Not available")
    common_label = common_result.get("common_essential_label", "Not available")

    dep_score = depmap_result.get("median_dependency_score")
    dep_percent = depmap_result.get("percent_dependent")

    pan_percent = common_result.get("pan_cancer_percent_dependent")

    warnings = []
    strengths = []

    # Strengths
    if dependency_label == "Strong dependency":
        strengths.append(
            f"{gene} shows a strong dependency signal in the selected {cancer_type} model group."
        )
    elif dependency_label == "Moderate dependency":
        strengths.append(
            f"{gene} shows a moderate dependency signal in the selected {cancer_type} model group."
        )
    elif dependency_label == "Weak/variable dependency":
        strengths.append(
            f"{gene} shows a weak or variable dependency signal in the selected {cancer_type} model group."
        )
    else:
        warnings.append(
            f"{gene} does not show a strong dependency signal in the selected {cancer_type} model group."
        )

    # Common-essential caution
    if common_label == "High common-essential caution":
        warnings.append(
            f"{gene} is broadly dependency-associated across many cancer models, so the selected-cancer dependency may reflect general essentiality rather than selective vulnerability."
        )
    elif common_label == "Moderate common-essential caution":
        warnings.append(
            f"{gene} has moderate pan-cancer dependency, so specificity should be interpreted cautiously."
        )

    # Literature saturation
    if saturation_label == "High saturation":
        warnings.append(
            f"The {gene}/{cancer_type} literature appears highly saturated, so novelty likely requires a narrow mechanistic or computational angle."
        )
    elif saturation_label == "Low saturation":
        strengths.append(
            f"The {gene}/{cancer_type} literature appears relatively underexplored by PubMed title/abstract count."
        )

    # Tier logic
    if dependency_label == "Strong dependency" and common_label == "Low common-essential caution":
        verdict_tier = "Potentially selective dependency hypothesis"
        claim_style = "candidate selective vulnerability"
    elif dependency_label in {"Strong dependency", "Moderate dependency"} and common_label in {
        "High common-essential caution",
        "Moderate common-essential caution",
    }:
        verdict_tier = "Strong dependency but specificity-risk hypothesis"
        claim_style = "broad dependency-associated candidate, not a selective target"
    elif dependency_label in {"Strong dependency", "Moderate dependency"}:
        verdict_tier = "Moderate dependency hypothesis"
        claim_style = "dependency-associated candidate"
    elif saturation_label == "High saturation":
        verdict_tier = "Weak novelty / limited dependency hypothesis"
        claim_style = "known or weakly supported candidate"
    else:
        verdict_tier = "Exploratory hypothesis"
        claim_style = "exploratory candidate"

    safe_claim = (
        f"{gene} in {cancer_type} is best framed as a {claim_style}. "
        "This interpretation is based on public-data evidence and should be treated as hypothesis-generating, not clinically validated."
    )

    methods_note = (
        f"Auditor synthesis used PubMed count={pubmed_count}, "
        f"selected-group dependency={dep_score}, selected-group percent dependent={dep_percent}, "
        f"pan-cancer percent dependent={pan_percent}, and common-essential label='{common_label}'."
    )

    return {
        "verdict_tier": verdict_tier,
        "safe_claim": safe_claim,
        "strengths": strengths,
        "warnings": warnings,
        "methods_note": methods_note,
    }
