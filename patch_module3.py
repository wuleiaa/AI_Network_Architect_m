import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

filepath = r"F:\porj_AI_NetWork_Project\AI_Network_Architect\AI_NetWork_Project\streamlit_app.py"

with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

idx = content.find("# ==================== 模块三：原理深度追问 (新增) ====================")

# Find the end of this section - it"s the next # ==================== or EOF
rest = content[idx:]
end_idx = rest.find("# ====================", 5)  # skip the first one
if end_idx < 0:
    end_idx = len(rest)

old_section = rest[:end_idx]

new_section = """# ==================== 模块三：实验故障诊断 (新增) ====================
elif menu == \"\U0001f52c 实验故障诊断\":
    st.header(\"\U0001f52c 单片机实验故障诊断 | 苏格拉底式排错\")
    st.markdown(\"实验遇到 Bug？别急着找答案。描述你的现象和排查过程，我用苏格拉底提问引导你找到根源。\")

    concept = st.text_input(\"描述你遇到的实验问题\", placeholder=\"例如：LED灯不亮、串口收不到数据、定时器不工作、按键无响应...\")

    # 场景 A：点击按钮生成新对话
    if st.button(\"开始诊断\"):
        if concept:
            with st.chat_message(\"assistant\", avatar=\"\U0001f916\"):
                stream = st.session_state.ai_engine.socratic_quiz(concept)
                # 重点：存入记忆
                response_text = st.write_stream(stream)
                st.session_state.deep_inquiry_history = response_text

            # --- (新增) 自动存档逻辑 ---
            timestamp = datetime.now().strftime(\"%H:%M\")
            title = f\"[{timestamp}] {concept}\"

            # 存入列表
            new_record = {\"title\": title, \"content\": response_text}
            st.session_state.inquiry_chat_history_list.append(new_record)
#################################################################################
            if \"user_id\" in st.session_state:
                save_conversation(
                    user_id=st.session_state.user_id,
                    module=\"inquiry\",
                    title=title,
                    content=response_text
                )
###################################################################################
            # 限制只存 10 条 (超过就把最旧的删掉)
            if len(st.session_state.inquiry_chat_history_list) > 10:
                st.session_state.inquiry_chat_history_list.pop(0)

            # 重置查看状态为\"当前\"
            st.session_state.inquiry_active_history_index = None
        else:
            st.error(\"请输入实验问题描述\")

    # 场景 B: 用户点击了侧边栏的历史记录 (查看旧存档)
    elif st.session_state.inquiry_active_history_index is not None:
        # 根据索引取出历史数据
        record = st.session_state.inquiry_chat_history_list[st.session_state.inquiry_active_history_index]

        with st.chat_message(\"assistant\", avatar=\"\U0001f916\"):
            # 显示标题提示这是历史
            st.caption(f\"\U0001f4c2 正在查看历史存档：{record['title']}\")
            st.markdown(record[\"content\"])

    # 场景 B：没点按钮，但有历史记录（切换页面回来的情况）
    elif st.session_state.deep_inquiry_history:
        with st.chat_message(\"assistant\", avatar=\"\U0001f916\"):
            st.markdown(st.session_state.deep_inquiry_history)
    # 场景 C (新增)：默认初始化状态
    # 当没有点击按钮，且没有历史记录时，显示一个白色的空回答框（引导框）
    else:
        with st.chat_message(\"assistant\", avatar=\"\U0001f916\"):
            # 这个框是白色的（由之前的CSS决定），且高度会根据文字自动适应
            st.markdown(\"\"\"
                \U0001f44b **你好！我是你的单片机实验故障诊断导师。**

                请在上方输入你在单片机实验中遇到的具体问题（如 LED 不亮、串口乱码、电机不转等），
                我会用苏格拉底式提问引导你一步步排查，帮你自己找到问题的根源！\U0001f50d
                \"\"\")
"""

content = content[:idx] + new_section + content[idx+end_idx:]

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)

print(f"Replaced section from offset {idx} to {idx+end_idx}")
print("Done! Module 3 updated successfully.")
