from pathlib import Path


ROOT = Path(".")
streamlit_dir = ROOT / ".streamlit"
streamlit_dir.mkdir(exist_ok=True)

# 1. Add Streamlit theme config.
config_path = streamlit_dir / "config.toml"
config_path.write_text(
    """[theme]
base = "light"
primaryColor = "#2563EB"
backgroundColor = "#F8FAFC"
secondaryBackgroundColor = "#FFFFFF"
textColor = "#0F172A"
font = "sans serif"

[server]
headless = true
"""
)


# 2. Add shared UI style module.
ui_path = ROOT / "src" / "ui_style.py"
ui_path.write_text(
    r'''"""
Shared UI styling for OncoEvidence Auditor.
"""

import streamlit as st


def apply_global_style():
    """Apply global Streamlit styling."""
    st.markdown(
        """
        <style>
        :root {
            --oea-bg: #F8FAFC;
            --oea-card: #FFFFFF;
            --oea-ink: #0F172A;
            --oea-muted: #64748B;
            --oea-blue: #2563EB;
            --oea-blue-soft: #EFF6FF;
            --oea-border: #E2E8F0;
            --oea-green-soft: #ECFDF5;
            --oea-yellow-soft: #FFFBEB;
            --oea-red-soft: #FEF2F2;
        }

        .stApp {
            background:
                radial-gradient(circle at top left, rgba(37, 99, 235, 0.08), transparent 28rem),
                linear-gradient(180deg, #F8FAFC 0%, #F1F5F9 100%);
        }

        .block-container {
            padding-top: 2rem;
            padding-bottom: 4rem;
            max-width: 1320px;
        }

        h1, h2, h3 {
            letter-spacing: -0.025em;
            color: #0F172A;
        }

        h1 {
            font-weight: 800;
            font-size: 2.25rem;
        }

        h2 {
            border-bottom: 1px solid #E2E8F0;
            padding-bottom: 0.35rem;
            margin-top: 1.5rem;
        }

        h3 {
            margin-top: 1.15rem;
        }

        p, li, span, div {
            line-height: 1.55;
        }

        section[data-testid="stSidebar"] {
            background: #FFFFFF;
            border-right: 1px solid #E2E8F0;
        }

        section[data-testid="stSidebar"] h1,
        section[data-testid="stSidebar"] h2,
        section[data-testid="stSidebar"] h3 {
            color: #0F172A;
        }

        div[data-testid="stMetric"] {
            background: rgba(255, 255, 255, 0.92);
            border: 1px solid #E2E8F0;
            border-radius: 18px;
            padding: 1rem 1.1rem;
            box-shadow: 0 10px 30px rgba(15, 23, 42, 0.05);
        }

        div[data-testid="stMetricLabel"] {
            color: #64748B;
            font-weight: 650;
        }

        div[data-testid="stMetricValue"] {
            color: #0F172A;
            font-weight: 800;
        }

        div[data-testid="stExpander"] {
            border: 1px solid #E2E8F0;
            border-radius: 16px;
            background: #FFFFFF;
            box-shadow: 0 8px 24px rgba(15, 23, 42, 0.04);
            overflow: hidden;
        }

        div[data-testid="stAlert"] {
            border-radius: 16px;
            border: 1px solid #E2E8F0;
        }

        .stButton > button,
        .stDownloadButton > button {
            border-radius: 999px;
            border: 1px solid #CBD5E1;
            background: #FFFFFF;
            color: #0F172A;
            font-weight: 700;
            padding: 0.55rem 1rem;
            box-shadow: 0 6px 18px rgba(15, 23, 42, 0.06);
        }

        .stButton > button:hover,
        .stDownloadButton > button:hover {
            border-color: #2563EB;
            color: #2563EB;
            box-shadow: 0 8px 24px rgba(37, 99, 235, 0.14);
        }

        div[data-testid="stDataFrame"],
        div[data-testid="stTable"] {
            border: 1px solid #E2E8F0;
            border-radius: 16px;
            overflow: hidden;
            box-shadow: 0 8px 24px rgba(15, 23, 42, 0.04);
        }

        .stTabs [data-baseweb="tab-list"] {
            gap: 0.5rem;
            background: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 999px;
            padding: 0.35rem;
        }

        .stTabs [data-baseweb="tab"] {
            border-radius: 999px;
            padding: 0.35rem 0.85rem;
            color: #475569;
            font-weight: 700;
        }

        .stTabs [aria-selected="true"] {
            background: #EFF6FF;
            color: #2563EB;
        }

        div[data-testid="stPlotlyChart"] {
            background: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 18px;
            padding: 0.45rem;
            box-shadow: 0 10px 30px rgba(15, 23, 42, 0.04);
        }

        .oea-hero {
            background:
                linear-gradient(135deg, rgba(37, 99, 235, 0.12), rgba(14, 165, 233, 0.06)),
                #FFFFFF;
            border: 1px solid #DBEAFE;
            border-radius: 28px;
            padding: 1.6rem 1.8rem;
            margin-bottom: 1.4rem;
            box-shadow: 0 18px 45px rgba(15, 23, 42, 0.07);
        }

        .oea-eyebrow {
            display: inline-flex;
            align-items: center;
            gap: 0.35rem;
            color: #1D4ED8;
            background: #EFF6FF;
            border: 1px solid #BFDBFE;
            border-radius: 999px;
            padding: 0.25rem 0.65rem;
            font-size: 0.78rem;
            font-weight: 800;
            letter-spacing: 0.02em;
            text-transform: uppercase;
            margin-bottom: 0.75rem;
        }

        .oea-hero h1 {
            margin: 0;
            font-size: 2.35rem;
            line-height: 1.1;
        }

        .oea-hero p {
            color: #475569;
            font-size: 1.02rem;
            max-width: 860px;
            margin: 0.7rem 0 0 0;
        }

        .oea-card {
            background: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 20px;
            padding: 1.15rem 1.25rem;
            margin: 0.75rem 0;
            box-shadow: 0 10px 30px rgba(15, 23, 42, 0.045);
        }

        .oea-card-title {
            font-weight: 800;
            color: #0F172A;
            margin-bottom: 0.25rem;
        }

        .oea-card-body {
            color: #475569;
            margin: 0;
        }

        .oea-badge {
            display: inline-block;
            border-radius: 999px;
            padding: 0.22rem 0.58rem;
            font-size: 0.78rem;
            font-weight: 800;
            background: #EFF6FF;
            color: #1D4ED8;
            border: 1px solid #BFDBFE;
        }

        .oea-warning-card {
            background: #FFFBEB;
            border: 1px solid #FDE68A;
            border-radius: 18px;
            padding: 1rem 1.15rem;
            color: #78350F;
            margin: 0.8rem 0;
        }

        .oea-disclaimer {
            background: #F8FAFC;
            border: 1px dashed #CBD5E1;
            border-radius: 16px;
            padding: 0.9rem 1rem;
            color: #475569;
            font-size: 0.93rem;
        }

        hr {
            margin: 1.5rem 0;
            border-color: #E2E8F0;
        }

        code {
            border-radius: 8px;
        }

        @media (max-width: 768px) {
            .block-container {
                padding-top: 1rem;
            }

            .oea-hero {
                padding: 1.15rem 1.2rem;
                border-radius: 20px;
            }

            .oea-hero h1 {
                font-size: 1.8rem;
            }
        }
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


# 3. Patch app.py with style import and hero.
app_path = ROOT / "app.py"
app = app_path.read_text()

if "from src.ui_style import" not in app:
    lines = app.splitlines(keepends=True)
    insert_at = None
    for i, line in enumerate(lines):
        if line.startswith("from src.") or line.startswith("import src."):
            insert_at = i + 1
    if insert_at is None:
        insert_at = 0
    lines.insert(insert_at, "from src.ui_style import apply_global_style, render_hero, render_disclaimer\n")
    app = "".join(lines)

if "apply_global_style()" not in app:
    # Put style after page config if possible, otherwise near top.
    if "st.set_page_config" in app:
        marker_end = app.find("\n", app.find("st.set_page_config"))
        # Handle multiline page config by inserting after the first later line containing ")"
        start = app.find("st.set_page_config")
        close = app.find("\n)", start)
        if close != -1:
            insert_pos = close + 2
            app = app[:insert_pos] + "\napply_global_style()\n" + app[insert_pos:]
        else:
            app = app[:marker_end] + "\napply_global_style()\n" + app[marker_end:]
    else:
        app = app.replace("import streamlit as st\n", "import streamlit as st\n\napply_global_style()\n", 1)

# Replace title/subtitle/disclaimer if present.
if "render_hero(" not in app:
    app = app.replace(
        'st.title("OncoEvidence Auditor")',
        'render_hero()',
        1,
    )
    app = app.replace(
        'st.markdown("Contradiction-aware cancer gene hypothesis triage using public-data evidence layers.")',
        '',
        1,
    )
    app = app.replace(
        'st.warning("Research/education only. This tool is not a diagnostic, prognostic, or treatment recommendation system.")',
        'render_disclaimer()',
        1,
    )

app_path.write_text(app)


# 4. Patch Streamlit pages with global style only.
pages_dir = ROOT / "pages"
for page in sorted(pages_dir.glob("*.py")):
    text = page.read_text()

    if "from src.ui_style import apply_global_style" not in text:
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

        lines.insert(insert_at, "from src.ui_style import apply_global_style\n")
        text = "".join(lines)

    if "apply_global_style()" not in text:
        if "st.set_page_config" in text:
            start = text.find("st.set_page_config")
            close = text.find("\n)", start)
            if close != -1:
                insert_pos = close + 2
                text = text[:insert_pos] + "\napply_global_style()\n" + text[insert_pos:]
            else:
                line_end = text.find("\n", start)
                text = text[:line_end] + "\napply_global_style()\n" + text[line_end:]
        else:
            text = text.replace("import streamlit as st\n", "import streamlit as st\n\napply_global_style()\n", 1)

    page.write_text(text)


print("Applied Streamlit theme and global UI polish.")