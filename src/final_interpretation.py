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
    gene_role_result=None,
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

    role_category = _get(gene_role_result, "role_category")
    target_class = _get(gene_role_result, "target_class")
    role_risk_label = _get(gene_role_result, "role_risk_label")
    role_risk_note = _get(gene_role_result, "role_risk_note")

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

    # Gene-role-aware refinement
    if role_risk_label == "Proliferation/common-essential caution":
        final_interpretation += (
            f" Gene role annotation further strengthens this caution because {gene} is classified as "
            f"{role_category}, with a target class of {target_class}."
        )
        next_validation += (
            " Because the gene role is proliferation/cell-cycle-linked, prioritize tests that distinguish "
            "general growth dependence from cancer-lineage-specific vulnerability."
        )

    elif role_risk_label == "Tumor-suppressor framing caution":
        next_validation += (
            " Because the gene has tumor-suppressor framing, prioritize mutation/loss-of-function and pathway-context "
            "analyses over simple overexpression or dependency-target claims."
        )

    elif role_risk_label == "Subgroup/actionability context important":
        next_validation += (
            " Because the gene role suggests subgroup/actionability context, prioritize alteration-expression concordance "
            "and subgroup-specific evidence over broad pan-cohort claims."
        )

    elif role_risk_label == "Microenvironment/pathway-context caution":
        next_validation += (
            " Because the gene role may involve microenvironmental or extracellular biology, tumor-cell dependency alone "
            "may miss the main biological mechanism."
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

    if role_risk_note and role_risk_label not in {None, "No special role-based caution"}:
        next_validation += f" Role-based caution note: {role_risk_note}"

    return {
        "interpretation_label": interpretation_label,
        "final_interpretation": final_interpretation,
        "recommended_next_validation": next_validation,
        "verdict_tier": verdict_tier,
        "role_category": role_category,
        "role_risk_label": role_risk_label,
    }
