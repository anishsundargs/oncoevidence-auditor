"""
Evidence scoring logic for OncoEvidence Auditor.

The scoring rubric is intentionally transparent. It is not clinically validated.
It is for research-hypothesis prioritization only.
"""

from dataclasses import dataclass
from typing import Dict, List, Tuple


POINTS = {
    "tumor_expression": 15,
    "survival_association": 15,
    "geo_validation": 20,
    "depmap_dependency": 20,
    "normal_tissue_safety": 10,
    "mutation_cna_support": 10,
    "novelty_score": 10,
}


VALUE_WEIGHTS = {
    "strong": 1.0,
    "positive": 1.0,
    "moderate": 0.7,
    "partial": 0.5,
    "mixed": 0.35,
    "weak": 0.2,
    "negative": 0.0,
    "high": 0.0,   # for safety, high normal-tissue expression is bad
    "low": 1.0,    # for safety/novelty, low concern or low saturation can be good depending on field
}


def score_component(component: str, value: str) -> float:
    """Return weighted score for one evidence component."""
    v = str(value).strip().lower()
    max_points = POINTS.get(component, 0)

    # Custom interpretation for normal tissue safety:
    # low concern = good; moderate = partial; high concern = bad.
    if component == "normal_tissue_safety":
        safety_weights = {"low": 1.0, "moderate": 0.5, "high": 0.0, "mixed": 0.35}
        return max_points * safety_weights.get(v, 0.0)

    # Custom interpretation for novelty:
    # high novelty = good, low novelty = poor.
    if component == "novelty_score":
        novelty_weights = {"high": 1.0, "moderate": 0.6, "low": 0.1}
        return max_points * novelty_weights.get(v, 0.0)

    return max_points * VALUE_WEIGHTS.get(v, 0.0)


def calculate_score(row: Dict[str, str]) -> Tuple[int, Dict[str, float]]:
    """Calculate total evidence score and component breakdown."""
    breakdown = {}
    for component in POINTS:
        breakdown[component] = score_component(component, row.get(component, "weak"))

    total = round(sum(breakdown.values()))
    return total, breakdown


def classify_tier(score: int, flags: List[str]) -> str:
    """Classify evidence tier."""
    if any("contradiction" in f.lower() for f in flags):
        return "Contradictory / needs manual review"
    if score >= 80:
        return "Strong hypothesis"
    if score >= 60:
        return "Moderate hypothesis"
    if score >= 40:
        return "Weak or uncertain hypothesis"
    return "Poor hypothesis"


def generate_flags(row: Dict[str, str]) -> List[str]:
    """Generate contradiction and caution flags."""
    flags = []

    expression = str(row.get("tumor_expression", "")).lower()
    survival = str(row.get("survival_association", "")).lower()
    validation = str(row.get("geo_validation", "")).lower()
    dependency = str(row.get("depmap_dependency", "")).lower()
    safety = str(row.get("normal_tissue_safety", "")).lower()
    novelty = str(row.get("novelty_score", "")).lower()

    if expression in {"positive", "strong"} and survival in {"negative", "mixed"}:
        flags.append("Potential contradiction: tumor expression is elevated, but survival evidence is weak, mixed, or directionally unfavorable.")

    if dependency == "strong" and expression not in {"positive", "strong"}:
        flags.append("Potential contradiction: strong cell-line dependency but weak patient tumor-expression signal.")

    if survival in {"strong", "moderate"} and validation in {"weak", "partial", "mixed"}:
        flags.append("Validation caution: survival association needs stronger external validation.")

    if safety == "high":
        flags.append("Safety caution: high normal-tissue expression may weaken therapeutic-target framing.")

    if novelty == "low":
        flags.append("Novelty caution: gene/cancer pair may be oversaturated in the literature.")

    if not flags:
        flags.append("No major contradiction detected in current evidence layers.")

    return flags


def generate_safe_claim(row: Dict[str, str], score: int, tier: str) -> str:
    """Generate conservative, research-safe wording."""
    gene = row.get("gene", "This gene")
    cancer = row.get("cancer_type", "this cancer")

    if "Strong" in tier:
        return (
            f"{gene} shows multi-layer public-data support as a candidate gene in {cancer}, "
            "with evidence that may justify further mechanistic or experimental investigation."
        )

    if "Moderate" in tier:
        return (
            f"{gene} shows partial public-data support as a candidate gene in {cancer}, "
            "but the hypothesis should be framed cautiously and validated in independent cohorts."
        )

    if "Contradictory" in tier:
        return (
            f"Public-data evidence for {gene} in {cancer} is internally inconsistent. "
            "This gene is better framed as a hypothesis requiring additional validation, not as a confirmed biomarker or target."
        )

    return (
        f"Current public-data evidence is insufficient to strongly support {gene} as a candidate gene in {cancer}. "
        "Additional validation or a narrower biological claim is needed."
    )
