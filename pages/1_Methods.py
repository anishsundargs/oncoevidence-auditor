import streamlit as st
import pandas as pd

from src.cancer_registry import load_cancer_registry


st.set_page_config(
    page_title="Methods | OncoEvidence Auditor",
    page_icon="🧬",
    layout="wide",
)

st.title("Methods")
st.caption(
    "OncoEvidence Auditor is a public-data cancer bioinformatics tool for auditing "
    "gene/cancer hypotheses across multiple evidence layers."
)

st.warning(
    "Research-use only. This app does not provide clinical recommendations, diagnoses, "
    "or treatment guidance."
)

st.header("Core idea")

st.write(
    """
Most simple cancer bioinformatics projects ask whether a gene looks interesting in one dataset.
OncoEvidence Auditor is designed to ask a stricter question:

**Does the gene/cancer hypothesis remain plausible when checked across independent evidence layers?**

The app is especially focused on detecting contradictions, such as:
- strong cell-line dependency but weak patient-tumor alteration support,
- strong dependency but high common-essential risk,
- literature saturation that makes novelty weak,
- subgroup expression support rather than broad cohort-wide expression support.
"""
)

st.header("Current validated cancer types")

try:
    registry = load_cancer_registry()
    st.dataframe(registry, use_container_width=True)
except Exception as e:
    st.error("Could not load cancer registry.")
    st.code(str(e))

st.header("Evidence layers")

st.subheader("1. PubMed literature saturation")

st.write(
    """
The PubMed module builds a gene/cancer query using cancer-specific terms from the central
cancer registry. It returns the number of matching PubMed records and classifies the pair
as low, moderate, or highly saturated.

This is interpreted as a **novelty/saturation signal**, not as proof that the gene is or is
not biologically important.
"""
)

st.subheader("2. DepMap CRISPR dependency")

st.write(
    """
The DepMap module summarizes CRISPR gene-effect scores for cell lines matching the selected
cancer type. Cancer-specific DepMap filtering is based on OncotreeCode mappings stored in the
central cancer registry.

More negative gene-effect scores indicate stronger dependency. The app reports:
- median dependency score,
- dependent cell-line count,
- total matching cell lines,
- percent dependent,
- dependency label.
"""
)

st.subheader("3. Pan-cancer common-essential caution")

st.write(
    """
Some genes appear essential across many cancer lineages. These genes can look promising in one
cancer type while still being poor selective-target candidates.

The common-essential module compares the gene's dependency pattern across a broad pan-cancer
cell-line background and labels whether the gene has low, moderate, or high common-essential
caution.
"""
)

st.subheader("4. Lineage specificity index")

st.write(
    """
The lineage specificity index compares dependency in the selected cancer type against the
pan-cancer dependency background.

A strong cancer-specific dependency claim is weaker if the selected cancer type is not more
dependent than the pan-cancer background.
"""
)

st.subheader("5. cBioPortal patient-tumor alteration evidence")

st.write(
    """
The cBioPortal alteration module evaluates patient-tumor genomic alteration support using
mutation frequency, high-level amplification frequency, and deep-deletion frequency.

Broad CNA alteration frequency is reported separately, but it does not drive the patient
alteration support label because shallow gains/losses can overstate biological support.
"""
)

st.subheader("6. cBioPortal patient-tumor expression evidence")

st.write(
    """
The cBioPortal expression module summarizes mRNA expression z-score profiles for the selected
gene/cancer pair.

The app reports:
- median expression z-score,
- mean expression z-score,
- percent of tumors with high expression,
- percent of tumors with low expression,
- expression support label,
- expression reference type.

The module distinguishes broad expression support from subgroup high-expression support.
This matters because a gene can define a molecular subgroup without being highly expressed
across the full cohort.
"""
)

st.subheader("7. Auditor Verdict")

st.write(
    """
The Auditor Verdict combines the evidence layers into a cautious synthesis. It does not claim
that a gene is a treatment target. Instead, it produces a safer research interpretation, such as:

- candidate selective vulnerability,
- broad dependency-associated candidate,
- specificity-risk hypothesis,
- weak patient-support hypothesis,
- literature-saturated hypothesis.

The verdict includes strengths, warnings, and a safe claim statement so the output is less likely
to overstate evidence from one dataset.
"""
)


st.subheader("8. Batch Audit Mode")

st.write(
    """
Batch Audit Mode screens all curated genes for a selected cancer type. Fast mode uses
processed local evidence layers, while optional live modes add PubMed literature saturation
and cBioPortal patient alteration/expression evidence.

The batch table reports:
- DepMap dependency label,
- percent dependent,
- common-essential caution,
- lineage specificity label,
- specificity delta,
- contradiction pattern,
- auditor verdict tier,
- main warning.

This mode is designed to help identify which genes deserve deeper single-gene review.
The batch table also reports evidence coverage so incomplete profiles are not overinterpreted.
It is not a final biological conclusion by itself. For final interpretation, the single-gene
page and downloadable Markdown evidence report should be used.
"""
)


st.subheader("9. Evidence Coverage Score")

st.write(
    """
The Evidence Coverage Score reports how many major evidence layers are available for a
gene/cancer analysis.

Current coverage layers:
- PubMed literature saturation,
- DepMap dependency,
- pan-cancer common-essential caution,
- lineage specificity,
- cBioPortal patient alteration evidence,
- cBioPortal patient expression evidence.

This prevents the app from treating complete and incomplete evidence profiles as equally strong.
A result with missing patient evidence, for example, should be interpreted more cautiously than
a result supported across all major layers.
"""
)

st.header("Central cancer registry")

st.write(
    """
Cancer-specific mappings are centralized in:

`data/config/cancer_registry.csv`

This file stores:
- display cancer type,
- cBioPortal study candidates,
- DepMap OncotreeCode filters,
- PubMed cancer query terms.

This makes the project scalable because adding new cancer types requires updating one registry
rather than hard-coding mappings across multiple modules.
"""
)

st.header("Current limitations")

st.write(
    """
Important limitations:
- The app is hypothesis-generating only.
- Public datasets have batch effects, missingness, and cohort biases.
- DepMap cell-line dependency does not automatically imply patient therapeutic relevance.
- cBioPortal alteration and expression signals do not prove causality.
- Survival, pathway, immune, drug-sensitivity, and experimental validation layers are not yet included.
- Current validated case studies are GBM and gastric cancer.
"""
)

st.header("Best-use framing")

st.success(
    """
Best framing: OncoEvidence Auditor is a contradiction-aware cancer bioinformatics screening tool.
It helps identify when a gene/cancer hypothesis is supported, weak, oversaturated, non-specific,
or potentially overclaimed.
"""
)
