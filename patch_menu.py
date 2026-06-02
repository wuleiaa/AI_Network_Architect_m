import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

filepath = r"F:\porj_AI_NetWork_Project\AI_Network_Architect\AI_NetWork_Project\streamlit_app.py"

with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

# Update navigation menu
content = content.replace('"🔬 原理深度追问"', '"🔬 实验故障诊断"')

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)

print("Navigation menu updated!")
print(f"Remaining '原理深度追问' occurrences: {content.count('原理深度追问')}")
