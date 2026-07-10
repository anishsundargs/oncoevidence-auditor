from pathlib import Path


ui_path = Path("src/ui_style.py")

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


def _set_plotly_template(mode):
    """Set Plotly's default template so charts match the selected theme."""
    try:
        import plotly.io as pio

        if mode == "Dark":
            pio.templates.default = "plotly_dark"
        else:
            pio.templates.default = "plotly_white"
    except Exception:
        pass


def apply_global_style(mode=None):
    """Apply readable global Streamlit styling."""
    mode = mode or st.session_state.get("oea_display_mode", "Light")
    _set_plotly_template(mode)

    if mode == "Dark":
        colors = {
            "page_bg": "#0B1120",
            "page_bg_2": "#111827",
            "sidebar": "#111827",
            "card": "#182235",
            "card_soft": "#1E293B",
            "input": "#F8FAFC",
            "input_text": "#111827",
            "ink": "#F8FAFC",
            "muted": "#CBD5E1",
            "subtle": "#94A3B8",
            "blue": "#93C5FD",
            "blue_strong": "#60A5FA",
            "blue_soft": "rgba(96, 165, 250, 0.16)",
            "border": "#475569",
            "border_soft": "#334155",
            "shadow": "rgba(0, 0, 0, 0.28)",
            "warning_bg": "#2A2111",
            "warning_border": "#B45309",
            "warning_ink": "#FDE68A",
            "table_bg": "#F8FAFC",
            "table_text": "#111827",
        }
    else:
        colors = {
            "page_bg": "#F8FAFC",
            "page_bg_2": "#F1F5F9",
            "sidebar": "#FFFFFF",
            "card": "#FFFFFF",
            "card_soft": "#F8FAFC",
            "input": "#FFFFFF",
            "input_text": "#0F172A",
            "ink": "#0F172A",
            "muted": "#475569",
            "subtle": "#64748B",
            "blue": "#2563EB",
            "blue_strong": "#1D4ED8",
            "blue_soft": "#EFF6FF",
            "border": "#CBD5E1",
            "border_soft": "#E2E8F0",
            "shadow": "rgba(15, 23, 42, 0.07)",
            "warning_bg": "#FFFBEB",
            "warning_border": "#F59E0B",
            "warning_ink": "#78350F",
            "table_bg": "#FFFFFF",
            "table_text": "#0F172A",
        }

    st.markdown(
        f"""
        <style>
        .stApp {{
            background:
                radial-gradient(circle at top left, {colors["blue_soft"]}, transparent 28rem),
                linear-gradient(180deg, {colors["page_bg"]} 0%, {colors["page_bg_2"]} 100%);
            color: {colors["ink"]};
        }}

        .block-container {{
            padding-top: 1.75rem;
            padding-bottom: 4rem;
            max-width: 1240px;
        }}

        html, body, [class*="css"] {{
            font-size: 16px;
        }}

        h1, h2, h3, h4, h5, h6 {{
            color: {colors["ink"]} !important;
            letter-spacing: -0.02em;
        }}

        h1 {{
            font-size: clamp(2rem, 3vw, 2.55rem) !important;
            font-weight: 850 !important;
            line-height: 1.12 !important;
        }}

        h2 {{
            font-size: clamp(1.45rem, 2.2vw, 1.9rem) !important;
            border-bottom: 1px solid {colors["border_soft"]};
            padding-bottom: 0.35rem;
            margin-top: 1.35rem;
        }}

        h3 {{
            font-size: clamp(1.15rem, 1.8vw, 1.45rem) !important;
        }}

        p, li {{
            color: {colors["muted"]};
            line-height: 1.55;
        }}

        section[data-testid="stSidebar"] {{
            background: {colors["sidebar"]};
            border-right: 1px solid {colors["border_soft"]};
        }}

        section[data-testid="stSidebar"] label,
        section[data-testid="stSidebar"] p,
        section[data-testid="stSidebar"] span,
        section[data-testid="stSidebar"] div {{
            color: {colors["ink"]} !important;
        }}

        /* Inputs/selectboxes: keep them readable in both themes. */
        div[data-baseweb="select"] > div {{
            background-color: {colors["input"]} !important;
            border-color: {colors["border"]} !important;
            color: {colors["input_text"]} !important;
            border-radius: 12px !important;
        }}

        div[data-baseweb="select"] span,
        div[data-baseweb="select"] input {{
            color: {colors["input_text"]} !important;
        }}

        input, textarea {{
            background-color: {colors["input"]} !important;
            color: {colors["input_text"]} !important;
            border-color: {colors["border"]} !important;
        }}

        /* Metric cards: prevent giant clipped text. */
        div[data-testid="stMetric"] {{
            background: {colors["card"]};
            border: 1px solid {colors["border_soft"]};
            border-radius: 18px;
            padding: 1rem 1.05rem;
            box-shadow: 0 10px 26px {colors["shadow"]};
            min-height: 112px;
            overflow: hidden;
        }}

        div[data-testid="stMetricLabel"] {{
            color: {colors["subtle"]} !important;
            font-weight: 750;
            font-size: 0.88rem !important;
            white-space: normal !important;
        }}

        div[data-testid="stMetricValue"] {{
            color: {colors["ink"]} !important;
            font-weight: 850;
            font-size: clamp(1.35rem, 2.5vw, 2.05rem) !important;
            line-height: 1.08 !important;
            white-space: normal !important;
            overflow-wrap: anywhere !important;
        }}

        div[data-testid="stMetricDelta"] {{
            color: {colors["subtle"]} !important;
        }}

        div[data-testid="stExpander"] {{
            border: 1px solid {colors["border_soft"]};
            border-radius: 16px;
            background: {colors["card"]};
            box-shadow: 0 8px 22px {colors["shadow"]};
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
        }}

        /* Dataframes remain light because Streamlit's dataframe renderer is more readable that way. */
        div[data-testid="stDataFrame"],
        div[data-testid="stTable"] {{
            background: {colors["table_bg"]};
            color: {colors["table_text"]};
            border: 1px solid {colors["border_soft"]};
            border-radius: 16px;
            padding: 0.35rem;
            box-shadow: 0 8px 22px {colors["shadow"]};
            overflow: hidden;
        }}

        div[data-testid="stPlotlyChart"] {{
            background: {colors["card"]};
            border: 1px solid {colors["border_soft"]};
            border-radius: 18px;
            padding: 0.45rem;
            box-shadow: 0 10px 26px {colors["shadow"]};
            overflow: hidden;
        }}

        .stTabs [data-baseweb="tab-list"] {{
            gap: 0.5rem;
            background: {colors["card"]};
            border: 1px solid {colors["border_soft"]};
            border-radius: 999px;
            padding: 0.35rem;
        }}

        .stTabs [data-baseweb="tab"] {{
            border-radius: 999px;
            padding: 0.35rem 0.85rem;
            color: {colors["subtle"]};
            font-weight: 750;
        }}

        .stTabs [aria-selected="true"] {{
            background: {colors["blue_soft"]};
            color: {colors["blue"]};
        }}

        .oea-hero {{
            background:
                linear-gradient(135deg, {colors["blue_soft"]}, transparent),
                {colors["card"]};
            border: 1px solid {colors["border_soft"]};
            border-radius: 24px;
            padding: 1.45rem 1.65rem;
            margin-bottom: 1.35rem;
            box-shadow: 0 18px 42px {colors["shadow"]};
            overflow: hidden;
        }}

        .oea-eyebrow {{
            display: inline-flex;
            align-items: center;
            color: {colors["blue"]};
            background: {colors["blue_soft"]};
            border: 1px solid {colors["border"]};
            border-radius: 999px;
            padding: 0.25rem 0.65rem;
            font-size: 0.75rem;
            font-weight: 850;
            letter-spacing: 0.02em;
            text-transform: uppercase;
            margin-bottom: 0.75rem;
        }}

        .oea-hero h1 {{
            margin: 0;
            color: {colors["ink"]} !important;
        }}

        .oea-hero p {{
            color: {colors["muted"]};
            font-size: 1rem;
            max-width: 860px;
            margin: 0.65rem 0 0 0;
        }}

        .oea-card {{
            background: {colors["card"]};
            border: 1px solid {colors["border_soft"]};
            border-radius: 18px;
            padding: 1.05rem 1.15rem;
            margin: 0.75rem 0;
            box-shadow: 0 10px 26px {colors["shadow"]};
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
            background: {colors["warning_bg"]};
            border: 1px solid {colors["warning_border"]};
            border-radius: 16px;
            padding: 0.9rem 1rem;
            color: {colors["warning_ink"]};
            font-size: 0.95rem;
        }}

        .oea-disclaimer strong {{
            color: {colors["warning_ink"]};
        }}

        hr {{
            margin: 1.4rem 0;
            border-color: {colors["border_soft"]};
        }}

        code {{
            border-radius: 8px;
        }}

        @media (max-width: 768px) {{
            .block-container {{
                padding-top: 1rem;
            }}

            .oea-hero {{
                padding: 1.1rem 1.2rem;
                border-radius: 18px;
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
            <strong>⚠️ Research/education only.</strong>
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

print("Fixed dark-mode readability styling.")