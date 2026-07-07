"""
Contradiction label module for OncoEvidence Auditor.

This module converts evidence-layer conflicts into compact labels that can be
used in reports, batch audit tables, and final interpretation.
"""


def _get(d, key):
    if not d:
        return None
    return d.get(key)


def _add(labels, label, severity, explanation):
    labels.append(
        {
            "label": label,
            "severity": severity,
            "explanation": explanation,
        }
    )


def build_contradiction_labels(
    gene,
    cancer_type,
    depmap_result=None,
    common_result=None,
    specificity_result=None,
    cbio_result=None,
    expression_result=None,
    survival_result=None,
    saturation_label=None,
):
    """
    Return contradiction labels for one gene/cancer analysis.
    """
    labels = []

    dep_label = _get(depmap_result, "dependency_label")
    common_label = _get(common_result, "common_essential_label")
    specificity_label = _get(specificity_result, "specificity_label")
    patient_support = _get(cbio_result, "patient_alteration_support")
    expression_support = _get(expression_result, "expression_support")
    survival_signal = _get(survival_result, "survival_signal")

    if dep_label == "Strong dependency" and common_label == "High common-essential caution":
        _add(
            labels,
            "Broad essentiality risk",
            "High",
            f"{gene} shows strong dependency in {cancer_type}, but it is also broadly dependency-associated across many cancer models.",
        )

    if dep_label == "Strong dependency" and specificity_label in {
        "Low lineage specificity",
        "Lower-than-background dependency",
    }:
        _add(
            labels,
            "Weak lineage specificity",
            "High",
            f"{gene} dependency is not clearly enriched in {cancer_type} compared with the pan-cancer background.",
        )

    if (
        dep_label == "Strong dependency"
        and patient_support == "Little or no patient alteration support"
        and expression_support == "Little or no expression support"
    ):
        _add(
            labels,
            "Dependency-only signal",
            "High",
            f"{gene} has strong cell-line dependency evidence but weak patient-tumor alteration and expression support.",
        )

    elif dep_label == "Strong dependency" and patient_support == "Little or no patient alteration support":
        _add(
            labels,
            "Weak patient alteration support",
            "Moderate",
            f"{gene} has strong dependency evidence but little or no patient-tumor alteration support.",
        )

    elif dep_label == "Strong dependency" and expression_support == "Little or no expression support":
        _add(
            labels,
            "Weak patient expression support",
            "Moderate",
            f"{gene} has strong dependency evidence but little or no patient-tumor expression support.",
        )

    if (
        dep_label in {"Little or no dependency", "Moderate dependency"}
        and patient_support in {"High patient alteration support", "Moderate patient alteration support"}
    ):
        _add(
            labels,
            "Alteration-without-dependency signal",
            "Moderate",
            f"{gene} has patient alteration support in {cancer_type}, but the current dependency signal is not strong.",
        )

    if expression_support == "Subgroup high-expression support":
        _add(
            labels,
            "Expression-defined subgroup signal",
            "Low",
            f"{gene} shows high expression in a tumor subgroup rather than broad high expression across the cohort.",
        )

    if patient_support in {"High patient alteration support", "Moderate patient alteration support"} and expression_support in {
        "Subgroup high-expression support",
        "Moderate expression support",
        "High broad expression support",
    }:
        _add(
            labels,
            "Patient-supported subgroup signal",
            "Low",
            f"{gene} has patient-level alteration and/or expression evidence supporting a tumor subgroup hypothesis.",
        )

    if saturation_label == "High saturation":
        _add(
            labels,
            "Literature-saturated target",
            "Moderate",
            f"The {gene}/{cancer_type} literature is highly saturated, so novelty requires a narrow mechanistic or computational angle.",
        )

    if survival_signal in {
        "Insufficient high-expression subgroup for survival comparison",
        "Insufficient comparison group for survival comparison",
    }:
        _add(
            labels,
            "Underpowered survival signal",
            "Moderate",
            f"Survival interpretation for {gene} in {cancer_type} is underpowered because one expression-defined group is too small.",
        )

    elif survival_signal == "No clear median-survival separation":
        _add(
            labels,
            "No clear prognostic separation",
            "Low",
            f"High {gene} expression does not show clear median-survival separation in the current descriptive screen.",
        )

    elif survival_signal == "High-expression subgroup shows worse-survival signal":
        _add(
            labels,
            "Possible adverse prognosis signal",
            "Moderate",
            f"High {gene} expression shows a worse-survival descriptive signal that needs formal survival validation.",
        )

    elif survival_signal == "High-expression subgroup shows better-survival signal":
        _add(
            labels,
            "Possible favorable prognosis signal",
            "Moderate",
            f"High {gene} expression shows a better-survival descriptive signal, which complicates a high-risk biomarker framing.",
        )

    if not labels:
        _add(
            labels,
            "No major contradiction detected",
            "Low",
            "No major cross-layer contradiction was detected by the current rule set.",
        )

    severity_rank = {"High": 3, "Moderate": 2, "Low": 1}
    labels = sorted(labels, key=lambda x: severity_rank.get(x["severity"], 0), reverse=True)

    primary = labels[0]

    return {
        "labels": labels,
        "primary_label": primary["label"],
        "primary_severity": primary["severity"],
        "primary_explanation": primary["explanation"],
        "label_summary": "; ".join([item["label"] for item in labels]),
    }
