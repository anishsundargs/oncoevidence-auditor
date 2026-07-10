"""
cBioPortal survival/prognosis evidence module for OncoEvidence Auditor.

This module compares survival summaries between:
- high-expression tumors: expression z-score >= 2
- other tumors: expression z-score < 2

It is intentionally cautious. It does not compute a full Kaplan-Meier/log-rank test yet.
That can be added later after the basic survival data pipeline is validated.
"""

from typing import Dict, List, Optional
import statistics
import requests

from src.cbioportal_alterations import (
    CBIO_BASE_URL,
    choose_available_study,
    get_gene_entrez_id,
    get_molecular_profiles,
    get_sample_list_id,
)
from src.cbioportal_expression import (
    find_expression_zscore_profile_id,
    fetch_expression_values,
)


HIGH_EXPRESSION_Z = 2.0
MIN_GROUP_SIZE = 5
MEANINGFUL_MEDIAN_OS_DIFFERENCE_MONTHS = 6.0


def cbio_get_params(endpoint: str, params: Optional[Dict] = None):
    """GET request to cBioPortal with optional query parameters."""
    response = requests.get(
        f"{CBIO_BASE_URL}{endpoint}",
        params=params or {},
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


def parse_float(value):
    """Safely parse numeric values."""
    try:
        return float(value)
    except Exception:
        return None


def parse_deceased(status_value) -> Optional[bool]:
    """
    Parse cBioPortal OS_STATUS values.

    Common examples:
    - "0:LIVING"
    - "1:DECEASED"
    - "LIVING"
    - "DECEASED"
    """
    if status_value is None:
        return None

    text = str(status_value).upper()

    if "DECEASED" in text or text.startswith("1:"):
        return True

    if "LIVING" in text or text.startswith("0:"):
        return False

    return None


def sample_to_patient_id(sample_id: str) -> str:
    """
    Convert a TCGA-style sample barcode to a patient barcode.

    TCGA sample IDs usually begin with a 12-character patient barcode:
    TCGA-XX-XXXX
    """
    sample_id = str(sample_id)

    if sample_id.startswith("TCGA-") and len(sample_id) >= 12:
        return sample_id[:12]

    # Fallback: return sample ID if no TCGA-style patient ID can be inferred.
    return sample_id


def fetch_patient_clinical_data(study_id: str) -> List[Dict]:
    """
    Fetch patient-level clinical data from cBioPortal.

    This endpoint returns records such as OS_MONTHS and OS_STATUS when available.
    """
    return cbio_get_params(
        f"/studies/{study_id}/clinical-data",
        params={
            "clinicalDataType": "PATIENT",
            "projection": "DETAILED",
        },
    )


def build_patient_survival_map(clinical_records: List[Dict]) -> Dict[str, Dict]:
    """
    Convert long-form clinical records into patient-level survival records.
    """
    patient_map = {}

    for record in clinical_records:
        patient_id = (
            record.get("patientId")
            or record.get("uniquePatientKey")
            or record.get("entityId")
        )

        attr = record.get("clinicalAttributeId")
        value = record.get("value")

        if not patient_id or not attr:
            continue

        patient_id = str(patient_id)
        attr = str(attr).upper()

        if patient_id not in patient_map:
            patient_map[patient_id] = {}

        patient_map[patient_id][attr] = value

    survival_map = {}

    for patient_id, attrs in patient_map.items():
        os_months = parse_float(
            attrs.get("OS_MONTHS")
            or attrs.get("OVERALL_SURVIVAL_MONTHS")
        )
        deceased = parse_deceased(
            attrs.get("OS_STATUS")
            or attrs.get("OVERALL_SURVIVAL_STATUS")
        )

        if os_months is None or deceased is None:
            continue

        survival_map[patient_id] = {
            "os_months": os_months,
            "deceased": deceased,
        }

    return survival_map


def summarize_survival_group(records: List[Dict]) -> Dict:
    """Summarize OS months and event rate for a group."""
    if not records:
        return {
            "n": 0,
            "median_os_months": None,
            "event_rate_percent": None,
        }

    os_values = [r["os_months"] for r in records if r.get("os_months") is not None]
    events = [r["deceased"] for r in records if r.get("deceased") is not None]

    if not os_values or not events:
        return {
            "n": len(records),
            "median_os_months": None,
            "event_rate_percent": None,
        }

    return {
        "n": len(records),
        "median_os_months": round(float(statistics.median(os_values)), 2),
        "event_rate_percent": round((sum(events) / len(events)) * 100, 2),
    }


def classify_survival_signal(high_summary: Dict, other_summary: Dict) -> str:
    """
    Classify survival signal cautiously from high-expression vs other tumors.
    """
    high_n = high_summary.get("n", 0)
    other_n = other_summary.get("n", 0)

    high_median = high_summary.get("median_os_months")
    other_median = other_summary.get("median_os_months")

    if high_n < MIN_GROUP_SIZE:
        return "Insufficient high-expression subgroup for survival comparison"

    if other_n < MIN_GROUP_SIZE:
        return "Insufficient comparison group for survival comparison"

    if high_median is None or other_median is None:
        return "Survival data incomplete"

    difference = round(high_median - other_median, 2)

    if difference <= -MEANINGFUL_MEDIAN_OS_DIFFERENCE_MONTHS:
        return "High-expression subgroup shows worse-survival signal"

    if difference >= MEANINGFUL_MEDIAN_OS_DIFFERENCE_MONTHS:
        return "High-expression subgroup shows better-survival signal"

    return "No clear median-survival separation"


def get_cbioportal_survival_summary(gene: str, cancer_type: str) -> Dict:
    """
    Return survival/prognosis summary for high-expression vs other tumors.
    """
    study_id = choose_available_study(cancer_type)

    if not study_id:
        return {
            "available": False,
            "gene": gene,
            "cancer_type": cancer_type,
            "note": f"No cBioPortal study mapping found or available for {cancer_type}.",
        }

    entrez_gene_id = get_gene_entrez_id(gene)

    if entrez_gene_id is None:
        return {
            "available": False,
            "gene": gene,
            "cancer_type": cancer_type,
            "study_id": study_id,
            "note": f"Could not resolve gene symbol {gene} to Entrez ID.",
        }

    profiles = get_molecular_profiles(study_id)
    expression_profile_id = find_expression_zscore_profile_id(profiles)

    if not expression_profile_id:
        return {
            "available": False,
            "gene": gene,
            "cancer_type": cancer_type,
            "study_id": study_id,
            "note": "No mRNA expression z-score profile found for survival grouping.",
        }

    sample_list_id = get_sample_list_id(study_id)

    expression_records = fetch_expression_values(
        expression_profile_id,
        sample_list_id,
        entrez_gene_id,
    )

    clinical_records = fetch_patient_clinical_data(study_id)
    survival_map = build_patient_survival_map(clinical_records)

    high_records = []
    other_records = []

    matched_patients = set()

    for record in expression_records:
        sample_id = record.get("sampleId")
        value = parse_float(record.get("value"))

        if sample_id is None or value is None:
            continue

        patient_id = sample_to_patient_id(sample_id)

        if patient_id not in survival_map:
            continue

        if patient_id in matched_patients:
            continue

        matched_patients.add(patient_id)

        survival_record = survival_map[patient_id].copy()
        survival_record["patient_id"] = patient_id
        survival_record["expression_zscore"] = value

        if value >= HIGH_EXPRESSION_Z:
            survival_record["group"] = "High expression"
            high_records.append(survival_record)
        else:
            survival_record["group"] = "Other expression"
            other_records.append(survival_record)

    high_summary = summarize_survival_group(high_records)
    other_summary = summarize_survival_group(other_records)

    survival_signal = classify_survival_signal(high_summary, other_summary)

    median_difference = None
    if (
        high_summary.get("median_os_months") is not None
        and other_summary.get("median_os_months") is not None
    ):
        median_difference = round(
            high_summary["median_os_months"] - other_summary["median_os_months"],
            2,
        )

    return {
        "available": True,
        "gene": gene,
        "cancer_type": cancer_type,
        "study_id": study_id,
        "expression_profile_id": expression_profile_id,
        "survival_patients_matched": len(matched_patients),
        "high_expression_threshold_z": HIGH_EXPRESSION_Z,
        "high_expression_survival_n": high_summary.get("n"),
        "other_expression_survival_n": other_summary.get("n"),
        "high_expression_median_os_months": high_summary.get("median_os_months"),
        "other_expression_median_os_months": other_summary.get("median_os_months"),
        "median_os_difference_months": median_difference,
        "high_expression_event_rate_percent": high_summary.get("event_rate_percent"),
        "other_expression_event_rate_percent": other_summary.get("event_rate_percent"),
        "survival_records": high_records + other_records,
        "high_expression_records": high_records,
        "other_expression_records": other_records,
        "survival_signal": survival_signal,
        "note": (
            "Survival comparison is based on high-expression tumors "
            f"(z >= {HIGH_EXPRESSION_Z}) versus other tumors. This is a descriptive "
            "screening summary, not a Kaplan-Meier/log-rank survival analysis."
        ),
    }
