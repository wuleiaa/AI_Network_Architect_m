import pathlib, re

P = "F:/porj_AI_NetWork_Project/AI_Network_Architect/AI_NetWork_Project"
bak = pathlib.Path(f"{P}/streamlit_app.py.bak")
content = bak.read_text("utf-8")
lines = content.split("\n")

# === Build new file line by line ===
out = []
# Lines 1-16: replace with new imports
new_imports = [
    'import os',
    'for proxy_var in ["HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy", "OPENAI_PROXY"]:',
    '    if proxy_var in os.environ:',
    '        del os.environ[proxy_var]',
    '',
    '',
    'from utils.db_helper import get_db_path',
    'import streamlit as st',
    'from utils.ai_engine import NetworkArchitectAI',
    'from utils.constants import MAX_HISTORY',
    'from utils.auth import register_user, authenticate_user',
    'from utils.db_ops import init_db, load_user_conversations, save_conversation',
    'from datetime import datetime',
    'from pathlib import Path',
    '',
    '',
    'init_db()',
    '',
]
out.extend(new_imports)

# Line 17-18: blank lines (skip)
# Lines 19-50: init_db function and comment (skip, already replaced by new imports)
# Lines 51-52: blank line and comment for init call (keep init_db() call at line 50 in new)
# Lines 53-97: auth functions (skip entirely)
# Lines 98-122: load_user_conversations, save_conversation (skip entirely)
# Line 123+: Keep everything until page_config area

# Find page config line (line 125, 0-indexed 124)
page_config_idx = None
for i, l in enumerate(lines):
    if l.strip() == "# 1. 页面配置":
        page_config_idx = i
        break

# Add page config through line before CSS (lines 125-138)
for i in range(page_config_idx, 138):
    l = lines[i]
    if l.strip() in ("# 1. 页面配置", ""):
        continue  # skip these
    out.append(l)

# Lines 139-240: CSS block - skip and replace
out.append("")
out.append("")
out.append('st.html(Path("assets/style.css").read_text())')
out.append("")

# Lines 241+: env checks and everything after CSS
for i in range(240, len(lines)):
    l = lines[i]
    stripped = l.strip()
    
    # Skip Chinese section comments
    if re.match(r"^# ====== .+ ======$", stripped):
        continue
    if re.match(r"^# ========== .+ ==========$", stripped):
        continue
    
    # Skip "新增" type headers
    if "新增：" in stripped:
        continue
    
    # Skip specific Chinese-only debug comments (not SQL docs)
    if stripped in ("# 创建数据库连接函数",):
        continue
    
    # Skip weekly_progress_count init
    if stripped == 'if "weekly_progress_count" not in st.session_state:':
        i += 1  # also skip the next line (initialization)
        continue
    
    # Skip weekly_progress sidebar usage  
    if "current_count = st.session_state.weekly_progress_count" in stripped:
        while i+1 < len(lines):
            i += 1
            if "再完成" in lines[i]:
                break
        continue
    
    # Skip weekly_progress increment
    if "weekly_progress_count < 10" in stripped:
        i += 1
        continue
    
    # Skip Chinese-only comment lines
    if re.match(r"^\s*#.*[\u4e00-\u9fff]", stripped) and not re.search(r"[a-zA-Z]{3,}", stripped):
        continue
    
    # Clean inline Chinese tail comments
    cleaned = re.sub(r"\s*#.*[\u4e00-\u9fff].*$", "", stripped).rstrip()
    if cleaned != stripped:
        if cleaned:
            out.append(cleaned)
        continue
    
    out.append(l)

result = "\n".join(out)
pathlib.Path(f"{P}/streamlit_app.py").write_text(result, "utf-8")
print(f"Done: {len(lines)} -> {len(out)} lines")
