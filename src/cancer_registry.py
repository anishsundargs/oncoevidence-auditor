"""
Cancer registry module for OncoEvidence Auditor.

This centralizes cancer-type mappings so the app can scale beyond the first two
validated case studies without hard-coding cancer metadata across multiple modules.
"""

from pathlib import Path
from typing import Dict, List, Optional
import pandas as pd


REGISTRY_PATH = Path("data/config/cancer_registry.csv")


def load_cancer_registry(path: Path = REGISTRY_PATH) -> pd.DataFrame:
    """Load cancer registry table."""
    return pd.read_csv(path)


def list_supported_cancers() -> List[str]:
    """Return supported cancer display names."""
    df = load_cancer_registry()
    return sorted(df["cancer_type"].dropna().unique().tolist())


def get_cancer_record(cancer_type: str) -> Optional[Dict]:
    """Return one cancer registry record as a dictionary."""
    df = load_cancer_registry()
    match = df[df["cancer_type"] == cancer_type]

    if match.empty:
        return None

    return match.iloc[0].to_dict()


def split_semicolon_field(value) -> List[str]:
    """Split semicolon-delimited fields into clean list."""
    if pd.isna(value):
        return []

    return [item.strip() for item in str(value).split(";") if item.strip()]


def get_cbio_study_candidates(cancer_type: str) -> List[str]:
    """Return cBioPortal study candidates for a cancer type."""
    record = get_cancer_record(cancer_type)
    if not record:
        return []

    return split_semicolon_field(record.get("cbio_study_candidates"))


def get_depmap_oncotree_codes(cancer_type: str) -> List[str]:
    """Return DepMap OncotreeCode filters for a cancer type."""
    record = get_cancer_record(cancer_type)
    if not record:
        return []

    return split_semicolon_field(record.get("depmap_oncotree_codes"))


def get_pubmed_query_terms(cancer_type: str) -> Optional[str]:
    """Return PubMed cancer query terms for a cancer type."""
    record = get_cancer_record(cancer_type)
    if not record:
        return None

    value = record.get("pubmed_query_terms")
    if pd.isna(value):
        return None

    return str(value).strip()
