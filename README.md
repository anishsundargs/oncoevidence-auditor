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
8. cBioPortal survival/prognosis evidence
9. Batch Audit Mode
10. Evidence Coverage Score

### Central registry

Cancer-specific mappings are stored in:

`data/config/cancer_registry.csv`

The registry currently controls:

- cBioPortal study candidates
- DepMap OncotreeCode filters
- PubMed cancer query terms
- Supported cancer dropdown options




### Survival/prognosis evidence

The survival/prognosis module uses cBioPortal clinical and expression data to descriptively compare high-expression tumors against other tumors.

Current outputs include:

- matched survival patient count
- high-expression survival group size
- comparison group size
- median overall survival for each group
- median overall survival difference
- event rates
- survival signal label

This layer is deliberately cautious. It does not yet perform a full Kaplan-Meier/log-rank survival analysis. If the high-expression subgroup is too small, the app marks the comparison as underpowered rather than claiming prognostic significance.

### Evidence Coverage Score

The Evidence Coverage Score reports how many major evidence layers are available for a gene/cancer analysis.

Current coverage layers:

- PubMed literature saturation
- DepMap dependency
- Pan-cancer common-essential caution
- Lineage specificity
- cBioPortal patient-tumor alteration evidence
- cBioPortal patient-tumor expression evidence
- cBioPortal survival/prognosis evidence

Coverage labels help distinguish complete evidence profiles from partial or limited profiles. This is important because a gene can look strong in one layer while patient-level or literature-level evidence is missing.

### Batch Audit Mode

Batch Audit Mode screens every curated gene for a selected cancer type and ranks genes by evidence patterns.

Fast mode uses local processed evidence layers. Optional live modes add PubMed literature saturation and cBioPortal patient alteration/expression evidence.

Current batch-level outputs include:

- DepMap dependency label
- Percent dependent
- Pan-cancer common-essential caution
- Lineage specificity label
- Specificity delta
- Contradiction pattern
- Auditor Verdict tier
- Main warning
- Evidence coverage label
- Evidence coverage percent
- Optional live PubMed count/literature saturation
- Optional live cBioPortal alteration/expression support
- Downloadable CSV output

This helps the app function as a screening/auditing tool rather than only a single-gene dashboard.

### Research-use disclaimer

This project is for research and educational use only. It does not provide clinical recommendations, diagnoses, or treatment guidance.

### Strong project framing

OncoEvidence Auditor is designed to detect contradiction across evidence layers. For example, a gene may show strong cell-line dependency but weak patient-tumor alteration support, weak expression support, or high common-essential risk.

That contradiction-aware synthesis is the main purpose of the tool.


## Example reports

The repository includes generated example reports in `docs/example_reports/`.

Recommended examples:

- `OIP5_GBM_example_report.md`  
  Demonstrates a strong DepMap dependency signal that is weakened by broad common-essentiality, low lineage specificity, weak patient-level support, and proliferation/cell-cycle role caution.

- `ERBB2_Gastric_cancer_example_report.md`  
  Demonstrates a therapeutically relevant biomarker/subgroup case where patient alteration/expression and therapeutic relevance exist despite weak DepMap dependency.

These examples illustrate the central purpose of the tool: not to rank genes by one evidence layer, but to expose contradictions across literature, dependency, patient tumors, survival, pathway context, and therapeutic relevance.

## Expanded 10-layer evidence profile

OncoEvidence Auditor evaluates gene/cancer hypotheses across a 10-layer evidence profile:

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

Coverage is a completeness metric, not a strength metric. A complete 10/10 profile can still produce a cautious or contradictory interpretation.

## Project summary

A polished project summary is available at:

`docs/PROJECT_SUMMARY.md`

This summary explains the motivation, 10-layer evidence profile, flagship examples, current limitations, and research-use disclaimer.

## Demo workflow

A step-by-step demonstration guide is available at:

`docs/DEMO_WORKFLOW.md`
