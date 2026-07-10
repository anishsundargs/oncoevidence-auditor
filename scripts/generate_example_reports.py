"""
Generate example OncoEvidence Auditor Markdown reports.

These examples are useful for README documentation, GitHub presentation,
manuscript supplements, and project demonstrations.
"""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.pubmed_saturation import get_pubmed_count, classify_literature_saturation
from src.depmap_dependency import get_dependency_result
from src.common_essential import get_common_essential_result
from src.specificity_index import calculate_specificity_index
from src.cbioportal_alterations import get_cbioportal_alteration_summary
from src.cbioportal_expression import get_cbioportal_expression_summary
from src.cbioportal_survival import get_cbioportal_survival_summary
from src.auditor_verdict import build_auditor_verdict
from src.report_builder import build_markdown_report


OUT_DIR = Path("docs/example_reports")
OUT_DIR.mkdir(parents=True, exist_ok=True)


EXAMPLES = [
    ("OIP5", "GBM"),
    ("ERBB2", "Gastric cancer"),
]


def novelty_from_saturation(saturation_label: str) -> str:
    if saturation_label == "High saturation":
        return "low"
    if saturation_label == "Low saturation":
        return "high"
    return "moderate"


def build_one_report(gene: str, cancer_type: str) -> Path:
    pubmed_result = get_pubmed_count(gene, cancer_type)

    # get_pubmed_count() may return either count or (count, query), depending on project version.
    if isinstance(pubmed_result, tuple):
        pubmed_count = pubmed_result[0]
    else:
        pubmed_count = pubmed_result

    saturation_label = classify_literature_saturation(pubmed_count)
    novelty_label = novelty_from_saturation(saturation_label)

    dep = get_dependency_result(gene, cancer_type)
    common = get_common_essential_result(gene)
    spec = calculate_specificity_index(dep, common)

    cbio = get_cbioportal_alteration_summary(gene, cancer_type)
    expr = get_cbioportal_expression_summary(gene, cancer_type)
    surv = get_cbioportal_survival_summary(gene, cancer_type)

    verdict = build_auditor_verdict(
        gene=gene,
        cancer_type=cancer_type,
        pubmed_count=pubmed_count,
        saturation_label=saturation_label,
        depmap_result=dep,
        common_result=common,
        specificity_result=spec,
        cbio_result=cbio,
        expression_result=expr,
        survival_result=surv,
    )

    report = build_markdown_report(
        gene=gene,
        cancer_type=cancer_type,
        pubmed_count=pubmed_count,
        saturation_label=saturation_label,
        novelty_label=novelty_label,
        depmap_result=dep,
        common_result=common,
        specificity_result=spec,
        cbio_result=cbio,
        expression_result=expr,
        survival_result=surv,
        verdict=verdict,
    )

    safe_cancer = cancer_type.replace(" ", "_").replace("/", "_")
    out_path = OUT_DIR / f"{gene}_{safe_cancer}_example_report.md"
    out_path.write_text(report)

    return out_path


def main():
    print("Generating example OncoEvidence Auditor reports...")

    for gene, cancer_type in EXAMPLES:
        out_path = build_one_report(gene, cancer_type)
        print(f"✅ Wrote {out_path}")

    print("Done.")


if __name__ == "__main__":
    main()
