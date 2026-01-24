#!/usr/bin/env python3
"""
自動上傳圖片到 ImgBB 並插入 URL 到對應的 prompt 檔案
ImgBB: 免費圖片托管，無需註冊（匿名上傳）
"""

import json
import base64
import argparse
import shutil
from pathlib import Path
from typing import Dict, List, Optional
import requests

class ImgBBUploader:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.upload_url = "https://api.imgbb.com/1/upload"
        self.image_dir = Path("Local_Media")

    def upload_image(self, image_path: Path) -> Dict:
        """上傳單張圖片到 ImgBB"""
        try:
            with open(image_path, 'rb') as f:
                image_data = base64.b64encode(f.read()).decode('utf-8')

            payload = {
                'key': self.api_key,
                'image': image_data
            }

            response = requests.post(
                self.upload_url,
                data=payload,
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    return {
                        'success': True,
                        'url': data['data']['url'],
                        'delete_url': data['data'].get('delete_url'),
                        'id': data['data'].get('id')
                    }
                else:
                    return {
                        'success': False,
                        'error': data.get('error', {}).get('message', 'Upload failed')
                    }
            else:
                return {
                    'success': False,
                    'error': f"HTTP {response.status_code}: {response.text}"
                }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def get_prompt_file(self, prompt_name: str, env: Optional[str] = None, type: Optional[str] = None) -> Optional[Path]:
        """根據指定的 prompt 檔案名稱取得檔案路徑"""
        test_envs = {'dev', 'stg', 'test'}
        
        # 1. 如果是測試環境 (dev, stg, test)，優先找 Test/
        if env and env.lower() in test_envs:
            test_file = Path("Test") / f"{prompt_name}.md"
            if test_file.exists():
                return test_file
            return None
        
        # 2. 如果是 prod，先看 Test/ 是否有檔案待移入
        if env and env.lower() == 'prod':
            test_file = Path("Test") / f"{prompt_name}.md"
            if test_file.exists():
                return test_file

        # 3. 搜尋 Prompt 資料夾
        search_dirs = []
        if type:
            if type.lower() == 'image':
                search_dirs = [Path("Prompt/Image"), Path("Prompt/Image/Shared"), Path("Prompt/Image/shared")]
            elif type.lower() == 'video':
                search_dirs = [Path("Prompt/Video"), Path("Prompt/Video/Shared"), Path("Prompt/Video/shared")]
        
        if not search_dirs:
            search_dirs = [
                Path("Prompt/Image"),
                Path("Prompt/Video"),
                Path("Prompt/Image/Shared"),
                Path("Prompt/Video/Shared"),
                Path("Prompt/Image/shared"),
                Path("Prompt/Video/shared")
            ]
        
        for search_dir in search_dirs:
            prompt_file = search_dir / f"{prompt_name}.md"
            if prompt_file.exists():
                return prompt_file
        return None
    
    def move_test_file_to_prompt(self, test_file: Path, prompt_name: str, type: str) -> Optional[Path]:
        """將 Test 資料夾的檔案移動到對應的 Prompt 資料夾"""
        test_envs = {'dev', 'stg', 'test'}
        
        if type.lower() == 'image':
            target_dir = Path("Prompt/Image")
        elif type.lower() == 'video':
            target_dir = Path("Prompt/Video")
        else:
            print(f"  [X] Unsupported type: {type}")
            return None
        
        if not target_dir.exists():
            target_dir.mkdir(parents=True, exist_ok=True)
        
        target_file = target_dir / f"{prompt_name}.md"
        
        if target_file.exists():
            print(f"  [!] Target file exists: {target_file}")
            response = input(f"  Overwrite? (y/n): ").strip().lower()
            if response != 'y':
                print(f"  [!] Skip move")
                return target_file
        
        try:
            shutil.move(str(test_file), str(target_file))
            print(f"  [V] Moved file: {test_file.name} -> {target_file}")
            return target_file
        except Exception as e:
            print(f"  [X] Move failed: {e}")
            return None

    def insert_image_url(self, prompt_file: Path, image_url: str, image_name: str, is_first_image: bool = False):
        """將圖片 URL 插入到 prompt 檔案末尾"""
        try:
            with open(prompt_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if image_url in content:
                print(f"  [!] {prompt_file.name} already contains this URL, skipping")
                return False
            
            has_example_section = "## 範例圖片" in content
            alt_text = Path(image_name).stem
            
            if is_first_image and not has_example_section:
                image_markdown = f"\n\n## 範例圖片\n\n![{alt_text}]({image_url})\n"
            else:
                image_markdown = f"\n![{alt_text}]({image_url})\n"
            
            new_content = content.rstrip() + image_markdown
            
            with open(prompt_file, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            return True
            
        except Exception as e:
            print(f"  [X] Insert failed: {e}")
            return False

    def cleanup_media_files(self):
        """刪除 Local_Media 資料夾中的所有媒體檔案"""
        if not self.image_dir.exists():
            return
        
        # 定義所有媒體檔案副檔名
        media_extensions = {
            # 圖片格式
            '.png', '.jpg', '.jpeg', '.gif', '.webp', '.bmp', '.tiff', '.svg',
            # 視頻格式
            '.mp4', '.mov', '.avi', '.mkv', '.wmv', '.flv', '.webm', '.m4v',
            # 音頻格式（如果需要）
            '.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a'
        }
        
        media_files = []
        for ext in media_extensions:
            media_files.extend(self.image_dir.glob(f'*{ext}'))
            media_files.extend(self.image_dir.glob(f'*{ext.upper()}'))
        
        if not media_files:
            print("\n[V] No media files to delete in Local_Media")
            return
        
        print(f"\nCleaning Local_Media folder...")
        deleted_count = 0
        skipped_count = 0
        for media_file in media_files:
            # 刪除前檢查文件是否存在
            if not media_file.exists():
                skipped_count += 1
                continue
            
            try:
                media_file.unlink()
                deleted_count += 1
            except FileNotFoundError:
                # 文件已經不存在，跳過
                skipped_count += 1
            except Exception as e:
                print(f"  [X] Delete failed {media_file.name}: {e}")
        
        if deleted_count > 0:
            print(f"  [V] Deleted {deleted_count} media files")
        if skipped_count > 0:
            print(f"  [!] Skipped {skipped_count} missing files")

    def process_all_images(self, prompt_name: str, env: Optional[str] = None, type: Optional[str] = None):
        """處理所有圖片並插入到指定的 prompt 檔案"""
        if not self.image_dir.exists():
            print(f"[X] Cannot find image dir: {self.image_dir}")
            return
        
        prompt_file = self.get_prompt_file(prompt_name, env, type)
        if not prompt_file:
            try:
                print(f"[X] Cannot find prompt file: {prompt_name}.md")
            except UnicodeEncodeError:
                print(f"[X] Cannot find prompt file (encoding error)")
            
            print(f"  Please make sure the file exists in one of:")
            print(f"    - Prompt/Image")
            print(f"    - Prompt/Video")
            print(f"    - Prompt/Image/Shared")
            print(f"    - Prompt/Video/Shared")
            if env and env.lower() in {'dev', 'stg', 'test'}:
                print(f"    - Test")
            return
        
        # 判斷是否需要移動檔案 (僅在 env == 'prod' 且檔案在 Test/ 時)
        if env and env.lower() == 'prod' and type and prompt_file.parent.name == "Test":
            print(f"\nProd environment detected and file in Test/, moving file...")
            moved_file = self.move_test_file_to_prompt(prompt_file, prompt_name, type)
            if moved_file:
                prompt_file = moved_file
            else:
                print(f"[X] Failed to move file, stopping")
                return
        
        extensions = {'.png', '.jpg', '.jpeg', '.gif', '.webp'}
        image_files_set = set()
        for ext in extensions:
            image_files_set.update(self.image_dir.glob(f'*{ext}'))
            image_files_set.update(self.image_dir.glob(f'*{ext.upper()}'))
        
        image_files = sorted(list(image_files_set))
        
        if not image_files:
            print("[V] No images found to upload")
            return
        
        print(f"\nFound {len(image_files)} images")
        try:
            print(f"Target prompt file: {prompt_file.name}")
        except UnicodeEncodeError:
            print(f"Target prompt file: (encoding error)")
        print("=" * 60)
        
        for idx, image_path in enumerate(image_files, 1):
            print(f"\n[{idx}/{len(image_files)}] Processing: {image_path.name}")
            
            print("  Uploading...", end=' ', flush=True)
            upload_result = self.upload_image(image_path)
            
            if not upload_result['success']:
                print(f"[X] Upload failed: {upload_result['error']}")
                continue
            
            image_url = upload_result['url']
            print(f"[V] Success: {image_url}")
            
            is_first_image = idx == 1
            if self.insert_image_url(prompt_file, image_url, image_path.name, is_first_image):
                try:
                    print(f"  [V] Inserted URL into {prompt_file.name}")
                except UnicodeEncodeError:
                    print(f"  [V] Inserted URL into file")
        
        # 處理完成後，刪除 Local_Media 中的所有媒體檔案
        self.cleanup_media_files()



def load_config(config_file: str = 'config/imgbb_config.json') -> Optional[Dict]:
    """載入設定檔"""
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"✗ 找不到設定檔: {config_file}")
        print("請先創建設定檔，參考 config/imgbb_config.example.json")
        return None


def main():
    parser = argparse.ArgumentParser(
        description='自動上傳圖片到 ImgBB 並插入 URL 到指定的 prompt 檔案',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
範例:
  python auto_upload_imgbb.py 貪吃蛇
  python auto_upload_imgbb.py "One leaf, one world"
  python auto_upload_imgbb.py "Kirby-IP-Copy-Ability" --env dev --type image
  python auto_upload_imgbb.py "test-video" --env stg --type video
  
注意: 
  - Local_Media 資料夾一次僅放一種型態的圖片
  - 當使用 --env (dev/stg/test) 且 --type (image/video) 時，會從 Test/ 資料夾找檔案並自動移動到對應的 Prompt 資料夾
        '''
    )
    parser.add_argument(
        'prompt_name',
        type=str,
        help='prompt 檔案名稱（不含副檔名），例如: 貪吃蛇 或 "One leaf, one world"'
    )
    parser.add_argument(
        '--env',
        type=str,
        choices=['dev', 'stg', 'test', 'prod'],
        default=None,
        help='環境變數：dev/stg/test/prod。dev/stg/test 會在 Test/ 資料夾更新；prod 或不指定則在 Prompt/ 資料夾更新。'
    )
    parser.add_argument(
        '--type',
        type=str,
        choices=['image', 'video'],
        default=None,
        help='類型：image/video。當從 Test/ 移動到 Prompt/ 時為必填。'
    )
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("自動上傳圖片到 ImgBB 並插入 URL 工具")
    print("=" * 60)
    
    # 檢查邏輯：如果是 prod 且檔案在 Test/，必須指定 type 才能移動
    # 這裡先不做過多限制，交給 process_all_images 判斷
    
    config = load_config()
    if not config:
        return
    
    api_key = config.get('api_key')
    if not api_key or api_key == "YOUR_IMGBB_API_KEY_HERE":
        print("✗ 請在 config/imgbb_config.json 中設定有效的 api_key")
        print("  取得方式: https://api.imgbb.com/")
        return
    
    uploader = ImgBBUploader(api_key)
    uploader.process_all_images(args.prompt_name, args.env, args.type)


if __name__ == "__main__":
    main()

