with open(r'F:\porj_AI_NetWork_Project\AI_Network_Architect\AI_NetWork_Project\streamlit_app.py', 'r', encoding='utf-8') as f:
    content = f.read()

old = '# ==================== 模块三：原理深度追问 (新增) ===================='
new = '# ==================== 模块三：实验故障诊断 (新增) ===================='

idx = content.find(old)
print(f'Found at offset: {idx}')
