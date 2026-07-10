"""
Final project audit for OncoEvidence Auditor.

This script summarizes local project scale, required files, example reports,
and reproducibility checks. It is intended for final GitHub/preprint packaging.
"""

from pathlib import Path
import subprocess
import sys

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]


REQUIRED_FILES = [
    "app.py",
    "README.md",
    "data/config/cancer_registry.csv",
    "data/config/gene_role_annotations.csv",
    "data/config/pathway_function_annotations.csv",
    "data/config/therapeutic_relevance_annotations.csv",
    "data/mock_gene_evidence.csv",
    "src/evidence_scoring.py",
    "src/live_evidence_score.py",
    "src/evidence_coverage.py",
    "src/auditor_verdict.py",
    "src/report_builder.py",
    "src/evidence_provenance.py",
    "pages/2_Batch_Audit.py",
    "pages/3_Examples_and_Interpretation_Guide.py",
    "pages/4_Catalog_Explorer.py",
    "pages/5_Evidence_Provenance.py",
    "docs/example_reports/OIP5_GBM_example_report.md",
    "docs/example_reports/ERBB2_Gastric_cancer_example_report.md",
    "docs/PROJECT_SUMMARY.md",
    "docs/DEMO_WORKFLOW.md",
]


def run_command(command):
    result = subprocess.run(
        command,
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    return result.returncode, result.stdout.strip(), result.stderr.strip()


def check_required_files():
    missing = []
    present = []

    for rel_path in REQUIRED_FILES:
        path = ROOT / rel_path
        if path.exists():
            present.append(rel_path)
        else:
            missing.append(rel_path)

    return present, missing


def summarize_catalog():
    catalog_path = ROOT / "data/mock_gene_evidence.csv"
    registry_path = ROOT / "data/config/cancer_registry.csv"

    catalog = pd.read_csv(catalog_path)
    registry = pd.read_csv(registry_path)

    pair_count = len(catalog.drop_duplicates(["gene", "cancer_type"]))
    unique_genes = catalog["gene"].nunique()
    cancer_types = catalog["cancer_type"].nunique()
    registry_cancers = registry["cancer_type"].nunique() if "cancer_type" in registry.columns else len(registry)

    by_cancer = (
        catalog.groupby("cancer_type")["gene"]
        .nunique()
        .sort_values(ascending=False)
        .reset_index(name="unique_genes")
    )

    return {
        "pair_count": pair_count,
        "unique_genes": unique_genes,
        "cancer_types": cancer_types,
        "registry_cancers": registry_cancers,
        "median_genes_per_cancer": float(by_cancer["unique_genes"].median()),
        "by_cancer": by_cancer,
    }


def check_example_reports():
    report_paths = [
        ROOT / "docs/example_reports/OIP5_GBM_example_report.md",
        ROOT / "docs/example_reports/ERBB2_Gastric_cancer_example_report.md",
    ]

    required_phrases = [
        "## Executive Summary",
        "## Live Evidence Score",
        "## Auditor Verdict",
        "## Final Interpretation and Next Validation",
        "## Contradiction Type Labels",
        "## Evidence Coverage",
        "## Evidence Source / Provenance",
        "## Limitations",
        "## Research-Use Disclaimer",
    ]

    results = {}

    for path in report_paths:
        text = path.read_text() if path.exists() else ""
        results[path.name] = {
            phrase: phrase in text for phrase in required_phrases
        }

    return results


def main():
    print("OncoEvidence Auditor Final Project Audit")
    print("=" * 48)

    print("\n1. Required files")
    present, missing = check_required_files()
    print(f"Present: {len(present)}/{len(REQUIRED_FILES)}")
    if missing:
        print("Missing files:")
        for item in missing:
            print(f"  - {item}")
    else:
        print("All required files are present.")

    print("\n2. Catalog scale")
    summary = summarize_catalog()
    print(f"Cancer types in catalog: {summary['cancer_types']}")
    print(f"Cancer types in registry: {summary['registry_cancers']}")
    print(f"Unique genes: {summary['unique_genes']}")
    print(f"Gene-cancer hypotheses: {summary['pair_count']}")
    print(f"Median genes per cancer: {summary['median_genes_per_cancer']}")

    print("\nTop 10 cancer types by local catalog gene count:")
    print(summary["by_cancer"].head(10).to_string(index=False))

    print("\n3. Example report sections")
    report_results = check_example_reports()
    failed_report_checks = []

    for report_name, checks in report_results.items():
        print(f"\n{report_name}")
        for phrase, ok in checks.items():
            status = "OK" if ok else "MISSING"
            print(f"  {status}: {phrase}")
            if not ok:
                failed_report_checks.append((report_name, phrase))

    print("\n4. Smoke test")
    code, out, err = run_command([sys.executable, "scripts/smoke_test.py"])
    if code == 0:
        print("Smoke test: PASS")
    else:
        print("Smoke test: FAIL")
        print(out)
        print(err)

    print("\n5. Project readiness check")
    code2, out2, err2 = run_command([sys.executable, "scripts/project_readiness_check.py"])
    if code2 == 0:
        print("Project readiness check: PASS")
    else:
        print("Project readiness check: FAIL")
        print(out2)
        print(err2)

    print("\n6. Git status")
    code3, out3, err3 = run_command(["git", "status", "--short"])
    if code3 == 0 and not out3:
        print("Git working tree: clean")
    elif code3 == 0:
        print("Git working tree has changes:")
        print(out3)
    else:
        print("Could not read git status.")
        print(err3)

    print("\nFinal audit result")
    print("-" * 48)

    if missing or failed_report_checks or code != 0 or code2 != 0:
        print("FAIL: Resolve the issues above before packaging.")
        raise SystemExit(1)

    print("PASS: Project is ready for final packaging/review.")


if __name__ == "__main__":
    main()