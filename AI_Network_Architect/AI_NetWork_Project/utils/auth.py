import sqlite3
import hashlib
from utils.db_helper import get_db_path


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def register_user(username, password):
    try:
        conn = sqlite3.connect(get_db_path(), check_same_thread=False)
        c = conn.cursor()
        c.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)",
                  (username, hash_password(password)))
        conn.commit()
        conn.close()
        return True, "注册成功！请登录"
    except sqlite3.IntegrityError:
        return False, "用户名已存在"


def authenticate_user(username, password):
    conn = sqlite3.connect(get_db_path(), check_same_thread=False)
    c = conn.cursor()
    c.execute("SELECT id FROM users WHERE username = ? AND password_hash = ?",
              (username, hash_password(password)))
    result = c.fetchone()
    conn.close()
    return result[0] if result else None
