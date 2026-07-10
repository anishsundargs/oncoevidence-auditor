from pathlib import Path


fig_path = Path("src/evidence_figures.py")
text = fig_path.read_text()

extra = '''

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

    return fig


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

    return fig


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

    return fig
'''

if "def plot_patient_alteration_bar(" not in text:
    fig_path.write_text(text.rstrip() + "\n" + extra.strip() + "\n")


app_path = Path("app.py")
app = app_path.read_text()

# Add imports into existing evidence_figures multiline import.
if "plot_patient_alteration_bar" not in app:
    old = '''    plot_specificity_delta_indicator,
)
'''
    new = '''    plot_specificity_delta_indicator,
    plot_patient_alteration_bar,
    plot_patient_expression_bar,
    plot_expression_summary_bar,
)
'''
    if old not in app:
        raise SystemExit("Could not find evidence_figures import block.")
    app = app.replace(old, new, 1)


# Insert alteration figure after alteration-note interpretation block.
alteration_anchor = '''Patient-tumor alteration support is weak by mutation/high-level amplification/deep-deletion criteria. Do not frame this gene as genomically altered in this cancer without another evidence layer.")
'''

# The app may not have that exact warning string as a standalone anchor in all versions, so use the next stable anchor:
stable_alteration_anchor = '''st.subheader("cBioPortal Patient-Tumor Expression Evidence")
'''

alteration_insert = '''
st.markdown("### Patient alteration visualization")

alteration_fig = plot_patient_alteration_bar(cbio_result if "cbio_result" in locals() else {})
if alteration_fig is not None:
    st.plotly_chart(alteration_fig, use_container_width=True)
else:
    st.info("Patient alteration figure unavailable for this run.")

st.divider()

st.subheader("cBioPortal Patient-Tumor Expression Evidence")
'''

if "Patient alteration visualization" not in app:
    if stable_alteration_anchor not in app:
        raise SystemExit("Could not find expression section anchor.")
    app = app.replace(stable_alteration_anchor, alteration_insert, 1)


# Insert expression figures before Auditor Verdict.
expression_anchor = '''st.subheader("Auditor Verdict")
'''

expression_insert = '''
st.markdown("### Patient expression visualization")

expr_fig_col1, expr_fig_col2 = st.columns(2)

with expr_fig_col1:
    expression_bar_fig = plot_patient_expression_bar(expr_result if "expr_result" in locals() else {})
    if expression_bar_fig is not None:
        st.plotly_chart(expression_bar_fig, use_container_width=True)

with expr_fig_col2:
    expression_summary_fig = plot_expression_summary_bar(expr_result if "expr_result" in locals() else {})
    if expression_summary_fig is not None:
        st.plotly_chart(expression_summary_fig, use_container_width=True)

if not (expr_result if "expr_result" in locals() else {}).get("available"):
    st.info("Patient expression figures unavailable for this run.")

st.divider()

st.subheader("Auditor Verdict")
'''

if "Patient expression visualization" not in app:
    if expression_anchor not in app:
        raise SystemExit("Could not find Auditor Verdict anchor.")
    app = app.replace(expression_anchor, expression_insert, 1)


app_path.write_text(app)

print("Added patient alteration/expression visualizations.")