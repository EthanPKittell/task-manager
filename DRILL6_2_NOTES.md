'{"tool_name":"Write","tool_input":{"file_path":"C:\\AI_Agents_5300\\PA6\\task-manager\\utils\\errors.py"}}' | python .claude/hooks/guard_writes.py; $LASTEXITCODE
returned 0

To fix this I replaced is_blocked with a version that converts the path to project relative form:
def to_rel(file_path: str) -> str: