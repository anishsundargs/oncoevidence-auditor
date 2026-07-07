# OncoEvidence Auditor

**OncoEvidence Auditor** is an early-stage Streamlit app for contradiction-aware cancer gene hypothesis triage.

Instead of only showing isolated expression or survival plots, the tool is designed to generate an **evidence card** for a gene/cancer pair and flag whether the public-data evidence is strong, weak, or internally contradictory.

## MVP Goal

Input:
- Gene symbol
- Cancer type

Output:
- Evidence score
- Evidence tier
- Tumor expression flag
- Survival association flag
- DepMap dependency flag
- Normal tissue safety flag
- GEO validation flag
- Contradiction warnings
- Safe research claim wording

## Current Status

This starter version uses mock evidence values so the UI and scoring logic can be tested first. The next development step is replacing the mock table with real data layers from TCGA/GDC, cBioPortal, DepMap, GTEx, and GEO.

## Why this is different

Most public cancer-genomics tools show data. This project audits whether a gene-level research claim is actually defensible across multiple evidence layers.

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Planned Data Layers

1. TCGA/GDC expression and clinical survival data
2. cBioPortal mutation and copy-number alteration data
3. DepMap CRISPR dependency data
4. GTEx or tumor-normal expression reference
5. GEO validation cohort per cancer type

## Disclaimer

This tool is for research and educational hypothesis triage only. It is not a clinical diagnostic, prognostic, or treatment recommendation system.

## Current MVP status

OncoEvidence Auditor is a Python/Streamlit cancer bioinformatics web application that audits gene/cancer hypotheses across multiple public evidence layers.

### Current validated case studies

- GBM
- Gastric cancer

### Current evidence layers

1. PubMed literature saturation
2. DepMap CRISPR dependency
3. Pan-cancer common-essential caution
4. Lineage specificity index
5. cBioPortal patient-tumor alteration evidence
6. cBioPortal patient-tumor expression evidence
7. Auditor Verdict synthesis
8. Batch Audit Mode

### Central registry

Cancer-specific mappings are stored in:

`data/config/cancer_registry.csv`

The registry currently controls:

- cBioPortal study candidates
- DepMap OncotreeCode filters
- PubMed cancer query terms
- Supported cancer dropdown options


### Batch Audit Mode

Batch Audit Mode screens every curated gene for a selected cancer type and ranks genes by local evidence patterns.

Current batch-level outputs include:

- DepMap dependency label
- Percent dependent
- Pan-cancer common-essential caution
- Lineage specificity label
- Specificity delta
- Contradiction pattern
- Auditor Verdict tier
- Main warning
- Downloadable CSV output

This helps the app function as a screening/auditing tool rather than only a single-gene dashboard.

### Research-use disclaimer

This project is for research and educational use only. It does not provide clinical recommendations, diagnoses, or treatment guidance.

### Strong project framing

OncoEvidence Auditor is designed to detect contradiction across evidence layers. For example, a gene may show strong cell-line dependency but weak patient-tumor alteration support, weak expression support, or high common-essential risk.

That contradiction-aware synthesis is the main purpose of the tool.

