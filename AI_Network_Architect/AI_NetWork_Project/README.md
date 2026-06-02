# MCU-Tutor - 单片机实验AI导师引擎

基于 Streamlit 的 **单片机实验AI导师引擎**。支持代码智能诊疗、自适应实验靶场、原理深度追问三大模块。

## 🚀 部署到 Streamlit Cloud

### 前提条件
- GitHub 账号
- DeepSeek API Key

### 部署步骤

#### 1. 推送代码到 GitHub
```bash
git remote add origin git@github.com:你的用户名/mcu-tutor.git
git add .
git commit -m "initial commit"
git push -u origin main
```

#### 2. 在 Streamlit Cloud 部署
1. 打开 https://share.streamlit.io
2. 点击 "Create app" → "From existing repo"
3. 选择仓库，Branch: main, Main file: streamlit_app.py
4. 点击 "Advanced settings..."

#### 3. 配置 Secrets
在 Streamlit Cloud 的 "Secrets" 部分粘贴：
```toml
AI_API_KEY = "sk-你的DeepSeek API密钥"
AI_BASE_URL = "https://api.deepseek.com/v1"
```

#### 4. 点击 Deploy，等待 1-2 分钟

### 本地开发
```bash
pip install -r requirements.txt
cp .env.example .env
# 编辑 .env 填入 API Key
streamlit run streamlit_app.py
```
