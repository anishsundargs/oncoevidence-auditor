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
