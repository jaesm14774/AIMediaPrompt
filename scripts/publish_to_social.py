#!/usr/bin/env python3
"""
一鍵上傳 Post/.md + Local_Media 圖檔到 Facebook、Twitter
上傳完成後將 Post/.md 與 Prompt/Image 或 Prompt/Video 的 .md 移到對應 shared/
"""

import argparse
import os
import re
import shutil
import sys
from pathlib import Path
from typing import List, Optional, Tuple

# 專案根目錄
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

IMAGE_EXT = {'.png', '.jpg', '.jpeg', '.gif', '.webp', '.bmp'}
VIDEO_EXT = {'.mp4', '.webm', '.mov', '.avi', '.mkv'}


def load_dotenv_simple(env_path: Path) -> dict:
    """簡易載入 .env 檔"""
    env = {}
    if not env_path.exists():
        return env
    with open(env_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                k, v = line.split('=', 1)
                env[k.strip()] = v.strip().strip('"\'')
    return env


def parse_post_md(content: str) -> Tuple[str, str]:
    """從 Post .md 提取 caption 與 hashtags"""
    lines = content.strip().split('\n')
    caption_parts = []
    hashtags = ""

    # 取第一行（標題）與 hook 段落（到 👇 或 ## 之前）
    for i, line in enumerate(lines):
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith('👇') or stripped.startswith('##') or stripped.startswith('🔍'):
            break
        if i == 0 or (i > 0 and not lines[i - 1].strip() and caption_parts):
            caption_parts.append(stripped)
        elif caption_parts and not any(x in stripped for x in ['**Prompt', '**Example', '**Key', '**Pro']):
            caption_parts.append(stripped)
            if len(caption_parts) >= 4:  # 標題 + 約 2~3 段 hook
                break

    caption = '\n\n'.join(caption_parts) if caption_parts else content[:500]

    # 提取 SEO Discovery Block 的 hashtags
    for i, line in enumerate(lines):
        if 'SEO Discovery' in line or '🔍' in line:
            for j in range(i + 1, min(i + 5, len(lines))):
                h = lines[j].strip()
                if h and (h.startswith('#') or '#' in h):
                    hashtags = h
                    break
            break

    return caption, hashtags


def find_post_file(name_or_path: str) -> Optional[Path]:
    """依名稱或路徑找到 Post .md"""
    p = Path(name_or_path)
    if p.exists() and p.suffix == '.md':
        return p
    post_dir = PROJECT_ROOT / "Post"
    if not post_dir.exists():
        return None
    for f in post_dir.rglob("*.md"):
        if f.parent.name == "shared":
            continue
        if name_or_path in f.stem or f.stem.endswith(name_or_path.replace(" ", "-")):
            return f
    pattern = f"*{name_or_path}*.md"
    matches = list(post_dir.glob(pattern))
    return matches[0] if matches else None


def find_prompt_file(prompt_name: str) -> Optional[Tuple[Path, str]]:
    """找到 Prompt 檔，回傳 (路徑, 'image'|'video')"""
    for media_type, folder in [('image', 'Prompt/Image'), ('video', 'Prompt/Video')]:
        base = PROJECT_ROOT / folder
        for sub in ['', 'shared']:
            candidate = base / sub / f"{prompt_name}.md"
            if candidate.exists():
                return (candidate, media_type)
        for f in base.rglob("*.md"):
            if prompt_name in f.stem:
                return (f, media_type)
    return None


def collect_media(media_dir: Path, limit: int = 4) -> List[Path]:
    """收集媒體檔（圖片優先最多 4 張，影片最多 10 支可同貼文）"""
    exts = IMAGE_EXT | VIDEO_EXT
    files = [f for f in media_dir.iterdir() if f.is_file() and f.suffix.lower() in exts]
    files.sort(key=lambda x: x.name)
    images = [f for f in files if f.suffix.lower() in IMAGE_EXT]
    videos = [f for f in files if f.suffix.lower() in VIDEO_EXT]
    result = images[:4] if images else videos[:10]
    return result


def _get_mime_type(path: Path) -> str:
    ext = path.suffix.lower()
    mime = {".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png",
            ".webp": "image/webp", ".gif": "image/gif", ".mp4": "video/mp4"}
    return mime.get(ext, "application/octet-stream")


def publish_facebook(caption: str, hashtags: str, media_paths: List[Path], config: dict) -> bool:
    """使用 Graph API 發布到 Facebook 粉絲專頁（支援多圖、多影片）
    參考 mediaoverload：使用 me 端點避免 page_id global id 錯誤"""
    token = config.get('FB_PAGE_ACCESS_TOKEN')
    if not token:
        print("[Warn] Facebook not configured (config/social_media/credentials/facebook.env)")
        return False

    try:
        import requests
        import time
        import json
    except ImportError:
        print("[Error] pip install requests")
        return False

    text = f"{caption}\n{hashtags}" if hashtags else caption
    if len(text) > 63200:
        text = text[:63200] + "..."

    base_url = "https://graph.facebook.com/v24.0/me"

    if not media_paths:
        r = requests.post(f"{base_url}/feed", data={"message": text, "access_token": token}, timeout=60)
    else:
        images = [p for p in media_paths if p.suffix.lower() in IMAGE_EXT]
        videos = [p for p in media_paths if p.suffix.lower() in VIDEO_EXT or p.suffix.lower() == ".gif"]

        if len(images) >= 2:
            media_ids = []
            for path in images[:10]:
                try:
                    with open(path, "rb") as f:
                        files = {"source": (path.name, f, _get_mime_type(path))}
                        data = {"published": "false", "access_token": token}
                        resp = requests.post(f"{base_url}/photos", files=files, data=data, timeout=120)
                    if resp.status_code in (200, 201):
                        pid = resp.json().get("id")
                        if pid:
                            media_ids.append(pid)
                    time.sleep(1)
                except Exception as e:
                    print(f"[Warn] FB upload failed {path.name}: {e}")

            if not media_ids:
                print("[Error] All images upload failed")
                return False

            feed_data = {"message": text, "access_token": token}
            for i, fid in enumerate(media_ids):
                feed_data[f"attached_media[{i}]"] = json.dumps({"media_fbid": fid})
            r = requests.post(f"{base_url}/feed", data=feed_data, timeout=60)

        elif len(images) == 1 and not videos:
            with open(images[0], "rb") as f:
                files = {"source": (images[0].name, f, _get_mime_type(images[0]))}
                data = {"message": text, "access_token": token}
                r = requests.post(f"{base_url}/photos", files=files, data=data, timeout=300)

        elif len(videos) >= 2:
            media_ids = []
            for path in videos[:10]:
                try:
                    with open(path, "rb") as f:
                        files = {"source": (path.name, f, _get_mime_type(path))}
                        data = {"published": "false", "access_token": token}
                        resp = requests.post(f"{base_url}/videos", files=files, data=data, timeout=300)
                    if resp.status_code in (200, 201):
                        vid = resp.json().get("id") or resp.json().get("video_id")
                        if vid:
                            media_ids.append(vid)
                    else:
                        try:
                            err = resp.json() if resp.text else {}
                        except Exception:
                            err = {}
                        if err.get("error", {}).get("code") == 10:
                            print("[Warn] Unpublished video needs pages_manage_ads, fallback to separate posts")
                            break
                    time.sleep(2)
                except Exception as e:
                    print(f"[Warn] FB video upload failed {path.name}: {e}")

            if media_ids:
                feed_data = {"message": text, "access_token": token}
                for i, fid in enumerate(media_ids):
                    feed_data[f"attached_media[{i}]"] = json.dumps({"media_fbid": fid})
                r = requests.post(f"{base_url}/feed", data=feed_data, timeout=60)
                if r.status_code not in (200, 201) and r.text:
                    try:
                        err = r.json()
                        if err.get("error", {}).get("code") == 10:
                            media_ids = []
                    except Exception:
                        pass
            if not media_ids:
                ok_count = 0
                for i, path in enumerate(videos[:10]):
                    try:
                        with open(path, "rb") as f:
                            files = {"source": (path.name, f, _get_mime_type(path))}
                            desc = text if i == 0 else ""
                            data = {"description": desc, "access_token": token}
                            resp = requests.post(f"{base_url}/videos", files=files, data=data, timeout=300)
                        if resp.status_code in (200, 201):
                            ok_count += 1
                            print(f"[OK] FB video {i+1}/{len(videos[:10])} published")
                        else:
                            print(f"[Warn] FB video {path.name}: {resp.status_code} {resp.text[:100]}")
                        time.sleep(2)
                    except Exception as e:
                        print(f"[Warn] FB video failed {path.name}: {e}")
                r = type("R", (), {"status_code": 200 if ok_count > 0 else 400})()

        elif videos:
            with open(videos[0], "rb") as f:
                files = {"source": (videos[0].name, f, _get_mime_type(videos[0]))}
                data = {"description": text, "access_token": token}
                r = requests.post(f"{base_url}/videos", files=files, data=data, timeout=300)

        else:
            r = requests.post(f"{base_url}/feed", data={"message": text, "access_token": token}, timeout=60)

    if r.status_code in (200, 201):
        print("[OK] Facebook published")
        return True
    print(f"[Error] Facebook failed: {r.status_code} {r.text[:200]}")
    return False


def publish_twitter(caption: str, hashtags: str, media_paths: List[Path], config: dict) -> bool:
    """使用 Tweepy 發布到 Twitter"""
    required = ['TWITTER_API_KEY', 'TWITTER_API_SECRET', 'TWITTER_ACCESS_TOKEN', 'TWITTER_ACCESS_TOKEN_SECRET']
    if not all(config.get(k) for k in required):
        print("[Warn] Twitter not configured (config/social_media/credentials/twitter.env)")
        return False

    try:
        import tweepy
    except ImportError:
        print("[Error] pip install tweepy")
        return False

    text = f"{caption}\n{hashtags}" if hashtags else caption
    if len(text) > 280:
        text = text[:277] + "..."

    auth = tweepy.OAuth1UserHandler(
        config['TWITTER_API_KEY'], config['TWITTER_API_SECRET'],
        config['TWITTER_ACCESS_TOKEN'], config['TWITTER_ACCESS_TOKEN_SECRET']
    )
    api = tweepy.API(auth, wait_on_rate_limit=False)
    media_ids = []

    for mp in media_paths[:4]:
        if not mp.exists():
            continue
        try:
            if mp.suffix.lower() == '.mp4':
                media = api.media_upload(str(mp), media_category='tweet_video')
            else:
                media = api.media_upload(str(mp))
            media_ids.append(media.media_id)
        except Exception as e:
            print(f"[Warn] Twitter media upload failed {mp.name}: {e}")

    try:
        if media_ids:
            api.update_status(status=text, media_ids=media_ids)
        else:
            api.update_status(status=text)
        print("[OK] Twitter published")
        return True
    except Exception as e:
        print(f"[Error] Twitter failed: {e}")
        return False


def move_to_shared(post_path: Path, prompt_path: Optional[Path], media_type: Optional[str]) -> None:
    """上傳成功後移動檔案到 shared/"""
    shared_post = PROJECT_ROOT / "Post" / "shared"
    shared_post.mkdir(parents=True, exist_ok=True)
    target_post = shared_post / post_path.name
    if target_post.exists():
        target_post.unlink()
    shutil.move(str(post_path), str(target_post))
    print(f"[OK] Post moved to {target_post.relative_to(PROJECT_ROOT)}")

    if prompt_path and prompt_path.exists() and media_type:
        if media_type == 'image':
            shared_prompt = PROJECT_ROOT / "Prompt" / "Image" / "shared"
        else:
            shared_prompt = PROJECT_ROOT / "Prompt" / "Video" / "shared"
        shared_prompt.mkdir(parents=True, exist_ok=True)
        target_prompt = shared_prompt / prompt_path.name
        if target_prompt.exists():
            target_prompt.unlink()
        shutil.move(str(prompt_path), str(target_prompt))
        print(f"[OK] Prompt moved to {target_prompt.relative_to(PROJECT_ROOT)}")


def main():
    parser = argparse.ArgumentParser(description='一鍵上傳 Post + 媒體到 Facebook、Twitter')
    parser.add_argument('post', help='Post 檔名、路徑或關鍵字')
    parser.add_argument('--prompt', help='對應的 Prompt 名稱（用於移動到 shared）')
    parser.add_argument('--type', choices=['image', 'video'], help='Prompt 類型')
    parser.add_argument('--platforms', default='fb,twitter', help='平台，逗號分隔 (fb,twitter)')
    parser.add_argument('--media-dir', default='Local_Media', help='媒體目錄')
    parser.add_argument('--dry-run', action='store_true', help='僅預覽，不實際發布')
    parser.add_argument('--no-move', action='store_true', help='發布後不移動檔案')

    args = parser.parse_args()

    print("=" * 50)
    print("[Publish] One-click post to social media")
    print("=" * 50)

    post_path = find_post_file(args.post)
    if not post_path:
        print(f"[Error] Post not found: {args.post}")
        return 1

    print(f"[Post] {post_path.relative_to(PROJECT_ROOT)}")
    content = post_path.read_text(encoding='utf-8')
    caption, hashtags = parse_post_md(content)
    print(f"[Caption] {len(caption)} chars")
    if hashtags:
        print(f"[Hashtags] {hashtags[:80]}...")

    media_dir = PROJECT_ROOT / args.media_dir
    media_paths = collect_media(media_dir) if media_dir.exists() else []
    if not media_paths:
        print("[Warn] No media in Local_Media, will post text only")
    else:
        print(f"[Media] {[m.name for m in media_paths]}")

    # 載入平台設定
    cred_dir = PROJECT_ROOT / "config" / "social_media" / "credentials"
    fb_env = load_dotenv_simple(cred_dir / "facebook.env")
    tw_env = load_dotenv_simple(cred_dir / "twitter.env")

    if args.dry_run:
        print("\n[Dry-run] No actual publish")
        return 0

    platforms = [p.strip().lower() for p in args.platforms.split(',')]
    results = {}
    media_str = [str(p) for p in media_paths]

    if 'fb' in platforms or 'facebook' in platforms:
        results['facebook'] = publish_facebook(caption, hashtags, media_paths, fb_env)
    if 'twitter' in platforms:
        results['twitter'] = publish_twitter(caption, hashtags, media_paths, tw_env)

    success = any(results.values())
    if not success:
        print("\n[Error] All platforms failed")
        return 1

    if success and not args.no_move:
        prompt_path, media_type = None, None
        if args.prompt:
            found = find_prompt_file(args.prompt)
            if found:
                prompt_path, media_type = found
            elif args.type:
                media_type = args.type
        move_to_shared(post_path, prompt_path, media_type)

    if media_paths and success:
        for f in media_paths:
            try:
                f.unlink()
                print(f"[Clean] Removed {f.name}")
            except Exception:
                pass

    print("=" * 50)
    return 0


if __name__ == "__main__":
    sys.exit(main())
