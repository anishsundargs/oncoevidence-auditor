"""
Build the processed DepMap dependency subset for OncoEvidence Auditor.

Inputs:
- data/depmap/raw/CRISPRGeneEffect.csv
- data/depmap/raw/Model.csv
- data/mock_gene_evidence.csv
- data/config/cancer_registry.csv

Output:
- data/depmap/depmap_dependency_subset.csv

The cancer-specific OncotreeCode filters now come from the central cancer registry.
"""

from pathlib import Path
import sys
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.cancer_registry import (
    get_depmap_oncotree_codes,
    list_supported_cancers,
)


RAW_DIR = Path("data/depmap/raw")
GENE_EFFECT_PATH = RAW_DIR / "CRISPRGeneEffect.csv"
MODEL_PATH = RAW_DIR / "Model.csv"
MOCK_EVIDENCE_PATH = Path("data/mock_gene_evidence.csv")
OUTPUT_PATH = Path("data/depmap/depmap_dependency_subset.csv")

DEPENDENCY_THRESHOLD = -0.5


def classify_dependency(median_dependency_score, percent_dependent):
    """
    Classify dependency strength from DepMap gene-effect values.

    More negative gene-effect scores indicate stronger dependency.
    """
    if pd.isna(median_dependency_score):
        return "Data not available"

    if percent_dependent >= 50:
        return "Strong dependency"

    if percent_dependent >= 20:
        return "Moderate dependency"

    return "Little or no dependency"


def find_gene_column(gene_effect_df, gene_symbol):
    """
    Find a DepMap gene-effect column for a gene symbol.

    DepMap columns are commonly formatted like:
    OIP5 (11339)
    EGFR (1956)
    """
    gene_symbol = gene_symbol.strip().upper()

    for col in gene_effect_df.columns:
        col_upper = str(col).upper()

        if col_upper == gene_symbol:
            return col

        if col_upper.startswith(f"{gene_symbol} ("):
            return col

    return None


def load_gene_cancer_pairs():
    """
    Load gene/cancer pairs from the app's evidence table.

    This keeps the processed DepMap subset aligned with the app's current
    supported gene/cancer examples.
    """
    if not MOCK_EVIDENCE_PATH.exists():
        raise FileNotFoundError(
            f"Could not find {MOCK_EVIDENCE_PATH}. "
            "The builder needs gene/cancer pairs to process."
        )

    df = pd.read_csv(MOCK_EVIDENCE_PATH)

    required = {"gene", "cancer_type"}
    missing = required - set(df.columns)

    if missing:
        raise ValueError(
            f"{MOCK_EVIDENCE_PATH} is missing required columns: {sorted(missing)}"
        )

    supported_cancers = set(list_supported_cancers())

    pairs = (
        df[["gene", "cancer_type"]]
        .dropna()
        .drop_duplicates()
        .query("cancer_type in @supported_cancers")
        .to_dict("records")
    )

    if not pairs:
        raise ValueError("No gene/cancer pairs found for supported registry cancers.")

    return pairs


def summarize_gene_dependency(gene_effect_df, model_df, gene, cancer_type):
    """
    Summarize one gene/cancer DepMap dependency signal.
    """
    oncotree_codes = get_depmap_oncotree_codes(cancer_type)

    if not oncotree_codes:
        return {
            "gene": gene,
            "cancer_type": cancer_type,
            "oncotree_codes": "",
            "median_dependency_score": None,
            "dependent_cell_lines": 0,
            "total_cell_lines": 0,
            "percent_dependent": None,
            "dependency_label": "Data not available",
            "note": "No DepMap OncotreeCode mapping found in cancer registry.",
        }

    gene_col = find_gene_column(gene_effect_df, gene)

    if not gene_col:
        return {
            "gene": gene,
            "cancer_type": cancer_type,
            "oncotree_codes": ";".join(oncotree_codes),
            "median_dependency_score": None,
            "dependent_cell_lines": 0,
            "total_cell_lines": 0,
            "percent_dependent": None,
            "dependency_label": "Data not available",
            "note": f"Gene column not found in CRISPRGeneEffect.csv for {gene}.",
        }

    cancer_models = model_df[model_df["OncotreeCode"].isin(oncotree_codes)].copy()

    merged = cancer_models[["ModelID", "OncotreeCode"]].merge(
        gene_effect_df[["ModelID", gene_col]],
        on="ModelID",
        how="inner",
    )

    values = pd.to_numeric(merged[gene_col], errors="coerce").dropna()

    total = int(values.shape[0])

    if total == 0:
        return {
            "gene": gene,
            "cancer_type": cancer_type,
            "oncotree_codes": ";".join(oncotree_codes),
            "median_dependency_score": None,
            "dependent_cell_lines": 0,
            "total_cell_lines": 0,
            "percent_dependent": None,
            "dependency_label": "Data not available",
            "note": "No matching DepMap cell-line values after OncotreeCode filtering.",
        }

    median_score = round(float(values.median()), 4)
    dependent_count = int((values <= DEPENDENCY_THRESHOLD).sum())
    percent_dependent = round((dependent_count / total) * 100, 1)

    label = classify_dependency(median_score, percent_dependent)

    return {
        "gene": gene,
        "cancer_type": cancer_type,
        "oncotree_codes": ";".join(oncotree_codes),
        "median_dependency_score": median_score,
        "dependent_cell_lines": dependent_count,
        "total_cell_lines": total,
        "percent_dependent": percent_dependent,
        "dependency_label": label,
        "note": f"Filtered by registry OncotreeCode values: {', '.join(oncotree_codes)}.",
    }


def main():
    if not GENE_EFFECT_PATH.exists():
        raise FileNotFoundError(f"Missing raw DepMap file: {GENE_EFFECT_PATH}")

    if not MODEL_PATH.exists():
        raise FileNotFoundError(f"Missing raw DepMap file: {MODEL_PATH}")

    print("Loading DepMap raw files...")
    gene_effect_df = pd.read_csv(GENE_EFFECT_PATH)
    model_df = pd.read_csv(MODEL_PATH)

    # Different DepMap releases name the model identifier column differently.
    # Normalize it to ModelID so the rest of the script is stable.
    gene_effect_id_candidates = [
        "ModelID",
        "DepMap_ID",
        "DepMapID",
        "Unnamed: 0",
    ]

    gene_effect_id_col = None

    for candidate in gene_effect_id_candidates:
        if candidate in gene_effect_df.columns:
            gene_effect_id_col = candidate
            break

    # Fallback: if the first column contains ACH-style DepMap model IDs, use it.
    if gene_effect_id_col is None:
        first_col = gene_effect_df.columns[0]
        first_values = gene_effect_df[first_col].astype(str).head(10).tolist()
        if any(value.startswith("ACH-") for value in first_values):
            gene_effect_id_col = first_col

    if gene_effect_id_col is None:
        raise ValueError(
            "Could not identify model ID column in CRISPRGeneEffect.csv. "
            f"Available columns start with: {list(gene_effect_df.columns[:10])}"
        )

    if gene_effect_id_col != "ModelID":
        gene_effect_df = gene_effect_df.rename(columns={gene_effect_id_col: "ModelID"})

    required_model_cols = {"ModelID", "OncotreeCode"}
    missing_model_cols = required_model_cols - set(model_df.columns)

    if missing_model_cols:
        raise ValueError(
            f"Model.csv is missing required columns: {sorted(missing_model_cols)}"
        )

    pairs = load_gene_cancer_pairs()

    print(f"Processing {len(pairs)} gene/cancer pairs...")
    rows = []

    for pair in pairs:
        gene = str(pair["gene"]).strip()
        cancer_type = str(pair["cancer_type"]).strip()

        print(f"- {gene} / {cancer_type}")
        rows.append(
            summarize_gene_dependency(
                gene_effect_df=gene_effect_df,
                model_df=model_df,
                gene=gene,
                cancer_type=cancer_type,
            )
        )

    output_df = pd.DataFrame(rows)
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    output_df.to_csv(OUTPUT_PATH, index=False)

    print(f"\nWrote {OUTPUT_PATH}")
    print(output_df)


if __name__ == "__main__":
    main()
