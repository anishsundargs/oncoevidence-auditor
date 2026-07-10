from pathlib import Path


p = Path("src/ui_style.py")
text = p.read_text()

# 1. Add a Streamlit plotly_chart wrapper that forces figure theme/background.
helper = r'''

def _patch_streamlit_plotly(mode):
    """Patch st.plotly_chart so existing figures match the selected app theme."""
    if getattr(st, "_oea_plotly_patched", False):
        st._oea_plotly_mode = mode
        return

    original_plotly_chart = st.plotly_chart
    st._oea_original_plotly_chart = original_plotly_chart
    st._oea_plotly_mode = mode

    def themed_plotly_chart(figure_or_data, *args, **kwargs):
        active_mode = getattr(st, "_oea_plotly_mode", "Light")

        try:
            if active_mode == "Dark":
                figure_or_data.update_layout(
                    template="plotly_dark",
                    paper_bgcolor="#142033",
                    plot_bgcolor="#142033",
                    font=dict(color="#E5E7EB"),
                    title=dict(font=dict(color="#F8FAFC")),
                    legend=dict(
                        bgcolor="rgba(20, 32, 51, 0)",
                        font=dict(color="#E5E7EB"),
                    ),
                    xaxis=dict(
                        gridcolor="#334155",
                        zerolinecolor="#475569",
                        linecolor="#475569",
                        tickfont=dict(color="#CBD5E1"),
                        title_font=dict(color="#CBD5E1"),
                    ),
                    yaxis=dict(
                        gridcolor="#334155",
                        zerolinecolor="#475569",
                        linecolor="#475569",
                        tickfont=dict(color="#CBD5E1"),
                        title_font=dict(color="#CBD5E1"),
                    ),
                    margin=dict(l=50, r=30, t=60, b=50),
                )
            else:
                figure_or_data.update_layout(
                    template="plotly_white",
                    paper_bgcolor="#FFFFFF",
                    plot_bgcolor="#FFFFFF",
                    font=dict(color="#0F172A"),
                    title=dict(font=dict(color="#0F172A")),
                    legend=dict(
                        bgcolor="rgba(255, 255, 255, 0)",
                        font=dict(color="#0F172A"),
                    ),
                    xaxis=dict(
                        gridcolor="#E2E8F0",
                        zerolinecolor="#CBD5E1",
                        linecolor="#CBD5E1",
                        tickfont=dict(color="#64748B"),
                        title_font=dict(color="#64748B"),
                    ),
                    yaxis=dict(
                        gridcolor="#E2E8F0",
                        zerolinecolor="#CBD5E1",
                        linecolor="#CBD5E1",
                        tickfont=dict(color="#64748B"),
                        title_font=dict(color="#64748B"),
                    ),
                    margin=dict(l=50, r=30, t=60, b=50),
                )
        except Exception:
            pass

        return original_plotly_chart(figure_or_data, *args, **kwargs)

    st.plotly_chart = themed_plotly_chart
    st._oea_plotly_patched = True
'''

if "def _patch_streamlit_plotly(" not in text:
    marker = "\ndef apply_global_style(mode=None):"
    if marker not in text:
        raise SystemExit("Could not find apply_global_style marker.")
    text = text.replace(marker, helper + marker, 1)


# 2. Make sure apply_global_style calls the Plotly patch.
old_call = '''    _set_plotly_template(mode)

    if mode == "Dark":'''

new_call = '''    _set_plotly_template(mode)
    _patch_streamlit_plotly(mode)

    if mode == "Dark":'''

if "_patch_streamlit_plotly(mode)" not in text:
    if old_call not in text:
        raise SystemExit("Could not find _set_plotly_template call block.")
    text = text.replace(old_call, new_call, 1)


# 3. Add CSS to remove the top white Streamlit header and make iframes/charts blend better.
css_anchor = '''        .stApp {
            background:'''

header_css = '''        header[data-testid="stHeader"] {
            background: transparent !important;
            border-bottom: none !important;
        }

        div[data-testid="stToolbar"] {
            background: transparent !important;
        }

        div[data-testid="stDecoration"] {
            display: none !important;
        }

        iframe {
            background: transparent !important;
        }

'''

if "header[data-testid=\"stHeader\"]" not in text:
    if css_anchor not in text:
        raise SystemExit("Could not find CSS anchor.")
    text = text.replace(css_anchor, header_css + css_anchor, 1)


p.write_text(text)

print("Patched Plotly dark backgrounds and removed Streamlit top white header.")