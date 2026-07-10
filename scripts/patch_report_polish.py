from pathlib import Path


path = Path("src/report_builder.py")
text = path.read_text()

# 1. Add derived executive-report variables before the giant report string.
anchor = '''    if not oncotree_codes and "OncotreeCode values:" in depmap_note:
        oncotree_codes = depmap_note.split("OncotreeCode values:", 1)[1].strip().rstrip(".")

    report = f"""# OncoEvidence Auditor Report
'''

insert = '''    if not oncotree_codes and "OncotreeCode values:" in depmap_note:
        oncotree_codes = depmap_note.split("OncotreeCode values:", 1)[1].strip().rstrip(".")

    best_supported_claim = (
        verdict.get("safe_claim")
        or final_interpretation_result.get("final_interpretation")
        or "No conservative claim was generated for this run."
    )

    main_contradiction = (
        f"{_safe(contradiction_result.get('primary_label'))} "
        f"({_safe(contradiction_result.get('primary_severity'))})"
    )

    unsafe_claim_to_avoid = (
        f"Do not claim that {_safe(gene)} is a clinically actionable or selectively targetable "
        f"{_safe(cancer_type)} target from this report alone. The auditor is designed for "
        "research triage, not treatment guidance."
    )

    recommended_validation = (
        final_interpretation_result.get("recommended_next_validation")
        or pathway_result.get("validation_suggestions")
        or therapeutic_result.get("validation_suggestions")
        or "Validate the hypothesis using independent patient cohorts, protein-level evidence, and functional perturbation assays."
    )

    executive_summary = (
        f"{_safe(gene)} in {_safe(cancer_type)} is classified as "
        f"{_safe(verdict.get('verdict_tier'))}. The most conservative claim style is "
        f"{_safe(claim_style)}. The primary contradiction is {main_contradiction}. "
        f"The recommended next step is: {_safe(recommended_validation)}"
    )

    report_limitations = [
        "This report integrates public and curated evidence layers for hypothesis triage only.",
        "DepMap dependency is based on cancer model systems and does not prove patient-tumor actionability.",
        "cBioPortal alteration and expression evidence are cohort-dependent and do not prove causality.",
        "mRNA expression does not prove protein abundance, surface localization, or antigen accessibility.",
        "Survival/prognosis output is descriptive and does not replace Kaplan-Meier/log-rank/Cox clinical modeling.",
        "Curated role, pathway, and therapeutic annotations are interpretive aids and require manual review.",
        "Therapeutic relevance annotations are not treatment recommendations.",
    ]

    report = f"""# OncoEvidence Auditor Report
'''

if "best_supported_claim =" not in text:
    if anchor not in text:
        raise SystemExit("Could not find report-string anchor in src/report_builder.py")
    text = text.replace(anchor, insert)


# 2. Insert polished executive sections after the metadata divider and before Auditor Verdict.
old_top = '''---

## Auditor Verdict
'''

new_top = '''---

## Executive Summary

{_safe(executive_summary)}

## Best Supported Claim

{_safe(best_supported_claim)}

## Main Contradiction

**Primary contradiction:** {_safe(contradiction_result.get("primary_label"))}  
**Severity:** {_safe(contradiction_result.get("primary_severity"))}  

{_safe(contradiction_result.get("primary_explanation") or "See contradiction labels below for detailed interpretation.")}

## Unsafe Claim to Avoid

{_safe(unsafe_claim_to_avoid)}

## Recommended Next Validation

{_safe(recommended_validation)}

---

## Auditor Verdict
'''

if "## Executive Summary" not in text:
    if old_top not in text:
        raise SystemExit("Could not find Auditor Verdict insertion point.")
    text = text.replace(old_top, new_top, 1)


# 3. Add limitations before Methods Note.
old_methods = '''---

## Methods Note

{_safe(verdict.get("methods_note"))}
'''

new_methods = '''---

## Limitations

{_bullet_list(report_limitations)}

---

## Methods Note

{_safe(verdict.get("methods_note"))}
'''

if "## Limitations" not in text:
    if old_methods not in text:
        raise SystemExit("Could not find Methods Note insertion point.")
    text = text.replace(old_methods, new_methods, 1)


path.write_text(text)

print("Polished Markdown report structure.")