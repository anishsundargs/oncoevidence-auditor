"""
Project readiness check for OncoEvidence Auditor.

This script verifies that the repository has the expected source modules,
configuration files, documentation, and generated example reports needed for
a credible demo or GitHub presentation.
"""

from pathlib import Path
import sys


REQUIRED_FILES = [
    "app.py",
    "README.md",
    "pages/1_Methods.py",
    "pages/2_Batch_Audit.py",
    "pages/3_Examples_and_Interpretation_Guide.py",
    "pages/4_Catalog_Explorer.py",
    "pages/5_Evidence_Provenance.py",
    "scripts/smoke_test.py",
    "scripts/generate_example_reports.py",
    "src/evidence_coverage.py",
    "src/pubmed_saturation.py",
    "src/depmap_dependency.py",
    "src/common_essential.py",
    "src/specificity_index.py",
    "src/cbioportal_alterations.py",
    "src/cbioportal_expression.py",
    "src/cbioportal_survival.py",
    "src/auditor_verdict.py",
    "src/final_interpretation.py",
    "src/contradiction_labels.py",
    "src/gene_role.py",
    "src/pathway_function.py",
    "src/therapeutic_relevance.py",
    "src/report_builder.py",
    "src/batch_audit.py",
    "data/config/cancer_registry.csv",
    "data/config/gene_role_annotations.csv",
    "data/config/pathway_function_annotations.csv",
    "data/config/therapeutic_relevance_annotations.csv",
    "docs/example_reports/OIP5_GBM_example_report.md",
    "docs/example_reports/ERBB2_Gastric_cancer_example_report.md",
]


REPORT_REQUIREMENTS = [
    "## Final Interpretation and Next Validation",
    "## Contradiction Type Labels",
    "## Gene Role Classification",
    "## Pathway / Function Annotation",
    "## Drug / Therapeutic Relevance Annotation",
    "**Layers available:** 10/10",
    "## Research-Use Disclaimer",
]


README_REQUIREMENTS = [
    "Expanded 10-layer evidence profile",
    "Example reports",
    "OncoEvidence Auditor",
]


def check_required_files() -> list[str]:
    failures = []

    for file_path in REQUIRED_FILES:
        if not Path(file_path).exists():
            failures.append(f"Missing required file: {file_path}")

    return failures


def check_example_reports() -> list[str]:
    failures = []

    report_paths = [
        Path("docs/example_reports/OIP5_GBM_example_report.md"),
        Path("docs/example_reports/ERBB2_Gastric_cancer_example_report.md"),
    ]

    for report_path in report_paths:
        if not report_path.exists():
            failures.append(f"Missing example report: {report_path}")
            continue

        text = report_path.read_text()

        for required in REPORT_REQUIREMENTS:
            if required not in text:
                failures.append(f"{report_path} missing required text: {required}")

    return failures


def check_readme() -> list[str]:
    failures = []

    readme = Path("README.md")
    if not readme.exists():
        return ["Missing README.md"]

    text = readme.read_text()

    for required in README_REQUIREMENTS:
        if required not in text:
            failures.append(f"README.md missing required text: {required}")

    return failures


def main():
    print("Running OncoEvidence Auditor project readiness check...\n")

    failures = []
    failures.extend(check_required_files())
    failures.extend(check_example_reports())
    failures.extend(check_readme())

    if failures:
        print("❌ Project readiness check failed.\n")
        for failure in failures:
            print(f"- {failure}")
        print("\nFix the issues above, then rerun this script.")
        sys.exit(1)

    print("✅ Required files present.")
    print("✅ Example reports include 10-layer coverage and major report sections.")
    print("✅ README includes expected project/demo sections.")
    print("\n🎉 Project readiness check passed.")


if __name__ == "__main__":
    main()
