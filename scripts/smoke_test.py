"""
Smoke tests for OncoEvidence Auditor.

Run from project root:

    python3 scripts/smoke_test.py

These tests are not full unit tests. They are quick checks that the main
modules still run and return expected fields.
"""

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.pubmed_saturation import get_pubmed_count, classify_literature_saturation
from src.depmap_dependency import get_dependency_result
from src.common_essential import get_common_essential_result
from src.specificity_index import calculate_specificity_index
from src.cbioportal_alterations import get_cbioportal_alteration_summary
from src.cbioportal_expression import get_cbioportal_expression_summary
from src.cbioportal_survival import get_cbioportal_survival_summary
from src.auditor_verdict import build_auditor_verdict
from src.report_builder import build_markdown_report
from src.batch_audit import build_batch_audit
from src.cancer_registry import list_supported_cancers


def assert_true(condition, message):
    if not condition:
        raise AssertionError(message)


def print_pass(message):
    print(f"✅ {message}")


def print_warn(message):
    print(f"⚠️  {message}")


def test_registry():
    cancers = list_supported_cancers()
    assert_true("GBM" in cancers, "GBM missing from cancer registry.")
    assert_true("Gastric cancer" in cancers, "Gastric cancer missing from cancer registry.")
    print_pass("Cancer registry loads expected validated cancer types.")


def test_pubmed():
    count, query = get_pubmed_count("EGFR", "GBM")
    label, novelty, note = classify_literature_saturation(count)

    assert_true(isinstance(count, int), "PubMed count is not an integer.")
    assert_true(count > 0, "PubMed count for EGFR/GBM should be greater than 0.")
    assert_true("EGFR" in query, "PubMed query does not contain gene.")
    assert_true(label is not None, "PubMed saturation label missing.")
    assert_true(novelty is not None, "PubMed novelty label missing.")

    print_pass(f"PubMed live query works. EGFR/GBM count={count}, label={label}.")


def test_depmap_common_specificity():
    dep = get_dependency_result("OIP5", "GBM")
    common = get_common_essential_result("OIP5")
    spec = calculate_specificity_index(dep, common)

    assert_true(dep.get("available") is True, "DepMap result unavailable for OIP5/GBM.")
    assert_true(dep.get("dependency_label") == "Strong dependency", "Unexpected OIP5/GBM dependency label.")
    assert_true(common.get("common_essential_label") is not None, "Common-essential label missing.")
    assert_true(spec.get("specificity_label") is not None, "Specificity label missing.")

    print_pass(
        f"DepMap/common/specificity work. OIP5 dependency={dep.get('dependency_label')}, "
        f"specificity={spec.get('specificity_label')}."
    )

    return dep, common, spec


def test_cbioportal():
    """
    Test cBioPortal when available.

    External API failures such as 502 Bad Gateway should warn instead of failing
    the whole local smoke test.
    """
    try:
        alteration = get_cbioportal_alteration_summary("ERBB2", "Gastric cancer")
        expression = get_cbioportal_expression_summary("ERBB2", "Gastric cancer")
    except Exception as e:
        print_warn(f"cBioPortal live API unavailable during smoke test: {e}")
        return False

    if not alteration.get("available") or not expression.get("available"):
        print_warn(
            "cBioPortal returned incomplete data during smoke test. "
            f"Alteration note={alteration.get('note')}; Expression note={expression.get('note')}"
        )
        return False

    assert_true(alteration.get("patient_alteration_support") is not None, "Patient alteration support missing.")
    assert_true(expression.get("expression_support") is not None, "Expression support missing.")

    print_pass(
        f"cBioPortal works. ERBB2/gastric alteration={alteration.get('patient_alteration_support')}, "
        f"expression={expression.get('expression_support')}."
    )

    return True



def test_survival():
    """
    Test survival/prognosis module when cBioPortal clinical data are available.
    External cBioPortal failures should warn instead of failing the entire smoke test.
    """
    try:
        result = get_cbioportal_survival_summary("ERBB2", "Gastric cancer")
    except Exception as e:
        print_warn(f"cBioPortal survival API unavailable during smoke test: {e}")
        return False

    if not result.get("available"):
        print_warn(f"Survival module returned unavailable result: {result.get('note')}")
        return False

    assert_true(result.get("survival_signal") is not None, "Survival signal missing.")
    assert_true(result.get("survival_patients_matched") is not None, "Matched survival patient count missing.")

    print_pass(
        f"Survival/prognosis module works. ERBB2/gastric signal={result.get('survival_signal')}, "
        f"matched patients={result.get('survival_patients_matched')}."
    )

    return True


def test_verdict_and_report(dep, common, spec):
    try:
        cbio = get_cbioportal_alteration_summary("OIP5", "GBM")
        expr = get_cbioportal_expression_summary("OIP5", "GBM")
        surv = get_cbioportal_survival_summary("OIP5", "GBM")
    except Exception as e:
        print_warn(f"Skipping live cBioPortal fields in verdict/report test because API failed: {e}")
        cbio = None
        expr = None
        surv = None

    verdict = build_auditor_verdict(
        gene="OIP5",
        cancer_type="GBM",
        pubmed_count=16,
        saturation_label="Low-moderate saturation",
        depmap_result=dep,
        common_result=common,
        specificity_result=spec,
        cbio_result=cbio,
        expression_result=expr,
        survival_result=surv,
    )

    assert_true(verdict.get("verdict_tier") is not None, "Verdict tier missing.")
    assert_true(verdict.get("safe_claim") is not None, "Safe claim missing.")
    assert_true(len(verdict.get("warnings", [])) > 0, "Expected warnings for OIP5/GBM.")

    report = build_markdown_report(
        gene="OIP5",
        cancer_type="GBM",
        pubmed_count=16,
        saturation_label="Low-moderate saturation",
        novelty_label="moderate",
        pubmed_query='("OIP5"[Title/Abstract]) AND (glioblastoma[Title/Abstract] OR GBM[Title/Abstract] OR glioma[Title/Abstract])',
        depmap_result=dep,
        common_result=common,
        specificity_result=spec,
        cbio_result=cbio,
        expression_result=expr,
        survival_result=surv,
        verdict=verdict,
    )

    assert_true("# OncoEvidence Auditor Report" in report, "Markdown report title missing.")
    assert_true("## Evidence Coverage" in report, "Markdown report coverage section missing.")
    assert_true("## Auditor Verdict" in report, "Markdown report verdict section missing.")
    assert_true("## cBioPortal Survival / Prognosis Evidence" in report, "Markdown report survival section missing.")

    print_pass(f"Auditor Verdict and Markdown report build successfully. Tier={verdict.get('verdict_tier')}.")


def test_batch_audit():
    fast_df = build_batch_audit(
        cancer_type="GBM",
        include_live_pubmed=False,
        include_live_cbio=False,
    )

    assert_true(not fast_df.empty, "Fast batch audit returned empty table.")
    assert_true("evidence_coverage_label" in fast_df.columns, "Batch audit missing coverage label.")
    assert_true("batch_pattern" in fast_df.columns, "Batch audit missing batch pattern.")

    print_pass(f"Fast batch audit works. Rows={len(fast_df)}.")

    try:
        pubmed_df = build_batch_audit(
            cancer_type="GBM",
            include_live_pubmed=True,
            include_live_cbio=False,
        )

        assert_true("pubmed_count" in pubmed_df.columns, "Live PubMed batch missing pubmed_count column.")
        assert_true(pubmed_df["pubmed_count"].notna().any(), "Live PubMed batch returned no PubMed counts.")

        print_pass("Live PubMed batch audit works.")
    except Exception as e:
        print_warn(f"Live PubMed batch audit unavailable during smoke test: {e}")


def main():
    print("\nRunning OncoEvidence Auditor smoke tests...\n")

    test_registry()
    test_pubmed()
    dep, common, spec = test_depmap_common_specificity()
    test_cbioportal()
    test_survival()
    test_verdict_and_report(dep, common, spec)
    test_batch_audit()

    print("\n🎉 Smoke test completed. Any warnings above were external API availability issues, not necessarily code failures.\n")


if __name__ == "__main__":
    main()
