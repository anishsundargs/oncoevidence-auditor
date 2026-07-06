"""
Build a small OncoEvidence-compatible DepMap dependency table from real DepMap files.

Expected inputs:
1. CRISPRGeneEffect.csv
   - Rows: DepMap model IDs / cell lines
   - Columns: genes, usually formatted like "EGFR (1956)"

2. Model.csv or sample metadata file
   - Should contain model IDs and disease/lineage metadata

Output:
- data/depmap/depmap_dependency_subset.csv

This script is intentionally flexible because DepMap column names can shift across releases.
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


CANCER_KEYWORDS = {
    "GBM": ["glioma", "glioblastoma", "central nervous system", "brain"],
    "Gastric cancer": ["gastric", "stomach"],
}


def clean_gene_name(col: str) -> str:
    """Convert 'EGFR (1956)' to 'EGFR' when needed."""
    col = str(col)
    match = GENE_PATTERN.match(col)
    if match:
        return match.group(1).strip()
    return col.strip()


def find_model_id_column(df: pd.DataFrame) -> str:
    candidates = ["ModelID", "DepMap_ID", "DepMapID", "model_id", "depmap_id", "Unnamed: 0"]
    for c in candidates:
        if c in df.columns:
            return c
    return df.columns[0]


def find_metadata_text_columns(df: pd.DataFrame):
    likely = []
    keywords = ["lineage", "disease", "cancer", "primary", "subtype", "oncotree", "tissue"]
    for c in df.columns:
        lower = c.lower()
        if any(k in lower for k in keywords):
            likely.append(c)
    return likely


def assign_cancer_type(row, text_cols):
    combined = " ".join(str(row[c]).lower() for c in text_cols if c in row and pd.notna(row[c]))

    for cancer_type, keywords in CANCER_KEYWORDS.items():
        if any(k in combined for k in keywords):
            return cancer_type

    return None


def load_gene_effect(path: Path) -> pd.DataFrame:
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


def build_subset(gene_effect_path: Path, model_metadata_path: Path, output_path: Path, genes):
    gene_effect = load_gene_effect(gene_effect_path)
    metadata = pd.read_csv(model_metadata_path)

    metadata_model_col = find_model_id_column(metadata)
    metadata = metadata.rename(columns={metadata_model_col: "ModelID"})

    text_cols = find_metadata_text_columns(metadata)
    if not text_cols:
        raise ValueError(
            "Could not find lineage/disease/tissue metadata columns. "
            "Open your Model.csv and inspect the column names."
        )

    metadata["oncoevidence_cancer_type"] = metadata.apply(
        lambda row: assign_cancer_type(row, text_cols),
        axis=1
    )

    merged = metadata[["ModelID", "oncoevidence_cancer_type"]].merge(
        gene_effect,
        on="ModelID",
        how="inner"
    )

    records = []

    for cancer_type in CANCER_KEYWORDS:
        cancer_df = merged[merged["oncoevidence_cancer_type"] == cancer_type].copy()

        for gene in genes:
            if gene not in cancer_df.columns:
                records.append({
                    "gene": gene,
                    "cancer_type": cancer_type,
                    "median_dependency_score": None,
                    "dependent_cell_lines": 0,
                    "total_cell_lines": len(cancer_df),
                    "dependency_note": f"{gene} not found in CRISPRGeneEffect columns."
                })
                continue

            values = pd.to_numeric(cancer_df[gene], errors="coerce").dropna()
            total = len(values)

            if total == 0:
                median_score = None
                dependent = 0
            else:
                median_score = round(float(values.median()), 4)
                dependent = int((values <= -0.5).sum())

            records.append({
                "gene": gene,
                "cancer_type": cancer_type,
                "median_dependency_score": median_score,
                "dependent_cell_lines": dependent,
                "total_cell_lines": total,
                "dependency_note": (
                    f"Derived from DepMap CRISPRGeneEffect. "
                    f"Dependent cell lines counted using score <= -0.5."
                )
            })

    out = pd.DataFrame(records)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(output_path, index=False)

    print(f"Wrote {len(out)} rows to {output_path}")
    print(out.head(10).to_string(index=False))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--gene-effect", required=True, help="Path to CRISPRGeneEffect.csv")
    parser.add_argument("--model", required=True, help="Path to Model.csv or DepMap model metadata")
    parser.add_argument(
        "--output",
        default="data/depmap/depmap_dependency_subset.csv",
        help="Output path"
    )
    parser.add_argument(
        "--genes",
        nargs="*",
        default=DEFAULT_GENES,
        help="Gene symbols to include"
    )

    args = parser.parse_args()

    build_subset(
        gene_effect_path=Path(args.gene_effect),
        model_metadata_path=Path(args.model),
        output_path=Path(args.output),
        genes=args.genes
    )


if __name__ == "__main__":
    main()
