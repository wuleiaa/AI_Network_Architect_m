import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

filepath = r"F:\porj_AI_NetWork_Project\AI_Network_Architect\AI_NetWork_Project\streamlit_app.py"

with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

# Replace the header line that was missed
content = content.replace('st.header("🔬 单片机原理深度追问 | 苏格拉底式教学")', 'st.header("🔬 单片机实验故障诊断 | 苏格拉底式排错")')

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)

remaining = content.count("原理深度追问")
print(f"Fixed header! Remaining occurrences: {remaining}")
if remaining > 0:
    idx = content.find("原理深度追问")
    print(f"Remaining at offset {idx}: ...{content[idx-30:idx+50]}...")
