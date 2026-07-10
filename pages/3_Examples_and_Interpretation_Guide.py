"""
Examples and interpretation guide for OncoEvidence Auditor.
"""

from pathlib import Path
import streamlit as st
from src.ui_style import apply_global_style, render_theme_selector


st.set_page_config(
    page_title="Examples & Interpretation Guide",
    page_icon="🧬",
    layout="wide",
)
_theme_mode = render_theme_selector()
apply_global_style(_theme_mode)


st.title("Examples & Interpretation Guide")

st.warning(
    "Research and educational use only. These examples are not diagnostic, prognostic, "
    "or treatment recommendations."
)

st.write(
    """
OncoEvidence Auditor is designed to expose **cross-layer contradictions** in cancer-gene
hypotheses. A gene can look strong in one evidence layer and weak, risky, or ambiguous
in another.

The examples below show two very different but important patterns.
"""
)

st.divider()

st.header("Example 1: OIP5 in GBM")

st.subheader("Pattern: strong dependency, weak patient support, broad essentiality risk")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### Why this case matters")
    st.write(
        """
OIP5 in GBM is useful as a stress test for the auditor because it shows a strong
DepMap dependency signal, but the broader evidence profile weakens a direct target claim.
"""
    )

    st.markdown("### Core interpretation")
    st.info(
        """
OIP5 is best framed as a **broad dependency-associated candidate**, not a selective
patient-supported GBM target.
"""
    )

with col2:
    st.markdown("### Key contradiction labels")
    st.write(
        """
- Broad essentiality risk
- Role-supported broad essentiality risk
- Weak lineage specificity
- Dependency-only signal
- Underpowered survival signal
"""
    )

    st.markdown("### Best next validation")
    st.write(
        """
Test whether OIP5 dependency reflects general proliferation/cell-cycle essentiality
rather than GBM-specific biology.
"""
    )

with st.expander("Open OIP5 / GBM example report"):
    report_path = Path("docs/example_reports/OIP5_GBM_example_report.md")
    if report_path.exists():
        st.markdown(report_path.read_text())
    else:
        st.error("Example report not found. Run: python3 scripts/generate_example_reports.py")

st.divider()

st.header("Example 2: ERBB2 in Gastric Cancer")

st.subheader("Pattern: therapeutic biomarker relevance without strong DepMap dependency")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### Why this case matters")
    st.write(
        """
ERBB2 in gastric cancer shows why therapeutic or biomarker relevance should not be
collapsed into DepMap dependency. Weak cell-line dependency does not mean weak biomarker
importance.
"""
    )

    st.markdown("### Core interpretation")
    st.info(
        """
ERBB2 is best framed as a **patient-supported therapeutic biomarker/subgroup hypothesis**,
not a strong cell-autonomous dependency target.
"""
    )

with col2:
    st.markdown("### Key contradiction labels")
    st.write(
        """
- Alteration-without-dependency signal
- Literature-saturated target
- Subgroup/actionability context
- Expression-defined subgroup signal
- Patient-supported subgroup signal
- No clear prognostic separation
"""
    )

    st.markdown("### Best next validation")
    st.write(
        """
Validate HER2 amplification-expression concordance, protein/IHC or FISH evidence,
subgroup-specific pathway activity, and therapy-response literature.
"""
    )

with st.expander("Open ERBB2 / Gastric cancer example report"):
    report_path = Path("docs/example_reports/ERBB2_Gastric_cancer_example_report.md")
    if report_path.exists():
        st.markdown(report_path.read_text())
    else:
        st.error("Example report not found. Run: python3 scripts/generate_example_reports.py")

st.divider()

st.header("How to interpret the 10-layer evidence profile")

st.write(
    """
A complete evidence profile means the auditor was able to retrieve or annotate all ten
layers. It does **not** mean the gene is a strong target.
"""
)

layers = [
    ("PubMed literature", "How saturated the gene/cancer literature already is."),
    ("DepMap dependency", "Whether cancer models depend on the gene."),
    ("Common-essential caution", "Whether the gene is broadly essential across cancer models."),
    ("Lineage specificity", "Whether the dependency is enriched in the selected cancer type."),
    ("Patient alteration", "Whether patient tumors show mutation, amplification, or deletion support."),
    ("Patient expression", "Whether patient tumors show high-expression subgroup or broad expression support."),
    ("Survival/prognosis", "Whether high expression shows a descriptive survival pattern."),
    ("Gene role classification", "Whether the gene is an oncogene, tumor suppressor, proliferation marker, etc."),
    ("Pathway/function annotation", "Which biological pathway or process gives context to the evidence."),
    ("Therapeutic relevance", "Whether curated biomarker or therapeutic context exists."),
]

st.table(
    [
        {"Layer": layer, "Interpretation purpose": purpose}
        for layer, purpose in layers
    ]
)

st.header("Rule of thumb")

st.success(
    """
The strongest projects are not just the ones with high scores. They are the ones where
the auditor finds a **clear, defensible contradiction** and proposes the right next
validation step.
"""
)
