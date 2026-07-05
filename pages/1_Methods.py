import streamlit as st

st.title("Methods")

st.write(
    """
    OncoEvidence Auditor is designed to evaluate whether a cancer gene hypothesis is
    supported across multiple public-data evidence layers.

    This starter version uses mock evidence values. The scoring framework is intentionally
    transparent and will be updated as real data layers are implemented.
    """
)

st.header("Evidence score")

st.markdown(
    """
    Total score: **100 points**

    - Tumor overexpression or cancer-relevant differential expression: 15
    - Survival association in expected biological direction: 15
    - Independent validation in GEO/external cohort: 20
    - Lineage-specific DepMap dependency: 20
    - Low normal tissue/safety concern: 10
    - Mutation/CNA/pathway support: 10
    - Literature novelty / not oversaturated: 10
    """
)

st.header("Interpretation")

st.markdown(
    """
    - **80–100:** Strong hypothesis
    - **60–79:** Moderate hypothesis
    - **40–59:** Weak or uncertain hypothesis
    - **<40:** Poor hypothesis
    - **Contradictory:** Major evidence layers conflict and need manual review
    """
)

st.header("Disclaimer")

st.warning(
    "This tool is for research and education only. It is not intended for clinical decision-making."
)
