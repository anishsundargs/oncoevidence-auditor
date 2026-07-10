from typing import Dict, Optional
import plotly.graph_objects as go
from src.plotly_theme import apply_plotly_theme

LAYER_ORDER = [
    "PubMed literature",
    "DepMap dependency",
    "Common-essential caution",
    "Lineage specificity",
    "Patient alteration",
    "Patient expression",
    "Survival/prognosis",
    "Gene role classification",
    "Pathway/function annotation",
    "Therapeutic relevance",
]


def plot_evidence_coverage_gauge(coverage_result: Dict) -> Optional[go.Figure]:
    if not coverage_result:
        return None

    percent = coverage_result.get("evidence_coverage_percent")
    if percent is None:
        return None

    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=percent,
            number={"suffix": "%"},
            title={"text": "Evidence coverage"},
            gauge={"axis": {"range": [0, 100]}},
        )
    )

    fig.update_layout(height=300, margin=dict(l=20, r=20, t=50, b=20))
    return apply_plotly_theme(fig)


def plot_evidence_layer_bar(coverage_result: Dict) -> Optional[go.Figure]:
    if not coverage_result:
        return None

    available = set(coverage_result.get("available_layers") or [])
    missing = set(coverage_result.get("missing_layers") or [])

    if not available and not missing:
        return None

    layers = []
    values = []
    labels = []

    for layer in LAYER_ORDER:
        layers.append(layer)
        if layer in available:
            values.append(1)
            labels.append("Available")
        elif layer in missing:
            values.append(0)
            labels.append("Missing")
        else:
            values.append(0)
            labels.append("Not returned")

    fig = go.Figure(
        go.Bar(
            x=values,
            y=layers,
            orientation="h",
            text=labels,
            textposition="auto",
            hovertemplate="%{y}: %{text}<extra></extra>",
        )
    )

    fig.update_layout(
        title="10-layer evidence profile",
        xaxis=dict(title="Layer available", range=[0, 1.05], tickvals=[0, 1], ticktext=["No", "Yes"]),
        yaxis=dict(title="", autorange="reversed"),
        height=440,
        margin=dict(l=20, r=20, t=60, b=20),
        showlegend=False,
    )

    return apply_plotly_theme(fig)
def plot_dependency_context_bar(depmap_result: Dict, common_result: Dict) -> Optional[go.Figure]:
    """Compare selected-cancer dependency against pan-cancer dependency."""
    if not depmap_result or not common_result:
        return None

    selected_percent = depmap_result.get("percent_dependent")
    pan_percent = common_result.get("pan_cancer_percent_dependent")

    if selected_percent is None and pan_percent is None:
        return None

    fig = go.Figure(
        data=[
            go.Bar(
                x=["Selected cancer", "Pan-cancer background"],
                y=[selected_percent or 0, pan_percent or 0],
                text=[selected_percent or 0, pan_percent or 0],
                textposition="auto",
            )
        ]
    )

    fig.update_layout(
        title="Dependency frequency: selected cancer vs pan-cancer",
        xaxis_title="Context",
        yaxis_title="Percent dependent cell lines",
        yaxis=dict(range=[0, 100]),
        height=380,
        margin=dict(l=20, r=20, t=60, b=20),
        showlegend=False,
    )

    return apply_plotly_theme(fig)


def plot_dependency_score_context_bar(depmap_result: Dict, common_result: Dict) -> Optional[go.Figure]:
    """Compare selected-cancer median dependency score against pan-cancer median dependency score."""
    if not depmap_result or not common_result:
        return None

    selected_median = depmap_result.get("median_dependency_score")
    pan_median = common_result.get("pan_cancer_median_dependency_score")

    if selected_median is None and pan_median is None:
        return None

    fig = go.Figure(
        data=[
            go.Bar(
                x=["Selected cancer", "Pan-cancer background"],
                y=[selected_median or 0, pan_median or 0],
                text=[selected_median or 0, pan_median or 0],
                textposition="auto",
            )
        ]
    )

    fig.update_layout(
        title="Median dependency score context",
        xaxis_title="Context",
        yaxis_title="Median CRISPRGeneEffect score",
        height=380,
        margin=dict(l=20, r=20, t=60, b=20),
        showlegend=False,
    )

    return apply_plotly_theme(fig)


def plot_specificity_delta_indicator(specificity_result: Dict) -> Optional[go.Figure]:
    """Show lineage specificity delta as an indicator."""
    if not specificity_result:
        return None

    delta = specificity_result.get("specificity_delta")
    if delta is None:
        return None

    fig = go.Figure(
        go.Indicator(
            mode="number+delta",
            value=delta,
            number={"suffix": " pp"},
            title={"text": "Specificity delta"},
            delta={"reference": 0, "relative": False},
        )
    )

    fig.update_layout(
        height=260,
        margin=dict(l=20, r=20, t=50, b=20),
    )

    return apply_plotly_theme(fig)
def plot_patient_alteration_bar(cbio_result: Dict) -> Optional[go.Figure]:
    """Show cBioPortal patient alteration frequencies."""
    if not cbio_result or not cbio_result.get("available"):
        return None

    values = {
        "Mutation": cbio_result.get("mutation_frequency"),
        "Amplification": cbio_result.get("amplification_frequency"),
        "Deep deletion": cbio_result.get("deep_deletion_frequency"),
    }

    if cbio_result.get("broad_cna_altered_frequency") is not None:
        values["Broad CNA altered"] = cbio_result.get("broad_cna_altered_frequency")

    clean = {k: v for k, v in values.items() if v is not None}

    if not clean:
        return None

    fig = go.Figure(
        data=[
            go.Bar(
                x=list(clean.keys()),
                y=list(clean.values()),
                text=list(clean.values()),
                textposition="auto",
            )
        ]
    )

    fig.update_layout(
        title="Patient alteration frequencies",
        xaxis_title="Alteration type",
        yaxis_title="Frequency (%)",
        yaxis=dict(range=[0, max(10, min(100, max(clean.values()) * 1.25))]),
        height=380,
        margin=dict(l=20, r=20, t=60, b=20),
        showlegend=False,
    )

    return apply_plotly_theme(fig)


def plot_patient_expression_bar(expression_result: Dict) -> Optional[go.Figure]:
    """Show high-expression and low-expression tumor fractions."""
    if not expression_result or not expression_result.get("available"):
        return None

    high = expression_result.get("percent_high_expression")
    low = expression_result.get("percent_low_expression")

    if high is None and low is None:
        return None

    fig = go.Figure(
        data=[
            go.Bar(
                x=["High expression tumors", "Low expression tumors"],
                y=[high or 0, low or 0],
                text=[high or 0, low or 0],
                textposition="auto",
            )
        ]
    )

    fig.update_layout(
        title="Expression subgroup frequencies",
        xaxis_title="Expression subgroup",
        yaxis_title="Tumors (%)",
        yaxis=dict(range=[0, 100]),
        height=380,
        margin=dict(l=20, r=20, t=60, b=20),
        showlegend=False,
    )

    return apply_plotly_theme(fig)


def plot_expression_summary_bar(expression_result: Dict) -> Optional[go.Figure]:
    """Show mean and median expression z-score summary."""
    if not expression_result or not expression_result.get("available"):
        return None

    median = expression_result.get("median_expression_zscore")
    mean = expression_result.get("mean_expression_zscore")

    if median is None and mean is None:
        return None

    fig = go.Figure(
        data=[
            go.Bar(
                x=["Median z-score", "Mean z-score"],
                y=[median or 0, mean or 0],
                text=[median or 0, mean or 0],
                textposition="auto",
            )
        ]
    )

    fig.update_layout(
        title="Expression z-score summary",
        xaxis_title="Statistic",
        yaxis_title="Expression z-score",
        height=340,
        margin=dict(l=20, r=20, t=60, b=20),
        showlegend=False,
    )

    return apply_plotly_theme(fig)
