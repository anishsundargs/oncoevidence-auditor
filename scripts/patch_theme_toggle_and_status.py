from pathlib import Path


ROOT = Path(".")

# 1. Replace UI style module with light/dark-aware styling.
ui_path = ROOT / "src" / "ui_style.py"

ui_path.write_text(
    r'''"""
Shared UI styling for OncoEvidence Auditor.
"""

import streamlit as st


def render_theme_selector():
    """Render a light/dark mode selector in the sidebar."""
    mode = st.sidebar.radio(
        "Display mode",
        ["Light", "Dark"],
        horizontal=True,
        key="oea_display_mode",
    )
    return mode


def apply_global_style(mode=None):
    """Apply global Streamlit styling."""
    mode = mode or st.session_state.get("oea_display_mode", "Light")

    if mode == "Dark":
        colors = {
            "bg": "#020617",
            "bg2": "#0F172A",
            "card": "#111827",
            "card2": "#1E293B",
            "ink": "#E5E7EB",
            "muted": "#94A3B8",
            "blue": "#60A5FA",
            "blue_soft": "rgba(37, 99, 235, 0.18)",
            "border": "#334155",
            "shadow": "rgba(0, 0, 0, 0.35)",
            "warning_bg": "#422006",
            "warning_border": "#92400E",
            "warning_ink": "#FDE68A",
            "disclaimer_bg": "#0B1120",
        }
    else:
        colors = {
            "bg": "#F8FAFC",
            "bg2": "#F1F5F9",
            "card": "#FFFFFF",
            "card2": "#FFFFFF",
            "ink": "#0F172A",
            "muted": "#64748B",
            "blue": "#2563EB",
            "blue_soft": "#EFF6FF",
            "border": "#E2E8F0",
            "shadow": "rgba(15, 23, 42, 0.06)",
            "warning_bg": "#FFFBEB",
            "warning_border": "#FDE68A",
            "warning_ink": "#78350F",
            "disclaimer_bg": "#F8FAFC",
        }

    st.markdown(
        f"""
        <style>
        .stApp {{
            background:
                radial-gradient(circle at top left, {colors["blue_soft"]}, transparent 30rem),
                linear-gradient(180deg, {colors["bg"]} 0%, {colors["bg2"]} 100%);
            color: {colors["ink"]};
        }}

        .block-container {{
            padding-top: 2rem;
            padding-bottom: 4rem;
            max-width: 1320px;
        }}

        h1, h2, h3, h4, h5, h6 {{
            color: {colors["ink"]};
            letter-spacing: -0.025em;
        }}

        h1 {{
            font-weight: 850;
            font-size: 2.3rem;
        }}

        h2 {{
            border-bottom: 1px solid {colors["border"]};
            padding-bottom: 0.35rem;
            margin-top: 1.5rem;
        }}

        p, li, span, div {{
            line-height: 1.55;
        }}

        section[data-testid="stSidebar"] {{
            background: {colors["card"]};
            border-right: 1px solid {colors["border"]};
        }}

        section[data-testid="stSidebar"] * {{
            color: {colors["ink"]};
        }}

        div[data-testid="stMetric"] {{
            background: {colors["card"]};
            border: 1px solid {colors["border"]};
            border-radius: 18px;
            padding: 1rem 1.1rem;
            box-shadow: 0 10px 30px {colors["shadow"]};
        }}

        div[data-testid="stMetricLabel"] {{
            color: {colors["muted"]};
            font-weight: 700;
        }}

        div[data-testid="stMetricValue"] {{
            color: {colors["ink"]};
            font-weight: 850;
        }}

        div[data-testid="stExpander"] {{
            border: 1px solid {colors["border"]};
            border-radius: 16px;
            background: {colors["card"]};
            box-shadow: 0 8px 24px {colors["shadow"]};
            overflow: hidden;
        }}

        div[data-testid="stAlert"] {{
            border-radius: 16px;
            border: 1px solid {colors["border"]};
        }}

        .stButton > button,
        .stDownloadButton > button {{
            border-radius: 999px;
            border: 1px solid {colors["border"]};
            background: {colors["card"]};
            color: {colors["ink"]};
            font-weight: 750;
            padding: 0.55rem 1rem;
            box-shadow: 0 6px 18px {colors["shadow"]};
        }}

        .stButton > button:hover,
        .stDownloadButton > button:hover {{
            border-color: {colors["blue"]};
            color: {colors["blue"]};
            box-shadow: 0 8px 24px {colors["shadow"]};
        }}

        div[data-testid="stDataFrame"],
        div[data-testid="stTable"],
        div[data-testid="stPlotlyChart"] {{
            background: {colors["card"]};
            border: 1px solid {colors["border"]};
            border-radius: 18px;
            padding: 0.45rem;
            box-shadow: 0 10px 30px {colors["shadow"]};
            overflow: hidden;
        }}

        .stTabs [data-baseweb="tab-list"] {{
            gap: 0.5rem;
            background: {colors["card"]};
            border: 1px solid {colors["border"]};
            border-radius: 999px;
            padding: 0.35rem;
        }}

        .stTabs [data-baseweb="tab"] {{
            border-radius: 999px;
            padding: 0.35rem 0.85rem;
            color: {colors["muted"]};
            font-weight: 750;
        }}

        .stTabs [aria-selected="true"] {{
            background: {colors["blue_soft"]};
            color: {colors["blue"]};
        }}

        input, textarea, select {{
            color: {colors["ink"]} !important;
        }}

        .oea-hero {{
            background:
                linear-gradient(135deg, {colors["blue_soft"]}, transparent),
                {colors["card"]};
            border: 1px solid {colors["border"]};
            border-radius: 28px;
            padding: 1.6rem 1.8rem;
            margin-bottom: 1.4rem;
            box-shadow: 0 18px 45px {colors["shadow"]};
        }}

        .oea-eyebrow {{
            display: inline-flex;
            align-items: center;
            gap: 0.35rem;
            color: {colors["blue"]};
            background: {colors["blue_soft"]};
            border: 1px solid {colors["border"]};
            border-radius: 999px;
            padding: 0.25rem 0.65rem;
            font-size: 0.78rem;
            font-weight: 850;
            letter-spacing: 0.02em;
            text-transform: uppercase;
            margin-bottom: 0.75rem;
        }}

        .oea-hero h1 {{
            margin: 0;
            color: {colors["ink"]};
            font-size: 2.35rem;
            line-height: 1.1;
        }}

        .oea-hero p {{
            color: {colors["muted"]};
            font-size: 1.02rem;
            max-width: 880px;
            margin: 0.7rem 0 0 0;
        }}

        .oea-card {{
            background: {colors["card"]};
            border: 1px solid {colors["border"]};
            border-radius: 20px;
            padding: 1.15rem 1.25rem;
            margin: 0.75rem 0;
            box-shadow: 0 10px 30px {colors["shadow"]};
        }}

        .oea-card-title {{
            font-weight: 850;
            color: {colors["ink"]};
            margin-bottom: 0.25rem;
        }}

        .oea-card-body {{
            color: {colors["muted"]};
            margin: 0;
        }}

        .oea-disclaimer {{
            background: {colors["disclaimer_bg"]};
            border: 1px dashed {colors["border"]};
            border-radius: 16px;
            padding: 0.9rem 1rem;
            color: {colors["muted"]};
            font-size: 0.93rem;
        }}

        .oea-warning-card {{
            background: {colors["warning_bg"]};
            border: 1px solid {colors["warning_border"]};
            border-radius: 18px;
            padding: 1rem 1.15rem;
            color: {colors["warning_ink"]};
            margin: 0.8rem 0;
        }}

        hr {{
            margin: 1.5rem 0;
            border-color: {colors["border"]};
        }}

        code {{
            border-radius: 8px;
        }}

        @media (max-width: 768px) {{
            .block-container {{
                padding-top: 1rem;
            }}

            .oea-hero {{
                padding: 1.15rem 1.2rem;
                border-radius: 20px;
            }}

            .oea-hero h1 {{
                font-size: 1.8rem;
            }}
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_hero(
    title="OncoEvidence Auditor",
    subtitle="Contradiction-aware cancer gene hypothesis triage using public-data evidence layers.",
    badge="Research-use computational oncology tool",
):
    """Render a polished page header."""
    st.markdown(
        f"""
        <div class="oea-hero">
            <div class="oea-eyebrow">{badge}</div>
            <h1>{title}</h1>
            <p>{subtitle}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_disclaimer():
    """Render a compact research-use disclaimer."""
    st.markdown(
        """
        <div class="oea-disclaimer">
            <strong>Research/education only.</strong>
            This tool is not a diagnostic, prognostic, or treatment recommendation system.
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_card(title, body):
    """Render a lightweight HTML card."""
    st.markdown(
        f"""
        <div class="oea-card">
            <div class="oea-card-title">{title}</div>
            <p class="oea-card-body">{body}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
'''
)


# 2. Patch app/pages imports and calls.
paths = [ROOT / "app.py"] + sorted((ROOT / "pages").glob("*.py"))

for path in paths:
    text = path.read_text()

    # Upgrade imports.
    text = text.replace(
        "from src.ui_style import apply_global_style, render_hero, render_disclaimer",
        "from src.ui_style import apply_global_style, render_hero, render_disclaimer, render_theme_selector",
    )
    text = text.replace(
        "from src.ui_style import apply_global_style\n",
        "from src.ui_style import apply_global_style, render_theme_selector\n",
    )

    if "from src.ui_style import" not in text:
        lines = text.splitlines(keepends=True)
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

        if path.name == "app.py":
            lines.insert(insert_at, "from src.ui_style import apply_global_style, render_hero, render_disclaimer, render_theme_selector\n")
        else:
            lines.insert(insert_at, "from src.ui_style import apply_global_style, render_theme_selector\n")
        text = "".join(lines)

    # Replace bare apply_global_style() with theme selector version.
    if "_theme_mode = render_theme_selector()" not in text:
        text = text.replace(
            "apply_global_style()",
            '_theme_mode = render_theme_selector()\napply_global_style(_theme_mode)',
            1,
        )

    # Remove/replace outdated MVP wording.
    replacements = {
        "MVP Status": "Score interpretation",
        "MVP status": "Score interpretation",
        "Main evidence card still uses curated mock values.": (
            "Static catalog score is a curated local prior; live evidence score and auditor verdict reflect current evidence layers."
        ),
        "Main evidence card still uses curated mock values": (
            "Static catalog score is a curated local prior; live evidence score and auditor verdict reflect current evidence layers"
        ),
        "curated mock values": "curated local prior values",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    path.write_text(text)


# 3. Keep Streamlit config clean and allow browser auto-open.
config_path = ROOT / ".streamlit" / "config.toml"
config_path.parent.mkdir(exist_ok=True)
config_path.write_text(
    """[theme]
base = "light"
primaryColor = "#2563EB"
backgroundColor = "#F8FAFC"
secondaryBackgroundColor = "#FFFFFF"
textColor = "#0F172A"
font = "sans serif"

[server]
headless = false
"""
)

print("Added light/dark mode selector and removed MVP status wording.")