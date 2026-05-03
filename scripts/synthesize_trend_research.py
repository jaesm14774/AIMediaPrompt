#!/usr/bin/env python3
"""
爆量題材研究整理器 / Trend Research Synthesizer

把手動蒐集的爆量 Reel / Post 觀察整理成可執行研究簡報。
Turn manually collected viral-post observations into a structured brief.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import date
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = PROJECT_ROOT / "config" / "gemini_config.json"
DEFAULT_MODEL = "gemini-2.5-flash"


def load_api_key() -> str:
    key = os.environ.get("GEMINI_API_KEY", "").strip()
    if key:
        return key
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, "r", encoding="utf-8") as file:
            data = json.load(file)
        return data.get("api_key", "").strip()
    return ""


def import_genai():
    try:
        from google import genai

        return genai
    except ImportError as exc:
        raise SystemExit(
            "缺少依賴：請先安裝 `google-genai`。\n"
            "Missing dependency: install `google-genai` first."
        ) from exc


def build_prompt(keyword: str, source_text: str) -> str:
    return (
        "你是社群內容研究員。請將以下手動蒐集的爆量 Reel / Post 觀察，"
        "整理成可直接拿去產生 prompt 的研究簡報。\n"
        "You are a social content researcher. Convert the observations into an actionable brief.\n\n"
        f"研究主題 / Topic: {keyword}\n\n"
        "輸出要求：\n"
        "- 必須使用繁體中文在前、英文在後的雙語格式。\n"
        "- 不要空泛鼓勵，要具體指出可重用模式。\n"
        "- 請聚焦題材、視覺 hook、情緒機制、鏡頭語法、可改寫方向。\n"
        "- 最後請給 5 個可直接進入 prompt 開發的概念方向。\n\n"
        "請用以下 Markdown 結構輸出：\n"
        "# [主題] 爆量題材研究 / Viral Trend Research\n"
        "## 來源摘要 / Source Summary\n"
        "## 爆量共通點 / Shared Winning Patterns\n"
        "## 視覺 Hook / Visual Hooks\n"
        "## 情緒與敘事機制 / Emotional and Narrative Mechanics\n"
        "## 可回收 Prompt 元件 / Reusable Prompt Components\n"
        "## 應避免的低效做法 / Anti-Patterns\n"
        "## 可直接開發的 5 個概念 / Five Prompt-Ready Directions\n"
        "## 下一步 / Next Step\n\n"
        "以下是原始觀察：\n"
        f"{source_text.strip()}\n"
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="整理手動蒐集的爆量題材觀察。 / Synthesize trend research notes."
    )
    parser.add_argument("keyword", help="研究主題 / Research keyword")
    parser.add_argument(
        "--source",
        required=True,
        help="手動整理好的來源檔案（Markdown 或純文字）。 / Source notes file.",
    )
    parser.add_argument(
        "--model",
        default=DEFAULT_MODEL,
        help=f"Gemini 模型名稱，預設 {DEFAULT_MODEL}。",
    )
    args = parser.parse_args()

    source_path = Path(args.source)
    if not source_path.is_absolute():
        source_path = PROJECT_ROOT / source_path
    if not source_path.exists():
        print(f"找不到來源檔案 / Source file not found: {source_path}")
        return 1

    api_key = load_api_key()
    if not api_key:
        print(
            "缺少 Gemini API 金鑰，請設定 `GEMINI_API_KEY` 或 `config/gemini_config.json`。\n"
            "Gemini API key is required for research synthesis."
        )
        return 1

    genai = import_genai()
    client = genai.Client(api_key=api_key)
    prompt = build_prompt(args.keyword, source_path.read_text(encoding="utf-8"))
    response = client.models.generate_content(model=args.model, contents=prompt)
    content = response.text.strip()

    output_dir = PROJECT_ROOT / "research" / args.keyword
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{date.today().isoformat()}-viral-research.md"
    output_path.write_text(content, encoding="utf-8")

    print(f"研究完成 / Research brief created: {output_path.relative_to(PROJECT_ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
