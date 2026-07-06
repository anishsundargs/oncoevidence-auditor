"""
PubMed literature saturation module for OncoEvidence Auditor.

This module counts how many PubMed records match a gene/cancer query.
It is used as a novelty/saturation signal, not as proof of biological importance.

Cancer-specific PubMed query terms are loaded from the central cancer registry:
data/config/cancer_registry.csv
"""

import os
from typing import Tuple
import requests

from src.cancer_registry import get_pubmed_query_terms


ESEARCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"


def build_pubmed_query(gene: str, cancer_type: str) -> str:
    """
    Build a PubMed query for a gene/cancer pair.

    Gene is restricted to Title/Abstract.
    Cancer terms come from the central cancer registry.
    """
    gene = gene.strip()

    cancer_terms = get_pubmed_query_terms(cancer_type)

    if not cancer_terms:
        cancer_terms = f'"{cancer_type}"[Title/Abstract] OR cancer[Title/Abstract]'

    gene_terms = f'"{gene}"[Title/Abstract]'

    return f"({gene_terms}) AND ({cancer_terms})"


def get_pubmed_count(gene: str, cancer_type: str) -> Tuple[int, str]:
    """
    Return PubMed result count and query string.
    """
    query = build_pubmed_query(gene, cancer_type)

    params = {
        "db": "pubmed",
        "term": query,
        "retmode": "json",
        "retmax": 0,
        "tool": "OncoEvidenceAuditor",
    }

    email = os.getenv("NCBI_EMAIL")
    if email:
        params["email"] = email

    response = requests.get(ESEARCH_URL, params=params, timeout=15)
    response.raise_for_status()

    payload = response.json()
    count = int(payload["esearchresult"]["count"])

    return count, query


def classify_literature_saturation(count: int) -> Tuple[str, str, str]:
    """
    Classify literature saturation from a PubMed hit count.
    """
    if count >= 250:
        return (
            "High saturation",
            "low",
            "This gene/cancer pair is heavily studied. Novelty is likely weak unless the project identifies a very specific new angle."
        )

    if count >= 75:
        return (
            "Moderate saturation",
            "moderate",
            "This gene/cancer pair has an existing literature base. A new project needs a sharper computational or mechanistic angle."
        )

    if count >= 15:
        return (
            "Low-moderate saturation",
            "moderate",
            "This gene/cancer pair has some literature but may still allow a focused public-data hypothesis."
        )

    return (
        "Low saturation",
        "high",
        "This gene/cancer pair appears relatively underexplored in PubMed title/abstract searches, but biological plausibility still needs validation."
    )
