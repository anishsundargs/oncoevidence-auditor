from pathlib import Path

readme = Path("README.md")
text = readme.read_text()

live_url = "https://oncoevidence-auditor.streamlit.app"

section = f"""# OncoEvidence Auditor

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)]({live_url})

**Live demo:** {live_url}

> The hosted Streamlit demo may take 30–90 seconds to wake if it has been inactive.

"""

if text.startswith("# OncoEvidence Auditor"):
    lines = text.splitlines()
    # Remove the first title line only, then prepend polished header.
    text = "\n".join(lines[1:]).lstrip()
    text = section + text
elif "Live demo:" not in text:
    text = section + "\n" + text

# Add demo cases if missing.
demo_cases = """
## Recommended Demo Cases

Use these gene-cancer pairs to test the core app behavior:

| Gene | Cancer type | Why it is useful |
|---|---|---|
| OIP5 | GBM | Flagship contradiction case: strong dependency but broad-essential/patient-support risk |
| ERBB2 | Gastric cancer | Patient-supported biomarker/subgroup case |
| ERBB2 | Breast cancer | Therapeutic biomarker context in a different cancer setting |
| KRAS | Pancreatic cancer | Canonical oncogenic driver example |
| EGFR | Lung adenocarcinoma | Common precision-oncology target context |

"""

if "## Recommended Demo Cases" not in text:
    marker = "##"
    idx = text.find(marker, len(section))
    if idx != -1:
        text = text[:idx] + demo_cases + text[idx:]
    else:
        text += "\n" + demo_cases

readme.write_text(text)
print("Updated README with live demo link and recommended demo cases.")