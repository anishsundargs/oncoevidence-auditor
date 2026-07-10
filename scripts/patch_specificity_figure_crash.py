from pathlib import Path

p = Path("app.py")
text = p.read_text()

old = '''specificity_indicator_fig = plot_specificity_delta_indicator(specificity_result)
if specificity_indicator_fig is not None:
    st.plotly_chart(specificity_indicator_fig, use_container_width=True)
'''

new = '''_figure_specificity_result = locals().get("specificity_result")

if _figure_specificity_result is None:
    try:
        _figure_specificity_result = calculate_specificity_index(depmap_result, common_result)
    except Exception:
        _figure_specificity_result = None

specificity_indicator_fig = plot_specificity_delta_indicator(_figure_specificity_result)
if specificity_indicator_fig is not None:
    st.plotly_chart(specificity_indicator_fig, use_container_width=True)
'''

if old not in text:
    raise SystemExit("Could not find specificity figure block in app.py")

p.write_text(text.replace(old, new))
print("Patched specificity figure crash.")