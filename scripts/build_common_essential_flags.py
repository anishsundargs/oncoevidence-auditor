"""
Build common-essential / pan-cancer dependency flags from DepMap CRISPRGeneEffect.

Input:
- data/depmap/raw/CRISPRGeneEffect.csv

Output:
- data/depmap/common_essential_flags.csv

Purpose:
A gene can look like a strong dependency in one cancer group simply because it is broadly essential
across most cancer cell lines. This script helps flag those cases.
"""

from pathlib import Path
import argparse
import re
import pandas as pd


GENE_PATTERN = re.compile(r"^(.+?)\s*\(\d+\)$")


DEFAULT_GENES = [
    "OIP5", "EGFR", "MGMT", "IDH1", "ATRX", "PDGFRA", "CDK4", "MDM2", "MKI67", "TOP2A",
    "TP53", "ERBB2", "MET", "KRAS", "MYC", "CDK1", "AURKA", "MMP9", "VEGFA", "CLDN18"
]


def clean_gene_name(col: str) -> str:
    """Convert 'EGFR (1956)' to 'EGFR' when needed."""
    col = str(col)
    match = GENE_PATTERN.match(col)
    if match:
        return match.group(1).strip()
    return col.strip()


def load_gene_effect(path: Path) -> pd.DataFrame:
    """Load CRISPRGeneEffect and clean gene column names."""
    df = pd.read_csv(path)

    first_col = df.columns[0]
    if first_col not in {"ModelID", "DepMap_ID", "DepMapID"}:
        df = df.rename(columns={first_col: "ModelID"})

    rename = {}
    for col in df.columns:
        if col != "ModelID":
            rename[col] = clean_gene_name(col)

    df = df.rename(columns=rename)
    return df


def classify_common_essential(median_score, percent_dependent):
    """
    Classify pan-cancer dependency risk.

    More negative scores and higher dependent percentages suggest broader essentiality.
    """
    if pd.isna(median_score):
        return "Not available"

    if median_score <= -0.75 and percent_dependent >= 60:
        return "High common-essential caution"

    if median_score <= -0.50 and percent_dependent >= 40:
        return "Moderate common-essential caution"

    if median_score <= -0.25 and percent_dependent >= 20:
        return "Low-moderate common-essential caution"

    return "Low common-essential caution"


def build_common_essential_flags(gene_effect_path: Path, output_path: Path, genes):
    df = load_gene_effect(gene_effect_path)

    records = []

    for gene in genes:
        if gene not in df.columns:
            records.append({
                "gene": gene,
                "pan_cancer_median_dependency_score": None,
                "pan_cancer_dependent_cell_lines": 0,
                "pan_cancer_total_cell_lines": 0,
                "pan_cancer_percent_dependent": None,
                "common_essential_label": "Not available",
                "common_essential_note": f"{gene} not found in CRISPRGeneEffect columns."
            })
            continue

        values = pd.to_numeric(df[gene], errors="coerce").dropna()
        total = len(values)

        if total == 0:
            median_score = None
            dependent = 0
            percent = None
        else:
            median_score = round(float(values.median()), 4)
            dependent = int((values <= -0.5).sum())
            percent = round((dependent / total) * 100, 1)

        label = classify_common_essential(median_score, percent if percent is not None else 0)

        if label == "High common-essential caution":
            note = (
                f"{gene} is broadly dependency-associated across many cancer models. "
                "A strong lineage-specific signal may reflect general essentiality rather than selective vulnerability."
            )
        elif label == "Moderate common-essential caution":
            note = (
                f"{gene} shows moderate broad dependency across cancer models. "
                "Interpret lineage-specific dependency with specificity caution."
            )
        elif label == "Low-moderate common-essential caution":
            note = (
                f"{gene} shows some broad dependency across cancer models. "
                "Specificity should still be checked against the selected cancer lineage."
            )
        elif label == "Low common-essential caution":
            note = (
                f"{gene} does not appear broadly essential by this simple pan-cancer dependency threshold."
            )
        else:
            note = f"No common-essential assessment available for {gene}."

        records.append({
            "gene": gene,
            "pan_cancer_median_dependency_score": median_score,
            "pan_cancer_dependent_cell_lines": dependent,
            "pan_cancer_total_cell_lines": total,
            "pan_cancer_percent_dependent": percent,
            "common_essential_label": label,
            "common_essential_note": note
        })

    out = pd.DataFrame(records)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(output_path, index=False)

    print(f"Wrote {len(out)} rows to {output_path}")
    print(out.to_string(index=False))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--gene-effect", required=True, help="Path to CRISPRGeneEffect.csv")
    parser.add_argument(
        "--output",
        default="data/depmap/common_essential_flags.csv",
        help="Output path"
    )
    parser.add_argument(
        "--genes",
        nargs="*",
        default=DEFAULT_GENES,
        help="Gene symbols to include"
    )

    args = parser.parse_args()

    build_common_essential_flags(
        gene_effect_path=Path(args.gene_effect),
        output_path=Path(args.output),
        genes=args.genes
    )


if __name__ == "__main__":
    main()
