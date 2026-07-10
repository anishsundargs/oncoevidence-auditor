# OncoEvidence Auditor Report

**Generated:** 2026-07-10 16:17  
**Gene:** OIP5  
**Cancer type:** GBM  

---

## Auditor Verdict

**Verdict tier:** Strong dependency but specificity/patient-support risk hypothesis  

**Claim style:** broad dependency-associated candidate, not a selective patient-supported target  

**Safe claim:**  
OIP5 in GBM is best framed as a broad dependency-associated candidate, not a selective patient-supported target. This interpretation is based on public-data evidence and should be treated as hypothesis-generating, not clinically validated.

### Strengths

- OIP5 shows a strong dependency signal in the selected GBM model group.

### Warnings

- OIP5 is broadly dependency-associated across many cancer models, so the selected-cancer dependency may reflect general essentiality rather than selective vulnerability.
- OIP5 has low lineage specificity by dependency-rate comparison, so the signal may reflect broad cancer dependency rather than GBM-specific vulnerability.
- OIP5 has little or no patient-tumor alteration support in GBM by mutation, high-level amplification, or deep-deletion criteria.
- OIP5 has little or no patient-tumor expression support in GBM by the current z-score criteria.
- Survival interpretation for OIP5 in GBM is underpowered because one expression-defined group is too small.

---

## Final Interpretation and Next Validation

**Interpretation label:** Broad dependency with weak patient-level support  

**Final interpretation:**  
OIP5 in GBM is best interpreted as a broad dependency-associated gene, not a selective patient-supported cancer target. The strongest evidence comes from cell-line dependency, but the signal is weakened by high common-essential caution, low lineage specificity, and weak patient alteration/expression support. Gene role annotation further strengthens this caution because OIP5 is classified as Proliferation/cell-cycle associated, with a target class of Proliferation-associated nuclear protein.

**Recommended next validation:**  
Test whether OIP5 dependency reflects general proliferation or cell-cycle essentiality rather than GBM-specific biology. Useful next checks include comparing dependency against known pan-essential/cell-cycle genes, testing independent DepMap releases, and looking for protein-level or single-cell evidence in patient tumors. Because the gene role is proliferation/cell-cycle-linked, prioritize tests that distinguish general growth dependence from cancer-lineage-specific vulnerability. The survival comparison is underpowered, so a larger cohort or different subgroup threshold is needed before making any prognostic claim. Role-based caution note: The gene role is linked to proliferation or cell-cycle biology and the gene also has high common-essential caution. Dependency evidence may reflect broad growth essentiality rather than selective cancer vulnerability.

---

## Contradiction Type Labels

**Primary contradiction label:** Broad essentiality risk  
**Primary severity:** High  

- **Broad essentiality risk** (High): OIP5 shows strong dependency in GBM, but it is also broadly dependency-associated across many cancer models.
- **Role-supported broad essentiality risk** (High): OIP5 is classified as Proliferation/cell-cycle associated and also has high common-essential caution, strengthening the concern that dependency reflects broad proliferation biology.
- **Weak lineage specificity** (High): OIP5 dependency is not clearly enriched in GBM compared with the pan-cancer background.
- **Dependency-only signal** (High): OIP5 has strong cell-line dependency evidence but weak patient-tumor alteration and expression support.
- **Underpowered survival signal** (Moderate): Survival interpretation for OIP5 in GBM is underpowered because one expression-defined group is too small.

---

## Gene Role Classification

**Role category:** Proliferation/cell-cycle associated  
**Target class:** Proliferation-associated nuclear protein  
**Biological process:** Cell-cycle progression and proliferation  

**Role interpretation note:**  
OIP5 should be interpreted cautiously as a dependency candidate because proliferation-linked genes can show broad essentiality across cancer models.

**Role-based caution:** Proliferation/common-essential caution  
**Role caution severity:** High  

**Role caution note:**  
The gene role is linked to proliferation or cell-cycle biology and the gene also has high common-essential caution. Dependency evidence may reflect broad growth essentiality rather than selective cancer vulnerability.

---

## Pathway / Function Annotation

**Pathway category:** Cell cycle / proliferation  
**Function group:** Proliferation and chromosome biology  
**Pathway process:** Cell-cycle progression and proliferation  

**Interpretive use:**  
OIP5 pathway context supports caution that dependency may reflect broad proliferation biology rather than GBM-specific vulnerability.

**Pathway caution:** Pathway-supported common-essential caution  
**Pathway caution severity:** High  

**Pathway caution note:**  
The gene is annotated to a proliferation, replication, or mitotic pathway and also has high common-essential caution. This strengthens the interpretation that dependency may reflect broad growth biology rather than a selective cancer vulnerability.

**Suggested validation:**  
Compare dependency with pan-essential and cell-cycle gene sets; check single-cell tumor-state expression and protein-level evidence.

---

## Drug / Therapeutic Relevance Annotation

**Therapeutic relevance:** Low direct therapeutic relevance  
**Biomarker type:** Proliferation/dependency hypothesis  

**Therapeutic context:**  
No curated direct therapeutic biomarker context for GBM

**Dependency interpretation:**  
OIP5 dependency should be treated as a research hypothesis rather than a therapeutic actionability signal.

**Therapeutic caution:**  
Do not frame OIP5 as therapeutically actionable without druggability, protein-level, and disease-specific validation.

**Dependency/actionability alignment:** Dependency without therapeutic actionability  
**Alignment severity:** High  

**Alignment note:**  
The gene shows dependency evidence but has low or uncertain curated therapeutic relevance. Do not equate dependency with druggability or clinical actionability.

**Suggested validation:**  
Check druggability, protein localization, single-cell expression, pan-essentiality, and orthogonal perturbation evidence.

**Important:** This section is for research triage only. It does not provide treatment recommendations.

---

## Evidence Coverage

**Coverage label:** Complete evidence profile  
**Layers available:** 10/10  
**Coverage percent:** 100.0%  

**Available layers:** PubMed literature, DepMap dependency, Common-essential caution, Lineage specificity, Patient alteration, Patient expression, Survival/prognosis, Gene role classification, Pathway/function annotation, Therapeutic relevance  

**Missing layers:** None  

---

## Evidence Summary

| Evidence layer | Result |
|---|---|
| Evidence coverage label | Complete evidence profile |
| Evidence coverage percent | 100.0% |
| Gene role category | Proliferation/cell-cycle associated |
| Role-based caution | Proliferation/common-essential caution |
| Pathway category | Cell cycle / proliferation |
| Pathway caution | Pathway-supported common-essential caution |
| Therapeutic relevance | Low direct therapeutic relevance |
| Therapeutic alignment | Dependency without therapeutic actionability |
| PubMed count | 16 |
| Literature saturation | ('Low-moderate saturation', 'moderate', 'This gene/cancer pair has some literature but may still allow a focused public-data hypothesis.') |
| Novelty label | moderate |
| DepMap dependency label | Strong dependency |
| DepMap median dependency score | -0.8872 |
| DepMap percent dependent | 84.0% |
| Pan-cancer common-essential caution | High common-essential caution |
| Pan-cancer percent dependent | 89.2% |
| Lineage specificity label | Low lineage specificity |
| Lineage specificity delta | -5.2 |
| Patient alteration support | Little or no patient alteration support |
| Mutation frequency | 0.0% |
| Amplification frequency | 0.34% |
| Deep deletion frequency | 0.17% |
| Patient expression support | Little or no expression support |
| Median expression z-score | 0.13 |
| Percent high expression | 1.25% |
| Survival signal | Insufficient high-expression subgroup for survival comparison |
| High-expression survival n | 2 |
| Other-expression survival n | 152 |
| Median OS difference | -3.97 months |

---

## PubMed Literature Saturation

**Query used:**  
`Not available`

**Interpretation:**  
PubMed count is used as a literature saturation and novelty signal. A high count does not prove biological importance; it means the gene/cancer pair is already heavily studied.

---

## DepMap Dependency Evidence

**Dependency label:** Strong dependency  
**Median dependency score:** -0.8872  
**Dependent cell lines:** 42  
**Total cell lines:** 50  
**Percent dependent:** 84.0%  
**Oncotree codes:** GB  

**Note:** Filtered by registry OncotreeCode values: GB.

---

## Common-Essential and Specificity Evidence

**Common-essential caution:** High common-essential caution  
**Pan-cancer median dependency score:** -0.9458  
**Pan-cancer percent dependent:** 89.2%  

**Lineage specificity label:** Low lineage specificity  
**Specificity delta:** -5.2  

---

## cBioPortal Patient-Tumor Alteration Evidence

**Study:** gbm_tcga_pan_can_atlas_2018  
**Total samples:** 592  
**Mutation frequency:** 0.0%  
**Amplification frequency:** 0.34%  
**Deep deletion frequency:** 0.17%  
**Broad CNA alteration frequency:** 29.39%  
**Patient alteration support:** Little or no patient alteration support  

**Note:** cBioPortal alteration summary using mutation and gene-level discrete GISTIC CNA profiles. Patient alteration support is based on mutation, high-level amplification, and deep-deletion frequencies. Broad CNA alteration frequency includes shallow gains/losses and is reported separately.

---

## cBioPortal Patient-Tumor Expression Evidence

**Study:** gbm_tcga_pan_can_atlas_2018  
**Expression profile:** gbm_tcga_pan_can_atlas_2018_rna_seq_v2_mrna_median_all_sample_Zscores  
**Expression reference:** All-sample-reference z-score profile  
**Expression samples:** 160  
**Median expression z-score:** 0.13  
**Mean expression z-score:** 0.0  
**Percent high expression:** 1.25%  
**Percent low expression:** 4.38%  
**Expression support:** Little or no expression support  

**Note:** cBioPortal mRNA expression z-score summary. High expression is counted as z >= 2. Low expression is counted as z <= -2. Interpretation depends on the reference profile used.

---

## cBioPortal Survival / Prognosis Evidence

**Study:** gbm_tcga_pan_can_atlas_2018  
**Matched survival patients:** 154  
**High-expression threshold:** z >= 2.0  

**High-expression survival n:** 2  
**Other-expression survival n:** 152  

**High-expression median OS:** 7.82 months  
**Other-expression median OS:** 11.79 months  
**Median OS difference:** -3.97 months  

**High-expression event rate:** 100.0%  
**Other-expression event rate:** 78.95%  

**Survival signal:** Insufficient high-expression subgroup for survival comparison  

**Note:** Survival comparison is based on high-expression tumors (z >= 2.0) versus other tumors. This is a descriptive screening summary, not a Kaplan-Meier/log-rank survival analysis.

---

## Methods Note

Auditor synthesis used PubMed count=16, selected-group dependency=-0.8872, selected-group percent dependent=84.0, pan-cancer percent dependent=89.2, common-essential label='High common-essential caution', specificity delta=-5.2, specificity label='Low lineage specificity', patient alteration support='Little or no patient alteration support', mutation frequency=0.0, amplification frequency=0.34, deep deletion frequency=0.17, expression support='Little or no expression support', median expression z-score=0.13, percent high expression=1.25, expression reference='All-sample-reference z-score profile', survival signal='Insufficient high-expression subgroup for survival comparison', matched survival patients=154, high-expression survival n=2, other-expression survival n=152, and median OS difference months=-3.97.

---

## Research-Use Disclaimer

This report is for research and educational use only. It does not provide clinical recommendations, diagnoses, or treatment guidance.
