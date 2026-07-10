"""
Shared UI styling for OncoEvidence Auditor.
"""

import streamlit as st


def render_theme_selector():
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


def _set_plotly_template(mode):
    """Set Plotly's default template so charts match the selected theme."""
    try:
        import plotly.io as pio

        pio.templates.default = "plotly_dark" if mode == "Dark" else "plotly_white"
    except Exception:
        pass


def apply_global_style(mode=None):
    """Apply readable global Streamlit styling."""
    mode = mode or st.session_state.get("oea_display_mode", "Light")
    _set_plotly_template(mode)

    if mode == "Dark":
        colors = {
            "page_bg": "#08111F",
            "page_bg_2": "#0E1728",
            "sidebar": "#111827",
            "card": "#142033",
            "card_2": "#172A45",
            "input": "#1E293B",
            "input_hover": "#26364F",
            "input_text": "#F8FAFC",
            "ink": "#F8FAFC",
            "muted": "#CBD5E1",
            "subtle": "#94A3B8",
            "blue": "#60A5FA",
            "cyan": "#22D3EE",
            "green": "#34D399",
            "purple": "#A78BFA",
            "orange": "#FBBF24",
            "red": "#F87171",
            "blue_soft": "rgba(96, 165, 250, 0.18)",
            "cyan_soft": "rgba(34, 211, 238, 0.14)",
            "green_soft": "rgba(52, 211, 153, 0.14)",
            "purple_soft": "rgba(167, 139, 250, 0.16)",
            "border": "#475569",
            "border_soft": "#334155",
            "shadow": "rgba(0, 0, 0, 0.34)",
            "warning_bg": "#2A2111",
            "warning_border": "#B45309",
            "warning_ink": "#FDE68A",
            "table_bg": "#F8FAFC",
            "table_text": "#111827",
        }
    else:
        colors = {
            "page_bg": "#F8FAFC",
            "page_bg_2": "#EEF4FF",
            "sidebar": "#FFFFFF",
            "card": "#FFFFFF",
            "card_2": "#F8FAFC",
            "input": "#FFFFFF",
            "input_hover": "#F8FAFC",
            "input_text": "#0F172A",
            "ink": "#0F172A",
            "muted": "#475569",
            "subtle": "#64748B",
            "blue": "#2563EB",
            "cyan": "#0891B2",
            "green": "#059669",
            "purple": "#7C3AED",
            "orange": "#D97706",
            "red": "#DC2626",
            "blue_soft": "#EFF6FF",
            "cyan_soft": "#ECFEFF",
            "green_soft": "#ECFDF5",
            "purple_soft": "#F5F3FF",
            "border": "#CBD5E1",
            "border_soft": "#E2E8F0",
            "shadow": "rgba(15, 23, 42, 0.08)",
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
                radial-gradient(circle at 12% 8%, {colors["blue_soft"]}, transparent 28rem),
                radial-gradient(circle at 92% 18%, {colors["purple_soft"]}, transparent 24rem),
                radial-gradient(circle at 65% 92%, {colors["cyan_soft"]}, transparent 28rem),
                linear-gradient(180deg, {colors["page_bg"]} 0%, {colors["page_bg_2"]} 100%);
            color: {colors["ink"]};
        }}

        .block-container {{
            padding-top: 1.7rem;
            padding-bottom: 4rem;
            max-width: 1240px;
        }}

        html, body, [class*="css"] {{
            font-size: 16px;
        }}

        h1, h2, h3, h4, h5, h6 {{
            color: {colors["ink"]} !important;
            letter-spacing: -0.025em;
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
            background:
                linear-gradient(180deg, {colors["sidebar"]} 0%, {colors["page_bg"]} 100%);
            border-right: 1px solid {colors["border_soft"]};
        }}

        section[data-testid="stSidebar"] label,
        section[data-testid="stSidebar"] p,
        section[data-testid="stSidebar"] span,
        section[data-testid="stSidebar"] div {{
            color: {colors["ink"]} !important;
        }}

        section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {{
            color: {colors["muted"]} !important;
        }}

        /* Hard fix for selectbox/dropdown readability. */
        .stSelectbox div[data-baseweb="select"],
        div[data-baseweb="select"] {{
            background-color: {colors["input"]} !important;
            border-radius: 14px !important;
        }}

        .stSelectbox div[data-baseweb="select"] > div,
        div[data-baseweb="select"] > div {{
            background-color: {colors["input"]} !important;
            border: 1px solid {colors["border"]} !important;
            color: {colors["input_text"]} !important;
            border-radius: 14px !important;
            min-height: 46px !important;
        }}

        .stSelectbox div[data-baseweb="select"]:hover > div,
        div[data-baseweb="select"]:hover > div {{
            background-color: {colors["input_hover"]} !important;
            border-color: {colors["blue"]} !important;
        }}

        .stSelectbox div[data-baseweb="select"] span,
        .stSelectbox div[data-baseweb="select"] input,
        .stSelectbox div[data-baseweb="select"] svg,
        div[data-baseweb="select"] span,
        div[data-baseweb="select"] input,
        div[data-baseweb="select"] svg {{
            color: {colors["input_text"]} !important;
            fill: {colors["input_text"]} !important;
        }}

        div[data-baseweb="popover"],
        div[data-baseweb="menu"],
        ul[role="listbox"] {{
            background-color: {colors["input"]} !important;
            color: {colors["input_text"]} !important;
            border: 1px solid {colors["border"]} !important;
            border-radius: 14px !important;
        }}

        div[role="option"],
        li[role="option"] {{
            background-color: {colors["input"]} !important;
            color: {colors["input_text"]} !important;
        }}

        div[role="option"]:hover,
        li[role="option"]:hover {{
            background-color: {colors["input_hover"]} !important;
            color: {colors["input_text"]} !important;
        }}

        input, textarea {{
            background-color: {colors["input"]} !important;
            color: {colors["input_text"]} !important;
            border-color: {colors["border"]} !important;
            border-radius: 12px !important;
        }}

        /* Metric cards. */
        div[data-testid="stMetric"] {{
            background:
                linear-gradient(135deg, {colors["card"]}, {colors["card_2"]});
            border: 1px solid {colors["border_soft"]};
            border-radius: 20px;
            padding: 1rem 1.05rem;
            box-shadow: 0 12px 28px {colors["shadow"]};
            min-height: 112px;
            overflow: hidden;
            position: relative;
        }}

        div[data-testid="stMetric"]::before {{
            content: "";
            position: absolute;
            left: 0;
            top: 0;
            height: 5px;
            width: 100%;
            background: linear-gradient(90deg, {colors["blue"]}, {colors["cyan"]}, {colors["green"]});
        }}

        div[data-testid="stMetricLabel"] {{
            color: {colors["subtle"]} !important;
            font-weight: 750;
            font-size: 0.86rem !important;
            white-space: normal !important;
        }}

        div[data-testid="stMetricValue"] {{
            color: {colors["ink"]} !important;
            font-weight: 850;
            font-size: clamp(1.25rem, 2.25vw, 1.9rem) !important;
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
            background: linear-gradient(135deg, {colors["card"]}, {colors["card_2"]});
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
                radial-gradient(circle at 90% 10%, {colors["cyan_soft"]}, transparent 11rem),
                radial-gradient(circle at 72% 72%, {colors["purple_soft"]}, transparent 13rem),
                linear-gradient(135deg, {colors["blue_soft"]}, transparent),
                {colors["card"]};
            border: 1px solid {colors["border_soft"]};
            border-radius: 26px;
            padding: 1.45rem 1.65rem;
            margin-bottom: 1.15rem;
            box-shadow: 0 18px 42px {colors["shadow"]};
            overflow: hidden;
            position: relative;
        }}

        .oea-hero::after {{
            content: "◬  ⟡  ⬡  ⟐";
            position: absolute;
            right: 1.4rem;
            top: 1.2rem;
            color: {colors["blue"]};
            opacity: 0.45;
            font-size: 2.1rem;
            letter-spacing: 0.55rem;
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

        .oea-feature-grid {{
            display: grid;
            grid-template-columns: repeat(4, minmax(0, 1fr));
            gap: 0.8rem;
            margin: 1rem 0 1.25rem 0;
        }}

        .oea-feature {{
            background:
                linear-gradient(135deg, {colors["card"]}, {colors["card_2"]});
            border: 1px solid {colors["border_soft"]};
            border-radius: 18px;
            padding: 0.95rem 1rem;
            box-shadow: 0 10px 24px {colors["shadow"]};
            position: relative;
            overflow: hidden;
        }}

        .oea-feature::before {{
            content: "";
            position: absolute;
            width: 80px;
            height: 80px;
            border-radius: 999px;
            right: -32px;
            top: -32px;
            background: {colors["blue_soft"]};
        }}

        .oea-feature-icon {{
            font-size: 1.35rem;
            margin-bottom: 0.35rem;
        }}

        .oea-feature-title {{
            color: {colors["ink"]};
            font-weight: 850;
            margin-bottom: 0.15rem;
        }}

        .oea-feature-body {{
            color: {colors["muted"]};
            font-size: 0.9rem;
            line-height: 1.38;
        }}

        .oea-section-chip {{
            display: inline-block;
            background: {colors["green_soft"]};
            color: {colors["green"]};
            border: 1px solid {colors["border_soft"]};
            border-radius: 999px;
            padding: 0.22rem 0.58rem;
            font-size: 0.78rem;
            font-weight: 850;
            margin: 0.25rem 0 0.6rem 0;
        }}

        hr {{
            margin: 1.4rem 0;
            border-color: {colors["border_soft"]};
        }}

        code {{
            border-radius: 8px;
        }}


        /* Remove Streamlit's top white header/bar completely. */
        header,
        header[data-testid="stHeader"],
        div[data-testid="stHeader"],
        .stApp > header {{
            background: transparent !important;
            height: 0rem !important;
            min-height: 0rem !important;
            max-height: 0rem !important;
            visibility: hidden !important;
            display: none !important;
        }}

        div[data-testid="stToolbar"],
        div[data-testid="stDecoration"],
        div[data-testid="stStatusWidget"] {{
            display: none !important;
            visibility: hidden !important;
            height: 0rem !important;
        }}

        /* Fix dark-mode text cursor/caret in text inputs. */
        input,
        textarea,
        [contenteditable="true"] {{
            caret-color: {colors["ink"]} !important;
        }}

        div[data-baseweb="input"] input,
        div[data-baseweb="textarea"] textarea {{
            caret-color: {colors["ink"]} !important;
        }}

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
        td {{
            background-color: {colors["card"]} !important;
            color: {colors["ink"]} !important;
            border-color: {colors["border_soft"]} !important;
        }}

        div[data-testid="stTable"] th,
        table th {{
            background-color: {colors["card_2"]} !important;
            color: {colors["ink"]} !important;
            font-weight: 800 !important;
        }}

        div[data-testid="stTable"] td,
        table td {{
            color: {colors["ink"]} !important;
        }}

        /* Dataframe shell only. Do not style internal canvas/divs or the table can disappear. */
        div[data-testid="stDataFrame"] {{
            background-color: {colors["card"]} !important;
            border: 1px solid {colors["border_soft"]} !important;
            border-radius: 16px !important;
            padding: 0.35rem !important;
            overflow: hidden !important;
        }}

        /* Kill white iframe/embedded-chart shells. */
        iframe,
        iframe html,
        iframe body {{
            background-color: {colors["card"]} !important;
        }}

        div[data-testid="stPlotlyChart"],
        div[data-testid="stVegaLiteChart"],
        div[data-testid="stPyplot"] {{
            background-color: {colors["card"]} !important;
            border-radius: 18px !important;
        }}

        div[data-testid="stPlotlyChart"] > div,
        div[data-testid="stVegaLiteChart"] > div,
        div[data-testid="stPyplot"] > div {{
            background-color: {colors["card"]} !important;
            border-radius: 16px !important;
        }}


        @media (max-width: 900px) {{
            .oea-feature-grid {{
                grid-template-columns: repeat(2, minmax(0, 1fr));
            }}
        }}

        @media (max-width: 600px) {{
            .oea-feature-grid {{
                grid-template-columns: 1fr;
            }}

            .block-container {{
                padding-top: 1rem;
            }}

            .oea-hero {{
                padding: 1.1rem 1.2rem;
                border-radius: 18px;
            }}

            .oea-hero::after {{
                display: none;
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


def render_feature_strip():
    """Render a colorful evidence-layer feature strip."""
    st.markdown(
        """
        <div class="oea-feature-grid">
            <div class="oea-feature">
                <div class="oea-feature-icon">🧬</div>
                <div class="oea-feature-title">Dependency</div>
                <div class="oea-feature-body">DepMap signal, common-essential caution, and lineage specificity.</div>
            </div>
            <div class="oea-feature">
                <div class="oea-feature-icon">📊</div>
                <div class="oea-feature-title">Patient evidence</div>
                <div class="oea-feature-body">cBioPortal alteration, expression, and survival/prognosis layers.</div>
            </div>
            <div class="oea-feature">
                <div class="oea-feature-icon">⚖️</div>
                <div class="oea-feature-title">Contradictions</div>
                <div class="oea-feature-body">Flags evidence conflicts before claims become overstated.</div>
            </div>
            <div class="oea-feature">
                <div class="oea-feature-icon">🧪</div>
                <div class="oea-feature-title">Validation</div>
                <div class="oea-feature-body">Generates conservative claims and next-step validation guidance.</div>
            </div>
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
