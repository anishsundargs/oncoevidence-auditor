# OncoEvidence Auditor: Project Summary

## One-sentence description

OncoEvidence Auditor is a contradiction-aware cancer gene hypothesis triage tool that integrates public literature, dependency, patient-tumor, survival, biological role, pathway, and therapeutic relevance evidence into cautious research-use reports.

## Core problem

Cancer gene prioritization often overweights one attractive evidence layer. A gene may show strong cell-line dependency but weak patient-tumor support, or it may be therapeutically relevant despite weak CRISPR dependency. OncoEvidence Auditor was built to expose these cross-layer contradictions instead of hiding them behind a single score.

## Current evidence profile

The current system evaluates gene/cancer hypotheses across a 10-layer evidence profile:

1. PubMed literature saturation
2. DepMap dependency
3. Common-essential caution
4. Lineage specificity
5. Patient-tumor alteration evidence
6. Patient-tumor expression evidence
7. Survival/prognosis evidence
8. Gene role classification
9. Pathway/function annotation
10. Drug/therapeutic relevance annotation

Coverage measures whether each evidence layer is available. It does not mean the hypothesis is strong.

## Main outputs

For each gene/cancer pair, the tool generates:

- evidence score and evidence tier
- dependency and specificity summaries
- patient alteration and expression summaries
- descriptive survival/prognosis screen
- auditor verdict
- final interpretation and recommended next validation
- contradiction type labels
- gene role classification
- pathway/function annotation
- therapeutic relevance annotation
- downloadable Markdown evidence report

## Flagship examples

### OIP5 in GBM

OIP5 shows strong GBM DepMap dependency, but the broader evidence profile weakens a direct target claim. It has high common-essential caution, low lineage specificity, weak patient alteration/expression support, underpowered survival interpretation, and proliferation/cell-cycle role and pathway caution.

Best framing: broad dependency-associated candidate, not a selective patient-supported GBM target.

Recommended next validation: test whether OIP5 dependency reflects general proliferation or cell-cycle essentiality rather than GBM-specific biology.

### ERBB2 in gastric cancer

ERBB2 in gastric cancer illustrates the opposite pattern. It has weak DepMap dependency, but patient alteration/expression support and curated therapeutic biomarker relevance support a subgroup/biomarker framing.

Best framing: patient-supported therapeutic biomarker/subgroup hypothesis, not a strong cell-autonomous dependency target.

Recommended next validation: check HER2 amplification-expression concordance, protein/IHC or FISH evidence, pathway activation, and therapy-response literature.

## Why this project is useful

The tool is useful because it avoids simplistic gene ranking. Instead, it identifies when evidence layers disagree and gives a safer interpretation. This makes it better suited for early-stage computational hypothesis triage, literature-aware target screening, and research planning.

## Current limitations

- Public-data only; not experimentally validated.
- Survival analysis is descriptive and does not yet perform full Kaplan-Meier/log-rank or multivariable modeling.
- Therapeutic relevance annotations are curated and incomplete.
- Gene role, pathway, and therapeutic annotations are currently local curated tables, not live ontology/database integrations.
- DepMap dependency may not capture immune-mediated, antibody-mediated, microenvironmental, or lineage biomarker mechanisms.
- This tool does not provide clinical recommendations.

## Research-use disclaimer

OncoEvidence Auditor is for research and educational use only. It does not provide diagnoses, prognoses, clinical actionability calls, or treatment recommendations.
