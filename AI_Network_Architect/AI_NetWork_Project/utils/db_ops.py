import sqlite3
from utils.db_helper import get_db_path


def init_db():
    conn = sqlite3.connect(get_db_path(), check_same_thread=False)
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

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

    conn.commit()
    conn.close()


def load_user_conversations(user_id):
    conn = sqlite3.connect(get_db_path(), check_same_thread=False)
    c = conn.cursor()

    c.execute(
        "SELECT id, title, content FROM conversations WHERE user_id = ? AND module = 's1' ORDER BY created_at DESC LIMIT 10",
        (user_id,))
    s1_list = [{"id": row[0], "title": row[1], "content": row[2]} for row in c.fetchall()]

    c.execute(
        "SELECT id, title, content, solution FROM conversations WHERE user_id = ? AND module = 's3' ORDER BY created_at DESC LIMIT 10",
        (user_id,))
    s3_list = [{"id": row[0], "title": row[1], "content": row[2], "solution": row[3] or ""} for row in c.fetchall()]

    c.execute(
        "SELECT id, title, content FROM conversations WHERE user_id = ? AND module = 'inquiry' ORDER BY created_at DESC LIMIT 10",
        (user_id,))
    inquiry_list = [{"id": row[0], "title": row[1], "content": row[2]} for row in c.fetchall()]

    conn.close()
    return s1_list, s3_list, inquiry_list


def save_conversation(user_id, module, title, content, solution=None):
    conn = sqlite3.connect(get_db_path(), check_same_thread=False)
    c = conn.cursor()
    c.execute("INSERT INTO conversations (user_id, module, title, content, solution) VALUES (?, ?, ?, ?, ?)",
              (user_id, module, title, content, solution))
    conversation_id = c.lastrowid
    conn.commit()
    conn.close()
    return conversation_id


def delete_conversation(user_id, module, conversation_id=None, title=None):
    conn = sqlite3.connect(get_db_path(), check_same_thread=False)
    c = conn.cursor()
    if conversation_id is not None:
        c.execute("DELETE FROM conversations WHERE id = ? AND user_id = ?",
                  (conversation_id, user_id))
    else:
        c.execute("DELETE FROM conversations WHERE user_id = ? AND module = ? AND title = ?",
                  (user_id, module, title))
    conn.commit()
    conn.close()
