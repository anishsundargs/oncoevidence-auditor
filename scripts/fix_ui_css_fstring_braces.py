from pathlib import Path


p = Path("src/ui_style.py")
text = p.read_text()

start_marker = '        /* Remove Streamlit\\\'s top white header/bar completely. */'
end_marker = '        @media (max-width: 900px) {'

start = text.find(start_marker)
end = text.find(end_marker, start)

if start == -1 or end == -1:
    raise SystemExit("Could not find the broken CSS block in src/ui_style.py")

fixed_block = r'''        /* Remove Streamlit's top white header/bar completely. */
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

        /* Data editor/dataframe containers: remove bright white shell where possible. */
        div[data-testid="stDataFrame"],
        div[data-testid="stDataFrame"] div,
        div[data-testid="stDataFrame"] canvas {{
            background-color: {colors["card"]} !important;
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

'''

text = text[:start] + fixed_block + text[end:]
p.write_text(text)

print("Fixed CSS braces inside ui_style.py f-string.")