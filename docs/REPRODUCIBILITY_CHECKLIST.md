# OncoEvidence Auditor Reproducibility Checklist

## Project purpose

OncoEvidence Auditor is a contradiction-aware cancer gene hypothesis triage tool. It integrates public-data and curated evidence layers to help evaluate whether a gene-cancer pair is best framed as a strong hypothesis, a subgroup biomarker hypothesis, a broad dependency signal, or a contradictory/validation-needed candidate.

This tool is for research and educational use only. It does not provide diagnosis, prognosis, treatment recommendations, or clinical decision support.

## Current project scale

The local pan-cancer catalog contains:

- 28 cancer types
- 154 unique genes
- 2,020 gene-cancer hypotheses
- Median of approximately 72 genes per cancer type

Catalog counts reflect curated local hypothesis rows available for local triage. Live evidence availability depends on PubMed, cBioPortal, DepMap-derived local files, and survival/expression data availability.

## Main evidence layers

The current auditor uses the following evidence layers:

1. PubMed literature saturation
2. DepMap dependency signal
3. Common-essential caution
4. Lineage specificity index
5. cBioPortal patient-tumor alteration evidence
6. cBioPortal patient-tumor expression evidence
7. cBioPortal survival/prognosis evidence
8. Gene role classification
9. Pathway/function annotation
10. Drug/therapeutic relevance annotation
11. Contradiction/caution labels
12. Live evidence score
13. Static catalog score

## Key distinction: static score vs live score

The static catalog score is a curated local prior derived from catalog fields. It is useful for fast triage and catalog browsing.

The live evidence score is generated during the current audit from evidence layers such as DepMap dependency, common-essential caution, lineage specificity, patient alteration, patient expression, survival/prognosis, therapeutic relevance, and contradiction severity.

The auditor verdict and final interpretation should be prioritized over either score alone.

## Required local files

Core app files:

- `app.py`
- `README.md`
- `src/evidence_scoring.py`
- `src/live_evidence_score.py`
- `src/evidence_coverage.py`
- `src/auditor_verdict.py`
- `src/report_builder.py`
- `src/evidence_provenance.py`

Configuration and catalog files:

- `data/config/cancer_registry.csv`
- `data/config/gene_role_annotations.csv`
- `data/config/pathway_function_annotations.csv`
- `data/config/therapeutic_relevance_annotations.csv`
- `data/mock_gene_evidence.csv`

Streamlit pages:

- `pages/2_Batch_Audit.py`
- `pages/3_Examples_and_Interpretation_Guide.py`
- `pages/4_Catalog_Explorer.py`
- `pages/5_Evidence_Provenance.py`

Example outputs:

- `docs/example_reports/OIP5_GBM_example_report.md`
- `docs/example_reports/ERBB2_Gastric_cancer_example_report.md`
- `docs/PROJECT_SUMMARY.md`
- `docs/DEMO_WORKFLOW.md`

## How to run the app

From the project root:

```bash
streamlit run app.py