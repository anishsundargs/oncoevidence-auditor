from pathlib import Path


# 1. Add a dedicated Plotly theme helper.
theme_path = Path("src/plotly_theme.py")
theme_path.write_text(
    r'''"""
Plotly theme helpers for OncoEvidence Auditor.

These helpers force figures to match the Streamlit light/dark toggle.
"""

from __future__ import annotations


def _get_mode() -> str:
    try:
        import streamlit as st

        return st.session_state.get("oea_display_mode", "Light")
    except Exception:
        return "Light"


def apply_plotly_theme(fig):
    """Apply current app theme directly to a Plotly figure."""
    mode = _get_mode()

    if mode == "Dark":
        paper = "#142033"
        plot = "#142033"
        card = "#142033"
        grid = "#334155"
        axis = "#CBD5E1"
        ink = "#F8FAFC"
        muted = "#CBD5E1"
        blue = "#60A5FA"
        green = "#34D399"
        orange = "#FBBF24"

        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor=paper,
            plot_bgcolor=plot,
            font=dict(color=muted),
            title=dict(font=dict(color=ink)),
            legend=dict(
                bgcolor="rgba(20, 32, 51, 0)",
                font=dict(color=muted),
            ),
            margin=dict(l=55, r=35, t=65, b=55),
        )

        # Update every x/y axis, including xaxis2/yaxis2 etc.
        for axis_name in list(fig.layout):
            if axis_name.startswith("xaxis") or axis_name.startswith("yaxis"):
                try:
                    fig.layout[axis_name].update(
                        gridcolor=grid,
                        zerolinecolor="#475569",
                        linecolor="#475569",
                        tickfont=dict(color=axis),
                        title_font=dict(color=axis),
                    )
                except Exception:
                    pass

        # Indicator/gauge traces need separate styling.
        for trace in fig.data:
            try:
                if trace.type == "indicator":
                    trace.update(
                        title=dict(font=dict(color=ink)),
                        number=dict(font=dict(color=ink)),
                        gauge=dict(
                            bgcolor=card,
                            bordercolor="#475569",
                            axis=dict(tickcolor=axis, tickfont=dict(color=axis)),
                            bar=dict(color=green),
                        ),
                    )
            except Exception:
                pass

            try:
                if trace.type == "bar" and not getattr(trace, "marker", None):
                    trace.update(marker=dict(color=blue))
            except Exception:
                pass

        return fig

    # Light mode
    fig.update_layout(
        template="plotly_white",
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        font=dict(color="#334155"),
        title=dict(font=dict(color="#0F172A")),
        legend=dict(
            bgcolor="rgba(255, 255, 255, 0)",
            font=dict(color="#334155"),
        ),
        margin=dict(l=55, r=35, t=65, b=55),
    )

    for axis_name in list(fig.layout):
        if axis_name.startswith("xaxis") or axis_name.startswith("yaxis"):
            try:
                fig.layout[axis_name].update(
                    gridcolor="#E2E8F0",
                    zerolinecolor="#CBD5E1",
                    linecolor="#CBD5E1",
                    tickfont=dict(color="#64748B"),
                    title_font=dict(color="#64748B"),
                )
            except Exception:
                pass

    for trace in fig.data:
        try:
            if trace.type == "indicator":
                trace.update(
                    title=dict(font=dict(color="#0F172A")),
                    number=dict(font=dict(color="#0F172A")),
                    gauge=dict(
                        bgcolor="#FFFFFF",
                        bordercolor="#CBD5E1",
                        axis=dict(tickcolor="#64748B", tickfont=dict(color="#64748B")),
                        bar=dict(color="#059669"),
                    ),
                )
        except Exception:
            pass

    return fig
'''
)


# 2. Patch figure modules so every returned fig is themed directly.
targets = [
    Path("src/evidence_figures.py"),
    Path("src/survival_figures.py"),
]

for path in targets:
    if not path.exists():
        continue

    text = path.read_text()

    import_line = "from src.plotly_theme import apply_plotly_theme\n"

    if import_line not in text:
        lines = text.splitlines(keepends=True)
        insert_at = None

        for i, line in enumerate(lines):
            if line.startswith("import ") or line.startswith("from "):
                insert_at = i + 1

        if insert_at is None:
            insert_at = 0

        lines.insert(insert_at, import_line)
        text = "".join(lines)

    text = text.replace("return fig", "return apply_plotly_theme(fig)")

    path.write_text(text)


# 3. Make chart containers dark but not force the inside white.
ui_path = Path("src/ui_style.py")
ui = ui_path.read_text()

old = '''        div[data-testid="stPlotlyChart"] {
            background: {colors["card"]};
            border: 1px solid {colors["border_soft"]};
            border-radius: 18px;
            padding: 0.45rem;
            box-shadow: 0 10px 26px {colors["shadow"]};
            overflow: hidden;
        }'''

new = '''        div[data-testid="stPlotlyChart"] {
            background: {colors["card"]} !important;
            border: 1px solid {colors["border_soft"]};
            border-radius: 18px;
            padding: 0.45rem;
            box-shadow: 0 10px 26px {colors["shadow"]};
            overflow: hidden;
        }

        div[data-testid="stPlotlyChart"] > div {
            background: {colors["card"]} !important;
            border-radius: 14px;
        }

        div[data-testid="stPlotlyChart"] iframe {
            background: {colors["card"]} !important;
            border-radius: 14px;
        }'''

if old in ui:
    ui = ui.replace(old, new, 1)

ui_path.write_text(ui)

print("Forced Plotly figures to use direct light/dark backgrounds.")