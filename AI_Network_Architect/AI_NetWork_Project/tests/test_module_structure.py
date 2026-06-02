import sys
import os

# Test that AI engine methods exist without importing openai
def test_module_methods():
    module_path = os.path.join(os.path.dirname(__file__), '..', 'utils', 'ai_engine.py')
    with open(module_path, 'r', encoding='utf-8') as f:
        content = f.read()
    # Check method signatures exist in the source
    assert 'def generate_hardware_simulation' in content
    assert 'def get_diagnostic_response' in content
    assert 'def generate_personalized_task' in content
    assert 'def generate_task_solution' in content
    assert 'def socratic_quiz' in content

def test_module_class_name():
    module_path = os.path.join(os.path.dirname(__file__), '..', 'utils', 'ai_engine.py')
    with open(module_path, 'r', encoding='utf-8') as f:
        content = f.read()
    assert 'class MCU_TutorAI' in content
