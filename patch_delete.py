import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

filepath = r"F:\porj_AI_NetWork_Project\AI_Network_Architect\AI_NetWork_Project\streamlit_app.py"

with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace('delete_menu == "🔬 原理深度追问"', 'delete_menu == "🔬 实验故障诊断"')

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)

print(f"Remaining '原理深度追问': {content.count('原理深度追问')}")
