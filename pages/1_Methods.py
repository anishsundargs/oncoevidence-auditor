import streamlit as st

st.title("Methods")

st.write(
    """
    **OncoEvidence Auditor** is a contradiction-aware cancer bioinformatics tool
    for evaluating whether a gene/cancer hypothesis is supported, weak, saturated,
    broadly essential, or lineage-specific based on public-data evidence layers.
    """
)

st.warning(
    "This tool is for research and education only. It is not a diagnostic, prognostic, or treatment recommendation system."
)

st.header("Current evidence layers")

st.markdown(
    """
    ### 1. Curated evidence-card layer

    The main evidence card currently uses a curated local table:

    `data/mock_gene_evidence.csv`

    This layer is used for early testing of the scoring rubric and claim-generation logic.
    It should not be treated as fully automated public-data evidence yet.

    ### 2. PubMed literature saturation

    The PubMed module uses NCBI ESearch to count how many PubMed title/abstract records
    match a selected gene/cancer pair.

    This is used as a **literature saturation / novelty-risk signal**, not as proof
    of biological importance.

    ### 3. DepMap dependency signal

    The DepMap module uses a processed subset derived from:

    `CRISPRGeneEffect.csv`

    The app calculates, for each selected gene/cancer pair:

    - median dependency score
    - number of dependent models
    - total models in the selected cancer group
    - percent dependent models
    - dependency strength label

    More negative gene-effect scores indicate stronger loss-of-viability dependency.

    ### 4. Exact Oncotree cancer-group filtering

    The current processed DepMap subset uses exact OncotreeCode filters:

    - **GBM:** `GB`
    - **Gastric cancer:** `STAD`, `DSTAD`, `TSTAD`, `MSTAD`, `SSRCC`, `STSC`, `STAS`

    This avoids broad keyword matching that could accidentally include unrelated CNS,
    esophageal, or non-cancerous models.

    ### 5. Common-essential caution

    The common-essential module compares a gene against all cancer models in the
    DepMap CRISPRGeneEffect matrix.

    It flags genes whose strong dependency signal may reflect broad cellular essentiality
    rather than cancer-lineage-specific vulnerability.

    ### 6. Lineage specificity index

    The lineage specificity index compares:

    `selected cancer percent dependent - pan-cancer percent dependent`

    Positive values suggest cancer-lineage enrichment. Values near zero suggest
    the gene may be broadly dependency-associated rather than cancer-specific.

    ### 7. Auditor verdict

    The auditor verdict synthesizes:

    - PubMed saturation
    - selected-cancer dependency
    - pan-cancer common-essential risk
    - lineage specificity

    The output is a conservative research interpretation, not a clinical claim.
    """
)

st.header("Current scoring rubric")

st.markdown(
    """
    The early evidence-card score uses a transparent 100-point rubric:

    - Tumor expression or cancer-relevant differential expression: 15
    - Survival association in expected biological direction: 15
    - Independent validation in GEO/external cohort: 20
    - Lineage-specific DepMap dependency: 20
    - Low normal tissue/safety concern: 10
    - Mutation/CNA/pathway support: 10
    - Literature novelty / not oversaturated: 10

    This rubric is not clinically validated. It is used for hypothesis triage.
    """
)

st.header("Interpretation limits")

st.markdown(
    """
    A strong dependency result does **not** automatically mean a gene is a therapeutic target.

    Key limitations:

    - CRISPR dependency does not prove druggability.
    - Pan-cancer essential genes may be poor selective targets.
    - Cell-line dependency may not translate directly to patient tumors.
    - PubMed count is a rough saturation signal, not a formal novelty analysis.
    - The current expression/survival layers are not fully automated yet.
    - All outputs are hypothesis-generating only.
    """
)

st.header("Current strongest use case")

st.write(
    """
    The current version is strongest for identifying when a gene looks promising from one
    evidence layer but becomes weaker after checking broad essentiality, saturation, or
    lineage specificity. This is the main novelty of the tool.
    """
)
