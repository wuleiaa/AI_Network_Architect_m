# Proxy cleanup disabled for cloud deploy. Uncomment if behind corporate proxy.
# import os
# for proxy_var in ['HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy', 'OPENAI_PROXY']:
#     if proxy_var in os.environ:
#         del os.environ[proxy_var]
# ===============================================


from utils.db_helper import get_db_path, init_db  # 浠呮涓€澶勫鍏?
import streamlit as st
from utils.ai_engine import MCU_TutorAI
from datetime import datetime  # 瀵煎叆 datetime 绫?
# ====== 鏂板锛氭暟鎹簱鍒濆鍖?======
import sqlite3
import hashlib
import os
# 鍦ㄦ枃浠舵渶椤堕儴娣诲姞闃叉姢锛堥槻姝㈠懡鍚嶅啿绐侊級


# 初始化数据库（由 db_helper.init_db 统一处理）
init_db()



# ====== 鏂板锛氱敤鎴疯璇佸嚱鏁?======
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def register_user(username, password):
    try:
        # 淇敼鍚庯紙浜戠鎸佷箙鍖栵紒锛?
        conn = sqlite3.connect(get_db_path(), check_same_thread=False)
        c = conn.cursor()
        c.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)",
                  (username, hash_password(password)))
        conn.commit()
        conn.close()
        return True, "娉ㄥ唽鎴愬姛锛佽鐧诲綍"
    except sqlite3.IntegrityError:
        return False, "鐢ㄦ埛鍚嶅凡瀛樺湪"


def authenticate_user(username, password):
    # 淇敼鍚庯紙浜戠鎸佷箙鍖栵紒锛?
    conn = sqlite3.connect(get_db_path(), check_same_thread=False)
    c = conn.cursor()
    c.execute("SELECT id FROM users WHERE username = ? AND password_hash = ?",
              (username, hash_password(password)))
    result = c.fetchone()
    conn.close()
    return result[0] if result else None


def load_user_conversations(user_id):
    """鍔犺浇鐢ㄦ埛鎵€鏈夊巻鍙插璇?""
    # 淇敼鍚庯紙浜戠鎸佷箙鍖栵紒锛?
    conn = sqlite3.connect(get_db_path(), check_same_thread=False)
    c = conn.cursor()

    # 鍔犺浇S1鍘嗗彶
    c.execute(
        "SELECT title, content FROM conversations WHERE user_id = ? AND module = 's1' ORDER BY created_at DESC LIMIT 10",
        (user_id,))
    s1_list = [{"title": row[0], "content": row[1]} for row in c.fetchall()]

    # 鍔犺浇S3鍘嗗彶
    c.execute(
        "SELECT title, content, solution FROM conversations WHERE user_id = ? AND module = 's3' ORDER BY created_at DESC LIMIT 10",
        (user_id,))
    s3_list = [{"title": row[0], "content": row[1], "solution": row[2] or ""} for row in c.fetchall()]

    # 鍔犺浇杩介棶鍘嗗彶
    c.execute(
        "SELECT title, content FROM conversations WHERE user_id = ? AND module = 'inquiry' ORDER BY created_at DESC LIMIT 10",
        (user_id,))
    inquiry_list = [{"title": row[0], "content": row[1]} for row in c.fetchall()]

    conn.close()
    return s1_list, s3_list, inquiry_list


def save_conversation(user_id, module, title, content, solution=None):
    """淇濆瓨鍗曟潯瀵硅瘽鍒版暟鎹簱"""
    # 淇敼鍚庯紙浜戠鎸佷箙鍖栵紒锛?
    conn = sqlite3.connect(get_db_path(), check_same_thread=False)
    c = conn.cursor()
    c.execute("INSERT INTO conversations (user_id, module, title, content, solution) VALUES (?, ?, ?, ?, ?)",
              (user_id, module, title, content, solution))
    conn.commit()
    conn.close()









# 1. 椤甸潰閰嶇疆
st.set_page_config(
    page_title="MCU-Tutor - 鍗曠墖鏈哄疄楠孉I瀵煎笀寮曟搸",
    page_icon="馃枼锔?,
    layout="wide"
)







# ========== CSS 鏍峰紡娉ㄥ叆 (娴呯豢鑹茶儗鏅?+ 缁嗚妭浼樺寲) ==========

st.html("""
<style>
/* ===== 鎵嬫満鏂囧瓧寮哄埗鍙锛堟繁鑹?娴呰壊妯″紡閫氬悆锛?==== */
* {
    color: #2D3748 !important; /* 娣辩伆鏂囧瓧 */
}
/* 1. 鍏ㄥ眬鑳屾櫙鑹?- 浜戦浘鐏?(楂樼銆佹姢鐪笺€佺獊鍑哄崱鐗囨劅) */
.stApp {
    background-color: #F5F7F8;
    color: #333333;
}
/* 椤堕儴 Header 鑳屾櫙鑹?*/
header[data-testid="stHeader"] {
    background-color: #F5F7F8;
}

/* 2. 渚ц竟鏍?- 寮哄埗绾櫧 */
section[data-testid="stSidebar"] {
    background-color: #FFFFFF !important;
    border-right: 1px solid #E0E0E0;
}
section[data-testid="stSidebar"] > div {
    background-color: #FFFFFF !important;
}

/* ========== 3. 鎸夐挳鏍峰紡浼樺寲锛堝叧閿慨鏀癸紒锛?========== */
/* 娴呯豢鑳屾櫙 + 绾粦瀛椾綋锛圵CAG AA绾у姣斿害 12.5:1锛?*/
div.stButton > button,
div.stDownloadButton > button,
button[kind="secondary"],
button[kind="primary"] {
    background-color: #A5D6A7 !important;  /* 鏌斿拰娴呯豢锛堥潪鍒虹溂锛?*/
    color: #000000 !important;             /* 绾粦瀛椾綋锛堟竻鏅伴攼鍒╋級 */
    border-radius: 8px !important;
    border: none !important;
    font-weight: 600 !important;
    padding: 0.6rem 1.2rem !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 2px 4px rgba(165, 214, 167, 0.3) !important;
    background-image: none !important;
}

/* 鎮仠鏁堟灉锛氱◢娣辩豢 + 榛戝瓧淇濇寔 */
div.stButton > button:hover,
button[kind="secondary"]:hover,
button[kind="primary"]:hover {
    background-color: #81C784 !important;  /* 鎮仠鍔犳繁 */
    color: #000000 !important;
    box-shadow: 0 4px 8px rgba(129, 199, 132, 0.4) !important;
    transform: translateY(-1px) !important;
}

/* 鎸変笅鏁堟灉 */
div.stButton > button:active {
    transform: translateY(0) !important;
    box-shadow: 0 2px 4px rgba(165, 214, 167, 0.3) !important;
}

/* 绂佺敤鐘舵€侊細鏋佹祬缁?+ 娣辩伆瀛楋紙浠嶆竻鏅板彲杈級 */
div.stButton > button:disabled,
button[kind="secondary"]:disabled,
button[kind="primary"]:disabled {
    background-color: #E8F5E9 !important;
    color: #666666 !important;
    cursor: not-allowed !important;
    opacity: 1 !important;
}

/* 4. 杈撳叆妗?鏂囨湰妗?*/
.stTextArea textarea, 
.stTextInput input, 
.stSelectbox div[data-baseweb="select"] {
    background-color: #FFFFFF;
    border: 1px solid #D1D5DB;
    border-radius: 6px;
}
.stTextArea textarea {
    border: 1px solid #a5d6a7;
}

/* 6. 杩涘害鏉￠鑹插悓姝ヤ紭鍖栵紙娴呯豢绯伙級 */
.stProgress > div > div > div > div {
    background-color: #A5D6A7 !important;
}

/* 7. 瀵煎笀鍙嶉姘旀场妗?*/
[data-testid="stChatMessage"] {
    background-color: #FFFFFF;
    border: 1px solid #E5E7EB;
    border-radius: 12px;
    padding: 15px;
    margin-top: 10px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}
/* 鏈哄櫒浜哄ご鍍忚儗鏅壊 */
[data-testid="stChatMessageAvatarBackground"] {
    background-color: #1976D2;
}
</style>
""")

# 妫€鏌ョ幆澧冨彉閲忥紙鍏抽敭锛丼treamlit Cloud 涓嶈 .env锛?
ai_api_key = os.getenv("AI_API_KEY")
ai_base_url = os.getenv("AI_BASE_URL")

# 涓ユ牸楠岃瘉
if not ai_api_key:
    st.error("鉂?**AI_API_KEY 鏈厤缃?*\n璇峰湪 Streamlit Cloud 鈫?Manage app 鈫?Secrets 涓坊鍔狅細\n`AI_API_KEY = sk-浣犵殑瀵嗛挜`")
    st.stop()
if not ai_base_url:
    st.error("鉂?**AI_BASE_URL 鏈厤缃?*\n璇峰湪 Secrets 涓坊鍔狅細\n`AI_BASE_URL = https://api.deepseek.com/v1`")
    st.stop()
if not ai_base_url.rstrip("/").endswith("/v1"):
    st.error(f"鉂?**AI_BASE_URL 鏍煎紡閿欒**\n褰撳墠鍊? `{ai_base_url}`\n鉁?姝ｇ‘鏍煎紡: `https://api.deepseek.com/v1`\n锛堝繀椤诲寘鍚?`/v1` 鍚庣紑锛?)
    st.stop()



# 2. 鍒濆鍖?AI
if "ai_engine" not in st.session_state:
    st.session_state.ai_engine = MCU_TutorAI()

# --- 鍒濆鍖栧涔犺繘搴﹁鏁板櫒 ---
if "weekly_progress_count" not in st.session_state:
    st.session_state.weekly_progress_count = 0  # 鍒濆涓?0

# --- 鍒濆鍖?S1 璇婄枟瀹ゅ璇濆巻鍙?---
if "s1_diagnosis_history" not in st.session_state:
    st.session_state.s1_diagnosis_history = ""  # 鍒濆鍖栦负绌哄瓧绗︿覆
# --- 鍒濆鍖?S3 闈跺満绛旀 & 鍘熺悊杩介棶鍘嗗彶 ---
if "s3_solution_text" not in st.session_state:
    st.session_state.s3_solution_text = ""  # S3 绛旀璁板繂
if "deep_inquiry_history" not in st.session_state:
    st.session_state.deep_inquiry_history = ""  # 鍘熺悊杩介棶璁板繂
# --- 鍒濆鍖?S1 鍘嗗彶璁板綍鍒楄〃 (瀛樺偍澶氳疆瀵硅瘽) ---
if "s1_chat_history_list" not in st.session_state:
    st.session_state.s1_chat_history_list = []  # 缁撴瀯: [{'title': 'GPIO...', 'content': '...'}]
if "s1_active_history_index" not in st.session_state:
    st.session_state.s1_active_history_index = None  # None浠ｈ〃褰撳墠鏂板璇濓紝鏁板瓧浠ｈ〃鏌ョ湅鐗瑰畾鍘嗗彶

# --- 鍒濆鍖?S3 闈跺満鍘嗗彶璁板綍 ---
if "s3_chat_history_list" not in st.session_state:
    st.session_state.s3_chat_history_list = []  # S3 闈跺満鍘嗗彶璁板綍鍒楄〃
if "s3_active_history_index" not in st.session_state:
    st.session_state.s3_active_history_index = None  # S3 褰撳墠鏌ョ湅鐨勫巻鍙茬储寮?

# --- 鍒濆鍖?娣卞害杩介棶鍘嗗彶璁板綍 ---
if "inquiry_chat_history_list" not in st.session_state:
    st.session_state.inquiry_chat_history_list = []  # 娣卞害杩介棶鍘嗗彶璁板綍鍒楄〃
if "inquiry_active_history_index" not in st.session_state:
    st.session_state.inquiry_active_history_index = None  # 娣卞害杩介棶褰撳墠鏌ョ湅鐨勫巻鍙茬储寮?

# --- 鍒濆鍖?S3 AI瀵煎笀瀹￠槄鐘舵€?---
if "s3_tutor_history" not in st.session_state:
    st.session_state.s3_tutor_history = []  # AI瀵煎笀瀵硅瘽鍘嗗彶
if "s3_tutor_feedback" not in st.session_state:
    st.session_state.s3_tutor_feedback = ""
if "s3_tutor_round" not in st.session_state:
    st.session_state.s3_tutor_round = 0
if "s3_show_final_answer" not in st.session_state:
    st.session_state.s3_show_final_answer = False
if "s3_task_submitted" not in st.session_state:
    st.session_state.s3_task_submitted = False
if "s3_is_correct" not in st.session_state:
    st.session_state.s3_is_correct = False


# --- 鍒濆鍖栧垹闄ゆā寮忕姸鎬?---
if "delete_mode" not in st.session_state:
    st.session_state.delete_mode = False
if "delete_menu" not in st.session_state:
    st.session_state.delete_menu = None

# 3. 渚ц竟鏍忥細涓汉瀛︿範妗ｆ
with st.sidebar:
    # 妫€鏌ユ槸鍚﹀凡鐧诲綍
    # 鏇挎崲涓轰互涓嬩唬鐮侊紙鍙繚鐣欏凡鐧诲綍鐘舵€佺殑鏄剧ず锛?
    if "user_id" not in st.session_state:
        st.title("鈿狅笍 鏈櫥褰?)
        st.info("璇峰厛鐧诲綍浠ヤ娇鐢ㄥ姛鑳?)

    else:
        # 宸茬櫥褰曠姸鎬侊細鏄剧ず鐢ㄦ埛淇℃伅鍜岀櫥鍑烘寜閽?
        st.title(f"馃懆鈥嶐煉?娆㈣繋 {st.session_state.username}")
        if st.button("馃毆 閫€鍑虹櫥褰?, use_container_width=True):
            # 娓呴櫎鎵€鏈夌敤鎴风浉鍏崇姸鎬?
            for key in ["user_id", "username", "s1_chat_history_list",
                        "s3_chat_history_list", "inquiry_chat_history_list"]:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()
    # 涓存椂璋冭瘯锛氭樉绀轰繚瀛樿褰?
    if st.session_state.get("debug_save"):
        with st.expander("馃攳 淇濆瓨璋冭瘯鏃ュ織"):
            for log in st.session_state.debug_save[-5:]:  # 鏄剧ず鏈€杩?鏉?
                st.text(log)
#===================================================================
    try:
        st.image("xinkecolorlog.png", use_container_width=True)
    except:
        # 涓囦竴鍥剧墖娌℃斁瀵逛綅缃紝鏄剧ず涓€涓枃瀛楁彁绀猴紝闃叉鎶ラ敊宕╂簝
        st.error("鈿狅笍 璇峰皢 xinkeyuanlog.png 澶嶅埗鍒伴」鐩牴鐩綍")
    st.write("")  # 鍔犱竴琛岀┖琛岋紝澧炲姞涓€鐐瑰懠鍚告劅
    st.image("server.png", width=60)

    st.title("馃敩 MCU 瀛︿範鎺у埗鍙?)
    st.caption("Ver 2.0 | 鍗曠墖鏈篈I瀵煎笀鐗?)
    st.markdown("---")


    # 瀵艰埅鏍?
    menu = st.radio(
        "鍔熻兘瀵艰埅",
        ["馃捇 浠ｇ爜鏅鸿兘璇婄枟", "馃幆 瀹為獙闈跺満宸ュ潑", "馃敩 鍘熺悊娣卞害杩介棶"],
        index=0
    )

    st.markdown("---")

    # 鍒犻櫎妯″紡鎸夐挳
    if st.button("馃棏锔?鍒犻櫎妯″紡", use_container_width=True):
        st.session_state.delete_mode = not st.session_state.delete_mode
        st.session_state.delete_menu = menu
        st.rerun()

    # 鏍规嵁鑿滃崟椤规樉绀轰笉鍚岀殑鍘嗗彶璁板綍
    if menu == "馃捇 浠ｇ爜鏅鸿兘璇婄枟":
        st.markdown("#### 馃晵 鍘嗗彶瀵硅瘽")

        # 1. 鏂板缓瀵硅瘽鎸夐挳
        if st.button("鉃?鏂板缓瀵硅瘽", use_container_width=True):
            st.session_state.s1_active_history_index = None  # 鍒囨崲鍥炰富瑙嗗浘
            st.session_state.s1_diagnosis_history = ""  # 娓呯┖褰撳墠灞忓箷
            st.rerun()  # 寮哄埗鍒锋柊

        # 2. 寰幆鏄剧ず鍘嗗彶璁板綍 (鍊掑簭锛氭渶鏂扮殑鍦ㄤ笂闈?
        # enumerate(reversed(...)) 璁╂垜浠粠鏈€鏂扮殑寮€濮嬮亶鍘?
        for i, chat in enumerate(reversed(st.session_state.s1_chat_history_list)):
            # 璁＄畻鍘熷鍒楄〃涓殑鐪熷疄绱㈠紩
            real_index = len(st.session_state.s1_chat_history_list) - 1 - i

            # 鎴彇鏍囬锛屽お闀挎樉绀虹渷鐣ュ彿
            display_title = (chat['title'][:10] + '..') if len(chat['title']) > 10 else chat['title']

            # 鍒犻櫎妯″紡涓嬬殑鐗规畩鏄剧ず
            if st.session_state.delete_mode and st.session_state.delete_menu == "馃捇 浠ｇ爜鏅鸿兘璇婄枟":
                # 鍒犻櫎妯″紡涓嬫樉绀哄垹闄ゆ寜閽?
                if st.button(f"鉂?{display_title}", key=f"del_s1_{real_index}"):
                    # 1. 浠巗ession_state鍒犻櫎
                    deleted_record = st.session_state.s1_chat_history_list.pop(real_index)
                    # 2. 浠庢暟鎹簱鍒犻櫎锛堝叧閿紒锛?
                    if "user_id" in st.session_state:
                        # 淇敼鍚庯紙浜戠鎸佷箙鍖栵紒锛?
                        conn = sqlite3.connect(get_db_path(), check_same_thread=False)
                        c = conn.cursor()
                        # 閫氳繃鏍囬+妯″潡+鐢ㄦ埛绮剧‘鍖归厤锛堝疄闄呯敓浜у缓璁敤ID锛?
                        c.execute("""DELETE FROM conversations 
                                        WHERE user_id = ? AND module = 's1' AND title = ?""",
                                  (st.session_state.user_id, deleted_record['title']))
                        conn.commit()
                        conn.close()
                    # 濡傛灉褰撳墠姝ｅ湪鏌ョ湅琚垹闄ょ殑璁板綍锛屽洖鍒板綋鍓嶅璇?
                    if st.session_state.s1_active_history_index == real_index:
                        st.session_state.s1_active_history_index = None
                    st.rerun()
            else:
                # 鐐瑰嚮鎸夐挳锛屽垏鎹㈠埌瀵瑰簲鐨勫巻鍙茶褰?
                # key=f"hist_{real_index}" 淇濊瘉姣忎釜鎸夐挳ID鍞竴锛屼笉鎶ラ敊
                if st.button(f"馃搫 {display_title}", key=f"hist_{real_index}"):
                    st.session_state.s1_active_history_index = real_index
                    st.rerun()

    elif menu == "馃幆 瀹為獙闈跺満宸ュ潑":
        st.markdown("#### 馃晵 鍘嗗彶瀵硅瘽")

        # 1. 鏂板缓瀵硅瘽鎸夐挳
        if st.button("鉃?鏂板缓瀵硅瘽", use_container_width=True):
            st.session_state.s3_active_history_index = None  # 鍒囨崲鍥炰富瑙嗗浘
            # 娓呯┖褰撳墠灞忓箷鐨勯鐩拰绛旀
            if "s3_task_text" in st.session_state:
                del st.session_state.s3_task_text
            st.session_state.s3_solution_text = ""
            st.session_state.s3_show_answer = False
            st.rerun()  # 寮哄埗鍒锋柊

        # 2. 寰幆鏄剧ず鍘嗗彶璁板綍 (鍊掑簭锛氭渶鏂扮殑鍦ㄤ笂闈?
        for i, chat in enumerate(reversed(st.session_state.s3_chat_history_list)):
            # 璁＄畻鍘熷鍒楄〃涓殑鐪熷疄绱㈠紩
            real_index = len(st.session_state.s3_chat_history_list) - 1 - i

            # 鎴彇鏍囬锛屽お闀挎樉绀虹渷鐣ュ彿
            display_title = (chat['title'][:10] + '..') if len(chat['title']) > 10 else chat['title']

            # 鍒犻櫎妯″紡涓嬬殑鐗规畩鏄剧ず
            if st.session_state.delete_mode and st.session_state.delete_menu == "馃幆 瀹為獙闈跺満宸ュ潑":
                # 鍒犻櫎妯″紡涓嬫樉绀哄垹闄ゆ寜閽?
                if st.button(f"鉂?{display_title}", key=f"del_s3_{real_index}"):
                    # 1. 浠巗ession_state鍒犻櫎
                    deleted_record = st.session_state.s3_chat_history_list.pop(real_index)

                    # 2. 浠庢暟鎹簱鍒犻櫎锛堝叧閿紒锛?
                    if "user_id" in st.session_state:
                        # 淇敼鍚庯紙浜戠鎸佷箙鍖栵紒锛?
                        conn = sqlite3.connect(get_db_path(), check_same_thread=False)
                        c = conn.cursor()
                        # 閫氳繃鏍囬+妯″潡+鐢ㄦ埛绮剧‘鍖归厤锛堝疄闄呯敓浜у缓璁敤ID锛?
                        c.execute("""DELETE FROM conversations 
                                        WHERE user_id = ? AND module = 's3' AND title = ?""",
                                  (st.session_state.user_id, deleted_record['title']))
                        conn.commit()
                        conn.close()
                    # 濡傛灉褰撳墠姝ｅ湪鏌ョ湅琚垹闄ょ殑璁板綍锛屽洖鍒板綋鍓嶅璇?
                    if st.session_state.s3_active_history_index == real_index:
                        st.session_state.s3_active_history_index = None
                    st.rerun()
            else:
                # 鐐瑰嚮鎸夐挳锛屽垏鎹㈠埌瀵瑰簲鐨勫巻鍙茶褰?
                if st.button(f"馃搫 {display_title}", key=f"s3_hist_{real_index}"):
                    st.session_state.s3_active_history_index = real_index
                    st.rerun()

    elif menu == "馃敩 鍘熺悊娣卞害杩介棶":
        st.markdown("#### 馃晵 鍘嗗彶瀵硅瘽")

        # 1. 鏂板缓瀵硅瘽鎸夐挳
        if st.button("鉃?鏂板缓瀵硅瘽", use_container_width=True):
            st.session_state.inquiry_active_history_index = None  # 鍒囨崲鍥炰富瑙嗗浘
            # 娓呯┖褰撳墠灞忓箷鐨勮拷闂褰?
            st.session_state.deep_inquiry_history = ""
            st.rerun()  # 寮哄埗鍒锋柊

        # 2. 寰幆鏄剧ず鍘嗗彶璁板綍 (鍊掑簭锛氭渶鏂扮殑鍦ㄤ笂闈?
        for i, chat in enumerate(reversed(st.session_state.inquiry_chat_history_list)):
            # 璁＄畻鍘熷鍒楄〃涓殑鐪熷疄绱㈠紩
            real_index = len(st.session_state.inquiry_chat_history_list) - 1 - i

            # 鎴彇鏍囬锛屽お闀挎樉绀虹渷鐣ュ彿
            display_title = (chat['title'][:10] + '..') if len(chat['title']) > 10 else chat['title']

            # 鍒犻櫎妯″紡涓嬬殑鐗规畩鏄剧ず
            if st.session_state.delete_mode and st.session_state.delete_menu == "馃敩 鍘熺悊娣卞害杩介棶":
                # 鍒犻櫎妯″紡涓嬫樉绀哄垹闄ゆ寜閽?
                if st.button(f"鉂?{display_title}", key=f"del_inquiry_{real_index}"):
                    # 1. 浠巗ession_state鍒犻櫎
                    deleted_record = st.session_state.inquiry_chat_history_list.pop(real_index)

                    # 2. 浠庢暟鎹簱鍒犻櫎锛堝叧閿紒锛?
                    if "user_id" in st.session_state:
                        conn = sqlite3.connect(get_db_path())
                        c = conn.cursor()
                        # 閫氳繃鏍囬+妯″潡+鐢ㄦ埛绮剧‘鍖归厤锛堝疄闄呯敓浜у缓璁敤ID锛?
                        c.execute("""DELETE FROM conversations 
                                        WHERE user_id = ? AND module = 'inquiry' AND title = ?""",
                                  (st.session_state.user_id, deleted_record['title']))
                        conn.commit()
                        conn.close()
                    # 濡傛灉褰撳墠姝ｅ湪鏌ョ湅琚垹闄ょ殑璁板綍锛屽洖鍒板綋鍓嶅璇?
                    if st.session_state.inquiry_active_history_index == real_index:
                        st.session_state.inquiry_active_history_index = None
                    st.rerun()
            else:
                # 鐐瑰嚮鎸夐挳锛屽垏鎹㈠埌瀵瑰簲鐨勫巻鍙茶褰?
                if st.button(f"馃搫 {display_title}", key=f"inquiry_hist_{real_index}"):
                    st.session_state.inquiry_active_history_index = real_index
                    st.rerun()

    # 鏄剧ず鍒犻櫎妯″紡鎻愮ず
    if st.session_state.delete_mode and st.session_state.delete_menu == menu:
        st.warning("鈿狅笍 宸茶繘鍏ュ垹闄ゆā寮忥紒鐐瑰嚮瀵硅瘽鏍囬鍗冲彲鍒犻櫎銆傚啀娆＄偣鍑诲垹闄ゆā寮忔寜閽€€鍑恒€?)

    # 妯℃嫙鐨勭敤鎴风姸鎬?
    # 鍔ㄦ€佺殑鐢ㄦ埛鐘舵€?
    # 璁＄畻鐧惧垎姣?(0 鍒?1.0 涔嬮棿)
    current_count = st.session_state.weekly_progress_count
    progress_percent = min(current_count / 10, 1.0)  # 灏侀《 100%

    st.write(f"**褰撳墠鐘舵€?(宸插畬鎴?{current_count}/10 浠诲姟)**")
    st.progress(progress_percent, text="鏈懆瀛︿範杩涘害")

    if current_count >= 10:
        st.success("馃帀 澶浜嗭紒鏈懆瀛︿範鐩爣宸茶揪鎴愶紒")
    else:
        # 浣跨敤鑷畾涔塇TML鏄剧ず绾㈣壊杩涘害鏉?
        st.markdown(f"""
           <div style="background-color: #FFCDD2; border-radius: 4px; padding: 2px;">
               <div style="background-color: #F44336; width: {progress_percent * 100}%; height: 20px; border-radius: 4px; text-align: center; line-height: 20px; color: white; font-size: 12px;">
                   {int(progress_percent * 100)}%
               </div>
           </div>
           """, unsafe_allow_html=True)
        # 鏂板杩欒锛氱粰瀛︾敓涓€鐐瑰姩鍔?
        st.caption(f"鍔犳补锛佸啀瀹屾垚 {10 - current_count} 涓换鍔″嵆鍙揪鎴愮洰鏍?馃殌")

    st.info("馃挕 鎻愮ず锛氬鎬濊€冿紝灏戜緷璧栥€傚厛灏濊瘯鑷繁鍒嗘瀽浠ｇ爜鎶ラ敊鍘熷洜銆?)

# =============== 灞呬腑鐧诲綍鐣岄潰锛堟彃鍏ユ澶勶級 ===============
if "user_id" not in st.session_state:
    # 灞呬腑瀹瑰櫒
    st.markdown("""
        <div style="display: flex; justify-content: center; align-items: center; min-height: 70vh;">
            <div style="width: 420px; padding: 35px; background: white; border-radius: 16px; 
                       box-shadow: 0 10px 30px rgba(0,0,0,0.12); text-align: center;">
                <h2 style="color: #2E7D32; margin-bottom: 10px;">馃敩 MCU-Tutor</h2>
                <p style="color: #555; margin-bottom: 25px;">鍗曠墖鏈哄疄楠孉I瀵煎笀寮曟搸</p>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # 鐧诲綍琛ㄥ崟锛堝眳涓垪锛?
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("login_form"):
            st.text_input("馃懁 鐢ㄦ埛鍚?, key="login_username")
            st.text_input("馃攽 瀵嗙爜", type="password", key="login_password")
            submit = st.form_submit_button("馃攼 鐧诲綍", use_container_width=True, type="primary")

            if submit:
                uid = authenticate_user(st.session_state.login_username, st.session_state.login_password)
                if uid:
                    st.session_state.user_id = uid
                    st.session_state.username = st.session_state.login_username
                    # 鍔犺浇鍘嗗彶
                    s1_h, s3_h, iq_h = load_user_conversations(uid)
                    st.session_state.s1_chat_history_list = s1_h
                    st.session_state.s3_chat_history_list = s3_h
                    st.session_state.inquiry_chat_history_list = iq_h
                    st.success(f"馃帀 娆㈣繋鍥炴潵锛寋st.session_state.username}锛?)
                    st.rerun()
                else:
                    st.error("鉂?鐢ㄦ埛鍚嶆垨瀵嗙爜閿欒")

        # 娉ㄥ唽鍖?
        st.markdown("---")
        if st.button("鉁?娌℃湁璐﹀彿锛熺珛鍗虫敞鍐?, use_container_width=True):
            st.session_state.show_register = True

        if st.session_state.get("show_register", False):
            with st.form("reg_form"):
                ru = st.text_input("鏂扮敤鎴峰悕", key="reg_user")
                rp = st.text_input("鏂板瘑鐮?, type="password", key="reg_pass")
                rsub = st.form_submit_button("鉁?娉ㄥ唽", use_container_width=True)
                if rsub:
                    ok, msg = register_user(ru, rp)
                    if ok:
                        st.success(msg)
                        st.session_state.show_register = False
                        st.session_state.login_username = ru  # 鑷姩濉厖
                    else:
                        st.error(msg)

    st.stop()  # 鈿狅笍 鍏抽敭锛氶樆姝㈠悗缁姛鑳芥ā鍧楁覆鏌?
# =============== 鐧诲綍鐣岄潰缁撴潫 ===============

# ==================== 妯″潡涓€锛氭櫤鑳芥晠闅滆瘖鐤楀 (S1 鍗囩骇鐗? ====================
if menu == "馃捇 浠ｇ爜鏅鸿兘璇婄枟":
    st.header("馃捇 鍗曠墖鏈轰唬鐮佹櫤鑳借瘖鐤?| AI瀵煎笀寮曟搸")
    st.markdown("LED 涓嶄寒锛熷畾鏃跺櫒涓嶅噯锛熷埆鎬ョ潃闂瓟妗堬紝鍏堝憡璇夋垜**浣犺寰?*鍝噷鍑轰簡闂銆?)

    col1, col2 = st.columns([1, 1], gap="medium")

    with col1:
        st.subheader("1. 鎻愪氦瀹為獙鏁版嵁")
        topic = st.selectbox(
            "馃敩 瀹為獙涓婚",
            [
                "GPIO 鎺у埗LED", "瀹氭椂鍣ㄤ腑鏂?, "UART 涓插彛閫氫俊", "I2C 鎬荤嚎閫氫俊", "SPI 閫氫俊鍗忚",
                "ADC 鐢靛帇閲囬泦", "PWM 鐢垫満璋冮€?, "澶栭儴涓柇閰嶇疆", "鐪嬮棬鐙楀畾鏃跺櫒", "DMA 鏁版嵁浼犺緭",
                "鎸夐敭娑堟姈澶勭悊", "LCD 娑叉櫠鏄剧ず", "DS18B20 娓╁害閲囬泦", "EEPROM 璇诲啓鎿嶄綔", "RTC 瀹炴椂鏃堕挓",
                "CAN 鎬荤嚎閫氫俊", "绾㈠閬ユ帶瑙ｇ爜", "姝ヨ繘鐢垫満椹卞姩", "瓒呭０娉㈡祴璺?, "DAC 娉㈠舰杈撳嚭"
            ],
            index=0
        )

        # 鍏抽敭鍗囩骇锛氬己鍒舵€濊€冪幆鑺?
        user_thought = st.text_area(
            "馃 鎴戠殑鍒濇鎺掓煡鎬濊矾 (蹇呭～)",
            height=100,
            placeholder="渚嬪锛氭垜瑙夊緱鏄?GPIO 鍒濆鍖栨ā寮忔病閰嶅锛屾垨鑰呮槸涓柇浼樺厛绾ц缃湁闂..."
        )

        user_code = st.text_area(
            "馃搵 绮樿创璁惧閰嶇疆 / 鎶ラ敊鏃ュ織",
            height=300,
            placeholder="// 绮樿创浣犵殑 Keil/STM32CubeIDE 浠ｇ爜鐗囨..."
        )

        analyze_btn = st.button("鎻愪氦缁?AI 瀵煎笀", use_container_width=True)

    with col2:
        st.subheader("2. 瀵煎笀鍙嶉")
        result_box = st.container()

        # 鍦烘櫙 A锛氱敤鎴峰垰鍒氱偣鍑讳簡"鎻愪氦"鎸夐挳锛堢敓鎴愭柊鍐呭锛?
        if analyze_btn:
            if not user_thought:
                st.warning("鈿狅笍 璇峰厛濉啓浣犵殑鎺掓煡鎬濊矾锛佸涔犱笉鑳藉彧闈?AI銆?)
            elif not user_code:
                st.warning("鈿狅笍 璇风矘璐撮厤缃唬鐮併€?)
            else:
                with result_box:
                    with st.chat_message("assistant", avatar="馃"):
                        st.markdown("#### 馃 瀵煎笀姝ｅ湪鍒嗘瀽...")
                        # 鑾峰彇娴佸紡鍝嶅簲
                        stream = st.session_state.ai_engine.get_diagnostic_response(user_code, user_thought, topic)

                        # --- 鍏抽敭淇敼锛歴t.write_stream 浼氳繑鍥炲畬鏁寸殑瀛楃涓?---
                        # 鎴戜滑涓嶄粎鎶婂畠鎵撳嵃鍑烘潵锛岃繕椤烘墜瀛樿繘 session_state 閲?
                        response_text = st.write_stream(stream)
                        st.session_state.s1_diagnosis_history = response_text
                        # --- (鏂板) 鑷姩瀛樻。閫昏緫 ---
                        # 1. 鏋勯€犳爣棰?(鐢ㄤ富棰?鏃堕棿鎴栨€濊矾)
                        timestamp = datetime.now().strftime("%H:%M")
                        title = f"[{timestamp}] {topic}"

                        # 2. 瀛樺叆鍒楄〃
                        new_record = {"title": title, "content": response_text}
                        st.session_state.s1_chat_history_list.append(new_record)
####################################################################
                        if "user_id" in st.session_state:
                            save_conversation(
                                user_id=st.session_state.user_id,
                                module="s1",
                                title=title,
                                content=response_text
                            )

###########################################################################
                        # 3. 闄愬埗鍙瓨 10 鏉?(瓒呰繃灏辨妸鏈€鏃х殑鍒犳帀)
                        if len(st.session_state.s1_chat_history_list) > 10:
                            st.session_state.s1_chat_history_list.pop(0)

                        # 4. 閲嶇疆鏌ョ湅鐘舵€佷负"褰撳墠"
                        st.session_state.s1_active_history_index = None
        # 鍦烘櫙 B: 鐢ㄦ埛鐐瑰嚮浜嗕晶杈规爮鐨勫巻鍙茶褰?(鏌ョ湅鏃у瓨妗?
        elif st.session_state.s1_active_history_index is not None:
            # 鏍规嵁绱㈠紩鍙栧嚭鍘嗗彶鏁版嵁
            record = st.session_state.s1_chat_history_list[st.session_state.s1_active_history_index]
            with result_box:
                with st.chat_message("assistant", avatar="馃"):
                    # 鏄剧ず鏍囬鎻愮ず杩欐槸鍘嗗彶
                    st.caption(f"馃搨 姝ｅ湪鏌ョ湅鍘嗗彶瀛樻。锛歿record['title']}")
                    st.markdown(record["content"])



        # 鍦烘櫙 B锛氱敤鎴锋病鐐规寜閽紝浣嗕箣鍓嶆湁鍘嗗彶璁板綍锛堝垏鎹㈤〉闈㈠洖鏉ュ悗鏄剧ず锛?
        elif st.session_state.s1_diagnosis_history:
            with result_box:
                with st.chat_message("assistant", avatar="馃"):
                    st.markdown("#### 馃 瀵煎笀鐨勫巻鍙插垎鏋?..")
                    # 鐩存帴鏄剧ず瀛樹笅鏉ョ殑鏂囧瓧
                    st.markdown(st.session_state.s1_diagnosis_history)
        # 鍦烘櫙 C (鏂板)锛氶粯璁ゅ垵濮嬪寲鐘舵€?
        else:
            with result_box:
                with st.chat_message("assistant", avatar="馃"):
                    st.markdown("""
                    馃憢 **浣犲ソ锛佹垜鏄綘鐨勫崟鐗囨満AI瀵煎笀銆?*

                    璇峰湪宸︿晶 **鎻愪氦瀹為獙鏁版嵁**锛?
                    1. 閫夋嫨瀹為獙涓婚锛圙PIO/Timer/UART绛夛級
                    2. 鎻忚堪浣犵殑鎺掓煡鎬濊矾
                    3. 绮樿创鎶ラ敊鐨勪唬鐮佹垨鎶ラ敊淇℃伅

                    鎴戜細鍦ㄨ繖閲屼负浣犳彁渚?**鑻忔牸鎷夊簳寮忚瘖鏂紩瀵?*锛屽姪浣犳壘鍒伴棶棰樻牴婧愶紒馃洜锔?
                    """)


# ==================== 妯″潡浜岋細浠婃棩瀹氬埗闈跺満 (S3 鍗囩骇鐗? ====================
elif menu == "馃幆 瀹為獙闈跺満宸ュ潑":
    st.header("馃幆 瀹為獙闈跺満宸ュ潑 | 鍗曠墖鏈哄疄璁敓鎴?)
    st.markdown("浠庝笅鏂瑰垪琛ㄩ€夋嫨浠婃棩瀹為獙璇鹃锛岀敓鎴愪笓灞炵殑瀹炴垬缁冧範浠诲姟銆?)

    c1, c2, c3 = st.columns([2, 2, 1])
    with c1:
        today_focus = st.selectbox("馃搮 閫夋嫨瀹為獙璇鹃", options=[
            "GPIO 杈撳叆杈撳嚭鎺у埗锛圠ED銆佹寜閿級",
            "瀹氭椂鍣?璁℃暟鍣ㄥ簲鐢?,
            "澶栭儴涓柇搴旂敤",
            "涓插彛閫氫俊锛圲ART锛?,
            "I2C 閫氫俊锛圤LED銆丒EPROM锛?,
            "SPI 閫氫俊",
            "PWM 杈撳嚭锛堝懠鍚哥伅銆佺數鏈鸿皟閫燂級",
            "ADC 妯℃嫙閲忛噰闆?,
            "鏁扮爜绠″姩鎬佹壂鎻?,
            "LCD 娑叉櫠鏄剧ず",
            "鐪嬮棬鐙楀畾鏃跺櫒",
            "鐙珛鎸夐敭涓庣煩闃甸敭鐩?,
            "绾㈠閬ユ帶瑙ｇ爜",
            "娓╁害浼犳劅鍣紙DS18B20锛?,
            "缁煎悎瀹為獙锛氭櫤鑳藉皬杞?,
            "缁煎悎瀹為獙锛氭暟瀛楁椂閽?,
            "缁煎悎瀹為獙锛氭俯婀垮害鐩戞祴绯荤粺"
        ])
    with c2:
        level = st.select_slider("馃搳 鎴戝璇ョ煡璇嗙偣鐨勬帉鎻″害", options=["瀹屽叏涓嶆噦", "浼兼噦闈炴噦", "鍩烘湰鎺屾彙", "鎴戞兂鎸戞垬鏋侀檺"])
    with c3:
        st.write("")
        st.write("")
        gen_btn = st.button("鐢熸垚浠诲姟鍗?, type="primary")

    st.markdown("---")

    # --- 鏍稿績閫昏緫淇敼锛氬紩鍏?Session State 闃叉鍒锋柊涓㈠け ---

    # 1. 璐熻矗鐢熸垚浠诲姟 (褰撶偣鍑荤敓鎴愭寜閽椂)
    if gen_btn and today_focus:
        # 閲嶇疆绛旀鏄剧ず鐨勫紑鍏筹紝鍥犱负鐢熸垚浜嗘柊棰?
        st.session_state.s3_show_answer = False
        st.session_state.current_task_scored = False  # <--- 鏂板杩欒锛氶噸缃鍒嗙姸鎬侊紝鍏佽鏂颁换鍔″姞鍒?
        st.session_state.s3_solution_text = ""  # <--- 鏂板锛氱敓鎴愭柊棰樻椂锛屾竻绌烘棫鐨勭瓟妗堣蹇嗭紒
        # --- AI瀵煎笀鐘舵€侀噸缃?---
        st.session_state.s3_tutor_history = []
        st.session_state.s3_tutor_feedback = ""
        st.session_state.s3_tutor_round = 0
        st.session_state.s3_show_final_answer = False
        st.session_state.s3_task_submitted = False
        st.session_state.s3_is_correct = False
        with st.spinner(f"姝ｅ湪鏋勫缓鍏充簬銆恵today_focus}銆戠殑鍗曠墖鏈哄疄楠屾柟妗?.."):
            # 璋冪敤 AI 鐢熸垚浠诲姟
            stream = st.session_state.ai_engine.generate_personalized_task(today_focus, level)
            # 鍏抽敭鐐癸細st.write_stream 浼氳繑鍥炲畬鏁寸殑鐢熸垚鏂囨湰锛屾垜浠皢瀹冨瓨鍏?session_state
            # 杩欐牱鐐瑰嚮"鏌ョ湅绛旀"鍒锋柊椤甸潰鍚庯紝棰樼洰鏂囧瓧鎵嶄笉浼氭秷澶?
            st.session_state.s3_task_text = st.write_stream(stream)

            # --- (鏂板) 鑷姩瀛樻。閫昏緫 ---
            timestamp = datetime.now().strftime("%H:%M")
            title = f"[{timestamp}] {today_focus}"

            # 2. 瀛樺叆鍒楄〃
            new_record = {"title": title, "content": st.session_state.s3_task_text, "level": level, "solution": ""}
            st.session_state.s3_chat_history_list.append(new_record)

            if "user_id" in st.session_state:
                save_conversation(
                    user_id=st.session_state.user_id,
                    module="s3",
                    title=title,
                    content=st.session_state.s3_task_text
                )





            # 3. 闄愬埗鍙瓨 10 鏉?(瓒呰繃灏辨妸鏈€鏃х殑鍒犳帀)
            if len(st.session_state.s3_chat_history_list) > 10:
                st.session_state.s3_chat_history_list.pop(0)

            # 4. 閲嶇疆鏌ョ湅鐘舵€佷负"褰撳墠"
            st.session_state.s3_active_history_index = None

    # 2. 璐熻矗鏄剧ず浠诲姟 (娣诲姞鍘嗗彶璁板綍鏌ョ湅閫昏緫)
    # 鍦烘櫙 A: 鐢ㄦ埛鐐瑰嚮浜嗕晶杈规爮鐨勫巻鍙茶褰?(鏌ョ湅鏃у瓨妗?
    if st.session_state.s3_active_history_index is not None:
        # 鏍规嵁绱㈠紩鍙栧嚭鍘嗗彶鏁版嵁
        record = st.session_state.s3_chat_history_list[st.session_state.s3_active_history_index]
        st.markdown(record["content"])
        st.markdown("---")

        # 鏄剧ず鍘嗗彶绛旀锛堝鏋滄湁锛?
        if record.get("solution"):
            st.subheader("馃摑 鍘嗗彶鍙傝€冪瓟妗堜笌瑙ｆ瀽")
            with st.chat_message("assistant", avatar="馃"):
                st.markdown(record["solution"])
            # 璁剧疆绛旀宸叉樉绀烘爣蹇?
            st.session_state.s3_show_answer = True
            st.session_state.s3_solution_text = record["solution"]

    # 2. 璐熻矗鏄剧ず浠诲姟 (鍙 session 閲屾湁棰樼洰锛屽氨涓€鐩存樉绀猴紝涓嶇鏄垰鐢熸垚鐨勮繕鏄埛鏂板悗鐨?
    elif "s3_task_text" in st.session_state and st.session_state.s3_task_text:
        with st.chat_message("assistant", avatar="馃"):
             st.markdown(st.session_state.s3_task_text)

    # 3. (鏂板) 榛樿鍒濆鍖栫姸鎬?- 鏄剧ず寮曞妗?
    else:
        with st.chat_message("assistant", avatar="馃"):
            st.markdown("""
                馃憢 **娆㈣繋鏉ュ埌瀹為獙闈跺満宸ュ潑锛?*

                杩欓噷鏄綘鐨?**涓撳睘鍗曠墖鏈哄疄璁敓鎴愬尯**銆?

                1. 鍦ㄤ笅鎷夊垪琛ㄤ腑閫夋嫨 **浠婃棩瀹為獙璇鹃**
                2. 鎷栧姩婊戝潡璋冩暣 **鎺屾彙绋嬪害**
                3. 鐐瑰嚮 **鐢熸垚浠诲姟鍗?*

                AI 瀵煎笀灏嗘牴鎹綘鐨勯€夋嫨锛岄噺韬畾鍒?**鐙竴鏃犱簩** 鐨勫疄鎴樼紪绋嬩换鍔′笌纭欢璋冭瘯鎸戞垬锛侌煄?
                """)

    # 3. 璐熻矗鏄剧ず"鏌ョ湅绛旀"鎸夐挳 (鍙湁瀛樺湪棰樼洰鏃舵墠鏄剧ず杩欎釜鎸夐挳)
    if ("s3_task_text" in st.session_state and st.session_state.s3_task_text) or \
            (st.session_state.s3_active_history_index is not None and
             st.session_state.s3_chat_history_list[st.session_state.s3_active_history_index].get("solution")):
        st.markdown("---")

# ====== S3 AI 瀵煎笀瀹￠槄鍖猴紙鏂板鍔熻兘锛?======

# 浠呭湪褰撳墠浠诲姟锛堥潪鍘嗗彶璁板綍锛夋椂鏄剧ずAI瀵煎笀瀹￠槄UI
if ("s3_task_text" in st.session_state and st.session_state.s3_task_text) and st.session_state.s3_active_history_index is None:
    # 鍒涘缓涓ゅ垪甯冨眬锛氫唬鐮佹彁浜ゅ尯 + 瀵硅瘽鍖?
    sub_col1, sub_col2 = st.columns([3, 2])

    with sub_col1:
        st.markdown("### 馃摑 鎻愪氦浣犵殑浠ｇ爜/鏂规")
        student_code = st.text_area(
            "鍦ㄦ绮樿创浣犵殑浠ｇ爜鎴栨柟妗堟弿杩?,
            height=200,
            placeholder="璇疯緭鍏ヤ綘鐨勪唬鐮佹垨瀹為獙鏂规...",
            key="s3_student_code_input"
        )

        # 鎻愪氦鎸夐挳
        submit_btn = st.button("馃 鎻愪氦缁橝I瀵煎笀瀹￠槄", type="primary", key="s3_submit_btn")

        if submit_btn and student_code.strip():
            # 淇濆瓨瀛︾敓鎻愪氦
            st.session_state.s3_tutor_history.append({
                "role": "student",
                "content": student_code
            })
            st.session_state.s3_task_submitted = True
            st.session_state.s3_tutor_round += 1

            # 璋冪敤AI瀵煎笀瀹￠槄
            with st.spinner("AI瀵煎笀姝ｅ湪瀹￠槄锛堢{}杞級...".format(st.session_state.s3_tutor_round)):
                with st.chat_message("assistant", avatar="馃"):
                    feedback_stream = st.session_state.ai_engine.review_student_submission(
                        st.session_state.s3_task_text,
                        student_code,
                        st.session_state.s3_tutor_history[:-1]
                    )
                    feedback_text = st.write_stream(feedback_stream)
                    st.session_state.s3_tutor_feedback = feedback_text
                    st.session_state.s3_tutor_history.append({
                        "role": "tutor",
                        "content": feedback_text
                    })

            # 妫€娴婣I鏄惁璁や负绛旀宸叉纭?
            if "浣犵殑鏂规宸插畬鍏ㄦ纭? in feedback_text or "宸插畬鍏ㄦ纭? in feedback_text:
                st.session_state.s3_is_correct = True

            st.rerun()

    with sub_col2:
        st.markdown("### 馃挰 AI瀵煎笀瀵硅瘽璁板綍")
        if len(st.session_state.s3_tutor_history) > 0:
            st.caption("宸茶凯浠?{} 杞?.format(st.session_state.s3_tutor_round))
            for i, msg in enumerate(st.session_state.s3_tutor_history):
                role_icon = "馃懁" if msg["role"] == "student" else "馃"
                role_name = "瀛︾敓" if msg["role"] == "student" else "AI瀵煎笀"
                with st.expander("{} {} - 绗瑊}杞?.format(role_icon, role_name, (i//2)+1), expanded=(i == len(st.session_state.s3_tutor_history)-1)):
                    content_preview = msg["content"][:200]
                    if len(msg["content"]) > 200:
                        content_preview += "..."
                    st.markdown(content_preview)
        else:
            st.info("馃憜 鍦ㄤ笂鏂规彁浜や綘鐨勪唬鐮侊紝AI瀵煎笀灏嗚繘琛屽闃呭拰鎸囧銆?)

    st.markdown("---")

    # 鏄剧ずAI瀵煎笀鐨勬渶鏂板弽棣堬紙濡傛灉鏈夛級
    if st.session_state.s3_tutor_feedback:
        st.subheader("馃 AI瀵煎笀鏈€鏂板弽棣?)
        with st.chat_message("assistant", avatar="馃"):
            st.markdown(st.session_state.s3_tutor_feedback)

    # 鏄剧ず"鏌ョ湅鏈€缁堢瓟妗?鎸夐挳
    if st.session_state.s3_task_submitted:
        if st.button("馃摉 鏌ョ湅鏈€缁堢瓟妗堜笌缁撹", key="s3_final_answer_btn"):
            st.session_state.s3_show_final_answer = True

    # 鏄剧ず鏈€缁堢瓟妗?
    if st.session_state.get("s3_show_final_answer", False):
        st.subheader("馃摉 鏈€缁堝弬鑰冪瓟妗堜笌缁撹")
        if st.session_state.s3_solution_text:
            with st.chat_message("assistant", avatar="馃"):
                st.markdown(st.session_state.s3_solution_text)
        else:
            with st.spinner("AI姝ｅ湪鐢熸垚鏈€缁堢瓟妗?.."):
                with st.chat_message("assistant", avatar="馃"):
                    ans_stream = st.session_state.ai_engine.generate_task_solution(
                        st.session_state.s3_task_text)
                    st.session_state.s3_solution_text = st.write_stream(ans_stream)

        # 鏇存柊鍘嗗彶璁板綍
        if st.session_state.s3_active_history_index is not None:
            st.session_state.s3_chat_history_list[st.session_state.s3_active_history_index]["solution"] = st.session_state.s3_solution_text
        elif len(st.session_state.s3_chat_history_list) > 0:
            st.session_state.s3_chat_history_list[-1]["solution"] = st.session_state.s3_solution_text

# ====== 鍙傝€冪瓟妗堟樉绀哄尯锛堥€氱敤锛屽巻鍙茶褰曚篃鏄剧ず锛?====

# 鏌ョ湅鍙傝€冪瓟妗堟寜閽紙鍘嗗彶璁板綍鎴栧綋鍓嶄换鍔￠兘鍙樉绀猴級
if ("s3_task_text" in st.session_state and st.session_state.s3_task_text) or \
        (st.session_state.s3_active_history_index is not None and
         st.session_state.s3_chat_history_list[st.session_state.s3_active_history_index].get("solution")):
    st.markdown("---")

    # 杩欐槸涓€涓紑鍏抽€昏緫锛氱偣鍑绘寜閽紝鎶婂紑鍏虫墦寮€
    if st.button("鉁?鏌ョ湅鏈€缁堝弬鑰冪瓟妗?):
        st.session_state.s3_show_answer = True

        # 闃叉閲嶅鐐瑰嚮鍒峰垎
        if not st.session_state.get("current_task_scored", False):
            if st.session_state.weekly_progress_count < 10:
                st.session_state.weekly_progress_count += 1
            st.session_state.current_task_scored = True
            st.rerun()

    # 鏄剧ず绛旀
    if st.session_state.get("s3_show_answer", False):
        st.subheader("馃摑 鏈€缁堝弬鑰冪瓟妗堜笌瑙ｆ瀽")
        # 宸茬粡鏈夊瓨涓嬫潵鐨勭瓟妗?
        if st.session_state.s3_solution_text:
            with st.chat_message("assistant", avatar="馃"):
                st.markdown(st.session_state.s3_solution_text)

            # 鏇存柊鍘嗗彶璁板綍涓殑绛旀
            if st.session_state.s3_active_history_index is not None:
                st.session_state.s3_chat_history_list[st.session_state.s3_active_history_index]["solution"] = st.session_state.s3_solution_text
        # 绗竴娆＄偣鏌ョ湅锛岀敓鎴愮瓟妗?
        else:
            with st.spinner("AI 姝ｅ湪鎾板啓瑙ｉ鎬濊矾..."):
                with st.chat_message("assistant", avatar="馃"):
                    ans_stream = st.session_state.ai_engine.generate_task_solution(
                        st.session_state.s3_task_text)
                    st.session_state.s3_solution_text = st.write_stream(ans_stream)

            # 鏇存柊鍘嗗彶璁板綍涓殑绛旀
            if st.session_state.s3_active_history_index is not None:
                st.session_state.s3_chat_history_list[st.session_state.s3_active_history_index]["solution"] = st.session_state.s3_solution_text
            elif len(st.session_state.s3_chat_history_list) > 0:
                st.session_state.s3_chat_history_list[-1]["solution"] = st.session_state.s3_solution_text
# ==================== 妯″潡涓夛細鍘熺悊娣卞害杩介棶 ====================
elif menu == "馃敩 鍘熺悊娣卞害杩介棶":
    st.header("馃敩 鍗曠墖鏈哄師鐞嗘繁搴﹁拷闂?| 鑻忔牸鎷夊簳寮忔暀瀛?)
    st.markdown("涓嶅啓浠ｇ爜锛屽彧鑱婂師鐞嗐€傜敤鑻忔牸鎷夊簳闂瓟娉曟楠屼綘瀵瑰崟鐗囨満鍘熺悊鐨勭悊瑙ｆ繁搴︺€?)

    concept = st.text_input("杈撳叆涓€涓浣犲洶鎯戠殑姒傚康", placeholder="渚嬪锛氬畾鏃跺櫒涓柇鏍囧織浣嶄负浠€涔堣杞欢娓呴櫎锛?)

    # 鍦烘櫙 A锛氱偣鍑绘寜閽敓鎴愭柊瀵硅瘽
    if st.button("寮€濮嬭拷闂?):
        if concept:
            with st.chat_message("assistant", avatar="馃"):
                stream = st.session_state.ai_engine.socratic_quiz(concept)
                # 閲嶇偣锛氬瓨鍏ヨ蹇?
                response_text = st.write_stream(stream)
                st.session_state.deep_inquiry_history = response_text

            # --- (鏂板) 鑷姩瀛樻。閫昏緫 ---
            timestamp = datetime.now().strftime("%H:%M")
            title = f"[{timestamp}] {concept}"

            # 瀛樺叆鍒楄〃
            new_record = {"title": title, "content": response_text}
            st.session_state.inquiry_chat_history_list.append(new_record)
#################################################################################
            if "user_id" in st.session_state:
                save_conversation(
                    user_id=st.session_state.user_id,
                    module="inquiry",
                    title=title,
                    content=response_text
                )
###################################################################################
            # 闄愬埗鍙瓨 10 鏉?(瓒呰繃灏辨妸鏈€鏃х殑鍒犳帀)
            if len(st.session_state.inquiry_chat_history_list) > 10:
                st.session_state.inquiry_chat_history_list.pop(0)

            # 閲嶇疆鏌ョ湅鐘舵€佷负"褰撳墠"
            st.session_state.inquiry_active_history_index = None
        else:
            st.error("璇疯緭鍏ユ蹇靛悕绉?)

    # 鍦烘櫙 B: 鐢ㄦ埛鐐瑰嚮浜嗕晶杈规爮鐨勫巻鍙茶褰?(鏌ョ湅鏃у瓨妗?
    elif st.session_state.inquiry_active_history_index is not None:
        # 鏍规嵁绱㈠紩鍙栧嚭鍘嗗彶鏁版嵁
        record = st.session_state.inquiry_chat_history_list[st.session_state.inquiry_active_history_index]

        with st.chat_message("assistant", avatar="馃"):
            # 鏄剧ず鏍囬鎻愮ず杩欐槸鍘嗗彶
            st.caption(f"馃搨 姝ｅ湪鏌ョ湅鍘嗗彶瀛樻。锛歿record['title']}")
            st.markdown(record["content"])

    # 鍦烘櫙 B锛氭病鐐规寜閽紝浣嗘湁鍘嗗彶璁板綍锛堝垏鎹㈤〉闈㈠洖鏉ョ殑鎯呭喌锛?
    elif st.session_state.deep_inquiry_history:
        with st.chat_message("assistant", avatar="馃"):
            st.markdown(st.session_state.deep_inquiry_history)
    # 鍦烘櫙 C (鏂板)锛氶粯璁ゅ垵濮嬪寲鐘舵€?
    # 褰撴病鏈夌偣鍑绘寜閽紝涓旀病鏈夊巻鍙茶褰曟椂锛屾樉绀轰竴涓櫧鑹茬殑绌哄洖绛旀锛堝紩瀵兼锛?
    else:
        with st.chat_message("assistant", avatar="馃"):
            # 杩欎釜妗嗘槸鐧借壊鐨勶紙鐢变箣鍓嶇殑CSS鍐冲畾锛夛紝涓旈珮搴︿細鏍规嵁鏂囧瓧鑷姩閫傚簲
            st.markdown("""
                馃憢 **浣犲ソ锛佹垜鏄綘鐨勫崟鐗囨満鍘熺悊瀵煎笀銆?*

                璇峰湪涓婃柟杈撳叆浣犳兂瑕佹繁鍏ョ悊瑙ｇ殑鍗曠墖鏈烘蹇碉紙濡?GPIO妯″紡銆佸畾鏃跺櫒鍘熺悊銆佷腑鏂搷搴旀祦绋嬬瓑锛夛紝
                鎴戜細鐢ㄨ嫃鏍兼媺搴曞紡鏁欏娉曞甫浣犱粠鍘熺悊灞傞潰鏀诲厠瀹冿紒馃殌
                """)

