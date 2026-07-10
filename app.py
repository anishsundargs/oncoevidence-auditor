import pandas as pd
import plotly.express as px
from src.survival_figures import plot_km_survival, plot_median_os_bar, plot_event_rate_bar
from src.evidence_figures import (
    plot_evidence_coverage_gauge,
    plot_evidence_layer_bar,
    plot_dependency_context_bar,
    plot_dependency_score_context_bar,
    plot_specificity_delta_indicator,
    plot_patient_alteration_bar,
    plot_patient_expression_bar,
    plot_expression_summary_bar,
)
import streamlit as st
from src.catalog_summary import get_catalog_summary

from src.evidence_coverage import calculate_evidence_coverage

from src.report_builder import build_markdown_report

from src.cancer_registry import list_supported_cancers

from src.evidence_scoring import calculate_score, classify_tier, generate_flags, generate_safe_claim
from src.pubmed_saturation import get_pubmed_count, classify_literature_saturation
from src.depmap_dependency import get_dependency_result, get_depmap_data_source_label
from src.common_essential import get_common_essential_result
from src.auditor_verdict import build_auditor_verdict
from src.specificity_index import calculate_specificity_index
from src.cbioportal_alterations import get_cbioportal_alteration_summary
from src.cbioportal_expression import get_cbioportal_expression_summary
from src.cbioportal_survival import get_cbioportal_survival_summary
from src.gene_role import get_gene_role_summary
from src.pathway_function import get_pathway_function_summary
from src.therapeutic_relevance import get_therapeutic_relevance_summary
from src.live_evidence_score import build_live_evidence_score


st.set_page_config(
    page_title="OncoEvidence Auditor",
    page_icon="🧬",
    layout="wide"
)

st.title("OncoEvidence Auditor")

catalog_summary = get_catalog_summary()

if catalog_summary.get("available"):
    st.markdown("### Pan-cancer catalog scale")

    cat_col1, cat_col2, cat_col3, cat_col4 = st.columns(4)

    with cat_col1:
        st.metric("Cancer types", catalog_summary["supported_cancer_types"])

    with cat_col2:
        st.metric("Unique genes", catalog_summary["unique_genes"])

    with cat_col3:
        st.metric("Gene-cancer hypotheses", catalog_summary["gene_cancer_pairs"])

    with cat_col4:
        st.metric("Median genes/cancer", catalog_summary["median_genes_per_cancer"])

    st.caption(catalog_summary["note"])

    with st.expander("Show catalog size by cancer type"):
        st.dataframe(
            catalog_summary["genes_per_cancer"],
            use_container_width=True,
            hide_index=True,
        )

    st.divider()
st.caption("Contradiction-aware cancer gene hypothesis triage using public-data evidence layers.")

st.warning(
    "Research/education only. This tool is not a diagnostic, prognostic, or treatment recommendation system.",
    icon="⚠️"
)


@st.cache_data
def load_mock_data():
    return pd.read_csv("data/mock_gene_evidence.csv")


@st.cache_data(show_spinner=False)
def cached_pubmed_count(gene, cancer_type):
    return get_pubmed_count(gene, cancer_type)


df = load_mock_data()

with st.sidebar:
    st.header("Input")
    cancer_type = st.selectbox("Cancer type", list_supported_cancers())
    genes = sorted(df.loc[df["cancer_type"] == cancer_type, "gene"].unique())
    gene = st.selectbox("Gene", genes)

    st.divider()
    st.subheader("MVP Status")
    st.write("Main evidence card still uses curated mock values.")
    st.write("PubMed literature saturation is now a live data layer using NCBI ESearch.")

row = df[(df["gene"] == gene) & (df["cancer_type"] == cancer_type)].iloc[0].to_dict()

score, breakdown = calculate_score(row)
flags = generate_flags(row)
tier = classify_tier(score, flags)
safe_claim = generate_safe_claim(row, score, tier)

# Preload PubMed values early so the Auditor Verdict can use them.
pubmed_count = None
pubmed_query = None
saturation_label = None
inferred_novelty = None
saturation_note = None

try:
    pubmed_count, pubmed_query = cached_pubmed_count(gene, cancer_type)
    saturation_label, inferred_novelty, saturation_note = classify_literature_saturation(pubmed_count)
except Exception:
    pass

col1, col2, col3 = st.columns([1, 1, 1])

with col1:
    st.metric("Static catalog score", f"{score}/100")
    st.caption("Curated local prior; not the final auditor verdict.")

with col2:
    st.metric("Evidence tier", tier)

with col3:
    st.metric("Cancer type", cancer_type)

st.divider()

st.subheader(f"Evidence Card: {gene} in {cancer_type}")

left, right = st.columns([1.1, 1])

with left:
    st.markdown("### Evidence layer summary")
    evidence_table = pd.DataFrame(
        [
            ["Tumor expression", row["tumor_expression"]],
            ["Survival association", row["survival_association"]],
            ["External/GEO validation", row["geo_validation"]],
            ["DepMap dependency", row["depmap_dependency"]],
            ["Normal tissue safety", row["normal_tissue_safety"]],
            ["Mutation/CNA/pathway support", row["mutation_cna_support"]],
            ["Novelty score", row["novelty_score"]],
        ],
        columns=["Evidence layer", "Current result"]
    )
    st.dataframe(evidence_table, use_container_width=True, hide_index=True)

    st.markdown("### Notes")
    st.write(row["notes"])

with right:
    st.markdown("### Score breakdown")
    plot_df = pd.DataFrame(
        {"Component": list(breakdown.keys()), "Points": list(breakdown.values())}
    )
    fig = px.bar(plot_df, x="Points", y="Component", orientation="h", range_x=[0, 20])
    fig.update_layout(height=420, margin=dict(l=10, r=10, t=20, b=10))
    st.plotly_chart(fig, use_container_width=True)

st.divider()

st.subheader("DepMap Dependency Signal")

depmap_result = get_dependency_result(gene, cancer_type)

if depmap_result["available"]:
    d1, d2, d3 = st.columns(3)

    with d1:
        st.metric("Median dependency score", depmap_result["median_dependency_score"])

    with d2:
        st.metric(
            "Dependent cell lines",
            f'{depmap_result["dependent_cell_lines"]}/{depmap_result["total_cell_lines"]}'
        )

    with d3:
        st.metric("Dependency label", depmap_result["dependency_label"])

    st.write(f'Percent dependent: **{depmap_result["percent_dependent"]}%**')
    st.write(depmap_result["dependency_note"])

    st.caption(f"Active dependency data source: {depmap_result['data_source']}")
else:
    st.warning(depmap_result["dependency_note"])

st.subheader("Common-Essential / Specificity Caution")

common_result = get_common_essential_result(gene)

if common_result["available"]:
    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric(
            "Pan-cancer median dependency",
            common_result["pan_cancer_median_dependency_score"]
        )

    with c2:
        st.metric(
            "Pan-cancer dependent models",
            f'{common_result["pan_cancer_dependent_cell_lines"]}/{common_result["pan_cancer_total_cell_lines"]}'
        )

    with c3:
        st.metric(
            "Common-essential label",
            common_result["common_essential_label"]
        )

    st.write(f'Pan-cancer percent dependent: **{common_result["pan_cancer_percent_dependent"]}%**')
    st.warning(common_result["common_essential_note"])
else:
    st.info(common_result["common_essential_note"])

st.markdown("### Dependency context visualization")

dep_fig_col1, dep_fig_col2 = st.columns(2)

with dep_fig_col1:
    dependency_context_fig = plot_dependency_context_bar(depmap_result, common_result)
    if dependency_context_fig is not None:
        st.plotly_chart(dependency_context_fig, use_container_width=True)

with dep_fig_col2:
    dependency_score_fig = plot_dependency_score_context_bar(depmap_result, common_result)
    if dependency_score_fig is not None:
        st.plotly_chart(dependency_score_fig, use_container_width=True)

_figure_specificity_result = locals().get("specificity_result")

if _figure_specificity_result is None:
    try:
        _figure_specificity_result = calculate_specificity_index(depmap_result, common_result)
    except Exception:
        _figure_specificity_result = None

specificity_indicator_fig = plot_specificity_delta_indicator(_figure_specificity_result)
if specificity_indicator_fig is not None:
    st.plotly_chart(specificity_indicator_fig, use_container_width=True)

st.caption(
    "Dependency context figures compare the selected cancer against the pan-cancer background. "
    "A strong selected-cancer dependency with similarly strong pan-cancer dependency may indicate broad essentiality rather than lineage specificity."
)

st.subheader("Lineage Specificity Index")

specificity_result = calculate_specificity_index(depmap_result, common_result)

if specificity_result["available"]:
    s1, s2, s3 = st.columns(3)

    with s1:
        st.metric("Selected-cancer % dependent", depmap_result["percent_dependent"])

    with s2:
        st.metric("Pan-cancer % dependent", common_result["pan_cancer_percent_dependent"])

    with s3:
        st.metric("Specificity delta", specificity_result["specificity_delta"])

    st.metric("Specificity label", specificity_result["specificity_label"])
    st.info(specificity_result["specificity_note"])
else:
    st.info(specificity_result["specificity_note"])

st.subheader("cBioPortal Patient-Tumor Alteration Evidence")

@st.cache_data(show_spinner=False)
def cached_cbioportal_summary(gene, cancer_type):
    return get_cbioportal_alteration_summary(gene, cancer_type)

try:
    with st.spinner("Querying cBioPortal patient-tumor alteration data..."):
        cbio_result = cached_cbioportal_summary(gene, cancer_type)

    if cbio_result["available"]:
        b1, b2, b3 = st.columns(3)

        with b1:
            st.metric("Mutation frequency", f'{cbio_result["mutation_frequency"]}%')

        with b2:
            st.metric("Amplification frequency", f'{cbio_result["amplification_frequency"]}%')

        with b3:
            st.metric("Patient alteration support", cbio_result["patient_alteration_support"])

        b4, b5, b6 = st.columns(3)

        with b4:
            st.metric("Deep deletion frequency", f'{cbio_result["deep_deletion_frequency"]}%')

        with b5:
            st.metric("Broad CNA altered frequency", f'{cbio_result["cna_alteration_frequency"]}%')

        with b6:
            st.metric("Study samples", cbio_result["total_samples"])

        st.write(f'Study: `{cbio_result["study_id"]}`')
        st.write(f'Mutation profile: `{cbio_result["mutation_profile_id"]}`')
        st.write(f'CNA profile: `{cbio_result["cna_profile_id"]}`')
        st.caption(cbio_result["note"])

        if cbio_result["patient_alteration_support"] == "Little or no patient alteration support":
            st.warning(
                "Patient-tumor alteration support is weak by mutation/high-level amplification/deep-deletion criteria. "
                "Do not frame this gene as genomically altered in this cancer without another evidence layer."
            )
        elif cbio_result["patient_alteration_support"] == "Moderate patient alteration support":
            st.info(
                "Patient-tumor alteration support is moderate. This may support a genomically altered subgroup hypothesis."
            )
        else:
            st.success(
                "Patient-tumor alteration support is strong by mutation/high-level amplification/deep-deletion criteria."
            )

    else:
        st.info(cbio_result["note"])

except Exception as e:
    cbio_result = {"available": False, "note": str(e)}
    st.error("cBioPortal module failed. Check internet connection or cBioPortal API availability.")
    st.code(str(e))

st.divider()


st.markdown("### Patient alteration visualization")

alteration_fig = plot_patient_alteration_bar(cbio_result if "cbio_result" in locals() else {})
if alteration_fig is not None:
    st.plotly_chart(alteration_fig, use_container_width=True)
else:
    st.info("Patient alteration figure unavailable for this run.")

st.divider()

st.subheader("cBioPortal Patient-Tumor Expression Evidence")

@st.cache_data(show_spinner=False)
def cached_cbioportal_expression(gene, cancer_type):
    return get_cbioportal_expression_summary(gene, cancer_type)

try:
    with st.spinner("Querying cBioPortal patient-tumor expression data..."):
        expr_result = cached_cbioportal_expression(gene, cancer_type)

    if expr_result["available"]:
        e1, e2, e3 = st.columns(3)

        with e1:
            st.metric("Median expression z-score", expr_result["median_expression_zscore"])

        with e2:
            st.metric("High-expression tumors", f'{expr_result["percent_high_expression"]}%')

        with e3:
            st.metric("Expression support", expr_result["expression_support"])

        e4, e5, e6 = st.columns(3)

        with e4:
            st.metric("Mean expression z-score", expr_result["mean_expression_zscore"])

        with e5:
            st.metric("Low-expression tumors", f'{expr_result["percent_low_expression"]}%')

        with e6:
            st.metric("Expression samples", expr_result["expression_sample_count"])

        st.write(f'Expression profile: `{expr_result["expression_profile_id"]}`')
        st.write(f'Reference type: **{expr_result["expression_reference"]}**')
        st.caption(expr_result["note"])

        if expr_result["expression_support"] in {"High broad expression support", "Moderate expression support"}:
            st.success("Patient expression evidence supports a tumor-expression hypothesis.")
        elif expr_result["expression_support"] == "Subgroup high-expression support":
            st.info("Expression evidence supports a subgroup-level expression hypothesis, not a broad pan-cohort expression claim.")
        elif expr_result["expression_support"] == "Low-expression signal":
            st.warning("Expression evidence suggests low expression in a meaningful subset or cohort-level downshift.")
        else:
            st.warning("Patient expression evidence is weak by the current z-score criteria.")

    else:
        st.info(expr_result["note"])

except Exception as e:
    expr_result = {"available": False, "note": str(e)}
    st.error("cBioPortal expression module failed. Check internet connection or cBioPortal API availability.")
    st.code(str(e))

st.divider()


st.markdown("### Patient expression visualization")

expr_fig_col1, expr_fig_col2 = st.columns(2)

with expr_fig_col1:
    expression_bar_fig = plot_patient_expression_bar(expr_result if "expr_result" in locals() else {})
    if expression_bar_fig is not None:
        st.plotly_chart(expression_bar_fig, use_container_width=True)

with expr_fig_col2:
    expression_summary_fig = plot_expression_summary_bar(expr_result if "expr_result" in locals() else {})
    if expression_summary_fig is not None:
        st.plotly_chart(expression_summary_fig, use_container_width=True)

if not (expr_result if "expr_result" in locals() else {}).get("available"):
    st.info("Patient expression figures unavailable for this run.")

st.divider()

st.subheader("Auditor Verdict")

try:
    _live_score_contradiction_result = build_contradiction_labels(
        gene=gene,
        cancer_type=cancer_type,
        depmap_result=depmap_result,
        common_result=common_result,
        specificity_result=specificity_result,
        cbio_result=cbio_result,
        expression_result=expr_result,
        survival_result=survival_result if "survival_result" in locals() else {},
        gene_role_result=gene_role_result if "gene_role_result" in locals() else {},
        saturation_label=saturation_label if "saturation_label" in locals() else None,
    )
except Exception:
    _live_score_contradiction_result = {}

try:
    _live_score_therapeutic_result = therapeutic_result
except Exception:
    _live_score_therapeutic_result = {}

live_score_result = build_live_evidence_score(
    depmap_result=depmap_result,
    common_result=common_result,
    specificity_result=specificity_result,
    cbio_result=cbio_result,
    expression_result=expr_result,
    survival_result=survival_result if "survival_result" in locals() else {},
    therapeutic_result=_live_score_therapeutic_result,
    contradiction_result=_live_score_contradiction_result,
)

live_col1, live_col2 = st.columns(2)
with live_col1:
    st.metric("Live evidence score", f"{live_score_result['live_evidence_score']}/100")
with live_col2:
    st.metric("Live evidence tier", live_score_result["live_evidence_tier"])

st.caption(live_score_result["interpretation_note"])

with st.expander("Show live evidence score breakdown"):
    st.dataframe(
        [
            {"Evidence component": key, "Points": value}
            for key, value in live_score_result["breakdown"].items()
        ],
        use_container_width=True,
    )


if pubmed_count is not None and saturation_label is not None:
    verdict = build_auditor_verdict(
        gene=gene,
        cancer_type=cancer_type,
        pubmed_count=pubmed_count,
        saturation_label=saturation_label,
        depmap_result=depmap_result,
        common_result=common_result,
        specificity_result=specificity_result,
        cbio_result=cbio_result if "cbio_result" in locals() else None,
        expression_result=expr_result if "expr_result" in locals() else None,
        survival_result=survival_result if "survival_result" in locals() else None,
    )

    st.metric("Final hypothesis tier", verdict["verdict_tier"])

    st.markdown("### Evidence strengths")
    if verdict["strengths"]:
        for item in verdict["strengths"]:
            st.success(item)
    else:
        st.info("No major strengths detected by the current auditor logic.")

    st.markdown("### Evidence warnings")
    if verdict["warnings"]:
        for item in verdict["warnings"]:
            st.warning(item)
    else:
        st.success("No major warnings detected by the current auditor logic.")

    st.markdown("### Conservative claim")
    st.info(verdict["safe_claim"])

    with st.expander("Auditor methods note"):
        st.write(verdict["methods_note"])

else:
    st.info("Auditor verdict will appear after PubMed and dependency modules finish loading.")

st.divider()

st.divider()

st.subheader("Live PubMed Literature Saturation")

try:
    with st.spinner("Querying PubMed through NCBI ESearch..."):
        pubmed_count, pubmed_query = cached_pubmed_count(gene, cancer_type)

    saturation_label, inferred_novelty, saturation_note = classify_literature_saturation(pubmed_count)

    p1, p2, p3 = st.columns(3)

    with p1:
        st.metric("PubMed count", pubmed_count)

    with p2:
        st.metric("Literature saturation", saturation_label)

    with p3:
        st.metric("Inferred novelty", inferred_novelty)

    st.write(saturation_note)

    with st.expander("Show PubMed query"):
        st.code(pubmed_query)

except Exception as e:
    st.error("PubMed module failed. Check your internet connection or try again later.")
    st.code(str(e))

st.divider()

st.subheader("Contradiction and caution flags")
for flag in flags:
    st.write(f"- {flag}")

st.subheader("Safe research claim")
st.info(safe_claim)

st.divider()

st.subheader("Exportable summary")

summary = {
    "gene": gene,
    "cancer_type": cancer_type,
    "score": score,
    "tier": tier,
    "pubmed_count": pubmed_count if "pubmed_count" in locals() else None,
    "depmap_dependency_label": depmap_result.get("dependency_label") if "depmap_result" in locals() else None,
    "depmap_median_dependency_score": depmap_result.get("median_dependency_score") if "depmap_result" in locals() else None,
    "depmap_percent_dependent": depmap_result.get("percent_dependent") if "depmap_result" in locals() else None,
    "common_essential_label": common_result.get("common_essential_label") if "common_result" in locals() else None,
    "pan_cancer_percent_dependent": common_result.get("pan_cancer_percent_dependent") if "common_result" in locals() else None,
    "specificity_delta": specificity_result.get("specificity_delta") if "specificity_result" in locals() else None,
    "specificity_label": specificity_result.get("specificity_label") if "specificity_result" in locals() else None,
    "auditor_verdict_tier": verdict.get("verdict_tier") if "verdict" in locals() else None,
    "auditor_safe_claim": verdict.get("safe_claim") if "verdict" in locals() else None,
    "cbioportal_patient_alteration_support": cbio_result.get("patient_alteration_support") if "cbio_result" in locals() else None,
    "cbioportal_mutation_frequency": cbio_result.get("mutation_frequency") if "cbio_result" in locals() else None,
    "cbioportal_amplification_frequency": cbio_result.get("amplification_frequency") if "cbio_result" in locals() else None,
    "cbioportal_expression_support": expr_result.get("expression_support") if "expr_result" in locals() else None,
    "cbioportal_median_expression_zscore": expr_result.get("median_expression_zscore") if "expr_result" in locals() else None,
    "cbioportal_percent_high_expression": expr_result.get("percent_high_expression") if "expr_result" in locals() else None,
    "literature_saturation": saturation_label if "saturation_label" in locals() else None,
    "inferred_novelty": inferred_novelty if "inferred_novelty" in locals() else None,
    "flags": flags,
    "safe_claim": safe_claim,
}

st.download_button(
    label="Download evidence summary as JSON",
    data=pd.Series(summary).to_json(indent=2),
    file_name=f"{gene}_{cancer_type}_evidence_summary.json",
    mime="application/json"
)




st.subheader("cBioPortal Survival / Prognosis Evidence")

@st.cache_data(show_spinner=False)
def cached_cbioportal_survival(gene, cancer_type):
    return get_cbioportal_survival_summary(gene, cancer_type)

try:
    with st.spinner("Querying cBioPortal survival/prognosis data..."):
        survival_result = cached_cbioportal_survival(gene, cancer_type)

    if survival_result["available"]:
        s1, s2, s3 = st.columns(3)

        with s1:
            st.metric("Survival patients matched", survival_result["survival_patients_matched"])

        with s2:
            st.metric("High-expression survival n", survival_result["high_expression_survival_n"])

        with s3:
            st.metric("Survival signal", survival_result["survival_signal"])

        s4, s5, s6 = st.columns(3)

        with s4:
            st.metric("High-expression median OS", f'{survival_result["high_expression_median_os_months"]} months')

        with s5:
            st.metric("Other-expression median OS", f'{survival_result["other_expression_median_os_months"]} months')

        with s6:
            st.metric("Median OS difference", f'{survival_result["median_os_difference_months"]} months')

        st.caption(survival_result["note"])

        if survival_result.get("survival_records"):
            st.markdown("### Survival figures")

            km_fig = plot_km_survival(survival_result)
            if km_fig is not None:
                st.plotly_chart(km_fig, use_container_width=True)

            fig_col1, fig_col2 = st.columns(2)

            with fig_col1:
                median_fig = plot_median_os_bar(survival_result)
                if median_fig is not None:
                    st.plotly_chart(median_fig, use_container_width=True)

            with fig_col2:
                event_fig = plot_event_rate_bar(survival_result)
                if event_fig is not None:
                    st.plotly_chart(event_fig, use_container_width=True)

            st.caption("These figures are descriptive visualizations from cBioPortal patient records and do not replace formal prognostic modeling.")
        else:
            st.info("Patient-level survival records were not returned, so survival figures are unavailable for this run.")

        if survival_result["survival_signal"] == "High-expression subgroup shows worse-survival signal":
            st.warning("High-expression tumors show a worse-survival descriptive signal.")
        elif survival_result["survival_signal"] == "High-expression subgroup shows better-survival signal":
            st.info("High-expression tumors show a better-survival descriptive signal.")
        elif "Insufficient" in survival_result["survival_signal"]:
            st.warning("Survival comparison is underpowered because one expression group is too small.")
        elif survival_result["survival_signal"] == "No clear median-survival separation":
            st.info("No clear median-survival separation was detected by this descriptive screen.")
        else:
            st.info(survival_result["survival_signal"])

    else:
        st.info(survival_result["note"])

except Exception as e:
    survival_result = {"available": False, "note": str(e)}
    st.error("cBioPortal survival module failed. Check internet connection or cBioPortal API availability.")
    st.code(str(e))

st.divider()

st.subheader("Gene Role Classification")

_role_gene = locals().get("gene") or locals().get("selected_gene") or locals().get("gene_input")
_role_common_result = locals().get("common_result")

if _role_gene:
    gene_role_result = get_gene_role_summary(_role_gene, _role_common_result)

    role_col1, role_col2 = st.columns(2)

    with role_col1:
        st.markdown("**Role category**")
        st.write(gene_role_result.get("role_category", "Not available"))

        st.markdown("**Target class**")
        st.write(gene_role_result.get("target_class", "Not available"))

        st.markdown("**Biological process**")
        st.write(gene_role_result.get("biological_process", "Not available"))

    with role_col2:
        st.markdown("**Role-based caution**")
        st.write(gene_role_result.get("role_risk_label", "Not available"))

        st.markdown("**Role caution severity**")
        st.write(gene_role_result.get("role_risk_severity", "Not available"))

    with st.expander("Gene role interpretation note"):
        st.write(gene_role_result.get("interpretation_note", "Not available"))
        st.write(gene_role_result.get("role_risk_note", "Not available"))
else:
    st.info("Gene role classification is unavailable because no gene was selected.")
st.subheader("Pathway / Function Annotation")

_pathway_gene = locals().get("gene") or locals().get("selected_gene") or locals().get("gene_input")
_pathway_common_result = locals().get("common_result")

if _pathway_gene:
    pathway_result = get_pathway_function_summary(_pathway_gene, _pathway_common_result)

    pathway_col1, pathway_col2 = st.columns(2)

    with pathway_col1:
        st.markdown("**Pathway category**")
        st.write(pathway_result.get("pathway_category", "Not available"))

        st.markdown("**Function group**")
        st.write(pathway_result.get("function_group", "Not available"))

        st.markdown("**Pathway process**")
        st.write(pathway_result.get("pathway_process", "Not available"))

    with pathway_col2:
        st.markdown("**Pathway caution**")
        st.write(pathway_result.get("pathway_caution_label", "Not available"))

        st.markdown("**Pathway caution severity**")
        st.write(pathway_result.get("pathway_caution_severity", "Not available"))

    with st.expander("Pathway/function interpretation note"):
        st.write(pathway_result.get("interpretive_use", "Not available"))
        st.write(pathway_result.get("pathway_caution_note", "Not available"))
        st.markdown("**Suggested validation**")
        st.write(pathway_result.get("validation_suggestions", "Not available"))
else:
    st.info("Pathway/function annotation is unavailable because no gene was selected.")
st.subheader("Drug / Therapeutic Relevance Annotation")

_therapeutic_gene = locals().get("gene") or locals().get("selected_gene") or locals().get("gene_input")
_therapeutic_cancer = locals().get("cancer_type") or locals().get("selected_cancer") or locals().get("cancer")
_therapeutic_depmap_result = locals().get("depmap_result")
_therapeutic_cbio_result = locals().get("cbio_result")
_therapeutic_expression_result = locals().get("expression_result")

if _therapeutic_gene and _therapeutic_cancer:
    therapeutic_result = get_therapeutic_relevance_summary(
        _therapeutic_gene,
        _therapeutic_cancer,
        depmap_result=_therapeutic_depmap_result,
        cbio_result=_therapeutic_cbio_result,
        expression_result=_therapeutic_expression_result,
    )

    therapeutic_col1, therapeutic_col2 = st.columns(2)

    with therapeutic_col1:
        st.markdown("**Therapeutic relevance**")
        st.write(therapeutic_result.get("therapeutic_relevance", "Not available"))

        st.markdown("**Biomarker type**")
        st.write(therapeutic_result.get("biomarker_type", "Not available"))

        st.markdown("**Dependency/actionability alignment**")
        st.write(therapeutic_result.get("therapeutic_alignment_label", "Not available"))

    with therapeutic_col2:
        st.markdown("**Alignment severity**")
        st.write(therapeutic_result.get("therapeutic_alignment_severity", "Not available"))

        st.markdown("**Therapeutic caution**")
        st.write(therapeutic_result.get("therapeutic_caution", "Not available"))

    with st.expander("Therapeutic relevance interpretation note"):
        st.markdown("**Therapeutic context**")
        st.write(therapeutic_result.get("therapeutic_context", "Not available"))

        st.markdown("**Dependency interpretation**")
        st.write(therapeutic_result.get("dependency_interpretation", "Not available"))

        st.markdown("**Alignment note**")
        st.write(therapeutic_result.get("therapeutic_alignment_note", "Not available"))

        st.markdown("**Suggested validation**")
        st.write(therapeutic_result.get("validation_suggestions", "Not available"))

        st.warning("Research triage only. This section does not provide treatment recommendations.")
else:
    st.info("Therapeutic relevance annotation is unavailable because no gene/cancer pair was selected.")
st.subheader("Evidence Coverage")


# Precompute interpretation-layer annotations before evidence coverage.
# Coverage depends on these being available.
# This block uses defensive local-variable lookup because app.py has evolved over time.
_coverage_gene = (
    locals().get("gene")
    or locals().get("selected_gene")
    or locals().get("gene_input")
    or locals().get("input_gene")
)

_coverage_cancer = (
    locals().get("cancer_type")
    or locals().get("selected_cancer")
    or locals().get("cancer")
    or locals().get("selected_cancer_type")
)

_coverage_common_result = (
    locals().get("common_result")
    or locals().get("common_essential_result")
)

_coverage_depmap_result = (
    locals().get("depmap_result")
    or locals().get("dependency_result")
)

_coverage_cbio_result = (
    locals().get("cbio_result")
    or locals().get("cbioportal_result")
    or locals().get("alteration_result")
)

_coverage_expression_result = (
    locals().get("expression_result")
    or locals().get("expr_result")
    or locals().get("expression_summary")
    or locals().get("cbio_expression_result")
)

try:
    gene_role_result = get_gene_role_summary(_coverage_gene, _coverage_common_result) if _coverage_gene else None
except Exception as e:
    gene_role_result = None
    st.warning(f"Gene role coverage layer unavailable: {e}")

try:
    pathway_result = get_pathway_function_summary(_coverage_gene, _coverage_common_result) if _coverage_gene else None
except Exception as e:
    pathway_result = None
    st.warning(f"Pathway/function coverage layer unavailable: {e}")

try:
    therapeutic_result = (
        get_therapeutic_relevance_summary(
            _coverage_gene,
            _coverage_cancer,
            depmap_result=_coverage_depmap_result,
            cbio_result=_coverage_cbio_result,
            expression_result=_coverage_expression_result,
        )
        if _coverage_gene and _coverage_cancer
        else None
    )
except Exception as e:
    therapeutic_result = None
    st.warning(f"Therapeutic relevance coverage layer unavailable: {e}")


coverage_result = calculate_evidence_coverage(
    pubmed_count=pubmed_count if "pubmed_count" in locals() else None,
    depmap_result=depmap_result if "depmap_result" in locals() else None,
    common_result=common_result if "common_result" in locals() else None,
    specificity_result=specificity_result if "specificity_result" in locals() else None,
    cbio_result=cbio_result if "cbio_result" in locals() else None,
    expression_result=expr_result if "expr_result" in locals() else None,
    survival_result=survival_result if "survival_result" in locals() else None,
    gene_role_result=gene_role_result,
    pathway_result=pathway_result,
    therapeutic_result=therapeutic_result,
)

cov1, cov2, cov3 = st.columns(3)

with cov1:
    st.metric(
        "Layers available",
        f'{coverage_result["evidence_layers_available"]}/{coverage_result["evidence_layers_possible"]}',
    )

with cov2:
    st.metric("Coverage percent", f'{coverage_result["evidence_coverage_percent"]}%')

with cov3:
    st.metric("Coverage label", coverage_result["evidence_coverage_label"])

st.markdown("### Evidence profile visualization")

fig_col1, fig_col2 = st.columns([1, 1.4])

with fig_col1:
    coverage_gauge_fig = plot_evidence_coverage_gauge(coverage_result)
    if coverage_gauge_fig is not None:
        st.plotly_chart(coverage_gauge_fig, use_container_width=True)

with fig_col2:
    coverage_bar_fig = plot_evidence_layer_bar(coverage_result)
    if coverage_bar_fig is not None:
        st.plotly_chart(coverage_bar_fig, use_container_width=True)

with st.expander("Coverage details"):
    st.write("Available layers:")
    st.write(coverage_result["available_layers"])

    st.write("Missing layers:")
    st.write(coverage_result["missing_layers"])

st.divider()

st.subheader("Download Evidence Report")

try:
    markdown_report = build_markdown_report(
        gene=gene,
        cancer_type=cancer_type,
        pubmed_count=pubmed_count if "pubmed_count" in locals() else None,
        saturation_label=saturation_label if "saturation_label" in locals() else None,
        novelty_label=novelty_label if "novelty_label" in locals() else (inferred_novelty if "inferred_novelty" in locals() else None),
        pubmed_query=pubmed_query if "pubmed_query" in locals() else None,
        depmap_result=depmap_result if "depmap_result" in locals() else None,
        common_result=common_result if "common_result" in locals() else None,
        specificity_result=specificity_result if "specificity_result" in locals() else None,
        cbio_result=cbio_result if "cbio_result" in locals() else None,
        expression_result=expr_result if "expr_result" in locals() else None,
        survival_result=survival_result if "survival_result" in locals() else None,
        verdict=verdict if "verdict" in locals() else None,
        coverage_result=coverage_result if "coverage_result" in locals() else None,
    )

    st.download_button(
        label="Download Markdown evidence report",
        data=markdown_report,
        file_name=f"{gene}_{cancer_type}_oncoevidence_report.md".replace(" ", "_"),
        mime="text/markdown",
    )

except Exception as e:
    st.info("Report download is unavailable for this run.")
    st.code(str(e))

