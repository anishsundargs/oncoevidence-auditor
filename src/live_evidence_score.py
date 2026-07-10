"""
Live evidence score for OncoEvidence Auditor.

This module scores the evidence produced during the current app run.
It is separate from the static catalog score, which is a curated local prior.
"""


def _contains(value, terms):
    text = str(value or "").lower()
    return any(term.lower() in text for term in terms)


def build_live_evidence_score(
    depmap_result=None,
    common_result=None,
    specificity_result=None,
    cbio_result=None,
    expression_result=None,
    survival_result=None,
    therapeutic_result=None,
    contradiction_result=None,
):
    """Build a 0-100 evidence-layer score from current live/local audit results."""
    depmap_result = depmap_result or {}
    common_result = common_result or {}
    specificity_result = specificity_result or {}
    cbio_result = cbio_result or {}
    expression_result = expression_result or {}
    survival_result = survival_result or {}
    therapeutic_result = therapeutic_result or {}
    contradiction_result = contradiction_result or {}

    breakdown = {}

    # 1. DepMap dependency signal: 0-20
    dep_label = depmap_result.get("dependency_label")
    if _contains(dep_label, ["strong"]):
        breakdown["DepMap dependency"] = 20
    elif _contains(dep_label, ["moderate"]):
        breakdown["DepMap dependency"] = 12
    elif _contains(dep_label, ["little", "weak", "no dependency"]):
        breakdown["DepMap dependency"] = 3
    elif depmap_result.get("available"):
        breakdown["DepMap dependency"] = 6
    else:
        breakdown["DepMap dependency"] = 0

    # 2. Lineage specificity and common-essential penalty: -15 to +15
    specificity_label = specificity_result.get("specificity_label")
    common_label = common_result.get("common_essential_label")

    specificity_points = 0
    if _contains(specificity_label, ["high"]):
        specificity_points += 15
    elif _contains(specificity_label, ["moderate"]):
        specificity_points += 8
    elif _contains(specificity_label, ["low"]):
        specificity_points -= 6

    if _contains(common_label, ["high common-essential"]):
        specificity_points -= 9
    elif _contains(common_label, ["moderate"]):
        specificity_points -= 4

    breakdown["Specificity/common-essential context"] = specificity_points

    # 3. Patient alteration support: 0-15
    alteration_label = cbio_result.get("patient_alteration_support") or cbio_result.get("alteration_support_label")
    if _contains(alteration_label, ["strong"]):
        breakdown["Patient alteration"] = 15
    elif _contains(alteration_label, ["moderate"]):
        breakdown["Patient alteration"] = 9
    elif _contains(alteration_label, ["subgroup"]):
        breakdown["Patient alteration"] = 7
    elif _contains(alteration_label, ["little", "weak", "no patient"]):
        breakdown["Patient alteration"] = 2
    elif cbio_result.get("available"):
        breakdown["Patient alteration"] = 4
    else:
        breakdown["Patient alteration"] = 0

    # 4. Patient expression support: 0-15
    expression_label = expression_result.get("expression_support_label") or expression_result.get("expression_support")
    if _contains(expression_label, ["strong"]):
        breakdown["Patient expression"] = 15
    elif _contains(expression_label, ["subgroup", "high-expression"]):
        breakdown["Patient expression"] = 10
    elif _contains(expression_label, ["moderate"]):
        breakdown["Patient expression"] = 8
    elif _contains(expression_label, ["little", "weak", "no expression"]):
        breakdown["Patient expression"] = 2
    elif expression_result.get("available"):
        breakdown["Patient expression"] = 4
    else:
        breakdown["Patient expression"] = 0

    # 5. Survival/prognosis support: 0-10
    survival_signal = survival_result.get("survival_signal")
    if _contains(survival_signal, ["clear", "strong"]):
        breakdown["Survival/prognosis"] = 10
    elif _contains(survival_signal, ["no clear"]):
        breakdown["Survival/prognosis"] = 4
    elif _contains(survival_signal, ["insufficient", "underpowered"]):
        breakdown["Survival/prognosis"] = 2
    elif survival_result.get("available"):
        breakdown["Survival/prognosis"] = 3
    else:
        breakdown["Survival/prognosis"] = 0

    # 6. Therapeutic relevance: 0-15
    therapeutic_label = therapeutic_result.get("therapeutic_relevance")
    alignment_label = therapeutic_result.get("therapeutic_alignment_label")

    if _contains(therapeutic_label, ["high therapeutic"]):
        breakdown["Therapeutic relevance"] = 15
    elif _contains(therapeutic_label, ["moderate"]):
        breakdown["Therapeutic relevance"] = 9
    elif _contains(therapeutic_label, ["research-context"]):
        breakdown["Therapeutic relevance"] = 5
    elif _contains(therapeutic_label, ["low direct"]):
        breakdown["Therapeutic relevance"] = 2
    else:
        breakdown["Therapeutic relevance"] = 3 if therapeutic_result else 0

    if _contains(alignment_label, ["without strong dependency", "mismatch", "not curated"]):
        breakdown["Therapeutic relevance"] -= 3

    # 7. Contradiction penalty: 0 to -15
    severity = contradiction_result.get("primary_severity")
    labels = contradiction_result.get("labels", [])

    if _contains(severity, ["high"]):
        breakdown["Contradiction penalty"] = -15
    elif _contains(severity, ["moderate"]):
        breakdown["Contradiction penalty"] = -8
    elif _contains(severity, ["low"]):
        breakdown["Contradiction penalty"] = -3
    elif labels:
        label_text = " ".join(str(item.get("severity", "")) for item in labels if isinstance(item, dict))
        if "high" in label_text.lower():
            breakdown["Contradiction penalty"] = -15
        elif "moderate" in label_text.lower():
            breakdown["Contradiction penalty"] = -8
        else:
            breakdown["Contradiction penalty"] = -3
    else:
        breakdown["Contradiction penalty"] = 0

    raw_score = sum(breakdown.values())
    score = round(max(0, min(100, raw_score)))

    if score >= 75:
        tier = "High live evidence support"
    elif score >= 55:
        tier = "Moderate live evidence support"
    elif score >= 35:
        tier = "Limited or conflicting live evidence support"
    else:
        tier = "Weak live evidence support"

    return {
        "live_evidence_score": score,
        "live_evidence_tier": tier,
        "breakdown": breakdown,
        "interpretation_note": (
            "This score summarizes the current live/local evidence layers. It is not a clinical score "
            "and should be interpreted alongside the auditor verdict and contradiction labels."
        ),
    }