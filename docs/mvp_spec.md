# MVP Specification: OncoEvidence Auditor

## Product thesis

Cancer bioinformatics beginners often overclaim from isolated database results. OncoEvidence Auditor helps users evaluate whether a cancer gene hypothesis is supported, weak, or contradictory across public-data layers.

## First MVP

### Supported cancer types
- GBM
- Gastric cancer

### Supported genes for first test set
- OIP5
- TP53
- EGFR
- MGMT
- IDH1
- ATRX
- CDK4
- MDM2
- PDGFRA
- MET
- ERBB2
- MYC

### Evidence layers
- Tumor expression signal
- Survival association
- Independent validation
- DepMap dependency
- Normal tissue/safety concern
- Mutation/CNA/pathway support

## Scoring rubric, v0.1

Total: 100 points

- Tumor overexpression or cancer-relevant differential expression: 15
- Survival association in biologically expected direction: 15
- Independent validation in GEO or external cohort: 20
- Lineage-specific DepMap dependency: 20
- Low normal tissue/safety concern: 10
- Mutation/CNA/pathway support: 10
- Novelty/not oversaturated: 10

## Evidence tiers

- 80–100: Strong hypothesis
- 60–79: Moderate hypothesis
- 40–59: Weak or uncertain hypothesis
- <40: Poor hypothesis
- Automatic override: Contradictory if major evidence directions conflict.

## Contradiction flags

Examples:
- Tumor expression high but survival association protective
- Strong DepMap dependency but no patient tumor signal
- Strong survival signal but no external validation
- Strong dependency but likely common-essential gene
- High tumor expression but high normal tissue expression
