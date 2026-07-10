from pathlib import Path


p = Path("src/plotly_theme.py")
text = p.read_text()

anchor = '''def apply_plotly_theme(fig):
    """Apply current app theme directly to a Plotly figure."""
    mode = _get_mode()

    if mode == "Dark":
'''

insert = '''def apply_plotly_theme(fig):
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
'''

if anchor not in text:
    raise SystemExit("Could not find apply_plotly_theme anchor.")

text = text.replace(anchor, insert, 1)
p.write_text(text)

print("Patched undefined Plotly chart titles.")