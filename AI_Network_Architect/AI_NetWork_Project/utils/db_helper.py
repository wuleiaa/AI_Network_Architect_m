import os
import sqlite3
from pathlib import Path

def get_db_path():
    """智能判断运行环境"""
    if os.getenv("STREAMLIT_CLOUD"):
        return "/mount/src/netarchitect/netarchitect.db"
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
        salt TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    # 对话历史表（统一存储三个模块）
    c.execute('''CREATE TABLE IF NOT EXISTS conversations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        module TEXT NOT NULL,  -- 's1', 's3', 'inquiry'
        title TEXT NOT NULL,
        content TEXT NOT NULL,
        solution TEXT,         -- 仅s3需要
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
    # 兼容旧数据库迁移：补充 salt 列
    try:
        c.execute("ALTER TABLE users ADD COLUMN salt TEXT DEFAULT ''")
        conn.commit()
    except sqlite3.OperationalError:
        pass
    conn.close()
    return conn
