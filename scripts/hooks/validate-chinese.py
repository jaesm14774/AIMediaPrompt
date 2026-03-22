"""
Claude Code Hook: Validate Traditional Chinese
Triggers on Write/Edit for .md files in Post/, Prompt/, Test/
Blocks if simplified Chinese characters are detected.
"""

import json
import sys
import re

# Curated set of simplified Chinese characters that differ from Traditional
# These are common characters that indicate simplified Chinese usage
SIMPLIFIED_CHARS = set(
    "关键执确产优这还个们进认为么来对时从种让说开场该准"
    "发现问题据标记护创点类动强调术应选择连结构图辑"
    "与运设计处组织环节达标签过滤频导间线显缩编输"
    "变换转义节约龙华带团内备复杂质数学仅链语阶"
    "异战当声闻长门"
)


def has_simplified_chinese(text: str) -> list[str]:
    """Return list of simplified Chinese characters found in text."""
    found = []
    for char in text:
        if char in SIMPLIFIED_CHARS:
            found.append(char)
    return list(set(found))


def main():
    hook_input = json.loads(sys.stdin.read())
    tool_name = hook_input.get("tool_name", "")
    tool_input = hook_input.get("tool_input", {})

    # Only check Write and Edit tools
    if tool_name not in ("Write", "Edit"):
        print(json.dumps({"decision": "approve"}))
        return

    # Get file path
    file_path = tool_input.get("file_path", "")

    # Only check .md files in Post/, Prompt/, Test/
    if not file_path.endswith(".md"):
        print(json.dumps({"decision": "approve"}))
        return

    # Normalize path separators for matching
    normalized = file_path.replace("\\", "/")
    target_dirs = ("/Post/", "/Prompt/", "/Test/")
    if not any(d in normalized for d in target_dirs):
        print(json.dumps({"decision": "approve"}))
        return

    # Get content to check
    content = ""
    if tool_name == "Write":
        content = tool_input.get("content", "")
    elif tool_name == "Edit":
        content = tool_input.get("new_string", "")

    if not content:
        print(json.dumps({"decision": "approve"}))
        return

    simplified_found = has_simplified_chinese(content)
    if simplified_found:
        chars_display = "、".join(simplified_found[:10])
        print(json.dumps({
            "decision": "block",
            "reason": f"Simplified Chinese detected: {chars_display}. All content must use Traditional Chinese (繁體中文)."
        }))
    else:
        print(json.dumps({"decision": "approve"}))


if __name__ == "__main__":
    main()
