"""
Claude Code Hook: Validate Post Filename Format
Triggers on Write for files in Post/ directory.
Blocks if filename doesn't match YYYY-MM-DD-[Name].md format.
"""

import json
import sys
import re
import os


def main():
    hook_input = json.loads(sys.stdin.read())
    tool_name = hook_input.get("tool_name", "")
    tool_input = hook_input.get("tool_input", {})

    # Only check Write tool (new file creation)
    if tool_name != "Write":
        print(json.dumps({"decision": "approve"}))
        return

    file_path = tool_input.get("file_path", "")
    if not file_path:
        print(json.dumps({"decision": "approve"}))
        return

    # Normalize path
    normalized = file_path.replace("\\", "/")

    # Only check .md files directly in Post/ or Post/Test/
    if "/Post/" not in normalized or not normalized.endswith(".md"):
        print(json.dumps({"decision": "approve"}))
        return

    # Extract filename
    filename = os.path.basename(file_path)

    # Validate format: YYYY-MM-DD-[Name].md
    pattern = r"^\d{4}-\d{2}-\d{2}-.+\.md$"
    if not re.match(pattern, filename):
        print(json.dumps({
            "decision": "block",
            "reason": f"Post filename '{filename}' must match format YYYY-MM-DD-[Name].md (e.g., 2026-01-07-Kirby-Office.md)"
        }))
    else:
        print(json.dumps({"decision": "approve"}))


if __name__ == "__main__":
    main()
