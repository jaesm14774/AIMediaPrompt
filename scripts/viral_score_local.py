#!/usr/bin/env python3
"""
Viral Score (local runner)

為了讓 full-pipeline 在本機可完全自動化，提供一個可用 CLI 執行的 viral-score 評估器，
評估對象是 Post 成品（Markdown），可選擇附帶一張圖片做視覺衝擊力加權判斷。

規格來源：.claude/skills/viral-score/skill.md
S 級硬門檻：
- overall_score >= 9.0
- copy_hook >= 9.0
- visual_impact >= 8.5
- shareability >= 9.0
並且不得出現核心保留意見（會滑過、只適合粉絲、只有可愛…）
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_MODEL = "gemini-2.5-flash"


def load_api_key() -> str:
    key = os.environ.get("GEMINI_API_KEY", "").strip()
    if key:
        return key
    config_path = PROJECT_ROOT / "config" / "gemini_config.json"
    if config_path.exists():
        try:
            data = json.loads(config_path.read_text(encoding="utf-8"))
            return str(data.get("api_key", "")).strip()
        except Exception:
            return ""
    return ""


def import_genai():
    try:
        from google import genai
        from google.genai import types

        return genai, types
    except ImportError as exc:
        raise SystemExit("缺少依賴：請先安裝 google-genai（pip install google-genai）。") from exc


def read_post(post_path: Path) -> str:
    if not post_path.exists():
        raise SystemExit(f"找不到 Post 檔案：{post_path}")
    return post_path.read_text(encoding="utf-8")


def extract_json_loose(text: str) -> dict[str, Any]:
    """
    Gemini 偶爾會多輸出前後文字；這裡做容錯：
    - 優先找第一個 {...} 區塊
    - 再嘗試 json.loads
    """
    text = text.strip()
    try:
        return json.loads(text)
    except Exception:
        pass

    m = re.search(r"\{[\s\S]*\}", text)
    if not m:
        raise ValueError("No JSON object found in model output.")
    return json.loads(m.group(0))


def build_prompt(platform: str, media_type: str, detailed: bool) -> str:
    detail_line = "請提供每個維度的 2-4 句理由與 1-3 條可行優化建議。" if detailed else "理由可簡短。"
    return (
        "你是嚴格的社群成長策略總監。請只輸出 JSON，不要加上 Markdown 或其他文字。\n"
        "You are a strict social growth strategist. Return JSON only.\n\n"
        f"目標平台 / Platform: {platform}\n"
        f"內容型態 / Type: {media_type}\n\n"
        "請依以下五大維度評分（0.0-10.0，允許一位小數），並計算加權總分：\n"
        "- copy_hook (25%): 文案鉤子力\n"
        "- visual_impact (20%): 視覺衝擊力（若提供圖片，需參考）\n"
        "- emotional_resonance (15%): 情感共鳴度\n"
        "- shareability (20%): 可分享性\n"
        "- platform_fit (20%): 平台適配度（含 hashtag 策略）\n\n"
        "木桶效應上限規則：\n"
        "- 任一維度 < 5.0 → overall_cap = 'C'\n"
        "- 任一維度 < 7.0 → overall_cap = 'A'\n"
        "- copy_hook < 7.0 → overall_cap = 'B'\n\n"
        "S 級硬門檻：\n"
        "- overall_score >= 9.0\n"
        "- copy_hook >= 9.0\n"
        "- visual_impact >= 8.5\n"
        "- shareability >= 9.0\n"
        "- must_not_have_reservations = true（不得出現『會滑過』『只適合粉絲』『只有可愛』等核心保留意見）\n\n"
        f"{detail_line}\n\n"
        "輸出 JSON 結構必須完全符合：\n"
        "{\n"
        '  "platform": "fb|ig|x",\n'
        '  "type": "image|video",\n'
        '  "scores": {\n'
        '    "copy_hook": 0.0,\n'
        '    "visual_impact": 0.0,\n'
        '    "emotional_resonance": 0.0,\n'
        '    "shareability": 0.0,\n'
        '    "platform_fit": 0.0\n'
        "  },\n"
        '  "weighted_score": 0.0,\n'
        '  "overall_cap": "S|A|B|C|D",\n'
        '  "final_grade": "S|A|B|C|D",\n'
        '  "passes_s_hard_gate": true,\n'
        '  "must_not_have_reservations": true,\n'
        '  "memory_point": "一句話說明最強記憶點 / the single strongest memory point",\n'
        '  "why_stop": "一句話說明為何會停滑 / why people stop scrolling",\n'
        '  "why_share": "一句話說明為何會想分享 / why people share",\n'
        '  "reservations": ["..."],\n'
        '  "top_improvements": ["..."]\n'
        "}\n"
    )


def calc_weighted(scores: dict[str, float]) -> float:
    return round(
        scores["copy_hook"] * 0.25
        + scores["visual_impact"] * 0.20
        + scores["emotional_resonance"] * 0.15
        + scores["shareability"] * 0.20
        + scores["platform_fit"] * 0.20,
        1,
    )


def apply_caps(scores: dict[str, float]) -> str:
    if any(v < 5.0 for v in scores.values()):
        return "C"
    if scores["copy_hook"] < 7.0:
        return "B"
    if any(v < 7.0 for v in scores.values()):
        return "A"
    return "S"


def grade_from_score(score: float) -> str:
    if score >= 9.0:
        return "S"
    if score >= 8.0:
        return "A"
    if score >= 7.0:
        return "B"
    if score >= 6.0:
        return "C"
    return "D"


def hard_gate_s(scores: dict[str, float], weighted: float, must_not_have_reservations: bool) -> bool:
    return (
        weighted >= 9.0
        and scores["copy_hook"] >= 9.0
        and scores["visual_impact"] >= 8.5
        and scores["shareability"] >= 9.0
        and must_not_have_reservations
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Viral Score (local) — evaluate Post markdown for virality")
    parser.add_argument("post", help="Post 檔案路徑（.md）")
    parser.add_argument("--image", help="可選：配圖路徑（用於視覺衝擊力判斷）")
    parser.add_argument("--type", choices=["image", "video"], default="image")
    parser.add_argument("--platform", choices=["fb", "ig", "x"], default="fb")
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--detailed", action="store_true")
    args = parser.parse_args()

    api_key = load_api_key()
    if not api_key:
        print("❌ 找不到 Gemini API Key（請設定 GEMINI_API_KEY 或 config/gemini_config.json）")
        return 2

    post_path = Path(args.post)
    if not post_path.is_absolute():
        post_path = PROJECT_ROOT / post_path

    image_path = None
    if args.image:
        image_path = Path(args.image)
        if not image_path.is_absolute():
            image_path = PROJECT_ROOT / image_path
        if not image_path.exists():
            print(f"⚠️  找不到 image：{image_path}（將以純文案評估）")
            image_path = None

    post_text = read_post(post_path)

    genai, types = import_genai()
    client = genai.Client(api_key=api_key)

    system_prompt = build_prompt(args.platform, args.type, args.detailed)
    contents: list[Any] = [system_prompt, "\n=== POST MARKDOWN START ===\n", post_text, "\n=== POST MARKDOWN END ===\n"]
    if image_path:
        mime = "image/png" if image_path.suffix.lower() == ".png" else "image/jpeg"
        contents.append(types.Part.from_bytes(data=image_path.read_bytes(), mime_type=mime))

    response = client.models.generate_content(
        model=args.model,
        contents=contents,
        config=types.GenerateContentConfig(
            temperature=0.2,
            response_mime_type="application/json",
        ),
    )

    raw = ""
    for cand in getattr(response, "candidates", []) or []:
        for part in getattr(cand, "content", None).parts or []:
            if getattr(part, "text", None):
                raw += part.text
    raw = raw.strip()

    try:
        payload = extract_json_loose(raw)
    except Exception as e:
        print("❌ 模型輸出無法解析為 JSON")
        print(str(e))
        print("---- raw ----")
        print(raw[:2000])
        return 1

    scores = payload.get("scores") or {}
    try:
        norm_scores = {
            "copy_hook": float(scores["copy_hook"]),
            "visual_impact": float(scores["visual_impact"]),
            "emotional_resonance": float(scores["emotional_resonance"]),
            "shareability": float(scores["shareability"]),
            "platform_fit": float(scores["platform_fit"]),
        }
    except Exception:
        print("❌ JSON scores 欄位不完整或格式錯誤")
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 1

    weighted = calc_weighted(norm_scores)
    cap = apply_caps(norm_scores)
    grade = grade_from_score(weighted)
    if cap == "C" and grade in ("S", "A", "B"):
        grade = "C"
    elif cap == "B" and grade in ("S", "A"):
        grade = "B"
    elif cap == "A" and grade == "S":
        grade = "A"

    reservations = payload.get("reservations", [])
    if not isinstance(reservations, list):
        reservations = [str(reservations)]
    # 只要有任何 reservations，就視為不符合「不得出現核心保留意見」的硬門檻
    must_not = bool(payload.get("must_not_have_reservations", False)) and len(reservations) == 0
    passes = hard_gate_s(norm_scores, weighted, must_not)

    result = {
        "platform": args.platform,
        "type": args.type,
        "scores": norm_scores,
        "weighted_score": weighted,
        "overall_cap": cap,
        "final_grade": "S" if passes else grade,
        "passes_s_hard_gate": passes,
        "must_not_have_reservations": must_not,
        "memory_point": payload.get("memory_point", ""),
        "why_stop": payload.get("why_stop", ""),
        "why_share": payload.get("why_share", ""),
        "reservations": reservations,
        "top_improvements": payload.get("top_improvements", []),
        "post_path": str(post_path.relative_to(PROJECT_ROOT)),
        "image_path": str(image_path.relative_to(PROJECT_ROOT)) if image_path else None,
        "model": args.model,
    }

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

