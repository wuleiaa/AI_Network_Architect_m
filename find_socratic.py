import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

filepath = r"F:\porj_AI_NetWork_Project\AI_Network_Architect\AI_NetWork_Project\utils\ai_engine.py"

with open(filepath, "r", encoding="utf-8") as f:
    lines = f.readlines()

# Find the socratic_quiz method
start_idx = None
end_idx = None
for i, line in enumerate(lines):
    if "def socratic_quiz" in line:
        start_idx = i
    if start_idx is not None and i > start_idx:
        # Find the next method definition (starting at column 0)
        if line.startswith("    def ") or (line.startswith("def ") and i > start_idx + 1):
            end_idx = i
            break

if end_idx is None:
    end_idx = len(lines)

print(f"socratic_quiz method: lines {start_idx+1} to {end_idx}")
print("---OLD METHOD---")
for line in lines[start_idx:end_idx]:
    print(line, end="")
print("---END---")
