import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

filepath = r"F:\porj_AI_NetWork_Project\AI_Network_Architect\AI_NetWork_Project\streamlit_app.py"

with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

# Count before
print(f"Before: '原理深度追问' count = {content.count('原理深度追问')}")

# Replace ALL references to "🔬 原理深度追问" menu name in elif conditions
content = content.replace('elif menu == "🔬 原理深度追问"', 'elif menu == "🔬 实验故障诊断"')

# Replace ALL comment headers
content = content.replace('模块三：原理深度追问', '模块三：实验故障诊断')

# Replace any remaining old description text with new
content = content.replace(
    'st.markdown("不写代码，只聊原理。用苏格拉底问答法检验你对单片机原理的理解深度。")',
    'st.markdown("实验遇到 Bug？别急着找答案。描述你的现象和排查过程，我用苏格拉底提问引导你找到根源。")'
)

# Replace old concept input
old_input = 'concept = st.text_input("输入一个让你困惑的概念", placeholder="例如：定时器中断标志位为什么要软件清除？")'
new_input = 'concept = st.text_input("描述你遇到的实验问题", placeholder="例如：LED灯不亮、串口收不到数据、定时器不工作、按键无响应...")'
content = content.replace(old_input, new_input)

old_btn = 'if st.button("开始追问")'
new_btn = 'if st.button("开始诊断")'
content = content.replace(old_btn, new_btn)

old_error = 'st.error("请输入概念名称")'
new_error = 'st.error("请输入实验问题描述")'
content = content.replace(old_error, new_error)

old_default = """                👋 **你好！我是你的单片机原理导师。**

                请在上方输入你想要深入理解的单片机概念（如 GPIO模式、定时器原理、中断响应流程等），
                我会用苏格拉底式教学法带你从原理层面攻克它！🚀"""

new_default = """                👋 **你好！我是你的单片机实验故障诊断导师。**

                请在上方输入你在单片机实验中遇到的具体问题（如 LED 不亮、串口乱码、电机不转等），
                我会用苏格拉底式提问引导你一步步排查，帮你自己找到问题的根源！🔍"""

content = content.replace(old_default, new_default)

# Also fix the sidebar history section"s description
old_sidebar_desc = 'st.markdown("不写代码，只聊原理。用苏格拉底问答法检验你对单片机原理的理解深度。")'
# Already replaced above

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)

print(f"After: '原理深度追问' count = {content.count('原理深度追问')}")
print("All remaining references cleaned up!")

# Check what"s left
if content.count('原理深度追问') > 0:
    for i, line in enumerate(content.split('\n')):
        if '原理深度追问' in line:
            print(f"  LINE {i+1}: {line.strip()[:80]}")
