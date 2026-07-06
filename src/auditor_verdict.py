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
    specificity_result=None,
    cbio_result=None,
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

    specificity_label = None
    specificity_delta = None
    if specificity_result:
        specificity_label = specificity_result.get('specificity_label')
        specificity_delta = specificity_result.get('specificity_delta')

    patient_support = None
    mutation_frequency = None
    amplification_frequency = None
    deep_deletion_frequency = None
    if cbio_result and cbio_result.get("available"):
        patient_support = cbio_result.get("patient_alteration_support")
        mutation_frequency = cbio_result.get("mutation_frequency")
        amplification_frequency = cbio_result.get("amplification_frequency")
        deep_deletion_frequency = cbio_result.get("deep_deletion_frequency")

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

    # Lineage specificity
    if specificity_label == "High lineage specificity":
        strengths.append(
            f"{gene} shows higher dependency in the selected {cancer_type} group than in the pan-cancer background, supporting a lineage-enriched hypothesis."
        )
    elif specificity_label == "Moderate lineage specificity":
        strengths.append(
            f"{gene} shows moderately higher dependency in the selected {cancer_type} group than in the pan-cancer background."
        )
    elif specificity_label == "Low lineage specificity":
        warnings.append(
            f"{gene} has low lineage specificity by dependency-rate comparison, so the signal may reflect broad cancer dependency rather than {cancer_type}-specific vulnerability."
        )
    elif specificity_label == "Lower-than-background dependency":
        warnings.append(
            f"{gene} has lower dependency in the selected {cancer_type} group than in the pan-cancer background, weakening a lineage-specific dependency claim."
        )

    # Patient-tumor alteration support
    if patient_support == "High patient alteration support":
        strengths.append(
            f"{gene} has strong patient-tumor genomic alteration support in {cancer_type}, based on mutation, high-level amplification, or deep-deletion frequency."
        )
    elif patient_support == "Moderate patient alteration support":
        strengths.append(
            f"{gene} has moderate patient-tumor genomic alteration support in {cancer_type}, which may support a genomically altered subgroup hypothesis."
        )
    elif patient_support == "Low patient alteration support":
        warnings.append(
            f"{gene} has only low patient-tumor alteration support in {cancer_type}; any genomic-alteration claim should be narrow."
        )
    elif patient_support == "Little or no patient alteration support":
        warnings.append(
            f"{gene} has little or no patient-tumor alteration support in {cancer_type} by mutation, high-level amplification, or deep-deletion criteria."
        )

    # Tier logic
    if (
        dependency_label == "Strong dependency"
        and common_label == "Low common-essential caution"
        and specificity_label in {"High lineage specificity", "Moderate lineage specificity"}
        and patient_support in {"High patient alteration support", "Moderate patient alteration support"}
    ):
        verdict_tier = "Potentially selective dependency hypothesis"
        claim_style = "candidate selective vulnerability with patient-tumor support"
    elif dependency_label in {"Strong dependency", "Moderate dependency"} and (
        common_label in {"High common-essential caution", "Moderate common-essential caution"}
        or specificity_label in {"Low lineage specificity", "Lower-than-background dependency"}
        or patient_support == "Little or no patient alteration support"
    ):
        verdict_tier = "Strong dependency but specificity/patient-support risk hypothesis"
        claim_style = "broad dependency-associated candidate, not a selective patient-supported target"
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
        f"pan-cancer percent dependent={pan_percent}, common-essential label='{common_label}', "
        f"specificity delta={specificity_delta}, specificity label='{specificity_label}', "
        f"patient alteration support='{patient_support}', mutation frequency={mutation_frequency}, "
        f"amplification frequency={amplification_frequency}, and deep deletion frequency={deep_deletion_frequency}."
    )

    return {
        "verdict_tier": verdict_tier,
        "safe_claim": safe_claim,
        "strengths": strengths,
        "warnings": warnings,
        "methods_note": methods_note,
    }
