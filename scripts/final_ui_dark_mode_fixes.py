from pathlib import Path
import re


ui_path = Path("src/ui_style.py")
text = ui_path.read_text()

# 1. Replace render_theme_selector with query-param persistent version.
old_selector = re.search(
    r"def render_theme_selector\(\):.*?def _set_plotly_template",
    text,
    flags=re.S,
)

new_selector = r'''def render_theme_selector():
    """Render a light/dark mode selector in the sidebar and persist it across pages."""
    try:
        qp_theme = st.query_params.get("theme", None)
    except Exception:
        qp_theme = None

    if qp_theme in {"Light", "Dark"} and "oea_display_mode" not in st.session_state:
        st.session_state["oea_display_mode"] = qp_theme

    current = st.session_state.get("oea_display_mode", "Light")
    index = 1 if current == "Dark" else 0

    mode = st.sidebar.radio(
        "Display mode",
        ["Light", "Dark"],
        horizontal=True,
        index=index,
        key="oea_display_mode",
    )

    try:
        st.query_params["theme"] = mode
    except Exception:
        pass

    return mode


def _set_plotly_template'''

if old_selector:
    text = text[:old_selector.start()] + new_selector + text[old_selector.end():]
else:
    raise SystemExit("Could not find render_theme_selector block.")


# 2. Inject stronger CSS fixes inside the style block before @media.
css_marker = "        @media (max-width: 900px) {"

extra_css = r'''
        /* Remove Streamlit's top white header/bar completely. */
        header,
        header[data-testid="stHeader"],
        div[data-testid="stHeader"],
        .stApp > header {
            background: transparent !important;
            height: 0rem !important;
            min-height: 0rem !important;
            max-height: 0rem !important;
            visibility: hidden !important;
            display: none !important;
        }

        div[data-testid="stToolbar"],
        div[data-testid="stDecoration"],
        div[data-testid="stStatusWidget"] {
            display: none !important;
            visibility: hidden !important;
            height: 0rem !important;
        }

        /* Fix dark-mode text cursor/caret in text inputs. */
        input,
        textarea,
        [contenteditable="true"] {
            caret-color: {colors["ink"]} !important;
        }

        div[data-baseweb="input"] input,
        div[data-baseweb="textarea"] textarea {
            caret-color: {colors["ink"]} !important;
        }

        /* Make regular Streamlit tables match dark mode instead of staying white. */
        div[data-testid="stTable"] table,
        div[data-testid="stTable"] thead,
        div[data-testid="stTable"] tbody,
        div[data-testid="stTable"] tr,
        div[data-testid="stTable"] th,
        div[data-testid="stTable"] td,
        table,
        thead,
        tbody,
        tr,
        th,
        td {
            background-color: {colors["card"]} !important;
            color: {colors["ink"]} !important;
            border-color: {colors["border_soft"]} !important;
        }

        div[data-testid="stTable"] th,
        table th {
            background-color: {colors["card_2"]} !important;
            color: {colors["ink"]} !important;
            font-weight: 800 !important;
        }

        div[data-testid="stTable"] td,
        table td {
            color: {colors["ink"]} !important;
        }

        /* Data editor/dataframe containers: remove bright white shell where possible. */
        div[data-testid="stDataFrame"],
        div[data-testid="stDataFrame"] div,
        div[data-testid="stDataFrame"] canvas {
            background-color: {colors["card"]} !important;
        }

        /* Kill white iframe/embedded-chart shells. */
        iframe,
        iframe html,
        iframe body {
            background-color: {colors["card"]} !important;
        }

        div[data-testid="stPlotlyChart"],
        div[data-testid="stVegaLiteChart"],
        div[data-testid="stPyplot"] {
            background-color: {colors["card"]} !important;
            border-radius: 18px !important;
        }

        div[data-testid="stPlotlyChart"] > div,
        div[data-testid="stVegaLiteChart"] > div,
        div[data-testid="stPyplot"] > div {
            background-color: {colors["card"]} !important;
            border-radius: 16px !important;
        }

'''

if "Remove Streamlit's top white header/bar completely" not in text:
    if css_marker not in text:
        raise SystemExit("Could not find CSS media marker.")
    text = text.replace(css_marker, extra_css + "\n" + css_marker, 1)


ui_path.write_text(text)


# 3. Patch any direct Plotly charts in app/pages to use apply_plotly_theme.
paths = [Path("app.py")] + sorted(Path("pages").glob("*.py"))

for path in paths:
    src = path.read_text()

    if "st.plotly_chart" in src and "from src.plotly_theme import apply_plotly_theme" not in src:
        lines = src.splitlines(keepends=True)
        insert_at = None
        for i, line in enumerate(lines):
            if line.startswith("from src.") or line.startswith("import src."):
                insert_at = i + 1
        if insert_at is None:
            for i, line in enumerate(lines):
                if line.startswith("import ") or line.startswith("from "):
                    insert_at = i + 1
        if insert_at is None:
            insert_at = 0
        lines.insert(insert_at, "from src.plotly_theme import apply_plotly_theme\n")
        src = "".join(lines)

    # Common direct chart patterns.
    src = re.sub(
        r"st\.plotly_chart\((\w+),",
        r"st.plotly_chart(apply_plotly_theme(\1),",
        src,
    )

    path.write_text(src)


# 4. If the score breakdown is a matplotlib/st.bar_chart/altair artifact, convert common app.py score chart block if present.
app_path = Path("app.py")
app = app_path.read_text()

# Add a helper import for pandas is usually already there; do not force it.
if "def render_score_breakdown_chart(" not in app:
    helper = r'''

def render_score_breakdown_chart(breakdown):
    """Render score breakdown using themed Plotly instead of a white-background chart."""
    try:
        import plotly.express as px
        from src.plotly_theme import apply_plotly_theme

        items = [
            {"component": str(k), "points": float(v)}
            for k, v in breakdown.items()
        ]

        if not items:
            return

        fig = px.bar(
            items,
            x="points",
            y="component",
            orientation="h",
            title="Score breakdown",
            labels={"points": "Points", "component": "Component"},
        )
        fig.update_traces(marker_color="#60A5FA")
        st.plotly_chart(apply_plotly_theme(fig), use_container_width=True)
    except Exception:
        st.write(breakdown)
'''
    # Put helper after imports / page config region by adding near top after ui imports if possible.
    insert_anchor = "from src.ui_style"
    pos = app.find(insert_anchor)
    if pos != -1:
        line_end = app.find("\n", pos)
        app = app[:line_end + 1] + helper + app[line_end + 1:]


# Replace very common old chart calls if present.
app = app.replace("st.bar_chart(breakdown)", "render_score_breakdown_chart(breakdown)")
app = app.replace("st.bar_chart(score_breakdown)", "render_score_breakdown_chart(score_breakdown)")
app = app.replace("st.bar_chart(breakdown_df)", "render_score_breakdown_chart(breakdown)")

app_path.write_text(app)

print("Applied final dark-mode fixes: persistent theme, top bar removal, caret color, dark tables, themed direct charts.")