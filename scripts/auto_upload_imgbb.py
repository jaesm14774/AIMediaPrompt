#!/usr/bin/env python3
"""
自動上傳圖片到 ImgBB 並插入 URL 到對應的 prompt 檔案
ImgBB: 免費圖片托管，無需註冊（匿名上傳）
"""

import json
import base64
import argparse
from pathlib import Path
from typing import Dict, List, Optional
import requests

class ImgBBUploader:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.upload_url = "https://api.imgbb.com/1/upload"
        self.image_dir = Path("Local_Media")
        self.prompt_dir = Path("Prompt/Image")

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
                        'error': data.get('error', {}).get('message', '上傳失敗')
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

    def get_prompt_file(self, prompt_name: str) -> Optional[Path]:
        """根據指定的 prompt 檔案名稱取得檔案路徑"""
        prompt_file = self.prompt_dir / f"{prompt_name}.txt"
        if prompt_file.exists():
            return prompt_file
        return None

    def insert_image_url(self, prompt_file: Path, image_url: str, image_name: str, is_first_image: bool = False):
        """將圖片 URL 插入到 prompt 檔案末尾"""
        try:
            with open(prompt_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if image_url in content:
                print(f"  ⚠ {prompt_file.name} 已包含此圖片 URL，跳過")
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
            print(f"  ✗ 插入失敗: {e}")
            return False

    def process_all_images(self, prompt_name: str):
        """處理所有圖片並插入到指定的 prompt 檔案"""
        if not self.image_dir.exists():
            print(f"✗ 找不到圖片資料夾: {self.image_dir}")
            return
        
        prompt_file = self.get_prompt_file(prompt_name)
        if not prompt_file:
            print(f"✗ 找不到 prompt 檔案: {prompt_name}.txt")
            print(f"  請確認檔案存在於 {self.prompt_dir} 資料夾中")
            return
        
        extensions = {'.png', '.jpg', '.jpeg', '.gif', '.webp'}
        image_files_set = set()
        for ext in extensions:
            image_files_set.update(self.image_dir.glob(f'*{ext}'))
            image_files_set.update(self.image_dir.glob(f'*{ext.upper()}'))
        
        image_files = sorted(list(image_files_set))
        
        if not image_files:
            print("✓ 沒有找到需要上傳的圖片")
            return
        
        print(f"\n找到 {len(image_files)} 張圖片")
        print(f"目標 prompt 檔案: {prompt_file.name}")
        print("=" * 60)
        
        for idx, image_path in enumerate(image_files, 1):
            print(f"\n[{idx}/{len(image_files)}] 處理: {image_path.name}")
            
            print("  上傳中...", end=' ', flush=True)
            upload_result = self.upload_image(image_path)
            
            if not upload_result['success']:
                print(f"✗ 上傳失敗: {upload_result['error']}")
                continue
            
            image_url = upload_result['url']
            print(f"✓ 成功: {image_url}")
            
            is_first_image = idx == 1
            if self.insert_image_url(prompt_file, image_url, image_path.name, is_first_image):
                print(f"  ✓ 已插入 URL 到 {prompt_file.name}")


def load_config(config_file: str = 'scripts/imgbb_config.json') -> Optional[Dict]:
    """載入設定檔"""
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"✗ 找不到設定檔: {config_file}")
        print("請先創建設定檔，參考 imgbb_config.example.json")
        return None


def main():
    parser = argparse.ArgumentParser(
        description='自動上傳圖片到 ImgBB 並插入 URL 到指定的 prompt 檔案',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
範例:
  python auto_upload_imgbb.py 貪吃蛇
  python auto_upload_imgbb.py "One leaf, one world"
  
注意: Local_Media 資料夾一次僅放一種型態的圖片
        '''
    )
    parser.add_argument(
        'prompt_name',
        type=str,
        help='prompt 檔案名稱（不含副檔名），例如: 貪吃蛇 或 "One leaf, one world"'
    )
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("自動上傳圖片到 ImgBB 並插入 URL 工具")
    print("=" * 60)
    
    config = load_config()
    if not config:
        return
    
    api_key = config.get('api_key')
    if not api_key or api_key == "YOUR_IMGBB_API_KEY_HERE":
        print("✗ 請在 scripts/imgbb_config.json 中設定有效的 api_key")
        print("  取得方式: https://api.imgbb.com/")
        return
    
    uploader = ImgBBUploader(api_key)
    uploader.process_all_images(args.prompt_name)


if __name__ == "__main__":
    main()

