import pathlib, re

P = "F:/porj_AI_NetWork_Project/AI_Network_Architect/AI_NetWork_Project"
p = pathlib.Path(f"{P}/streamlit_app.py")
content = p.read_text("utf-8")
lines = content.split("\n")

out = []
skip_until = -1

for i, l in enumerate(lines):
    if i <= skip_until:
        continue
    
    stripped = l.strip()
    
    # Remove CSS comment header
    if "CSS 样式注入" in stripped:
        continue
    
    # Remove weekly_progress init leftover
    if stripped == "st.session_state.weekly_progress_count = 0":
        continue
    
    # Remove weekly_progress sidebar display block
    if "current_count = st.session_state.weekly_progress_count" in stripped:
        # Skip until "再完成" line
        for j in range(i+1, len(lines)):
            skip_until = j
            if "再完成" in lines[j] or "caption" in lines[j] and "10" in lines[j]:
                skip_until = j
                break
        continue
    
    # Remove any remaining weekly_progress increment
    if "weekly_progress_count < 10" in stripped or "weekly_progress_count += 1" in stripped:
        continue
    
    # Remove st.progress that uses progress_percent
    if "st.progress(progress_percent" in stripped:
        continue
    
    # Remove progress_percent HTML references  
    if "progress_percent" in stripped:
        continue
    
    # Replace direct sqlite3 connections in delete mode
    # These should use the db_ops delete function if available, 
    # but for now just remove the sqlite3 calls and add a note
    if "sqlite3.connect" in stripped and ("get_db_path" in stripped or "netarchitect.db" in stripped):
        # Skip the entire DB operation block
        # Look for the pattern: conn = ... c = conn.cursor() ... c.execute ... conn.commit ... conn.close
        depth = 0
        for j in range(i, min(i+10, len(lines))):
            skip_until = j
            if "conn.close()" in lines[j]:
                break
        # Also remove the indented c.execute lines that follow
        continue
    
    # Remove "progress_percent" variable assignments
    if stripped.startswith("progress_percent"):
        continue
    
    out.append(l)

result = "\n".join(out)
p.write_text(result, "utf-8")
print(f"Done: {len(lines)} -> {len(out)} lines")
