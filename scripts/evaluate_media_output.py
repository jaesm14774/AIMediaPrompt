#!/usr/bin/env python3
"""
成品品質評估器 / Media Output Evaluator

用 Gemini 直接評估實際生成出的圖片或影片，而不是只評估 prompt 文字。
Evaluate generated images or videos with a structured rubric instead of
grading only the prompt template.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Iterable

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = PROJECT_ROOT / "config" / "gemini_config.json"

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}
VIDEO_EXTENSIONS = {".mp4", ".mov", ".webm"}
DEFAULT_MODEL = "gemini-3-flash-preview"

RUBRIC = {
    "subject_clarity": "主體是否一眼可辨識，是否有清楚焦點。"
    " / Whether the main subject is immediately readable and visually dominant.",
    "composition": "構圖是否有層次、視線引導與畫面張力。"
    " / Whether composition has hierarchy, eye guidance, and tension.",
    "emotional_impact": "情緒是否明確，是否有停留感與故事感。"
    " / Whether the scene carries strong emotion and narrative pull.",
    "technical_quality": "是否出現 AI 常見瑕疵、變形、混亂細節或不自然文字。"
    " / Whether the output avoids common AI artifacts and incoherent details.",
    "social_thumbstop": "是否適合社群首屏停留，是否有足夠吸睛度。"
    " / Whether the output is strong enough to stop scrolling on social media.",
}


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
        from google.genai import types

        return genai, types
    except ImportError as exc:
        raise SystemExit(
            "缺少依賴：請先安裝 `google-genai`。\n"
            "Missing dependency: install `google-genai` first."
        ) from exc


def collect_targets(path: Path) -> list[Path]:
    if path.is_file():
        return [path]

    targets = []
    for candidate in sorted(path.iterdir()):
        if candidate.suffix.lower() in IMAGE_EXTENSIONS | VIDEO_EXTENSIONS:
            targets.append(candidate)
    return targets


def ensure_ffmpeg() -> str | None:
    return shutil.which("ffmpeg")


def extract_video_frames(video_path: Path, frame_count: int) -> list[Path]:
    ffmpeg = ensure_ffmpeg()
    if not ffmpeg:
        raise SystemExit(
            "找不到 ffmpeg，無法評估影片。請先安裝 ffmpeg 或改為評估圖片。\n"
            "ffmpeg was not found, so video evaluation is unavailable."
        )

    temp_dir = Path(tempfile.mkdtemp(prefix="aimedia-eval-"))
    output_pattern = temp_dir / "frame_%02d.jpg"
    command = [
        ffmpeg,
        "-i",
        str(video_path),
        "-vf",
        f"fps={frame_count}/8",
        "-frames:v",
        str(frame_count),
        str(output_pattern),
        "-y",
    ]
    subprocess.run(command, check=True, capture_output=True)
    return sorted(temp_dir.glob("frame_*.jpg"))


def build_prompt(media_type: str, prompt_context: str | None, file_name: str) -> str:
    context_block = (
        f"\n原始創作上下文 / Original prompt context:\n{prompt_context.strip()}\n"
        if prompt_context
        else ""
    )
    rubric_lines = "\n".join(
        f"- {key}: {description}" for key, description in RUBRIC.items()
    )
    return (
        "你是嚴格的 AI 視覺總監。請只輸出 JSON，不要加上 Markdown 或額外說明。\n"
        "You are a strict AI visual director. Return JSON only.\n\n"
        f"檔名 / File: {file_name}\n"
        f"媒體類型 / Media type: {media_type}\n"
        f"{context_block}"
        "請根據以下 rubric 給分，每項 0-10，可有小數：\n"
        "Score each rubric item from 0-10 with decimals allowed.\n"
        f"{rubric_lines}\n\n"
        "請輸出這個 JSON 結構：\n"
        "{\n"
        '  "overall_score": number,\n'
        '  "grade": "S|A|B|C|D",\n'
        '  "subscores": {\n'
        '    "subject_clarity": number,\n'
        '    "composition": number,\n'
        '    "emotional_impact": number,\n'
        '    "technical_quality": number,\n'
        '    "social_thumbstop": number\n'
        "  },\n"
        '  "strengths": ["..."],\n'
        '  "issues": ["..."],\n'
        '  "improvement_actions": ["..."],\n'
        '  "reuse_components": ["適合保留的元件 / reusable prompt modules"],\n'
        '  "reject_components": ["應避免再用的元件 / modules to avoid"],\n'
        '  "summary_zh": "繁體中文一句話總結",\n'
        '  "summary_en": "One-sentence English summary"\n'
        "}\n"
        "評分標準：9.0 以上才算 S 級。\n"
        "Grading rule: only 9.0+ qualifies as S-grade."
    )


def _normalize_json_response(text: str) -> str:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        cleaned = cleaned.replace("json", "", 1).strip()
    return cleaned


def _read_text_response(response) -> str:
    if hasattr(response, "text") and response.text:
        return response.text

    texts: list[str] = []
    for candidate in getattr(response, "candidates", []) or []:
        content = getattr(candidate, "content", None)
        parts = getattr(content, "parts", []) if content else []
        for part in parts:
            text = getattr(part, "text", None)
            if text:
                texts.append(text)
    return "\n".join(texts)


def evaluate_with_gemini(
    file_path: Path,
    prompt_context: str | None,
    model: str,
    frame_count: int,
) -> dict:
    api_key = load_api_key()
    if not api_key:
        raise SystemExit(
            "缺少 Gemini API 金鑰，請設定 `GEMINI_API_KEY` 或 `config/gemini_config.json`。\n"
            "Gemini API key is required for media evaluation."
        )

    genai, types = import_genai()
    client = genai.Client(api_key=api_key)

    parts: list = [build_prompt(_media_type(file_path), prompt_context, file_path.name)]
    cleanup_paths: list[Path] = []

    if file_path.suffix.lower() in IMAGE_EXTENSIONS:
        parts.append(types.Part.from_bytes(data=file_path.read_bytes(), mime_type=_mime_type(file_path)))
    else:
        frames = extract_video_frames(file_path, frame_count)
        cleanup_paths.extend(frames)
        parts.append(
            "這是影片抽出的代表影格，請綜合判斷角色一致性、敘事連續性與畫面品質。"
            " / These are representative frames sampled from the video."
        )
        for frame in frames:
            parts.append(types.Part.from_bytes(data=frame.read_bytes(), mime_type="image/jpeg"))

    response = client.models.generate_content(
        model=model,
        contents=parts,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.2,
        ),
    )

    raw_text = _normalize_json_response(_read_text_response(response))
    payload = json.loads(raw_text)
    payload["file"] = str(file_path.relative_to(PROJECT_ROOT))

    for frame in cleanup_paths:
        try:
            frame.unlink()
        except OSError:
            pass
    temp_dir = cleanup_paths[0].parent if cleanup_paths else None
    if temp_dir and temp_dir.exists():
        try:
            temp_dir.rmdir()
        except OSError:
            pass

    return payload


def _media_type(file_path: Path) -> str:
    return "image" if file_path.suffix.lower() in IMAGE_EXTENSIONS else "video"


def _mime_type(file_path: Path) -> str:
    return {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".webp": "image/webp",
        ".mp4": "video/mp4",
        ".mov": "video/quicktime",
        ".webm": "video/webm",
    }[file_path.suffix.lower()]


def load_prompt_context(path: str | None) -> str | None:
    if not path:
        return None
    prompt_path = Path(path)
    if not prompt_path.is_absolute():
        prompt_path = PROJECT_ROOT / prompt_path
    return prompt_path.read_text(encoding="utf-8")


def save_report(target_root: Path, results: Iterable[dict]) -> Path:
    report_dir = PROJECT_ROOT / "logs" / "media_evaluations"
    report_dir.mkdir(parents=True, exist_ok=True)
    safe_name = target_root.stem if target_root.is_file() else target_root.name
    output_path = report_dir / f"{safe_name}-evaluation.json"
    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(list(results), file, ensure_ascii=False, indent=2)
    return output_path


def print_summary(results: list[dict], report_path: Path) -> None:
    print("=" * 72)
    print("成品評估摘要 / Media Evaluation Summary")
    print("=" * 72)
    for result in results:
        print(
            f"- {result['file']}: {result['overall_score']:.1f}/10 "
            f"({result['grade']})"
        )
        print(f"  摘要 / Summary: {result['summary_zh']}")
        if result.get("issues"):
            print(f"  主要問題 / Top issues: {', '.join(result['issues'][:2])}")
    print("-" * 72)
    print(f"報告已輸出 / Report saved: {report_path.relative_to(PROJECT_ROOT)}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="評估實際生成出的圖片或影片成品質量。"
        " / Evaluate generated media outputs.",
    )
    parser.add_argument(
        "target",
        help="單一檔案或資料夾。 / Single file or directory to evaluate.",
    )
    parser.add_argument(
        "--prompt-file",
        help="可選的 prompt/template 檔案，提供評估上下文。"
        " / Optional prompt/template file for context.",
    )
    parser.add_argument(
        "--model",
        default=DEFAULT_MODEL,
        help=f"Gemini 模型名稱，預設 {DEFAULT_MODEL}。",
    )
    parser.add_argument(
        "--frame-count",
        type=int,
        default=3,
        help="影片評估時抽取的代表影格數，預設 3。 / Video frame samples.",
    )
    args = parser.parse_args()

    target_path = Path(args.target)
    if not target_path.is_absolute():
        target_path = PROJECT_ROOT / target_path
    if not target_path.exists():
        print(f"找不到目標 / Target not found: {target_path}")
        return 1

    prompt_context = load_prompt_context(args.prompt_file)
    files = collect_targets(target_path)
    if not files:
        print("沒有可評估的媒體檔案。 / No media files found to evaluate.")
        return 1

    results = [
        evaluate_with_gemini(file_path, prompt_context, args.model, args.frame_count)
        for file_path in files
    ]
    report_path = save_report(target_path, results)
    print_summary(results, report_path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
