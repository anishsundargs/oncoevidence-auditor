"""
Final interpretation builder for OncoEvidence Auditor.

This module converts evidence-layer outputs into a concise research interpretation
and a recommended next validation step.
"""


def _get(d, key):
    if not d:
        return None
    return d.get(key)


def build_final_interpretation(
    gene,
    cancer_type,
    depmap_result=None,
    common_result=None,
    specificity_result=None,
    cbio_result=None,
    expression_result=None,
    survival_result=None,
    verdict=None,
    saturation_label=None,
):
    """
    Build final interpretation and next validation guidance.
    """
    dep_label = _get(depmap_result, "dependency_label")
    common_label = _get(common_result, "common_essential_label")
    specificity_label = _get(specificity_result, "specificity_label")
    patient_support = _get(cbio_result, "patient_alteration_support")
    expression_support = _get(expression_result, "expression_support")
    survival_signal = _get(survival_result, "survival_signal")
    verdict_tier = _get(verdict, "verdict_tier")
    safe_claim = _get(verdict, "safe_claim")

    interpretation_label = "General hypothesis-generating result"

    final_interpretation = safe_claim or (
        f"{gene} in {cancer_type} should be treated as a hypothesis-generating signal, "
        "not as a validated biomarker or therapeutic target."
    )

    next_validation = (
        "Validate this gene/cancer hypothesis in an independent dataset and avoid making "
        "clinical or therapeutic claims without experimental support."
    )

    if (
        dep_label == "Strong dependency"
        and common_label == "High common-essential caution"
        and specificity_label in {"Low lineage specificity", "Lower-than-background dependency"}
        and patient_support == "Little or no patient alteration support"
        and expression_support == "Little or no expression support"
    ):
        interpretation_label = "Broad dependency with weak patient-level support"
        final_interpretation = (
            f"{gene} in {cancer_type} is best interpreted as a broad dependency-associated gene, "
            "not a selective patient-supported cancer target. The strongest evidence comes from "
            "cell-line dependency, but the signal is weakened by high common-essential caution, "
            "low lineage specificity, and weak patient alteration/expression support."
        )
        next_validation = (
            f"Test whether {gene} dependency reflects general proliferation or cell-cycle essentiality "
            f"rather than {cancer_type}-specific biology. Useful next checks include comparing dependency "
            "against known pan-essential/cell-cycle genes, testing independent DepMap releases, and looking "
            "for protein-level or single-cell evidence in patient tumors."
        )

    elif (
        dep_label in {"Little or no dependency", "Moderate dependency"}
        and patient_support in {"High patient alteration support", "Moderate patient alteration support"}
    ):
        interpretation_label = "Patient-supported biomarker/subgroup hypothesis"
        final_interpretation = (
            f"{gene} in {cancer_type} is better framed as a patient-tumor alteration or subgroup hypothesis "
            "than as a strong dependency target. Patient alteration support exists, but the current DepMap "
            "dependency signal is not strong enough to claim selective vulnerability."
        )
        next_validation = (
            f"Validate whether {gene}-altered {cancer_type} tumors form a biologically distinct subgroup. "
            "Recommended next checks include alteration-expression correlation, pathway enrichment, drug-response "
            "association, and independent cohort validation."
        )

    elif expression_support == "Subgroup high-expression support":
        interpretation_label = "Expression-defined subgroup hypothesis"
        final_interpretation = (
            f"{gene} in {cancer_type} appears most suitable as an expression-defined subgroup hypothesis. "
            "The evidence supports a subset of high-expression tumors more than a broad cohort-wide claim."
        )
        next_validation = (
            f"Check whether the high-{gene} subgroup has distinct pathway activity, copy-number/mutation patterns, "
            "drug sensitivity, or survival behavior in independent datasets."
        )

    elif dep_label == "Strong dependency" and common_label == "Low common-essential caution":
        interpretation_label = "Potential selective dependency hypothesis"
        final_interpretation = (
            f"{gene} in {cancer_type} may represent a more selective dependency hypothesis, but the claim should "
            "still be treated as computational and hypothesis-generating until validated experimentally."
        )
        next_validation = (
            f"Prioritize orthogonal validation for {gene}, such as independent CRISPR/siRNA evidence, rescue experiments, "
            f"and comparison across {cancer_type} molecular subtypes."
        )

    if survival_signal == "High-expression subgroup shows worse-survival signal":
        next_validation += (
            " Because high expression also shows a worse-survival descriptive signal, a formal Kaplan-Meier/log-rank "
            "analysis and multivariable survival model should be prioritized."
        )
    elif survival_signal == "No clear median-survival separation":
        next_validation += (
            " Since the current survival screen shows no clear median-survival separation, avoid framing this as a "
            "prognostic biomarker unless stronger survival evidence appears."
        )
    elif survival_signal in {
        "Insufficient high-expression subgroup for survival comparison",
        "Insufficient comparison group for survival comparison",
    }:
        next_validation += (
            " The survival comparison is underpowered, so a larger cohort or different subgroup threshold is needed "
            "before making any prognostic claim."
        )

    if saturation_label == "High saturation":
        next_validation += (
            " The literature is already highly saturated, so future work should emphasize a specific contradiction, "
            "subgroup, mechanism, or validation angle rather than presenting the gene/cancer pair as broadly novel."
        )

    return {
        "interpretation_label": interpretation_label,
        "final_interpretation": final_interpretation,
        "recommended_next_validation": next_validation,
        "verdict_tier": verdict_tier,
    }
