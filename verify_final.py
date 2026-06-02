python -c "import sys, io; sys.stdout=io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8'))
" 2>$null

# Check streamlit_app.py
Write-Host "=== streamlit_app.py ===" -ForegroundColor Cyan
Write-Host "--- Navigation Menu ---"
Select-String -Path "F:\porj_AI_NetWork_Project\AI_Network_Architect\AI_NetWork_Project\streamlit_app.py" -Pattern "功能导航" -Context 0,3 | ForEach-Object { $_.Line }

Write-Host "`n--- Sidebar History Section ---"
Select-String -Path "F:\porj_AI_NetWork_Project\AI_Network_Architect\AI_NetWork_Project\streamlit_app.py" -Pattern "elif menu.*故障|delete_menu.*故障" -Context 0,1 | ForEach-Object { $_.Line }

Write-Host "`n--- Main Module Section ---"
Select-String -Path "F:\porj_AI_NetWork_Project\AI_Network_Architect\AI_NetWork_Project\streamlit_app.py" -Pattern "模块三|st.header|st.markdown|concept =|st.text_input|st.button.*开始|st.error|你好.*导师|故障诊断导师|问题根源" | Where-Object { $_.Line -match "🔬|实验故障|苏格拉底|开始诊断|实验问题|问题根源|st.header|st.markdown" } | Select-Object -First 15 | ForEach-Object { $_.Line }

Write-Host "`n--- Check for remaining old text ---"
$remaining = Select-String -Path "F:\porj_AI_NetWork_Project\AI_Network_Architect\AI_NetWork_Project\streamlit_app.py" -Pattern "原理深度追问|不写代码，只聊原理|输入一个让你困惑的概念|开始追问|请输入概念名称"
if ($remaining) {
    Write-Host "WARNING: Found old text!" -ForegroundColor Red
    $remaining | ForEach-Object { $_.Line }
} else {
    Write-Host "No old text remaining!" -ForegroundColor Green
}

Write-Host "`n=== ai_engine.py ===" -ForegroundColor Cyan
Select-String -Path "F:\porj_AI_NetWork_Project\AI_Network_Architect\AI_NetWork_Project\utils\ai_engine.py" -Pattern "def socratic_quiz|不要直接给出答案|苏格拉底式诊断|通过提问引导学生|实验问题" -Context 0,2 | ForEach-Object { $_.Line }
