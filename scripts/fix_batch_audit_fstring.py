from pathlib import Path


p = Path("pages/2_Batch_Audit.py")
lines = p.read_text().splitlines()

fixed = []
changed = False

for line in lines:
    if "No curated genes found for" in line and "st.session_state.get(" in line:
        indent = line[: len(line) - len(line.lstrip())]
        fixed.append(f'{indent}selected_cancer_for_message = st.session_state.get("batch_audit_cancer_type", "the selected cancer")')
        fixed.append(f'{indent}st.info(f"No curated genes found for {{selected_cancer_for_message}}.")')
        changed = True
    else:
        fixed.append(line)

if not changed:
    raise SystemExit("Could not find the broken Batch Audit f-string line.")

p.write_text("\n".join(fixed) + "\n")
print("Fixed Batch Audit f-string syntax error.")