from pathlib import Path
import pandas as pd


def upsert(df, rows, keys):
    rows_df = pd.DataFrame(rows)

    for col in rows_df.columns:
        if col not in df.columns:
            df[col] = None

    for col in df.columns:
        if col not in rows_df.columns:
            rows_df[col] = None

    key_tuples = set(tuple(row[k] for k in keys) for row in rows)

    keep_mask = ~df.apply(
        lambda r: tuple(r[k] for k in keys) in key_tuples,
        axis=1,
    )

    return pd.concat([df[keep_mask], rows_df[df.columns]], ignore_index=True)


# Restore OIP5 gene role
role_path = Path("data/config/gene_role_annotations.csv")
role_df = pd.read_csv(role_path)

role_rows = [
    {
        "gene": "OIP5",
        "role_category": "Proliferation/cell-cycle associated",
        "target_class": "Proliferation-associated nuclear protein",
        "biological_process": "Cell cycle, proliferation, and chromosome-associated biology",
        "interpretation_note": (
            "OIP5 should be interpreted cautiously as a dependency signal because its biology is tied to "
            "proliferation/cell-cycle programs. Strong dependency may reflect broad proliferative essentiality "
            "rather than a selective GBM target."
        ),
    }
]

role_df = upsert(role_df, role_rows, ["gene"])
role_df.to_csv(role_path, index=False)


# Restore OIP5 pathway/function annotation
pathway_path = Path("data/config/pathway_function_annotations.csv")
pathway_df = pd.read_csv(pathway_path)

pathway_rows = [
    {
        "gene": "OIP5",
        "pathway_category": "Cell cycle / proliferation",
        "function_group": "Proliferation-associated nuclear/chromosome protein",
        "pathway_process": "Cell-cycle progression and proliferative tumor-state biology",
        "interpretive_use": (
            "Use OIP5 as a proliferation-linked dependency hypothesis, not as a direct GBM-specific "
            "therapeutic target without additional selectivity evidence."
        ),
        "validation_suggestions": (
            "Compare OIP5 dependency with pan-essential and cell-cycle gene sets; test whether dependency "
            "tracks proliferation rate, cell-cycle state, and broad essentiality rather than GBM-specific biology."
        ),
    }
]

pathway_df = upsert(pathway_df, pathway_rows, ["gene"])
pathway_df.to_csv(pathway_path, index=False)


# Restore OIP5 therapeutic relevance annotation for GBM
ther_path = Path("data/config/therapeutic_relevance_annotations.csv")
ther_df = pd.read_csv(ther_path)

ther_rows = [
    {
        "gene": "OIP5",
        "cancer_type": "GBM",
        "therapeutic_relevance": "Low direct therapeutic relevance",
        "therapeutic_context": (
            "OIP5 has dependency-associated research interest but no direct curated GBM therapeutic "
            "or biomarker context in this app."
        ),
        "biomarker_type": "Research-use dependency candidate",
        "dependency_interpretation": (
            "Strong dependency should be interpreted cautiously because OIP5 may reflect broad proliferation "
            "or cell-cycle essentiality."
        ),
        "therapeutic_caution": (
            "Dependency without therapeutic actionability. Do not frame OIP5 as clinically actionable or "
            "selectively targetable without additional validation."
        ),
        "validation_suggestions": (
            "Validate whether OIP5 dependency is GBM-specific versus pan-essential; test recurrence retention, "
            "tumor-state specificity, protein-level relevance, and normal proliferative-cell safety."
        ),
    }
]

ther_df = upsert(ther_df, ther_rows, ["gene", "cancer_type"])
ther_df.to_csv(ther_path, index=False)


# Restore OIP5/GBM curated evidence row so the old score is not 0.
mock_path = Path("data/mock_gene_evidence.csv")
mock_df = pd.read_csv(mock_path)

mock_rows = [
    {
        "gene": "OIP5",
        "cancer_type": "GBM",
        "tumor_expression": "Moderate/high in tumor",
        "survival_association": "Unclear",
        "geo_validation": "Needs validation",
        "depmap_dependency": "Strong dependency",
        "normal_tissue_safety": "Potential proliferation safety concern",
        "mutation_cna_support": "Weak patient alteration support",
        "novelty_score": 7,
        "notes": (
            "Flagship contradiction case: strong GBM DepMap dependency but high common-essential caution, "
            "low lineage specificity, weak patient alteration/expression support, and low direct therapeutic relevance."
        ),
    }
]

mock_df = upsert(mock_df, mock_rows, ["gene", "cancer_type"])
mock_df.to_csv(mock_path, index=False)


# Patch expansion script so future reruns preserve OIP5.
script_path = Path("scripts/expand_pancancer_catalog.py")
if script_path.exists():
    script = script_path.read_text()

    if '"OIP5": (' not in script:
        marker = 'GENE_META = {\n'
        if marker in script:
            oip5_meta = (
                '    "OIP5": ("Proliferation/cell-cycle associated", '
                '"Proliferation-associated nuclear protein", '
                '"Cell cycle, proliferation, and chromosome-associated biology", '
                '"Cell cycle / proliferation"),\n'
            )
            script = script.replace(marker, marker + oip5_meta)

    old = '''def therapeutic_for_pair(gene, cancer_type):
    if gene == "ERBB2" and cancer_type == "Gastric cancer":'''

    new = '''def therapeutic_for_pair(gene, cancer_type):
    if gene == "OIP5" and cancer_type == "GBM":
        return {
            "gene": gene,
            "cancer_type": cancer_type,
            "therapeutic_relevance": "Low direct therapeutic relevance",
            "therapeutic_context": "OIP5 has dependency-associated research interest but no direct curated GBM therapeutic or biomarker context in this app.",
            "biomarker_type": "Research-use dependency candidate",
            "dependency_interpretation": "Strong dependency should be interpreted cautiously because OIP5 may reflect broad proliferation or cell-cycle essentiality.",
            "therapeutic_caution": "Dependency without therapeutic actionability. Do not frame OIP5 as clinically actionable or selectively targetable without additional validation.",
            "validation_suggestions": "Validate whether OIP5 dependency is GBM-specific versus pan-essential; test recurrence retention, tumor-state specificity, protein-level relevance, and normal proliferative-cell safety.",
        }

    if gene == "ERBB2" and cancer_type == "Gastric cancer":'''

    if old in script and 'if gene == "OIP5" and cancer_type == "GBM"' not in script:
        script = script.replace(old, new)

    script_path.write_text(script)


print("Restored flagship OIP5/GBM annotations and protected expansion script.")