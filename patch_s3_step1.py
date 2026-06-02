import sys
sys.stdout.reconfigure(encoding="utf-8")

with open("F:/porj_AI_NetWork_Project/AI_Network_Architect/AI_NetWork_Project/streamlit_app.py", "r", encoding="utf-8") as f:
    content = f.read()

print("Original length:", len(content))

# === Modification 1: Add new session state variables ===
# After the S3 initialization block, add AI tutor session variables
old_init = """# --- 初始化 S3 靶场历史记录 ---
if "s3_chat_history_list" not in st.session_state:
    st.session_state.s3_chat_history_list = []  # S3 靶场历史记录列表
if "s3_active_history_index" not in st.session_state:
    st.session_state.s3_active_history_index = None  # S3 当前查看的历史索引"""

new_init = """# --- 初始化 S3 靶场历史记录 ---
if "s3_chat_history_list" not in st.session_state:
    st.session_state.s3_chat_history_list = []  # S3 靶场历史记录列表
if "s3_active_history_index" not in st.session_state:
    st.session_state.s3_active_history_index = None  # S3 当前查看的历史索引

# --- 初始化 S3 AI导师审阅状态 ---
if "s3_tutor_history" not in st.session_state:
    st.session_state.s3_tutor_history = []  # AI导师与学生的多轮对话历史 [{role, content}]
if "s3_tutor_feedback" not in st.session_state:
    st.session_state.s3_tutor_feedback = ""  # 最新的AI导师反馈
if "s3_tutor_round" not in st.session_state:
    st.session_state.s3_tutor_round = 0  # 迭代轮次计数
if "s3_show_final_answer" not in st.session_state:
    st.session_state.s3_show_final_answer = False  # 是否显示最终答案
if "s3_task_submitted" not in st.session_state:
    st.session_state.s3_task_submitted = False  # 学生是否已提交过
if "s3_is_correct" not in st.session_state:
    st.session_state.s3_is_correct = False  # 学生答案是否已完全正确"""

if old_init in content:
    content = content.replace(old_init, new_init)
    print("Mod 1: Session vars added, pos:", content.find(new_init))
else:
    print("ERROR: Mod 1 marker not found")
    sys.exit(1)

with open("F:/porj_AI_NetWork_Project/AI_Network_Architect/AI_NetWork_Project/streamlit_app.py", "w", encoding="utf-8") as f:
    f.write(content)

print("Mod 1 applied, new length:", len(content))
