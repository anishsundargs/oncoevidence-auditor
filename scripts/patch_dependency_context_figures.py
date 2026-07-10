from pathlib import Path


fig_path = Path("src/evidence_figures.py")
text = fig_path.read_text()

extra = '''

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

    return fig


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

    return fig


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

    return fig
'''

if "def plot_dependency_context_bar(" not in text:
    fig_path.write_text(text.rstrip() + "\n" + extra.strip() + "\n")
else:
    print("Dependency context figure helpers already present.")


app_path = Path("app.py")
app = app_path.read_text()

old_import = "from src.evidence_figures import plot_evidence_coverage_gauge, plot_evidence_layer_bar\n"

new_import = (
    "from src.evidence_figures import (\n"
    "    plot_evidence_coverage_gauge,\n"
    "    plot_evidence_layer_bar,\n"
    "    plot_dependency_context_bar,\n"
    "    plot_dependency_score_context_bar,\n"
    "    plot_specificity_delta_indicator,\n"
    ")\n"
)

if "plot_dependency_context_bar" not in app:
    if old_import not in app:
        raise SystemExit("Could not find evidence_figures import in app.py")
    app = app.replace(old_import, new_import)


anchor = '''else:
    st.info(common_result["common_essential_note"])
'''

insert = '''else:
    st.info(common_result["common_essential_note"])

st.markdown("### Dependency context visualization")

dep_fig_col1, dep_fig_col2 = st.columns(2)

with dep_fig_col1:
    dependency_context_fig = plot_dependency_context_bar(depmap_result, common_result)
    if dependency_context_fig is not None:
        st.plotly_chart(dependency_context_fig, use_container_width=True)

with dep_fig_col2:
    dependency_score_fig = plot_dependency_score_context_bar(depmap_result, common_result)
    if dependency_score_fig is not None:
        st.plotly_chart(dependency_score_fig, use_container_width=True)

specificity_indicator_fig = plot_specificity_delta_indicator(specificity_result)
if specificity_indicator_fig is not None:
    st.plotly_chart(specificity_indicator_fig, use_container_width=True)

st.caption(
    "Dependency context figures compare the selected cancer against the pan-cancer background. "
    "A strong selected-cancer dependency with similarly strong pan-cancer dependency may indicate broad essentiality rather than lineage specificity."
)
'''

if "Dependency context visualization" not in app:
    if anchor not in app:
        raise SystemExit("Could not find common-essential block anchor in app.py")
    app = app.replace(anchor, insert, 1)

app_path.write_text(app)

print("Added dependency context figures to single-gene app page.")