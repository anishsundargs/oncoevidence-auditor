"""
Specificity index module for OncoEvidence Auditor.

This module compares selected-cancer dependency against pan-cancer dependency.
It helps identify whether a gene's dependency signal is lineage-specific or broadly essential.
"""


def calculate_specificity_index(depmap_result, common_result):
    """
    Calculate selected-cancer dependency percentage minus pan-cancer dependency percentage.
    """
    selected_percent = depmap_result.get("percent_dependent")
    pan_percent = common_result.get("pan_cancer_percent_dependent")

    if selected_percent is None or pan_percent is None:
        return {
            "available": False,
            "specificity_delta": None,
            "specificity_label": "Not available",
            "specificity_note": "Specificity index could not be calculated because dependency percentages are missing."
        }

    delta = round(float(selected_percent) - float(pan_percent), 1)

    if delta >= 25:
        label = "High lineage specificity"
        note = (
            "The selected cancer group has a much higher dependency rate than the pan-cancer background, "
            "supporting a potentially lineage-enriched vulnerability hypothesis."
        )
    elif delta >= 10:
        label = "Moderate lineage specificity"
        note = (
            "The selected cancer group has a moderately higher dependency rate than the pan-cancer background. "
            "This may support a lineage-enriched hypothesis, but additional validation is needed."
        )
    elif delta >= -10:
        label = "Low lineage specificity"
        note = (
            "The selected cancer dependency rate is similar to the pan-cancer background. "
            "This suggests the signal may not be cancer-lineage specific."
        )
    else:
        label = "Lower-than-background dependency"
        note = (
            "The selected cancer group has a lower dependency rate than the pan-cancer background. "
            "This weakens a lineage-specific dependency claim."
        )

    return {
        "available": True,
        "specificity_delta": delta,
        "specificity_label": label,
        "specificity_note": note
    }
