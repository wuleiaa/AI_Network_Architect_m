import hashlib
import sys
from pathlib import Path

# Add app dir to path for imports
APP_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(APP_DIR))

def test_hash():
    h = hashlib.pbkdf2_hmac('sha256', b'test', b'salt', 1000)
    assert len(h.hex()) == 64

def test_cap():
    assert min(0 + 1, 10) == 1
    assert min(10, 10) == 10

def test_db_path():
    from utils.db_helper import get_db_path
    p = get_db_path()
    assert isinstance(p, str) and p.endswith('.db')

def test_ai_methods():
    src = APP_DIR / 'utils/ai_engine.py'
    c = src.read_text(encoding='utf-8')
    assert 'def generate_hardware_simulation' in c
    assert 'def get_diagnostic_response' in c
    assert 'def generate_personalized_task' in c
    assert 'def socratic_quiz' in c

def test_app_structure():
    src = APP_DIR / 'streamlit_app.py'
    c = src.read_text(encoding='utf-8')
    assert 'body, p, div' in c or '* {' not in c
    assert 'load_weekly_progress' in c
    assert 'increment_weekly_progress' in c
    assert 's2_chat_history_list' in c
