"""
cBioPortal alteration evidence module for OncoEvidence Auditor.

Goal:
For a gene/cancer pair, retrieve patient-tumor alteration evidence from cBioPortal.

This module currently supports the first validated case studies:
- GBM
- Gastric cancer

It is structured so additional cancer types can be added later by extending STUDY_CANDIDATES.
"""

from typing import Dict, List, Optional
import requests

from src.cancer_registry import get_cbio_study_candidates


CBIO_BASE_URL = "https://www.cbioportal.org/api"


def cbio_get(path: str, params: Optional[dict] = None):
    """GET request helper for cBioPortal API."""
    url = f"{CBIO_BASE_URL}{path}"
    response = requests.get(
        url,
        params=params,
        headers={"Accept": "application/json"},
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


def cbio_post(path: str, payload: dict):
    """POST request helper for cBioPortal API."""
    url = f"{CBIO_BASE_URL}{path}"
    response = requests.post(
        url,
        json=payload,
        headers={"Accept": "application/json", "Content-Type": "application/json"},
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


def choose_available_study(cancer_type: str) -> Optional[str]:
    """Pick the first available cBioPortal study ID from the central cancer registry."""
    candidates = get_cbio_study_candidates(cancer_type)

    for study_id in candidates:
        try:
            cbio_get(f"/studies/{study_id}")
            return study_id
        except Exception:
            continue

    return None


def get_study_sample_count(study_id: str) -> int:
    """Return number of samples in a study."""
    try:
        samples = cbio_get(f"/studies/{study_id}/samples", params={"projection": "SUMMARY"})
        return len(samples)
    except Exception:
        return 0


def get_gene_entrez_id(gene: str) -> Optional[int]:
    """Resolve a Hugo gene symbol to Entrez ID through cBioPortal."""
    try:
        gene_info = cbio_get(f"/genes/{gene}")
        return int(gene_info["entrezGeneId"])
    except Exception:
        return None


def get_molecular_profiles(study_id: str) -> List[dict]:
    """Get molecular profiles for a study."""
    return cbio_get(f"/studies/{study_id}/molecular-profiles")


def find_mutation_profile_id(profiles: List[dict]) -> Optional[str]:
    """
    Find mutation profile.

    Prefer molecularAlterationType == MUTATION_EXTENDED and datatype == MAF.
    """
    for profile in profiles:
        if (
            profile.get("molecularAlterationType") == "MUTATION_EXTENDED"
            and profile.get("datatype") == "MAF"
        ):
            return profile.get("molecularProfileId")

    for profile in profiles:
        profile_id = str(profile.get("molecularProfileId", "")).lower()
        name = str(profile.get("name", "")).lower()
        if "mutation" in profile_id or "mutation" in name:
            return profile.get("molecularProfileId")

    return None


def find_discrete_cna_profile_id(profiles: List[dict]) -> Optional[str]:
    """
    Find gene-level discrete copy-number profile.

    Correct profile should usually be:
    - molecularAlterationType == COPY_NUMBER_ALTERATION
    - datatype == DISCRETE
    - often profile ID ends with '_gistic'

    Avoid arm-level CNA because that is a GENERIC_ASSAY, not gene-level CNA.
    """
    # Best case: exact type/datatype match and gistic ID.
    for profile in profiles:
        profile_id = str(profile.get("molecularProfileId", "")).lower()
        if (
            profile.get("molecularAlterationType") == "COPY_NUMBER_ALTERATION"
            and profile.get("datatype") == "DISCRETE"
            and "gistic" in profile_id
        ):
            return profile.get("molecularProfileId")

    # Second best: any discrete gene-level CNA profile.
    for profile in profiles:
        if (
            profile.get("molecularAlterationType") == "COPY_NUMBER_ALTERATION"
            and profile.get("datatype") == "DISCRETE"
        ):
            return profile.get("molecularProfileId")

    return None


def get_sample_list_id(study_id: str) -> str:
    """
    Return an all-samples list ID.
    cBioPortal commonly uses '<study_id>_all'.
    """
    return f"{study_id}_all"


def fetch_discrete_cna_values(
    molecular_profile_id: str,
    sample_list_id: str,
    entrez_gene_id: int,
) -> List[dict]:
    """
    Fetch discrete copy-number calls for one gene.

    Values:
    -2 = homozygous/deep deletion
    -1 = shallow deletion
     0 = neutral
     1 = gain
     2 = high-level amplification
    """
    payload = {
        "entrezGeneIds": [entrez_gene_id],
        "sampleListId": sample_list_id,
    }

    return cbio_post(
        f"/molecular-profiles/{molecular_profile_id}/molecular-data/fetch",
        payload,
    )


def fetch_mutations(
    molecular_profile_id: str,
    sample_list_id: str,
    entrez_gene_id: int,
) -> List[dict]:
    """Fetch mutations for one gene."""
    payload = {
        "entrezGeneIds": [entrez_gene_id],
        "sampleListId": sample_list_id,
    }

    return cbio_post(
        f"/molecular-profiles/{molecular_profile_id}/mutations/fetch",
        payload,
    )


def summarize_cna(records: List[dict], total_samples: int) -> Dict:
    """Summarize discrete CNA records."""
    if not records or total_samples == 0:
        return {
            "amplified_samples": 0,
            "deep_deleted_samples": 0,
            "cna_altered_samples": 0,
            "cna_alteration_frequency": 0.0,
        }

    amplified = 0
    deep_deleted = 0
    altered = 0

    for record in records:
        value = record.get("value")

        try:
            value = int(float(value))
        except Exception:
            continue

        if value == 2:
            amplified += 1
        if value == -2:
            deep_deleted += 1
        if value != 0:
            altered += 1

    return {
        "amplified_samples": amplified,
        "deep_deleted_samples": deep_deleted,
        "cna_altered_samples": altered,
        "amplification_frequency": round((amplified / total_samples) * 100, 2),
        "deep_deletion_frequency": round((deep_deleted / total_samples) * 100, 2),
        "cna_alteration_frequency": round((altered / total_samples) * 100, 2),
    }


def summarize_mutations(records: List[dict], total_samples: int) -> Dict:
    """Summarize mutation records."""
    if total_samples == 0:
        return {
            "mutated_samples": 0,
            "mutation_frequency": 0.0,
        }

    sample_ids = set()

    for record in records:
        sample_id = record.get("sampleId")
        if sample_id:
            sample_ids.add(sample_id)

    mutated = len(sample_ids)

    return {
        "mutated_samples": mutated,
        "mutation_frequency": round((mutated / total_samples) * 100, 2),
    }


def classify_patient_alteration_support(
    mutation_frequency: float,
    amplification_frequency: float,
    deep_deletion_frequency: float,
) -> str:
    """
    Simple patient alteration support label.

    This intentionally emphasizes mutations, high-level amplifications, and deep deletions.
    Broad GISTIC altered frequency can include shallow gains/losses and should not drive
    strong support by itself.
    """
    max_driver_like_freq = max(
        mutation_frequency,
        amplification_frequency,
        deep_deletion_frequency,
    )

    if max_driver_like_freq >= 20:
        return "High patient alteration support"
    if max_driver_like_freq >= 10:
        return "Moderate patient alteration support"
    if max_driver_like_freq >= 3:
        return "Low patient alteration support"
    return "Little or no patient alteration support"


def get_cbioportal_alteration_summary(gene: str, cancer_type: str) -> Dict:
    """
    Return alteration summary for a gene/cancer pair.
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
            "note": f"Could not resolve gene symbol {gene} to an Entrez ID through cBioPortal."
        }

    total_samples = get_study_sample_count(study_id)
    sample_list_id = get_sample_list_id(study_id)
    profiles = get_molecular_profiles(study_id)

    mutation_profile_id = find_mutation_profile_id(profiles)
    cna_profile_id = find_discrete_cna_profile_id(profiles)

    mutation_records = []
    cna_records = []

    mutation_error = None
    cna_error = None

    if mutation_profile_id:
        try:
            mutation_records = fetch_mutations(
                mutation_profile_id,
                sample_list_id,
                entrez_gene_id,
            )
        except Exception as e:
            mutation_error = str(e)

    if cna_profile_id:
        try:
            cna_records = fetch_discrete_cna_values(
                cna_profile_id,
                sample_list_id,
                entrez_gene_id,
            )
        except Exception as e:
            cna_error = str(e)

    mutation_summary = summarize_mutations(mutation_records, total_samples)
    cna_summary = summarize_cna(cna_records, total_samples)

    rough_any_altered = mutation_summary["mutated_samples"] + cna_summary["cna_altered_samples"]
    rough_any_freq = round((rough_any_altered / total_samples) * 100, 2) if total_samples else 0.0

    alteration_support = classify_patient_alteration_support(
        mutation_summary["mutation_frequency"],
        cna_summary["amplification_frequency"],
        cna_summary["deep_deletion_frequency"],
    )

    return {
        "available": True,
        "gene": gene,
        "cancer_type": cancer_type,
        "study_id": study_id,
        "entrez_gene_id": entrez_gene_id,
        "total_samples": total_samples,
        "mutation_profile_id": mutation_profile_id,
        "cna_profile_id": cna_profile_id,
        "mutated_samples": mutation_summary["mutated_samples"],
        "mutation_frequency": mutation_summary["mutation_frequency"],
        "amplified_samples": cna_summary["amplified_samples"],
        "deep_deleted_samples": cna_summary["deep_deleted_samples"],
        "cna_altered_samples": cna_summary["cna_altered_samples"],
        "amplification_frequency": cna_summary["amplification_frequency"],
        "deep_deletion_frequency": cna_summary["deep_deletion_frequency"],
        "cna_alteration_frequency": cna_summary["cna_alteration_frequency"],
        "rough_any_alteration_count": rough_any_altered,
        "rough_any_alteration_frequency": rough_any_freq,
        "patient_alteration_support": alteration_support,
        "mutation_error": mutation_error,
        "cna_error": cna_error,
        "note": (
            "cBioPortal alteration summary using mutation and gene-level discrete GISTIC CNA profiles. "
            "Patient alteration support is based on mutation, high-level amplification, and deep-deletion frequencies. "
            "Broad CNA alteration frequency includes shallow gains/losses and is reported separately."
        )
    }
