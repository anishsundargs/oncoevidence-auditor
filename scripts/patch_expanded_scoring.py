from pathlib import Path


p = Path("src/evidence_scoring.py")
text = p.read_text()

old = '''def score_component(component: str, value: str) -> float:
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
'''

new = '''def score_component(component: str, value: str) -> float:
    """Return weighted score for one evidence component.

    The original app used compact labels such as strong/moderate/weak.
    The expanded pan-cancer catalog uses richer descriptive labels such as
    "Strong dependency", "Context-dependent", and "Known cancer-context gene".
    This function supports both vocabularies.
    """
    raw = value
    v = str(value).strip().lower()
    max_points = POINTS.get(component, 0)

    if v in {"", "none", "nan", "not available"}:
        return 0.0

    # Numeric novelty values, usually 0-10.
    if component == "novelty_score":
        try:
            numeric = float(raw)
            if numeric > 10:
                numeric = 10
            if numeric < 0:
                numeric = 0
            return max_points * (numeric / 10.0)
        except Exception:
            pass

        novelty_weights = {
            "high": 1.0,
            "moderate": 0.6,
            "medium": 0.6,
            "low": 0.1,
        }

        if v in novelty_weights:
            return max_points * novelty_weights[v]

        if "high" in v:
            return max_points * 1.0
        if "moderate" in v or "medium" in v:
            return max_points * 0.6
        if "low" in v:
            return max_points * 0.1

        return 0.0

    # Normal tissue safety is inverted: lower safety concern is better.
    if component == "normal_tissue_safety":
        if any(term in v for term in ["low", "favorable", "limited concern"]):
            return max_points * 1.0
        if any(term in v for term in ["moderate", "context-dependent", "context dependent", "mixed"]):
            return max_points * 0.5
        if any(term in v for term in ["potential", "caution", "concern", "safety required"]):
            return max_points * 0.35
        if any(term in v for term in ["high", "unsafe", "broad normal"]):
            return max_points * 0.0
        return max_points * 0.35

    # Component-specific descriptive scoring.
    if component == "tumor_expression":
        if any(term in v for term in ["strong", "high", "moderate/high", "broad"]):
            return max_points * 1.0
        if any(term in v for term in ["subgroup", "cell-state", "cell state", "context-dependent", "context dependent", "epithelial expression"]):
            return max_points * 0.65
        if any(term in v for term in ["moderate"]):
            return max_points * 0.6
        if any(term in v for term in ["weak", "low", "unclear"]):
            return max_points * 0.2

    if component == "survival_association":
        if any(term in v for term in ["strong", "worse", "better", "significant"]):
            return max_points * 1.0
        if any(term in v for term in ["moderate", "subtype", "context"]):
            return max_points * 0.55
        if any(term in v for term in ["unclear", "needs validation", "mixed"]):
            return max_points * 0.25
        if any(term in v for term in ["weak", "none"]):
            return max_points * 0.1

    if component == "geo_validation":
        if any(term in v for term in ["strong", "validated", "external support"]):
            return max_points * 1.0
        if any(term in v for term in ["partial", "moderate"]):
            return max_points * 0.55
        if any(term in v for term in ["needs validation", "not validated", "weak", "unclear"]):
            return max_points * 0.2

    if component == "depmap_dependency":
        if any(term in v for term in ["strong dependency", "strong"]):
            return max_points * 1.0
        if any(term in v for term in ["moderate dependency", "moderate"]):
            return max_points * 0.6
        if any(term in v for term in ["variable", "context-dependent", "context dependent"]):
            return max_points * 0.45
        if any(term in v for term in ["not primary dependency", "weak", "little", "none"]):
            return max_points * 0.15

    if component == "mutation_cna_support":
        if any(term in v for term in ["strong", "canonical", "amplification", "fusion", "mutation/pathway", "alteration/pathway"]):
            return max_points * 1.0
        if any(term in v for term in ["known cancer-context", "known cancer context", "alteration", "expression/antigen", "pathway", "subgroup", "context"]):
            return max_points * 0.65
        if any(term in v for term in ["weak", "unclear", "needs validation"]):
            return max_points * 0.25

    # Backward compatibility with original compact labels.
    if v in VALUE_WEIGHTS:
        return max_points * VALUE_WEIGHTS[v]

    # Generic fallback for expanded catalog values.
    if any(term in v for term in ["strong", "high", "validated"]):
        return max_points * 1.0
    if any(term in v for term in ["moderate", "partial", "subgroup", "context", "variable"]):
        return max_points * 0.5
    if any(term in v for term in ["weak", "low", "unclear", "needs validation"]):
        return max_points * 0.2

    return 0.0
'''

if old not in text:
    raise SystemExit("Could not find original score_component function.")

text = text.replace(old, new)

old_flags = '''def generate_flags(row: Dict[str, str]) -> List[str]:
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
'''

new_flags = '''def generate_flags(row: Dict[str, str]) -> List[str]:
    """Generate contradiction and caution flags."""
    flags = []

    expression = str(row.get("tumor_expression", "")).lower()
    survival = str(row.get("survival_association", "")).lower()
    validation = str(row.get("geo_validation", "")).lower()
    dependency = str(row.get("depmap_dependency", "")).lower()
    safety = str(row.get("normal_tissue_safety", "")).lower()
    novelty = str(row.get("novelty_score", "")).lower()
    mutation_support = str(row.get("mutation_cna_support", "")).lower()

    expression_strong = any(term in expression for term in ["positive", "strong", "high", "moderate/high", "broad"])
    expression_weak = any(term in expression for term in ["weak", "low", "unclear"]) or not expression_strong
    dependency_strong = "strong" in dependency
    survival_claimed = any(term in survival for term in ["strong", "moderate", "worse", "better", "significant"])
    validation_weak = any(term in validation for term in ["weak", "partial", "mixed", "needs validation", "unclear"])
    safety_concern = any(term in safety for term in ["high", "potential", "caution", "concern", "safety required"])
    mutation_weak = any(term in mutation_support for term in ["weak", "unclear", "little", "none"])

    if expression_strong and any(term in survival for term in ["negative", "mixed", "worse", "unclear"]):
        flags.append("Potential contradiction: tumor expression is elevated, but survival evidence is weak, mixed, or directionally unfavorable.")

    if dependency_strong and expression_weak:
        flags.append("Potential contradiction: strong cell-line dependency but weak or context-dependent patient tumor-expression signal.")

    if dependency_strong and mutation_weak:
        flags.append("Potential contradiction: strong cell-line dependency but weak patient alteration support.")

    if survival_claimed and validation_weak:
        flags.append("Validation caution: survival association needs stronger external validation.")

    if safety_concern:
        flags.append("Safety caution: normal-tissue or proliferative-cell safety may weaken therapeutic-target framing.")

    try:
        novelty_numeric = float(novelty)
        if novelty_numeric <= 3:
            flags.append("Novelty caution: gene/cancer pair may be oversaturated or low-novelty by the current catalog score.")
    except Exception:
        if "low" in novelty:
            flags.append("Novelty caution: gene/cancer pair may be oversaturated in the literature.")

    if not flags:
        flags.append("No major contradiction detected in current evidence layers.")

    return flags
'''

if old_flags not in text:
    raise SystemExit("Could not find original generate_flags function.")

text = text.replace(old_flags, new_flags)

p.write_text(text)

print("Expanded static scoring rubric for pan-cancer catalog values.")