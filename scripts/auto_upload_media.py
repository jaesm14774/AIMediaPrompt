#!/usr/bin/env python3
"""
自動上傳媒體檔案（圖片 + 影片）並插入 URL 到對應的 prompt 檔案
- 圖片 → ImgBB（免費）
- 影片 → Cloudinary（免費，支援影片）
"""

import json
import base64
import argparse
import shutil
from pathlib import Path
from typing import Dict, List, Optional
import requests

# 支援的檔案格式
IMAGE_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.gif', '.webp', '.bmp'}
VIDEO_EXTENSIONS = {'.mp4', '.webm', '.mov', '.avi', '.mkv'}

class MediaUploader:
    def __init__(self, imgbb_key: str, cloudinary_config: Optional[Dict] = None):
        self.imgbb_key = imgbb_key
        self.cloudinary_config = cloudinary_config
        self.media_dir = Path("Local_Media")

    def detect_file_type(self, file_path: Path) -> str:
        """偵測檔案類型（圖片/影片）"""
        ext = file_path.suffix.lower()
        if ext in IMAGE_EXTENSIONS:
            return 'image'
        elif ext in VIDEO_EXTENSIONS:
            return 'video'
        else:
            return 'unknown'

    def upload_image_to_imgbb(self, image_path: Path) -> Dict:
        """上傳圖片到 ImgBB"""
        try:
            with open(image_path, 'rb') as f:
                image_data = base64.b64encode(f.read()).decode('utf-8')

            payload = {
                'key': self.imgbb_key,
                'image': image_data
            }

            response = requests.post(
                "https://api.imgbb.com/1/upload",
                data=payload,
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    return {
                        'success': True,
                        'url': data['data']['url'],
                        'type': 'image',
                        'service': 'ImgBB'
                    }

            return {
                'success': False,
                'error': f"ImgBB upload failed: {response.text}"
            }
        except Exception as e:
            return {
                'success': False,
                'error': f"ImgBB upload error: {str(e)}"
            }

    def upload_video_to_cloudinary(self, video_path: Path) -> Dict:
        """上傳影片到 Cloudinary"""
        if not self.cloudinary_config:
            return {
                'success': False,
                'error': "Cloudinary config not found. Please set up config/cloudinary_config.json"
            }

        try:
            import cloudinary
            import cloudinary.uploader

            # 配置 Cloudinary
            cloudinary.config(
                cloud_name=self.cloudinary_config['cloud_name'],
                api_key=self.cloudinary_config['api_key'],
                api_secret=self.cloudinary_config['api_secret']
            )

            # 上傳影片
            result = cloudinary.uploader.upload(
                str(video_path),
                resource_type="video",
                folder="ai-prompts"
            )

            return {
                'success': True,
                'url': result['secure_url'],
                'type': 'video',
                'service': 'Cloudinary'
            }
        except ImportError:
            return {
                'success': False,
                'error': "Cloudinary library not installed. Run: pip install cloudinary"
            }
        except Exception as e:
            return {
                'success': False,
                'error': f"Cloudinary upload error: {str(e)}"
            }

    def upload_video_to_imgur(self, video_path: Path) -> Dict:
        """備用方案：上傳影片到 Imgur（匿名上傳）"""
        try:
            # Imgur 支援匿名影片上傳
            headers = {'Authorization': 'Client-ID YOUR_IMGUR_CLIENT_ID'}

            with open(video_path, 'rb') as f:
                response = requests.post(
                    'https://api.imgur.com/3/upload',
                    headers=headers,
                    files={'video': f},
                    timeout=60
                )

            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    return {
                        'success': True,
                        'url': data['data']['link'],
                        'type': 'video',
                        'service': 'Imgur'
                    }

            return {
                'success': False,
                'error': f"Imgur upload failed: {response.text}"
            }
        except Exception as e:
            return {
                'success': False,
                'error': f"Imgur upload error: {str(e)}"
            }

    def upload_file(self, file_path: Path) -> Dict:
        """智能上傳：根據檔案類型選擇服務"""
        file_type = self.detect_file_type(file_path)

        print(f"\n📤 上傳 {file_path.name} ({file_type})...")

        if file_type == 'image':
            return self.upload_image_to_imgbb(file_path)
        elif file_type == 'video':
            # 優先使用 Cloudinary，失敗則嘗試 Imgur
            result = self.upload_video_to_cloudinary(file_path)
            if not result['success'] and 'Cloudinary config not found' in result.get('error', ''):
                print("⚠️  Cloudinary 未配置，嘗試使用 Imgur...")
                result = self.upload_video_to_imgur(file_path)
            return result
        else:
            return {
                'success': False,
                'error': f"Unsupported file type: {file_path.suffix}"
            }

    def upload_all_media(self) -> List[Dict]:
        """上傳 Local_Media 中的所有媒體檔案"""
        if not self.media_dir.exists():
            print(f"❌ 找不到 {self.media_dir} 資料夾")
            return []

        # 收集所有媒體檔案
        extensions = IMAGE_EXTENSIONS | VIDEO_EXTENSIONS
        media_files = [
            f for f in self.media_dir.iterdir()
            if f.is_file() and f.suffix.lower() in extensions
        ]

        if not media_files:
            print(f"⚠️  {self.media_dir} 資料夾中沒有媒體檔案")
            return []

        # 依檔名排序
        media_files.sort(key=lambda x: x.name)

        print(f"\n找到 {len(media_files)} 個媒體檔案")

        results = []
        for media_file in media_files:
            result = self.upload_file(media_file)
            result['filename'] = media_file.name
            results.append(result)

            if result['success']:
                print(f"✅ 上傳成功: {result['url']} ({result['service']})")
            else:
                print(f"❌ 上傳失敗: {result['error']}")

        return results

    def cleanup_local_media(self):
        """刪除 Local_Media 中的媒體檔案"""
        if not self.media_dir.exists():
            return

        extensions = IMAGE_EXTENSIONS | VIDEO_EXTENSIONS
        media_files = [
            f for f in self.media_dir.iterdir()
            if f.is_file() and f.suffix.lower() in extensions
        ]

        if not media_files:
            return

        print(f"\n🧹 清理 Local_Media 資料夾...")
        count = 0
        for f in media_files:
            try:
                f.unlink()
                count += 1
            except Exception as e:
                print(f"❌ 刪除失敗 {f.name}: {e}")
        
        if count > 0:
            print(f"✅ 已刪除 {count} 個本機媒體檔案")

def load_config(config_type: str) -> Dict:
    """載入配置檔案"""
    config_file = Path(f"config/{config_type}_config.json")
    if not config_file.exists():
        return {}

    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"⚠️  無法讀取 {config_file}: {e}")
        return {}

def move_test_file_to_prompt(test_file: Path, prompt_name: str, media_type: str) -> Optional[Path]:
    """將 Test 資料夾的檔案移動到對應的 Prompt 資料夾"""
    if media_type.lower() == 'image':
        target_dir = Path("Prompt/Image")
    elif media_type.lower() == 'video':
        target_dir = Path("Prompt/Video")
    else:
        print(f"❌ 不支援的類型: {media_type}")
        return None

    if not target_dir.exists():
        target_dir.mkdir(parents=True, exist_ok=True)

    target_file = target_dir / f"{prompt_name}.md"

    if target_file.exists():
        print(f"⚠️  目標檔案已存在: {target_file}")
        response = input(f"是否覆蓋? (y/n): ").strip().lower()
        if response != 'y':
            print(f"⏸️  跳過移動")
            return target_file

    try:
        shutil.move(str(test_file), str(target_file))
        print(f"✅ 已移動檔案: {test_file.name} → {target_file}")
        return target_file
    except Exception as e:
        print(f"❌ 移動失敗: {e}")
        return None

def move_post_test_to_shared(prompt_name: str) -> bool:
    """將 Post/Test/ 的教學文移動到 Post/shared/"""
    test_post_dir = Path("Post/Test")
    shared_post_dir = Path("Post/shared")

    if not shared_post_dir.exists():
        shared_post_dir.mkdir(parents=True, exist_ok=True)

    # 尋找匹配的教學文（可能有日期前綴）
    matching_files = list(test_post_dir.glob(f"*{prompt_name}*.md"))

    if not matching_files:
        print(f"⚠️  找不到 Post/Test/ 中的教學文: {prompt_name}")
        return False

    for test_file in matching_files:
        target_file = shared_post_dir / test_file.name

        try:
            shutil.move(str(test_file), str(target_file))
            print(f"✅ 已移動教學文: {test_file.name} → Post/shared/")
        except Exception as e:
            print(f"❌ 移動教學文失敗: {e}")
            return False

    return True

def insert_urls_to_prompt(prompt_file: Path, urls: List[str], is_video: bool = False):
    """將 URL 插入到 prompt 檔案"""
    if not prompt_file.exists():
        print(f"❌ 找不到 prompt 檔案: {prompt_file}")
        return

    with open(prompt_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # 檢查是否已包含範例媒體區塊
    if is_video:
        if "## 範例影片" not in content and "## Example Video" not in content:
            content += "\n\n---\n\n## 範例影片 / Example Video\n\n"
    else:
        if "## 範例圖片" not in content and "## Example Images" not in content:
            content += "\n\n---\n\n## 範例圖片 / Example Images\n\n"

    # 添加 URL
    for url in urls:
        if url not in content:
            if is_video:
                content += f"\n[Video]({url})\n"
            else:
                content += f"\n![Image]({url})\n"

    # 寫回檔案
    with open(prompt_file, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"✅ 已插入 {len(urls)} 個 URL 到 {prompt_file.name}")

def main():
    parser = argparse.ArgumentParser(description='自動上傳媒體檔案（圖片+影片）並移動到正式區')
    parser.add_argument('prompt_name', help='Prompt 檔案名稱（不含副檔名）')
    parser.add_argument('--env', choices=['dev', 'stg', 'test', 'prod'],
                       default='prod', help='環境（預設：prod）')
    parser.add_argument('--type', choices=['image', 'video'],
                       help='Prompt 類型（image/video），從 Test/ 移到 Prompt/ 時必填')

    args = parser.parse_args()

    print("=" * 60)
    print("📤 自動上傳媒體檔案（圖片 + 影片）")
    print("=" * 60)

    # 載入配置
    imgbb_config = load_config('imgbb')
    cloudinary_config = load_config('cloudinary')

    if not imgbb_config.get('api_key'):
        print("❌ 請先設定 ImgBB API Key (config/imgbb_config.json)")
        return

    # 尋找 prompt 檔案
    prompt_file = None
    original_in_test = False

    if args.env in ['dev', 'stg', 'test']:
        # 測試環境：在 Test/ 中尋找
        prompt_file = Path(f"Test/{args.prompt_name}.md")
        original_in_test = True
    else:
        # 生產環境：先檢查 Test/，再檢查 Prompt/
        test_file = Path(f"Test/{args.prompt_name}.md")
        if test_file.exists():
            prompt_file = test_file
            original_in_test = True
        else:
            # 在 Prompt/ 中尋找
            for folder in ['Prompt/Image', 'Prompt/Video', 'Prompt/Image/Shared', 'Prompt/Video/Shared']:
                candidate = Path(f"{folder}/{args.prompt_name}.md")
                if candidate.exists():
                    prompt_file = candidate
                    break

    if not prompt_file or not prompt_file.exists():
        print(f"❌ 找不到 prompt 檔案: {args.prompt_name}.md")
        print(f"請確認檔案存在於以下位置之一：")
        print(f"  - Test/")
        print(f"  - Prompt/Image/ 或 Prompt/Video/")
        return

    print(f"✅ 找到 prompt 檔案: {prompt_file}")

    # 判斷是否需要移動檔案（prod 環境 + 檔案在 Test/）
    if args.env == 'prod' and original_in_test:
        if not args.type:
            print(f"❌ 從 Test/ 移動到 Prompt/ 時，必須指定 --type (image/video)")
            return

        print(f"\n🚀 生產環境偵測到檔案在 Test/，準備移動...")
        moved_prompt = move_test_file_to_prompt(prompt_file, args.prompt_name, args.type)

        if not moved_prompt:
            print(f"❌ 移動 Prompt 檔案失敗，停止執行")
            return

        prompt_file = moved_prompt

        # 同時移動 Post/Test/ 的教學文到 Post/shared/
        print(f"\n📝 檢查是否有對應的教學文需要移動...")
        move_post_test_to_shared(args.prompt_name)

    # 建立上傳器
    uploader = MediaUploader(
        imgbb_key=imgbb_config['api_key'],
        cloudinary_config=cloudinary_config if cloudinary_config else None
    )

    # 上傳所有媒體
    print(f"\n📤 開始上傳 Local_Media/ 中的媒體檔案...")
    results = uploader.upload_all_media()

    if not results:
        print(f"⚠️  沒有檔案需要上傳")
        return

    # 分類 URL
    image_urls = [r['url'] for r in results if r['success'] and r['type'] == 'image']
    video_urls = [r['url'] for r in results if r['success'] and r['type'] == 'video']

    # 插入 URL 到 prompt 檔案
    if image_urls:
        insert_urls_to_prompt(prompt_file, image_urls, is_video=False)
    if video_urls:
        insert_urls_to_prompt(prompt_file, video_urls, is_video=True)

    # 統計報告
    print("\n" + "="*60)
    print("📊 上傳統計報告")
    print("="*60)
    print(f"總檔案數: {len(results)}")
    print(f"成功上傳: {sum(1 for r in results if r['success'])}")
    print(f"失敗: {sum(1 for r in results if not r['success'])}")
    print(f"圖片: {len(image_urls)}")
    print(f"影片: {len(video_urls)}")

    if args.env == 'prod' and original_in_test:
        print(f"\n✅ 檔案已移動到正式區:")
        print(f"   Prompt: {prompt_file}")
        print(f"   Post: Post/shared/ (如果存在)")

    # 清理本機媒體檔案
    uploader.cleanup_local_media()

    print("="*60)

if __name__ == "__main__":
    main()
