from typing import Dict, Optional
import plotly.graph_objects as go

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
    return fig


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

    return fig
