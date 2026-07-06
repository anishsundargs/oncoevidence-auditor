"""
cBioPortal patient-tumor expression evidence module for OncoEvidence Auditor.

Goal:
For a gene/cancer pair, fetch mRNA expression z-score values from cBioPortal and summarize:
- median expression z-score
- percent of tumors with high expression
- percent of tumors with low expression
- expression support label

This module reuses helper functions from cbioportal_alterations.py.
"""

from typing import Dict, List, Optional
import statistics

from src.cbioportal_alterations import (
    cbio_post,
    choose_available_study,
    get_gene_entrez_id,
    get_molecular_profiles,
    get_sample_list_id,
)


def find_expression_zscore_profile_id(profiles: List[dict]) -> Optional[str]:
    """
    Find the best mRNA expression z-score profile.

    Preference order:
    1. Normal-reference z-scores, when available
    2. All-sample-reference z-scores
    3. Diploid-sample-reference z-scores
    """
    normal_ref_candidates = []
    all_sample_candidates = []
    diploid_candidates = []

    for profile in profiles:
        profile_id = str(profile.get("molecularProfileId", "")).lower()
        name = str(profile.get("name", "")).lower()
        description = str(profile.get("description", "")).lower()
        combined = " ".join([profile_id, name, description])

        if (
            profile.get("molecularAlterationType") == "MRNA_EXPRESSION"
            and profile.get("datatype") == "Z-SCORE"
        ):
            if "ref_normal" in profile_id or "normal samples" in combined:
                normal_ref_candidates.append(profile.get("molecularProfileId"))
            elif "all_sample" in profile_id or "all samples" in combined:
                all_sample_candidates.append(profile.get("molecularProfileId"))
            else:
                diploid_candidates.append(profile.get("molecularProfileId"))

    if normal_ref_candidates:
        return normal_ref_candidates[0]
    if all_sample_candidates:
        return all_sample_candidates[0]
    if diploid_candidates:
        return diploid_candidates[0]

    return None


def fetch_expression_values(
    molecular_profile_id: str,
    sample_list_id: str,
    entrez_gene_id: int,
) -> List[dict]:
    """
    Fetch mRNA expression z-score values for one gene.
    """
    payload = {
        "entrezGeneIds": [entrez_gene_id],
        "sampleListId": sample_list_id,
    }

    return cbio_post(
        f"/molecular-profiles/{molecular_profile_id}/molecular-data/fetch",
        payload,
    )


def classify_expression_support(median_zscore, percent_high, percent_low) -> str:
    """
    Classify expression support from z-score distribution.

    Important:
    - Broad expression support means the cohort-level distribution is shifted upward.
    - Subgroup high-expression support means a meaningful subset of tumors has high expression,
      even if the cohort median is not high.
    """
    if median_zscore is None:
        return "Expression data not available"

    if median_zscore >= 1.0 or percent_high >= 20:
        return "High broad expression support"

    if median_zscore >= 0.5 or percent_high >= 10:
        return "Moderate expression support"

    if percent_high >= 5:
        return "Subgroup high-expression support"

    if median_zscore <= -1.0 or percent_low >= 20:
        return "Low-expression signal"

    return "Little or no expression support"


def describe_expression_reference(expression_profile_id: str) -> str:
    """
    Describe what the selected expression z-score profile is using as reference.
    """
    profile = str(expression_profile_id).lower()

    if "ref_normal" in profile:
        return "Normal-reference z-score profile"

    if "all_sample" in profile:
        return "All-sample-reference z-score profile"

    if "median_zscores" in profile:
        return "Diploid-sample-reference z-score profile"

    return "Expression z-score profile"


def get_cbioportal_expression_summary(gene: str, cancer_type: str) -> Dict:
    """
    Return patient-tumor expression summary for a gene/cancer pair.
    """
    study_id = choose_available_study(cancer_type)

    if not study_id:
        return {
            "available": False,
            "gene": gene,
            "cancer_type": cancer_type,
            "note": f"No cBioPortal study mapping found or available for {cancer_type}."
        }

    entrez_gene_id = get_gene_entrez_id(gene)

    if entrez_gene_id is None:
        return {
            "available": False,
            "gene": gene,
            "cancer_type": cancer_type,
            "study_id": study_id,
            "note": f"Could not resolve gene symbol {gene} to Entrez ID through cBioPortal."
        }

    profiles = get_molecular_profiles(study_id)
    expression_profile_id = find_expression_zscore_profile_id(profiles)

    if not expression_profile_id:
        return {
            "available": False,
            "gene": gene,
            "cancer_type": cancer_type,
            "study_id": study_id,
            "note": "No mRNA expression z-score profile found for this study."
        }

    sample_list_id = get_sample_list_id(study_id)

    try:
        records = fetch_expression_values(
            expression_profile_id,
            sample_list_id,
            entrez_gene_id,
        )
    except Exception as e:
        return {
            "available": False,
            "gene": gene,
            "cancer_type": cancer_type,
            "study_id": study_id,
            "expression_profile_id": expression_profile_id,
            "note": str(e),
        }

    values = []

    for record in records:
        value = record.get("value")
        try:
            values.append(float(value))
        except Exception:
            continue

    if not values:
        return {
            "available": False,
            "gene": gene,
            "cancer_type": cancer_type,
            "study_id": study_id,
            "expression_profile_id": expression_profile_id,
            "note": "No expression values returned for this gene/profile."
        }

    total = len(values)
    median_z = round(float(statistics.median(values)), 3)
    mean_z = round(float(statistics.mean(values)), 3)
    high_count = sum(v >= 2.0 for v in values)
    low_count = sum(v <= -2.0 for v in values)

    percent_high = round((high_count / total) * 100, 2)
    percent_low = round((low_count / total) * 100, 2)

    expression_support = classify_expression_support(
        median_z,
        percent_high,
        percent_low,
    )

    return {
        "available": True,
        "gene": gene,
        "cancer_type": cancer_type,
        "study_id": study_id,
        "entrez_gene_id": entrez_gene_id,
        "expression_profile_id": expression_profile_id,
        "expression_reference": describe_expression_reference(expression_profile_id),
        "expression_sample_count": total,
        "median_expression_zscore": median_z,
        "mean_expression_zscore": mean_z,
        "high_expression_samples": high_count,
        "low_expression_samples": low_count,
        "percent_high_expression": percent_high,
        "percent_low_expression": percent_low,
        "expression_support": expression_support,
        "note": (
            "cBioPortal mRNA expression z-score summary. High expression is counted as z >= 2. "
            "Low expression is counted as z <= -2. Interpretation depends on the reference profile used."
        )
    }
