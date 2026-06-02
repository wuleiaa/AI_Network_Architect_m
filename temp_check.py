import re

filepath = r'F:\porj_AI_NetWork_Project\AI_Network_Architect\AI_NetWork_Project\streamlit_app.py'

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

old_start = '# ==================== 模块三：原理深度追问 (新增) ===================='
new_start = '# ==================== 模块三：实验故障诊断 (新增) ===================='

idx = content.find(old_start)
if idx < 0:
    print('ERROR: starting marker not found')
    exit(1)

# Find the next module boundary or similar marker after this section
rest = content[idx:]
# Search for the pattern that follows this section (next elif or end)
# The section ends with ')"""' or similar
end_marker = '                """)'
end_idx = rest.find(end_marker)
if end_idx < 0:
    print('ERROR: end marker not found')
    exit(1)

# The actual end is after the closing
end_idx += len(end_marker) + 1  # +1 for newline

print(f'Found section from offset {idx} to {idx+end_idx}')
print('---OLD---')
print(rest[:end_idx])
print('---END---')
