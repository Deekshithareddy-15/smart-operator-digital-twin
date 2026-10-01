import re

with open("app.py", "r", encoding="utf-8") as f:
    code = f.read()

start_idx = code.find("def render_operator_assistant_view(")
end_idx = code.find("def render_digital_twin_view(")
func_code = code[start_idx:end_idx]

# Pattern to find st.markdown triple quoted strings
pattern = r'(st\.markdown\(\s*f?""")(.*?)("""\s*,\s*unsafe_allow_html=True\s*\))'

def fix_match(m):
    prefix = m.group(1)
    body = m.group(2)
    suffix = m.group(3)
    
    # Strip leading 4+ spaces from each line in body
    lines = body.split("\n")
    fixed_lines = []
    for line in lines:
        if line.startswith("    "):
            fixed_lines.append(line.lstrip())
        else:
            fixed_lines.append(line)
    return prefix + "\n" + "\n".join(fixed_lines) + "\n" + suffix

new_func_code = re.sub(pattern, fix_match, func_code, flags=re.DOTALL)

code = code[:start_idx] + new_func_code + code[end_idx:]

with open("app.py", "w", encoding="utf-8") as f:
    f.write(code)

print("Cleaned all st.markdown multiline HTML strings in render_operator_assistant_view!")
