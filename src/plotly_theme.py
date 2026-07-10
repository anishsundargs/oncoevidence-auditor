"""
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

    # Clean bad auto-generated Plotly/Vega titles.
    try:
        title_text = getattr(fig.layout.title, "text", None)
        title_clean = str(title_text).strip().lower()

        if title_text is None or title_clean in {"", "none", "nan", "undefined"}:
            x_title = str(getattr(getattr(fig.layout, "xaxis", None), "title", "")).lower()
            y_title = str(getattr(getattr(fig.layout, "yaxis", None), "title", "")).lower()

            # Score breakdown charts use Points vs Component.
            if "points" in x_title and "component" in y_title:
                fig.update_layout(title_text="Score breakdown")
            else:
                fig.update_layout(title_text="")
    except Exception:
        pass

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
