from pathlib import Path
import re


# 1. Fix the overly broad dataframe CSS that blanked the table.
ui_path = Path("src/ui_style.py")
ui = ui_path.read_text()

bad_blocks = [
    '''        /* Data editor/dataframe containers: remove bright white shell where possible. */
        div[data-testid="stDataFrame"],
        div[data-testid="stDataFrame"] div,
        div[data-testid="stDataFrame"] canvas {{
            background-color: {colors["card"]} !important;
        }}

''',
    '''        /* Data editor/dataframe containers: remove bright white shell where possible. */
        div[data-testid="stDataFrame"],
        div[data-testid="stDataFrame"] div,
        div[data-testid="stDataFrame"] canvas {
            background-color: {colors["card"]} !important;
        }

''',
]

replacement = '''        /* Dataframe shell only. Do not style internal canvas/divs or the table can disappear. */
        div[data-testid="stDataFrame"] {{
            background-color: {colors["card"]} !important;
            border: 1px solid {colors["border_soft"]} !important;
            border-radius: 16px !important;
            padding: 0.35rem !important;
            overflow: hidden !important;
        }}

'''

for bad in bad_blocks:
    ui = ui.replace(bad, replacement)

# Extra safety: remove any remaining rule that targets every dataframe div/canvas.
ui = re.sub(
    r'\s*div\[data-testid="stDataFrame"\] div,\s*\n\s*div\[data-testid="stDataFrame"\] canvas\s*\{\{?.*?\}\}?\s*',
    "\n",
    ui,
    flags=re.S,
)

ui_path.write_text(ui)


# 2. Replace score breakdown chart helper with a clean Plotly Graph Objects version.
app_path = Path("app.py")
app = app_path.read_text()

helper_pattern = re.compile(
    r"\ndef render_score_breakdown_chart\(breakdown\):.*?(?=\n\S)",
    flags=re.S,
)

new_helper = r'''

def render_score_breakdown_chart(breakdown):
    """Render score breakdown using a clean themed Plotly chart."""
    try:
        import plotly.graph_objects as go
        from src.plotly_theme import apply_plotly_theme

        if hasattr(breakdown, "to_dict"):
            try:
                breakdown = breakdown.to_dict()
            except Exception:
                pass

        if isinstance(breakdown, list):
            cleaned = []
            for item in breakdown:
                if isinstance(item, dict):
                    component = (
                        item.get("component")
                        or item.get("Component")
                        or item.get("Evidence component")
                        or item.get("index")
                    )
                    points = item.get("points") or item.get("Points") or item.get("score") or item.get("Score")
                    if component is not None and points is not None:
                        cleaned.append((str(component), float(points)))
        elif isinstance(breakdown, dict):
            cleaned = [(str(k), float(v)) for k, v in breakdown.items()]
        else:
            cleaned = []

        cleaned = [(k, v) for k, v in cleaned if k.lower() not in {"undefined", "none", "nan"}]

        if not cleaned:
            st.info("Score breakdown unavailable for this selected row.")
            return

        components = [k for k, _ in cleaned]
        points = [v for _, v in cleaned]

        fig = go.Figure(
            data=[
                go.Bar(
                    x=points,
                    y=components,
                    orientation="h",
                    marker=dict(color="#6366F1"),
                    hovertemplate="%{y}: %{x}<extra></extra>",
                )
            ]
        )

        fig.update_layout(
            title="Score breakdown",
            xaxis_title="Points",
            yaxis_title="Component",
            height=max(380, 52 * len(components)),
            showlegend=False,
        )

        st.plotly_chart(apply_plotly_theme(fig), use_container_width=True)
    except Exception as exc:
        st.warning(f"Could not render score breakdown chart: {exc}")
'''

if "def render_score_breakdown_chart(breakdown):" in app:
    app = helper_pattern.sub(new_helper, app, count=1)
else:
    # Insert helper after imports if missing.
    insert_pos = 0
    lines = app.splitlines(keepends=True)
    for i, line in enumerate(lines):
        if line.startswith("from ") or line.startswith("import "):
            insert_pos = i + 1
    lines.insert(insert_pos, new_helper + "\n")
    app = "".join(lines)


# 3. Make sure the chart call is using the helper, not a raw st.bar_chart/st.plotly_chart conversion.
app = app.replace("st.bar_chart(breakdown)", "render_score_breakdown_chart(breakdown)")
app = app.replace("st.bar_chart(score_breakdown)", "render_score_breakdown_chart(score_breakdown)")
app = app.replace("st.bar_chart(breakdown_df)", "render_score_breakdown_chart(breakdown)")

# If a prior regex made st.plotly_chart(apply_plotly_theme(fig),...) inside helper weird, the helper replacement above fixes it.

app_path.write_text(app)

print("Fixed blank evidence summary table CSS and cleaned score breakdown title.")