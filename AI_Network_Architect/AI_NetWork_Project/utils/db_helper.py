import os
import sqlite3
from pathlib import Path

def get_db_path():
    """智能判断运行环境：云端使用项目目录，本地使用当前目录"""
    if os.getenv("STREAMLIT_CLOUD"):
        mount_base = os.getenv("STREAMLIT_MOUNT", "/mount/src/ai_network_architect_m")
        db_dir = os.path.join(mount_base, "AI_Network_Architect", "AI_NetWork_Project")
        os.makedirs(db_dir, exist_ok=True)
        return os.path.join(db_dir, "netarchitect.db")
    return "netarchitect.db"

def init_db():
    """统一数据库初始化：创建表结构（幂等）"""
    db_path = get_db_path()
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path, check_same_thread=False)
    c = conn.cursor()

    # 用户表
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        salt TEXT DEFAULT "",
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    # 对话历史表（统一存储三个模块）
    c.execute('''CREATE TABLE IF NOT EXISTS conversations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        module TEXT NOT NULL,
        title TEXT NOT NULL,
        content TEXT NOT NULL,
        solution TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )''')

    # 周进度表
    c.execute('''CREATE TABLE IF NOT EXISTS weekly_progress (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        week_start DATE NOT NULL,
        count INTEGER DEFAULT 0,
        UNIQUE(user_id, week_start),
        FOREIGN KEY (user_id) REFERENCES users(id)
    )''')

    conn.commit()
    try:
        c.execute("ALTER TABLE users ADD COLUMN salt TEXT DEFAULT ''")
        conn.commit()
    except sqlite3.OperationalError:
        pass
    conn.close()
    return conn