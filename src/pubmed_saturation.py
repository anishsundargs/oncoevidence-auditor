"""
PubMed literature saturation module for OncoEvidence Auditor.

This module counts how many PubMed records match a gene/cancer query.
It is used as a novelty/saturation signal, not as proof of biological importance.
"""

import os
from typing import Tuple
import requests


ESEARCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"


CANCER_QUERY_TERMS = {
    "GBM": '("glioblastoma"[Title/Abstract] OR "GBM"[Title/Abstract] OR "glioma"[Title/Abstract])',
    "Gastric cancer": '("gastric cancer"[Title/Abstract] OR "stomach cancer"[Title/Abstract] OR "gastric adenocarcinoma"[Title/Abstract])',
}


def build_pubmed_query(gene: str, cancer_type: str) -> str:
    """
    Build a PubMed query for a gene/cancer pair.

    Restricting to Title/Abstract keeps the result count more relevant.
    """
    gene = gene.strip()
    cancer_terms = CANCER_QUERY_TERMS.get(
        cancer_type,
        f'("{cancer_type}"[Title/Abstract] OR "cancer"[Title/Abstract])'
    )

    gene_terms = f'("{gene}"[Title/Abstract])'
    return f"{gene_terms} AND {cancer_terms}"


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
