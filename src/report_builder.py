"""
Markdown report builder for OncoEvidence Auditor.

This module turns one app analysis into a downloadable research-style summary.
"""

from datetime import datetime

from src.evidence_coverage import calculate_evidence_coverage
from src.auditor_verdict import build_auditor_verdict
from src.final_interpretation import build_final_interpretation
from src.contradiction_labels import build_contradiction_labels
from src.gene_role import get_gene_role_summary


def _safe(value, fallback="Not available"):
    """Return a clean display value."""
    if value is None:
        return fallback
    if value == "":
        return fallback
    return value


def _bullet_list(items):
    """Convert a list of strings into Markdown bullets."""
    if not items:
        return "- None reported"

    return "\n".join(f"- {item}" for item in items)


def build_markdown_report(
    gene,
    cancer_type,
    pubmed_count=None,
    saturation_label=None,
    novelty_label=None,
    pubmed_query=None,
    depmap_result=None,
    common_result=None,
    specificity_result=None,
    cbio_result=None,
    expression_result=None,
    survival_result=None,
    verdict=None,
    coverage_result=None,
):
    """
    Build a Markdown report for one gene/cancer analysis.
    """
    depmap_result = depmap_result or {}
    common_result = common_result or {}
    specificity_result = specificity_result or {}
    cbio_result = cbio_result or {}
    expression_result = expression_result or {}
    survival_result = survival_result or {}
    verdict = verdict or {}

    # Rebuild verdict inside the report so late-added evidence layers, such as
    # survival/prognosis, are included even if the app created an earlier verdict
    # before those layers finished loading.
    try:
        verdict = build_auditor_verdict(
            gene=gene,
            cancer_type=cancer_type,
            pubmed_count=pubmed_count,
            saturation_label=saturation_label,
            depmap_result=depmap_result,
            common_result=common_result,
            specificity_result=specificity_result,
            cbio_result=cbio_result,
            expression_result=expression_result,
            survival_result=survival_result,
        )
    except Exception:
        # Keep the provided verdict if rebuilding fails.
        verdict = verdict or {}

    if coverage_result is None:
        coverage_result = calculate_evidence_coverage(
            pubmed_count=pubmed_count,
            depmap_result=depmap_result,
            common_result=common_result,
            specificity_result=specificity_result,
            cbio_result=cbio_result,
            expression_result=expression_result,
            survival_result=survival_result,
        )

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

    strengths = verdict.get("strengths", [])
    warnings = verdict.get("warnings", [])
    claim_style = verdict.get("claim_style") or verdict.get("claim_type") or verdict.get("verdict_tier")

    gene_role_result = get_gene_role_summary(gene, common_result)

    final_interpretation_result = build_final_interpretation(
        gene=gene,
        cancer_type=cancer_type,
        depmap_result=depmap_result,
        common_result=common_result,
        specificity_result=specificity_result,
        cbio_result=cbio_result,
        expression_result=expression_result,
        survival_result=survival_result,
        gene_role_result=gene_role_result,
        verdict=verdict,
        saturation_label=saturation_label,
    )

    contradiction_result = build_contradiction_labels(
        gene=gene,
        cancer_type=cancer_type,
        depmap_result=depmap_result,
        common_result=common_result,
        specificity_result=specificity_result,
        cbio_result=cbio_result,
        expression_result=expression_result,
        survival_result=survival_result,
        gene_role_result=gene_role_result,
        saturation_label=saturation_label,
    )

    contradiction_lines = "\n".join(
        [
            f"- **{item['label']}** ({item['severity']}): {item['explanation']}"
            for item in contradiction_result.get("labels", [])
        ]
    ) or "- None"

    available_layers_text = ", ".join(coverage_result.get("available_layers", [])) or "None"
    missing_layers_text = ", ".join(coverage_result.get("missing_layers", [])) or "None"

    depmap_note = depmap_result.get("note") or depmap_result.get("dependency_note") or ""
    oncotree_codes = depmap_result.get("oncotree_codes")

    if not oncotree_codes and "OncotreeCode values:" in depmap_note:
        oncotree_codes = depmap_note.split("OncotreeCode values:", 1)[1].strip().rstrip(".")

    report = f"""# OncoEvidence Auditor Report

**Generated:** {timestamp}  
**Gene:** {_safe(gene)}  
**Cancer type:** {_safe(cancer_type)}  

---

## Auditor Verdict

**Verdict tier:** {_safe(verdict.get("verdict_tier"))}  

**Claim style:** {_safe(claim_style)}  

**Safe claim:**  
{_safe(verdict.get("safe_claim"))}

### Strengths

{_bullet_list(strengths)}

### Warnings

{_bullet_list(warnings)}

---

## Final Interpretation and Next Validation

**Interpretation label:** {_safe(final_interpretation_result.get("interpretation_label"))}  

**Final interpretation:**  
{_safe(final_interpretation_result.get("final_interpretation"))}

**Recommended next validation:**  
{_safe(final_interpretation_result.get("recommended_next_validation"))}

---

## Contradiction Type Labels

**Primary contradiction label:** {_safe(contradiction_result.get("primary_label"))}  
**Primary severity:** {_safe(contradiction_result.get("primary_severity"))}  

{contradiction_lines}

---

## Gene Role Classification

**Role category:** {_safe(gene_role_result.get("role_category"))}  
**Target class:** {_safe(gene_role_result.get("target_class"))}  
**Biological process:** {_safe(gene_role_result.get("biological_process"))}  

**Role interpretation note:**  
{_safe(gene_role_result.get("interpretation_note"))}

**Role-based caution:** {_safe(gene_role_result.get("role_risk_label"))}  
**Role caution severity:** {_safe(gene_role_result.get("role_risk_severity"))}  

**Role caution note:**  
{_safe(gene_role_result.get("role_risk_note"))}

---

## Evidence Coverage

**Coverage label:** {_safe(coverage_result.get("evidence_coverage_label"))}  
**Layers available:** {_safe(coverage_result.get("evidence_layers_available"))}/{_safe(coverage_result.get("evidence_layers_possible"))}  
**Coverage percent:** {_safe(coverage_result.get("evidence_coverage_percent"))}%  

**Available layers:** {available_layers_text}  

**Missing layers:** {missing_layers_text}  

---

## Evidence Summary

| Evidence layer | Result |
|---|---|
| Evidence coverage label | {_safe(coverage_result.get("evidence_coverage_label"))} |
| Evidence coverage percent | {_safe(coverage_result.get("evidence_coverage_percent"))}% |
| Gene role category | {_safe(gene_role_result.get("role_category"))} |
| Role-based caution | {_safe(gene_role_result.get("role_risk_label"))} |
| PubMed count | {_safe(pubmed_count)} |
| Literature saturation | {_safe(saturation_label)} |
| Novelty label | {_safe(novelty_label)} |
| DepMap dependency label | {_safe(depmap_result.get("dependency_label"))} |
| DepMap median dependency score | {_safe(depmap_result.get("median_dependency_score"))} |
| DepMap percent dependent | {_safe(depmap_result.get("percent_dependent"))}% |
| Pan-cancer common-essential caution | {_safe(common_result.get("common_essential_label"))} |
| Pan-cancer percent dependent | {_safe(common_result.get("pan_cancer_percent_dependent"))}% |
| Lineage specificity label | {_safe(specificity_result.get("specificity_label"))} |
| Lineage specificity delta | {_safe(specificity_result.get("specificity_delta"))} |
| Patient alteration support | {_safe(cbio_result.get("patient_alteration_support"))} |
| Mutation frequency | {_safe(cbio_result.get("mutation_frequency"))}% |
| Amplification frequency | {_safe(cbio_result.get("amplification_frequency"))}% |
| Deep deletion frequency | {_safe(cbio_result.get("deep_deletion_frequency"))}% |
| Patient expression support | {_safe(expression_result.get("expression_support"))} |
| Median expression z-score | {_safe(expression_result.get("median_expression_zscore"))} |
| Percent high expression | {_safe(expression_result.get("percent_high_expression"))}% |
| Survival signal | {_safe(survival_result.get("survival_signal"))} |
| High-expression survival n | {_safe(survival_result.get("high_expression_survival_n"))} |
| Other-expression survival n | {_safe(survival_result.get("other_expression_survival_n"))} |
| Median OS difference | {_safe(survival_result.get("median_os_difference_months"))} months |

---

## PubMed Literature Saturation

**Query used:**  
`{_safe(pubmed_query)}`

**Interpretation:**  
PubMed count is used as a literature saturation and novelty signal. A high count does not prove biological importance; it means the gene/cancer pair is already heavily studied.

---

## DepMap Dependency Evidence

**Dependency label:** {_safe(depmap_result.get("dependency_label"))}  
**Median dependency score:** {_safe(depmap_result.get("median_dependency_score"))}  
**Dependent cell lines:** {_safe(depmap_result.get("dependent_cell_lines"))}  
**Total cell lines:** {_safe(depmap_result.get("total_cell_lines"))}  
**Percent dependent:** {_safe(depmap_result.get("percent_dependent"))}%  
**Oncotree codes:** {_safe(oncotree_codes)}  

**Note:** {_safe(depmap_note)}

---

## Common-Essential and Specificity Evidence

**Common-essential caution:** {_safe(common_result.get("common_essential_label"))}  
**Pan-cancer median dependency score:** {_safe(common_result.get("pan_cancer_median_dependency_score"))}  
**Pan-cancer percent dependent:** {_safe(common_result.get("pan_cancer_percent_dependent"))}%  

**Lineage specificity label:** {_safe(specificity_result.get("specificity_label"))}  
**Specificity delta:** {_safe(specificity_result.get("specificity_delta"))}  

---

## cBioPortal Patient-Tumor Alteration Evidence

**Study:** {_safe(cbio_result.get("study_id"))}  
**Total samples:** {_safe(cbio_result.get("total_samples"))}  
**Mutation frequency:** {_safe(cbio_result.get("mutation_frequency"))}%  
**Amplification frequency:** {_safe(cbio_result.get("amplification_frequency"))}%  
**Deep deletion frequency:** {_safe(cbio_result.get("deep_deletion_frequency"))}%  
**Broad CNA alteration frequency:** {_safe(cbio_result.get("cna_alteration_frequency"))}%  
**Patient alteration support:** {_safe(cbio_result.get("patient_alteration_support"))}  

**Note:** {_safe(cbio_result.get("note"))}

---

## cBioPortal Patient-Tumor Expression Evidence

**Study:** {_safe(expression_result.get("study_id"))}  
**Expression profile:** {_safe(expression_result.get("expression_profile_id"))}  
**Expression reference:** {_safe(expression_result.get("expression_reference"))}  
**Expression samples:** {_safe(expression_result.get("expression_sample_count"))}  
**Median expression z-score:** {_safe(expression_result.get("median_expression_zscore"))}  
**Mean expression z-score:** {_safe(expression_result.get("mean_expression_zscore"))}  
**Percent high expression:** {_safe(expression_result.get("percent_high_expression"))}%  
**Percent low expression:** {_safe(expression_result.get("percent_low_expression"))}%  
**Expression support:** {_safe(expression_result.get("expression_support"))}  

**Note:** {_safe(expression_result.get("note"))}

---

## cBioPortal Survival / Prognosis Evidence

**Study:** {_safe(survival_result.get("study_id"))}  
**Matched survival patients:** {_safe(survival_result.get("survival_patients_matched"))}  
**High-expression threshold:** z >= {_safe(survival_result.get("high_expression_threshold_z"))}  

**High-expression survival n:** {_safe(survival_result.get("high_expression_survival_n"))}  
**Other-expression survival n:** {_safe(survival_result.get("other_expression_survival_n"))}  

**High-expression median OS:** {_safe(survival_result.get("high_expression_median_os_months"))} months  
**Other-expression median OS:** {_safe(survival_result.get("other_expression_median_os_months"))} months  
**Median OS difference:** {_safe(survival_result.get("median_os_difference_months"))} months  

**High-expression event rate:** {_safe(survival_result.get("high_expression_event_rate_percent"))}%  
**Other-expression event rate:** {_safe(survival_result.get("other_expression_event_rate_percent"))}%  

**Survival signal:** {_safe(survival_result.get("survival_signal"))}  

**Note:** {_safe(survival_result.get("note"))}

---

## Methods Note

{_safe(verdict.get("methods_note"))}

---

## Research-Use Disclaimer

This report is for research and educational use only. It does not provide clinical recommendations, diagnoses, or treatment guidance.
"""

    return report
