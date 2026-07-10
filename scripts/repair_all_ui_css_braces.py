from pathlib import Path


p = Path("src/ui_style.py")
lines = p.read_text().splitlines(keepends=True)

fixed = []
in_style = False

for line in lines:
    stripped = line.strip()

    if "<style>" in line:
        in_style = True
        fixed.append(line)
        continue

    if "</style>" in line:
        in_style = False
        fixed.append(line)
        continue

    if in_style:
        # CSS opening block lines look like:
        # selector {
        # They must become:
        # selector {{
        if stripped.endswith("{") and not stripped.endswith("{{"):
            line = line[: line.rfind("{")] + "{{" + line[line.rfind("{") + 1 :]

        # CSS closing block lines look like:
        # }
        # They must become:
        # }}
        if stripped == "}":
            leading = line[: len(line) - len(line.lstrip())]
            newline = "\n" if line.endswith("\n") else ""
            line = leading + "}}" + newline

    fixed.append(line)

p.write_text("".join(fixed))

print("Escaped unescaped CSS braces inside src/ui_style.py style block.")