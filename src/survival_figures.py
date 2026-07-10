from typing import Dict, List, Optional
import plotly.graph_objects as go
from src.plotly_theme import apply_plotly_theme


def _valid_records(records: List[Dict]) -> List[Dict]:
    clean = []
    for r in records or []:
        try:
            os_months = float(r.get('os_months'))
            deceased = bool(r.get('deceased'))
            group = r.get('group') or 'Unknown'
        except Exception:
            continue
        if os_months < 0:
            continue
        clean.append({'os_months': os_months, 'deceased': deceased, 'group': group})
    return clean


def _km_points(records: List[Dict]):
    records = sorted(records, key=lambda r: r['os_months'])
    event_times = sorted({r['os_months'] for r in records if r['deceased']})

    x = [0.0]
    y = [1.0]
    survival = 1.0

    for t in event_times:
        at_risk = sum(1 for r in records if r['os_months'] >= t)
        events = sum(1 for r in records if r['os_months'] == t and r['deceased'])

        if at_risk <= 0:
            continue

        survival *= 1.0 - (events / at_risk)
        x.append(t)
        y.append(survival)

    return x, y


def plot_km_survival(survival_result: Dict) -> Optional[go.Figure]:
    records = _valid_records(survival_result.get('survival_records', []))
    if not records:
        return None

    fig = go.Figure()

    preferred_order = ['High expression', 'Other expression']
    groups = [g for g in preferred_order if any(r['group'] == g for r in records)]
    groups += sorted({r['group'] for r in records if r['group'] not in groups})

    for group in groups:
        group_records = [r for r in records if r['group'] == group]
        if not group_records:
            continue

        x, y = _km_points(group_records)
        fig.add_trace(
            go.Scatter(
                x=x,
                y=y,
                mode='lines',
                line_shape='hv',
                name=f'{group} (n={len(group_records)})',
            )
        )

    fig.update_layout(
        title='Descriptive Kaplan-Meier-style survival curve',
        xaxis_title='Overall survival time (months)',
        yaxis_title='Estimated survival probability',
        yaxis=dict(range=[0, 1.05]),
        height=460,
        margin=dict(l=20, r=20, t=60, b=20),
        legend_title_text='Expression group',
    )

    return apply_plotly_theme(fig)


def plot_median_os_bar(survival_result: Dict) -> Optional[go.Figure]:
    high = survival_result.get('high_expression_median_os_months')
    other = survival_result.get('other_expression_median_os_months')

    if high is None and other is None:
        return None

    fig = go.Figure(
        data=[
            go.Bar(
                x=['High expression', 'Other expression'],
                y=[high or 0, other or 0],
            )
        ]
    )

    fig.update_layout(
        title='Median overall survival by expression group',
        xaxis_title='Expression group',
        yaxis_title='Median OS (months)',
        height=360,
        margin=dict(l=20, r=20, t=60, b=20),
    )

    return apply_plotly_theme(fig)


def plot_event_rate_bar(survival_result: Dict) -> Optional[go.Figure]:
    high = survival_result.get('high_expression_event_rate_percent')
    other = survival_result.get('other_expression_event_rate_percent')

    if high is None and other is None:
        return None

    fig = go.Figure(
        data=[
            go.Bar(
                x=['High expression', 'Other expression'],
                y=[high or 0, other or 0],
            )
        ]
    )

    fig.update_layout(
        title='Observed event rate by expression group',
        xaxis_title='Expression group',
        yaxis_title='Event rate (%)',
        yaxis=dict(range=[0, 100]),
        height=360,
        margin=dict(l=20, r=20, t=60, b=20),
    )

    return apply_plotly_theme(fig)
