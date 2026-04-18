#!/usr/bin/env python3
"""
使用 Gemini API 生成圖片或影片
- 圖片：gemini-3.1-flash-image-preview
- 影片：veo-3.1-lite-generate-preview（必須搭配 reference image）

需要安裝：pip install google-genai
API Key 來源（優先順序）：
  1. GEMINI_API_KEY 環境變數
  2. config/gemini_config.json 的 api_key 欄位
"""

import argparse
import base64
import json
import os
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

IMAGE_MODEL = "gemini-3.1-flash-image-preview"
VIDEO_MODEL = "veo-3.1-lite-generate-preview"
# VIDEO_MODEL = "veo-3.1-fast-generate-preview"

VIDEO_DURATION_SECONDS = 8  # 8s 最穩定，支援 reference_images

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}
VIDEO_EXTENSIONS = {".mp4", ".webm", ".mov"}


def load_api_key() -> str:
    """從環境變數或設定檔載入 API Key"""
    key = os.environ.get("GEMINI_API_KEY", "").strip()
    if key:
        return key

    config_file = PROJECT_ROOT / "config" / "gemini_config.json"
    if config_file.exists():
        try:
            with open(config_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            key = data.get("api_key", "").strip()
            if key:
                return key
        except Exception as e:
            print(f"⚠️  無法讀取 {config_file}: {e}")

    return ""


def generate_image(prompt: str, output_path: Path, api_key: str) -> bool:
    """使用 Gemini API 生成圖片"""
    try:
        from google import genai
        from google.genai import types
    except ImportError:
        print("❌ 請安裝 google-genai：pip install google-genai")
        return False

    try:
        client = genai.Client(api_key=api_key)
        print(f"🎨 呼叫 Gemini 圖片生成 API ({IMAGE_MODEL})...")
        print(f"   Prompt：{prompt[:80]}{'...' if len(prompt) > 80 else ''}")

        response = client.models.generate_content(
            model=IMAGE_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_modalities=["IMAGE", "TEXT"]
            ),
        )

        # 從 response 中提取圖片
        image_bytes = None
        for candidate in response.candidates:
            for part in candidate.content.parts:
                if hasattr(part, "inline_data") and part.inline_data is not None:
                    raw = part.inline_data.data
                    if isinstance(raw, str):
                        image_bytes = base64.b64decode(raw)
                    else:
                        image_bytes = raw
                    break
            if image_bytes:
                break

        if not image_bytes:
            print("❌ API 未回傳圖片資料")
            return False

        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_bytes(image_bytes)
        print(f"✅ 圖片已儲存：{output_path}")
        return True

    except Exception as e:
        print(f"❌ 圖片生成失敗：{e}")
        return False


def generate_video(
    prompt: str,
    output_path: Path,
    api_key: str,
    reference_image_path: Path,
    character_anchor_path: Path | None = None,
    duration_seconds: int = VIDEO_DURATION_SECONDS,
    aspect_ratio: str = "16:9",
) -> bool:
    """使用 Veo API 生成影片（以 reference image 為起始畫面）

    character_anchor_path: 角色錨點圖（通常是 scene_01.png），作為 asset reference
                           確保角色外觀全片一致。與 reference_image_path 不同：
                           reference_image_path = 前幕中段幀（決定畫面起始狀態）
                           character_anchor_path = 初始角色圖（鎖定角色外觀）
    duration_seconds:      8（最穩定，必須用 8 才能使用 reference_images）
    api_note:              排除元素請寫入主 Prompt（官方 Veo 指南：以名詞描述、避免 no/don't）。
                           公開 API 規格表未列 negative_prompt 參數。
    """
    try:
        from google import genai
        from google.genai import types
    except ImportError:
        print("❌ 請安裝 google-genai：pip install google-genai")
        return False

    try:
        client = genai.Client(api_key=api_key)
        print(f"🎬 呼叫 Veo 影片生成 API ({VIDEO_MODEL})...")
        print(f"   Prompt：{prompt[:80]}{'...' if len(prompt) > 80 else ''}")
        print(f"   Reference image：{reference_image_path}")
        if character_anchor_path:
            print(f"   Character anchor：{character_anchor_path}")
        print(f"   Duration：{duration_seconds}s")

        reference_image = types.Image.from_file(location=str(reference_image_path))

        # 建立 config — duration=8 是使用 reference_images 的必要條件
        config_kwargs: dict = {
            "aspect_ratio": aspect_ratio,
            "number_of_videos": 1,
            "duration_seconds": str(duration_seconds),
        }
        # 角色錨點（asset reference）— 鎖定角色外觀跨幕一致
        if character_anchor_path and character_anchor_path.exists():
            anchor_img = types.Image.from_file(location=str(character_anchor_path))
            config_kwargs["reference_images"] = [
                types.VideoGenerationReferenceImage(
                    image=anchor_img,
                    reference_type="asset",
                )
            ]

        # 同官方文件：image-to-video 以 prompt、image 參數呼叫（非 GenerateVideosSource）
        operation = client.models.generate_videos(
            model=VIDEO_MODEL,
            prompt=prompt,
            image=reference_image,
            config=types.GenerateVideosConfig(**config_kwargs),
        )

        print("⏳ 等待影片生成（可能需要 60-120 秒）...")
        max_wait = 300  # 最多等 5 分鐘
        start = time.time()

        while not operation.done:
            if time.time() - start > max_wait:
                print("❌ 影片生成超時（超過 5 分鐘）")
                return False
            elapsed = int(time.time() - start)
            print(f"   已等待 {elapsed}s...")
            time.sleep(10)
            operation = client.operations.get(operation)

        if not operation.response or not operation.response.generated_videos:
            error = getattr(operation, "error", None)
            print(f"❌ 影片生成失敗：{error or '未知錯誤'}")
            return False

        video_obj = operation.response.generated_videos[0]
        video_file = video_obj.video

        print("📥 下載影片...")
        video_bytes = client.files.download(file=video_file)

        output_path.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(video_bytes, bytes):
            output_path.write_bytes(video_bytes)
        else:
            # 可能回傳 file-like object
            with open(output_path, "wb") as f:
                for chunk in video_bytes:
                    f.write(chunk)

        print(f"✅ 影片已儲存：{output_path}")
        return True

    except Exception as e:
        print(f"❌ 影片生成失敗：{e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="使用 Gemini API 生成圖片或影片",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
範例：
  # 生成圖片，存入 Local_Media/KirbyTemplate/01.png
  python scripts/generate_media_gemini.py --prompt "..." --output Local_Media/KirbyTemplate/01.png --type image

  # 先生成圖片，再用圖片生成影片
  python scripts/generate_media_gemini.py --prompt "..." --output Local_Media/KirbyTemplate/01.png --type image
  python scripts/generate_media_gemini.py --prompt "..." --output Local_Media/KirbyTemplate/01.mp4 --type video --reference-image Local_Media/KirbyTemplate/01.png

  # 使用 --template 自動決定資料夾，--index 決定檔名序號
  python scripts/generate_media_gemini.py --prompt "..." --template "KirbyTemplate" --index 1 --type image
        """,
    )
    parser.add_argument("--prompt", "-p", required=True, help="生成描述（Prompt 文字）")
    parser.add_argument(
        "--output", "-o", help="輸出路徑（例：Local_Media/TemplateName/01.png）"
    )
    parser.add_argument(
        "--template", "-t", help="Prompt Template 名稱，用於決定資料夾（與 --index 搭配使用）"
    )
    parser.add_argument(
        "--index", "-i", type=int, default=1, help="此次生成的序號（用於自動命名）"
    )
    parser.add_argument(
        "--type",
        choices=["image", "video"],
        default="image",
        help="生成類型：image（預設）或 video",
    )
    parser.add_argument(
        "--reference-image",
        "-r",
        help="影片生成使用的 reference image 路徑（前幕中段幀，決定畫面起始狀態）",
    )
    parser.add_argument(
        "--character-anchor",
        help="角色錨點圖路徑（通常為 scene_01.png），鎖定角色外觀跨幕一致（Veo 3.1 asset reference）",
    )
    parser.add_argument(
        "--duration",
        type=int,
        default=VIDEO_DURATION_SECONDS,
        choices=[4, 6, 8],
        help=f"影片時長（秒），預設 {VIDEO_DURATION_SECONDS}；Veo API 僅支援 4/6/8 三種時長",
    )
    parser.add_argument(
        "--aspect-ratio",
        default="16:9",
        choices=["16:9", "9:16"],
        help="影片畫面比例（Veo 公開 API：16:9 或 9:16；9:16 適合直式短片）",
    )

    args = parser.parse_args()

    # 決定輸出路徑
    if args.output:
        output_path = Path(args.output)
        # 若為相對路徑，相對於 PROJECT_ROOT
        if not output_path.is_absolute():
            output_path = PROJECT_ROOT / output_path
    elif args.template:
        ext = ".png" if args.type == "image" else ".mp4"
        output_path = PROJECT_ROOT / "Local_Media" / args.template / f"{args.index:02d}{ext}"
    else:
        print("❌ 請指定 --output 路徑或 --template 名稱")
        parser.print_help()
        sys.exit(1)

    print("=" * 60)
    print(f"{'🖼️  Gemini 圖片生成' if args.type == 'image' else '🎬 Veo 影片生成'}")
    print("=" * 60)

    # 載入 API Key
    api_key = load_api_key()
    if not api_key:
        print("❌ 找不到 Gemini API Key")
        print("   請設定 GEMINI_API_KEY 環境變數")
        print("   或建立 config/gemini_config.json：")
        print('   {"api_key": "YOUR_API_KEY"}')
        sys.exit(1)

    reference_image_path = None
    character_anchor_path = None

    if args.type == "video":
        if args.reference_image:
            reference_image_path = Path(args.reference_image)
            if not reference_image_path.is_absolute():
                reference_image_path = PROJECT_ROOT / reference_image_path
        elif args.template:
            inferred_path = (
                PROJECT_ROOT / "Local_Media" / args.template / f"{args.index:02d}.png"
            )
            if inferred_path.exists():
                reference_image_path = inferred_path

        if reference_image_path is None:
            print("❌ 影片生成必須提供 reference image")
            print("   請先生成圖片，再使用 --reference-image 指定該圖片")
            print("   或搭配 --template 與 --index，並先建立對應的 PNG 檔")
            sys.exit(1)

        if not reference_image_path.exists():
            print(f"❌ 找不到 reference image：{reference_image_path}")
            sys.exit(1)

        # 角色錨點圖（asset reference）
        if args.character_anchor:
            character_anchor_path = Path(args.character_anchor)
            if not character_anchor_path.is_absolute():
                character_anchor_path = PROJECT_ROOT / character_anchor_path
            if not character_anchor_path.exists():
                print(f"⚠️  找不到角色錨點圖，略過：{character_anchor_path}")
                character_anchor_path = None

        # 使用 character_anchor 時強制 duration=8
        if character_anchor_path and args.duration != 8:
            print(f"⚠️  使用 reference_images 時 duration 必須為 8，已自動調整（原值：{args.duration}s）")
            args.duration = 8

    # 生成媒體
    if args.type == "image":
        success = generate_image(args.prompt, output_path, api_key)
    else:
        success = generate_video(
            args.prompt,
            output_path,
            api_key,
            reference_image_path=reference_image_path,
            character_anchor_path=character_anchor_path,
            duration_seconds=args.duration,
            aspect_ratio=args.aspect_ratio,
        )

    if not success:
        sys.exit(1)

    print("=" * 60)
    print(f"輸出位置：{output_path.relative_to(PROJECT_ROOT)}")
    print("=" * 60)


if __name__ == "__main__":
    main()
