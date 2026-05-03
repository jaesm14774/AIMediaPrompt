#!/usr/bin/env python3
"""
Prompt 元件組裝器 / Prompt Component Assembler

把風格聖經與鏡頭語法拆成可組裝元件，輸出新的教學模板。
Compose a prompt template from reusable style-bible components.
"""

from __future__ import annotations

import argparse
import json
import random
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
LIBRARY_PATH = PROJECT_ROOT / "template_components" / "library.json"
DEFAULT_CHARACTER = "[IP角色]"


def load_library() -> dict:
    with open(LIBRARY_PATH, "r", encoding="utf-8") as file:
        return json.load(file)


def choose_entry(library: dict, category: str, key: str | None) -> dict:
    pool = library["components"][category]
    if key:
        for entry in pool:
            if entry["id"] == key:
                return entry
        raise SystemExit(f"找不到元件 / Unknown component: {category}.{key}")
    return random.choice(pool)


def build_template(
    title: str,
    media_type: str,
    character: str,
    components: dict[str, dict],
    research_note: str | None,
) -> str:
    scene = components["scene"]["prompt"]
    shot = components["shot"]["prompt"]
    lighting = components["lighting"]["prompt"]
    style = components["style"]["prompt"]
    emotion = components["emotion"]["prompt"]
    hook = components["hook"]["prompt"]
    motion = components["motion"]["prompt"] if media_type == "video" else None

    prompt_lines = [
        f"{hook}",
        f"{scene}",
        f"Main subject: {character}.",
        f"{shot}",
        f"{lighting}",
        f"{emotion}",
        f"{style}",
        "Avoid clutter, weak focal points, broken anatomy, and unreadable text.",
    ]
    if motion:
        prompt_lines.append(motion)
    if research_note:
        prompt_lines.append(f"Trend adaptation note: {research_note}")

    prompt_block = " ".join(prompt_lines)
    example_block = prompt_block.replace(character, "Kirby", 1)

    component_summary = "\n".join(
        f"- **{name}**: {entry['label_zh']} / {entry['label_en']}"
        for name, entry in components.items()
        if not (media_type == "image" and name == "motion")
    )

    notes = [
        "- 保留主體焦點與單一情緒，不要把所有亮點塞進同一張圖。"
        " / Preserve one clear focal point and one emotional read.",
        "- 先固定鏡頭語法，再替換題材與角色。"
        " / Lock the shot grammar first, then swap topic and character.",
        "- 若成品未達 S 級，優先調整構圖、主體比例、光線對比。"
        " / If output misses S-grade, fix composition, scale, and light contrast first.",
    ]

    return (
        f"# {title}\n\n"
        f"媒體類型 / Media Type: **{media_type}**\n\n"
        "## 元件配方 / Component Recipe\n\n"
        f"{component_summary}\n\n"
        "## Prompt Template\n\n"
        f"{prompt_block}\n\n"
        "## Example\n\n"
        f"{example_block}\n\n"
        "## 教學重點 / Teaching Notes\n\n"
        f"{chr(10).join(notes)}\n"
    )


def list_components(library: dict) -> None:
    print("可用元件 / Available components")
    for category, entries in library["components"].items():
        print(f"\n[{category}]")
        for entry in entries:
            print(f"- {entry['id']}: {entry['label_zh']} / {entry['label_en']}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="從可重用元件組裝新的 Prompt 模板。 / Assemble prompt templates.",
    )
    parser.add_argument("--name", required=False, help="模板名稱 / Template name")
    parser.add_argument(
        "--media-type",
        choices=["image", "video"],
        default="image",
        help="媒體類型 / Media type",
    )
    parser.add_argument(
        "--character",
        default=DEFAULT_CHARACTER,
        help="角色名稱，預設 [IP角色]。 / Character name.",
    )
    parser.add_argument("--scene", help="scene 元件 id")
    parser.add_argument("--shot", help="shot 元件 id")
    parser.add_argument("--lighting", help="lighting 元件 id")
    parser.add_argument("--style", help="style 元件 id")
    parser.add_argument("--emotion", help="emotion 元件 id")
    parser.add_argument("--hook", help="hook 元件 id")
    parser.add_argument("--motion", help="motion 元件 id，僅影片使用")
    parser.add_argument(
        "--research-note",
        help="將爆量題材洞察壓成一句，直接寫進 prompt。 / Trend research note.",
    )
    parser.add_argument(
        "--list-components",
        action="store_true",
        help="列出所有元件後離開。 / List available components.",
    )
    args = parser.parse_args()

    library = load_library()
    if args.list_components:
        list_components(library)
        return 0

    if not args.name:
        raise SystemExit("請提供 --name。 / Please provide --name.")

    components = {
        "scene": choose_entry(library, "scene", args.scene),
        "shot": choose_entry(library, "shot", args.shot),
        "lighting": choose_entry(library, "lighting", args.lighting),
        "style": choose_entry(library, "style", args.style),
        "emotion": choose_entry(library, "emotion", args.emotion),
        "hook": choose_entry(library, "hook", args.hook),
        "motion": choose_entry(library, "motion", args.motion or None),
    }

    content = build_template(
        title=args.name,
        media_type=args.media_type,
        character=args.character,
        components=components,
        research_note=args.research_note,
    )

    output_dir = PROJECT_ROOT / "Test"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{args.name}.md"
    output_path.write_text(content, encoding="utf-8")
    print(f"已建立模板 / Template created: {output_path.relative_to(PROJECT_ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
