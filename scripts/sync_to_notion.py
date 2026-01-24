#!/usr/bin/env python3
"""
將 Git 中的 prompt 檔案同步到 Notion
支援 Image 和 Video 資料夾中的所有 .md 檔案
"""

import json
import argparse
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from notion_client import Client
import time
import hashlib

# 設置輸出編碼為 UTF-8，避免 Windows 控制台編碼問題
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

class NotionSyncer:
    def __init__(self, api_key: str, database_id: str = None, page_id: str = None):
        self.notion = Client(auth=api_key)
        self.database_id = self._extract_id(database_id) if database_id else None
        self.page_id = self._extract_id(page_id) if page_id else None
        self.image_dir = Path("Prompt/Image")
        self.video_dir = Path("Prompt/Video")
        self.state_file = Path("config/notion_sync_state.json")
    
    def _extract_id(self, id_or_url: str) -> str:
        """從 URL 或 ID 中提取正確的 UUID"""
        if not id_or_url:
            return None
        
        # 移除空白
        id_or_url = id_or_url.strip()
        
        # 如果是完整的 URL，提取 ID 部分
        if 'notion.so' in id_or_url:
            # 從 URL 中提取 ID（32 個字元，可能包含連字號）
            match = re.search(r'([a-f0-9]{32}|[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})', id_or_url, re.IGNORECASE)
            if match:
                id_str = match.group(1)
                # 如果沒有連字號，添加連字號使其成為標準 UUID 格式
                if '-' not in id_str:
                    id_str = f"{id_str[:8]}-{id_str[8:12]}-{id_str[12:16]}-{id_str[16:20]}-{id_str[20:]}"
                return id_str
        
        # 如果已經是 UUID 格式（有連字號），直接返回
        if re.match(r'^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$', id_or_url, re.IGNORECASE):
            return id_or_url
        
        # 如果是 32 個字元的十六進制字串，添加連字號
        if re.match(r'^[a-f0-9]{32}$', id_or_url, re.IGNORECASE):
            return f"{id_or_url[:8]}-{id_or_url[8:12]}-{id_or_url[12:16]}-{id_or_url[16:20]}-{id_or_url[20:]}"
        
        # 如果都不符合，返回原始值（讓 API 報錯）
        return id_or_url
    
    def parse_markdown_file(self, file_path: Path) -> Optional[Tuple[str, str]]:
        """解析 markdown 檔案，返回標題和內容"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
            
            if not content:
                return None
            
            lines = content.split('\n')
            title = None
            body_lines = []
            
            for i, line in enumerate(lines):
                if line.startswith('###'):
                    title = line.replace('###', '').strip()
                    body_lines = lines[i+1:]
                    break
            
            if not title:
                title = file_path.stem
            
            body = '\n'.join(body_lines).strip()
            if not body:
                body = content
            
            return (title, body)
        
        except Exception as e:
            print(f"  ✗ 解析失敗: {e}")
            return None
    
    def normalize_path(self, file_path: str) -> str:
        """標準化路徑，統一 shared/Shared 的大小寫"""
        # 將路徑中的 Shared 統一為 shared（小寫）
        parts = file_path.split('\\')
        normalized_parts = []
        for part in parts:
            if part.lower() == 'shared':
                normalized_parts.append('shared')
            else:
                normalized_parts.append(part)
        return '\\'.join(normalized_parts)
    
    def get_all_prompts(self) -> List[Tuple[str, str, str, bool, str]]:
        """取得所有 prompt 檔案（標題、內容、類型、是否為 shared、檔案路徑）"""
        prompts = []
        seen_files = set()  # 使用檔名追蹤，避免重複
        
        # Image 資料夾下的檔案
        for md_file in sorted(self.image_dir.glob('*.md')):
            result = self.parse_markdown_file(md_file)
            if result:
                title, content = result
                file_path = str(md_file.relative_to(Path("Prompt")))
                file_path = self.normalize_path(file_path)
                file_name = Path(file_path).name
                if file_name not in seen_files:
                    prompts.append((title, content, 'Image', False, file_path))
                    seen_files.add(file_name)
        
        # Image/shared 或 Image/Shared 資料夾下的檔案
        shared_image_dirs = [
            self.image_dir / 'shared',
            self.image_dir / 'Shared'
        ]
        for shared_dir in shared_image_dirs:
            if shared_dir.exists():
                for md_file in sorted(shared_dir.glob('*.md')):
                    result = self.parse_markdown_file(md_file)
                    if result:
                        title, content = result
                        file_path = str(md_file.relative_to(Path("Prompt")))
                        file_path = self.normalize_path(file_path)
                        file_name = Path(file_path).name
                        # 如果已經在未分享列表中，移除它並添加為已分享
                        if file_name in seen_files:
                            # 找到並移除未分享的版本
                            prompts = [p for p in prompts if Path(p[4]).name != file_name]
                        prompts.append((title, content, 'Image', True, file_path))
                        seen_files.add(file_name)
        
        # Video 資料夾下的檔案
        for md_file in sorted(self.video_dir.glob('*.md')):
            result = self.parse_markdown_file(md_file)
            if result:
                title, content = result
                file_path = str(md_file.relative_to(Path("Prompt")))
                file_path = self.normalize_path(file_path)
                file_name = Path(file_path).name
                if file_name not in seen_files:
                    prompts.append((title, content, 'Video', False, file_path))
                    seen_files.add(file_name)
        
        # Video/shared 或 Video/Shared 資料夾下的檔案
        shared_video_dirs = [
            self.video_dir / 'shared',
            self.video_dir / 'Shared'
        ]
        for shared_dir in shared_video_dirs:
            if shared_dir.exists():
                for md_file in sorted(shared_dir.glob('*.md')):
                    result = self.parse_markdown_file(md_file)
                    if result:
                        title, content = result
                        file_path = str(md_file.relative_to(Path("Prompt")))
                        file_path = self.normalize_path(file_path)
                        file_name = Path(file_path).name
                        # 如果已經在未分享列表中，移除它並添加為已分享
                        if file_name in seen_files:
                            # 找到並移除未分享的版本
                            prompts = [p for p in prompts if Path(p[4]).name != file_name]
                        prompts.append((title, content, 'Video', True, file_path))
                        seen_files.add(file_name)
        
        return prompts
    
    def load_sync_state(self) -> Dict:
        """載入同步狀態"""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"  警告：無法讀取狀態檔案: {e}")
        return {}
    
    def save_sync_state(self, state: Dict):
        """儲存同步狀態"""
        try:
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(state, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"  警告：無法儲存狀態檔案: {e}")
    
    def get_content_hash(self, content: str) -> str:
        """計算內容的雜湊值"""
        return hashlib.md5(content.encode('utf-8')).hexdigest()
    
    def get_notion_blocks(self, page_id: str) -> List[Dict]:
        """取得 Notion 頁面中的所有 blocks"""
        all_blocks = []
        next_cursor = None
        
        while True:
            if next_cursor:
                blocks = self.notion.blocks.children.list(
                    block_id=page_id,
                    start_cursor=next_cursor
                )
            else:
                blocks = self.notion.blocks.children.list(block_id=page_id)
            
            all_blocks.extend(blocks.get('results', []))
            
            next_cursor = blocks.get('next_cursor')
            if not next_cursor:
                break
        
        return all_blocks
    
    def update_block_color(self, block_id: str, is_shared: bool):
        """更新 block 的顏色"""
        try:
            # 先取得現有的 block 來獲取標題和 children
            block = self.notion.blocks.retrieve(block_id=block_id)
            if block['type'] == 'toggle':
                title_text = ""
                if block['toggle'].get('rich_text'):
                    title_text = ''.join([rt.get('text', {}).get('content', '') for rt in block['toggle']['rich_text']])
                
                rich_text = {
                    "type": "text",
                    "text": {"content": title_text}
                }
                
                if is_shared:
                    rich_text["annotations"] = {"color": "red"}
                else:
                    rich_text["annotations"] = {"color": "default"}
                
                # 更新時需要保留 children，否則會丟失內容
                update_data = {
                    "rich_text": [rich_text]
                }
                
                self.notion.blocks.update(
                    block_id=block_id,
                    toggle=update_data
                )
                return True
        except Exception as e:
            print(f"  ✗ 更新 block 顏色失敗: {e}")
            return False
    
    def incremental_sync(self, prompts: List[Tuple[str, str, str, bool, str]]) -> bool:
        """增量同步：只更新變動的部分"""
        try:
            page_id = self.get_existing_page()
            if not page_id:
                # 如果沒有頁面，使用完整同步
                return self.create_or_update_page_full(prompts)
            
            print(f"找到現有頁面 (ID: {page_id[:8]}...)，執行增量同步...")
            
            # 載入狀態
            state = self.load_sync_state()
            # 標準化狀態檔案中的路徑
            normalized_state = {}
            for file_path, block_id in state.get('file_to_block', {}).items():
                normalized_path = self.normalize_path(file_path)
                normalized_state[normalized_path] = block_id
            
            # 使用檔名（不含路徑）作為唯一標識，以處理檔案移動的情況
            current_prompts_by_name = {}
            current_prompts_by_path = {}
            for prompt in prompts:
                title, content, prompt_type, is_shared, file_path = prompt
                file_path = self.normalize_path(file_path)
                file_name = Path(file_path).name
                current_prompts_by_name[file_name] = prompt
                current_prompts_by_path[file_path] = prompt
            
            # 取得 Notion 中的所有 blocks
            notion_blocks = self.get_notion_blocks(page_id)
            notion_blocks_by_id = {block['id']: block for block in notion_blocks if block['type'] == 'toggle'}
            
            # 建立檔名到 block_id 的映射（使用檔名而非路徑，以處理檔案移動）
            name_to_block_id = {}
            path_to_block_id = {}
            for file_path, block_id in normalized_state.items():
                if block_id in notion_blocks_by_id:
                    file_name = Path(file_path).name
                    # 如果檔名已存在，使用第一個 block_id（避免重複）
                    if file_name not in name_to_block_id:
                        name_to_block_id[file_name] = block_id
                    path_to_block_id[file_path] = block_id
            
            changes = {
                'add': [],      # 新增的 prompt
                'update': [],   # 需要更新的 prompt（狀態變更或內容變更）
                'delete': []    # 需要刪除的 prompt
            }
            
            # 檢查需要新增或更新的 prompt
            for title, content, prompt_type, is_shared, file_path in prompts:
                file_path = self.normalize_path(file_path)
                content_hash = self.get_content_hash(content)
                file_name = Path(file_path).name
                
                # 先檢查檔名（處理檔案移動的情況）
                if file_name in name_to_block_id:
                    block_id = name_to_block_id[file_name]
                    # 找到對應的舊狀態（可能路徑不同）
                    old_state = None
                    old_file_path = None
                    for old_path, old_block_id in normalized_state.items():
                        if old_block_id == block_id:
                            old_file_path = old_path
                            old_state = state.get('prompts', {}).get(old_path, {})
                            # 如果找不到，嘗試找原始路徑
                            if not old_state:
                                for orig_path in state.get('file_to_block', {}).keys():
                                    if self.normalize_path(orig_path) == old_path:
                                        old_state = state.get('prompts', {}).get(orig_path, {})
                                        break
                            break
                    
                    if old_state:
                        old_is_shared = old_state.get('is_shared', False)
                        old_hash = old_state.get('content_hash', '')
                        
                        # 如果路徑變更、狀態變更或內容變更，需要更新
                        if old_file_path != file_path or old_is_shared != is_shared or old_hash != content_hash:
                            changes['update'].append((title, content, prompt_type, is_shared, file_path, block_id, old_file_path))
                elif file_path in path_to_block_id:
                    # 如果檔名不在但路徑在
                    block_id = path_to_block_id[file_path]
                    old_state = state.get('prompts', {}).get(file_path, {})
                    # 如果找不到，嘗試找原始路徑
                    if not old_state:
                        for orig_path in state.get('file_to_block', {}).keys():
                            if self.normalize_path(orig_path) == file_path:
                                old_state = state.get('prompts', {}).get(orig_path, {})
                                break
                    old_is_shared = old_state.get('is_shared', False) if old_state else False
                    old_hash = old_state.get('content_hash', '') if old_state else ''
                    
                    if old_is_shared != is_shared or old_hash != content_hash:
                        changes['update'].append((title, content, prompt_type, is_shared, file_path, block_id, file_path))
                else:
                    # 新檔案
                    changes['add'].append((title, content, prompt_type, is_shared, file_path))
            
            # 檢查需要刪除的 prompt（檢查所有舊的 block，看是否還存在於當前 prompt 中）
            # 使用標準化路徑和檔名來檢查
            for orig_file_path, block_id in state.get('file_to_block', {}).items():
                normalized_old_path = self.normalize_path(orig_file_path)
                file_name = Path(normalized_old_path).name
                # 如果檔名和路徑都不在當前 prompt 中，則需要刪除
                if file_name not in current_prompts_by_name and normalized_old_path not in current_prompts_by_path:
                    if block_id in notion_blocks_by_id:
                        changes['delete'].append((normalized_old_path, block_id))
            
            # 執行變更
            if not any(changes.values()):
                print("✓ 沒有變更，無需同步")
                return True
            
            # 刪除
            for file_path, block_id in changes['delete']:
                try:
                    self.notion.blocks.delete(block_id=block_id)
                    print(f"  ✓ 已刪除: {file_path}")
                except Exception as e:
                    print(f"  ✗ 刪除失敗 {file_path}: {e}")
            
            # 更新
            for update_item in changes['update']:
                if len(update_item) == 7:
                    title, content, prompt_type, is_shared, file_path, block_id, old_file_path = update_item
                else:
                    # 向後兼容
                    title, content, prompt_type, is_shared, file_path, block_id = update_item
                    old_file_path = file_path
                
                try:
                    old_file_path_normalized = self.normalize_path(old_file_path)
                    old_state = state.get('prompts', {}).get(old_file_path, {})
                    # 如果找不到，嘗試找標準化路徑
                    if not old_state:
                        for orig_path in state.get('prompts', {}).keys():
                            if self.normalize_path(orig_path) == old_file_path_normalized:
                                old_state = state.get('prompts', {}).get(orig_path, {})
                                break
                    old_is_shared = old_state.get('is_shared', False) if old_state else False
                    old_hash = old_state.get('content_hash', '') if old_state else ''
                    content_hash = self.get_content_hash(content)
                    
                    # 更新顏色（如果狀態變更）
                    if old_is_shared != is_shared:
                        self.update_block_color(block_id, is_shared)
                        print(f"  ✓ 已更新顏色: {title} ({'已分享' if is_shared else '未分享'})")
                    
                    # 更新內容（如果內容變更）
                    if old_hash != content_hash:
                        # 刪除舊 block 並創建新的
                        self.notion.blocks.delete(block_id=block_id)
                        new_block = self.create_toggle_block_with_content(title, content, is_shared)
                        result = self.notion.blocks.children.append(
                            block_id=page_id,
                            children=[new_block]
                        )
                        new_block_id = result['results'][0]['id'] if result.get('results') else None
                        if new_block_id:
                            # 更新映射
                            file_name = Path(file_path).name
                            name_to_block_id[file_name] = new_block_id
                            path_to_block_id[file_path] = new_block_id
                            # 移除舊的映射（如果路徑變更）
                            if old_file_path != file_path:
                                old_file_name = Path(old_file_path).name
                                if old_file_name in name_to_block_id and name_to_block_id[old_file_name] == block_id:
                                    del name_to_block_id[old_file_name]
                                if old_file_path in path_to_block_id:
                                    del path_to_block_id[old_file_path]
                        print(f"  ✓ 已更新內容: {title}")
                except Exception as e:
                    print(f"  ✗ 更新失敗 {file_path}: {e}")
            
            # 新增
            if changes['add']:
                blocks_to_add = []
                for title, content, prompt_type, is_shared, file_path in changes['add']:
                    toggle_block = self.create_toggle_block_with_content(title, content, is_shared)
                    blocks_to_add.append(toggle_block)
                
                # 分批添加
                batch_size = 100
                for i in range(0, len(blocks_to_add), batch_size):
                    batch = blocks_to_add[i:i+batch_size]
                    result = self.notion.blocks.children.append(
                        block_id=page_id,
                        children=batch
                    )
                    
                    # 更新映射
                    if result.get('results'):
                        batch_file_paths = [p[4] for p in changes['add'][i:i+batch_size]]
                        for j, block_id in enumerate([r['id'] for r in result['results']]):
                            if j < len(batch_file_paths):
                                file_path = batch_file_paths[j]
                                file_name = Path(file_path).name
                                name_to_block_id[file_name] = block_id
                                path_to_block_id[file_path] = block_id
                    
                    if i + batch_size < len(blocks_to_add):
                        print(f"  已添加 {i + batch_size}/{len(blocks_to_add)} 個 blocks...")
                
                print(f"  ✓ 已新增 {len(changes['add'])} 個 prompt")
            
            # 更新狀態（合併 path_to_block_id 和 name_to_block_id）
            final_file_to_block = {}
            for file_path, prompt in current_prompts_by_path.items():
                file_name = Path(file_path).name
                block_id = name_to_block_id.get(file_name) or path_to_block_id.get(file_path)
                if block_id:
                    final_file_to_block[file_path] = block_id
            
            new_state = {
                'file_to_block': final_file_to_block,
                'prompts': {}
            }
            
            for title, content, prompt_type, is_shared, file_path in prompts:
                content_hash = self.get_content_hash(content)
                file_name = Path(file_path).name
                block_id = name_to_block_id.get(file_name) or path_to_block_id.get(file_path) or final_file_to_block.get(file_path)
                if block_id:
                    new_state['prompts'][file_path] = {
                        'title': title,
                        'prompt_type': prompt_type,
                        'is_shared': is_shared,
                        'content_hash': content_hash,
                        'block_id': block_id
                    }
                    final_file_to_block[file_path] = block_id
            
            self.save_sync_state(new_state)
            
            total_changes = len(changes['add']) + len(changes['update']) + len(changes['delete'])
            print(f"\n✓ 增量同步完成！")
            print(f"  新增: {len(changes['add'])}, 更新: {len(changes['update'])}, 刪除: {len(changes['delete'])}")
            
            return True
            
        except Exception as e:
            print(f"✗ 增量同步失敗: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def create_or_update_page_full(self, prompts: List[Tuple[str, str, str, bool, str]]) -> bool:
        """完整同步：清空後重新同步（用於首次同步或狀態損壞時）"""
        try:
            page_id = self.get_existing_page()
            
            if page_id:
                print(f"找到現有頁面 (ID: {page_id[:8]}...)，清空現有內容...")
                self.clear_page_content(page_id)
                print("✓ 已清空現有內容")
            else:
                print(f"創建新頁面...")
                if self.database_id:
                    page = self.notion.pages.create(
                        parent={"database_id": self.database_id},
                        properties={
                            "Name": {
                                "title": [
                                    {
                                        "text": {
                                            "content": "AI Media Prompts"
                                        }
                                    }
                                ]
                            }
                        }
                    )
                    page_id = page['id']
                    print(f"✓ 已創建新頁面 (ID: {page_id})")
                else:
                    raise ValueError("需要提供 database_id 或 page_id")
            
            blocks = []
            file_to_block_id = {}
            
            for title, content, prompt_type, is_shared, file_path in prompts:
                toggle_block = self.create_toggle_block_with_content(title, content, is_shared)
                blocks.append(toggle_block)
            
            # 分批添加 blocks（Notion API 限制每次最多 100 個）
            batch_size = 100
            for i in range(0, len(blocks), batch_size):
                batch = blocks[i:i+batch_size]
                result = self.notion.blocks.children.append(
                    block_id=page_id,
                    children=batch
                )
                
                # 記錄 block_id
                if result.get('results'):
                    batch_file_paths = [p[4] for p in prompts[i:i+batch_size]]
                    for j, block_id in enumerate([r['id'] for r in result['results']]):
                        if j < len(batch_file_paths):
                            file_to_block_id[batch_file_paths[j]] = block_id
                
                if i + batch_size < len(blocks):
                    print(f"  已添加 {i + batch_size}/{len(blocks)} 個 blocks...")
            
            # 儲存狀態
            state = {
                'file_to_block': file_to_block_id,
                'prompts': {}
            }
            
            for title, content, prompt_type, is_shared, file_path in prompts:
                content_hash = self.get_content_hash(content)
                block_id = file_to_block_id.get(file_path)
                if block_id:
                    state['prompts'][file_path] = {
                        'title': title,
                        'prompt_type': prompt_type,
                        'is_shared': is_shared,
                        'content_hash': content_hash,
                        'block_id': block_id
                    }
            
            self.save_sync_state(state)
            
            print(f"✓ 已更新頁面，共添加 {len(blocks)} 個 prompt")
            return True
        
        except Exception as e:
            print(f"✗ 同步失敗: {e}")
            if "should be a valid uuid" in str(e).lower():
                print("\n提示：")
                print("  Page ID 或 Database ID 格式不正確")
                print("  請從 Notion 頁面的 URL 中提取正確的 ID")
                print("  例如：https://www.notion.so/workspace/2dab80218be180faa39efd22aebb31cf")
                print("  ID 是：2dab80218be180faa39efd22aebb31cf")
                print("  或者直接貼上完整 URL，腳本會自動提取")
            import traceback
            traceback.print_exc()
            return False
    
    def create_toggle_block(self, title: str, content: str) -> Dict:
        """創建 Notion toggle block（可展開的列表）"""
        return {
            "object": "block",
            "type": "toggle",
            "toggle": {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {
                            "content": title
                        }
                    }
                ],
                "children": [
                    {
                        "object": "block",
                        "type": "paragraph",
                        "paragraph": {
                            "rich_text": [
                                {
                                    "type": "text",
                                    "text": {
                                        "content": content
                                    }
                                }
                            ]
                        }
                    }
                ]
            }
        }
    
    def parse_rich_text(self, text: str) -> List[Dict]:
        """解析 Markdown 格式文字為 Notion rich text（支援連結、粗體、斜體）"""
        if not text:
            return []
        
        rich_text = []
        remaining = text
        
        while remaining:
            # 尋找所有可能的格式標記位置
            link_match = re.search(r'\[([^\]]+)\]\(([^)]+)\)', remaining)
            bold_match = re.search(r'\*\*([^*]+)\*\*', remaining)
            italic_match = re.search(r'(?<!\*)\*([^*]+)\*(?!\*)', remaining)
            
            # 找出最早出現的格式
            matches = []
            if link_match:
                matches.append(('link', link_match.start(), link_match))
            if bold_match:
                matches.append(('bold', bold_match.start(), bold_match))
            if italic_match:
                matches.append(('italic', italic_match.start(), italic_match))
            
            if not matches:
                # 沒有更多格式，添加剩餘文字
                if remaining:
                    rich_text.append({
                        "type": "text",
                        "text": {"content": remaining}
                    })
                break
            
            # 排序找出最早的匹配
            matches.sort(key=lambda x: x[1])
            match_type, match_pos, match = matches[0]
            
            # 添加格式前的普通文字
            if match_pos > 0:
                rich_text.append({
                    "type": "text",
                    "text": {"content": remaining[:match_pos]}
                })
            
            # 處理匹配的格式
            if match_type == 'link':
                link_text = match.group(1)
                link_url = match.group(2)
                rich_text.append({
                    "type": "text",
                    "text": {
                        "content": link_text,
                        "link": {"url": link_url}
                    }
                })
                remaining = remaining[match.end():]
            
            elif match_type == 'bold':
                bold_text = match.group(1)
                rich_text.append({
                    "type": "text",
                    "text": {"content": bold_text},
                    "annotations": {"bold": True}
                })
                remaining = remaining[match.end():]
            
            elif match_type == 'italic':
                italic_text = match.group(1)
                rich_text.append({
                    "type": "text",
                    "text": {"content": italic_text},
                    "annotations": {"italic": True}
                })
                remaining = remaining[match.end():]
        
        return rich_text if rich_text else [{"type": "text", "text": {"content": text}}]
    
    def text_to_blocks(self, text: str) -> List[Dict]:
        """將 Markdown 內容轉換為 Notion blocks（支援圖片、連結、格式）"""
        blocks = []
        lines = text.split('\n')
        i = 0
        
        while i < len(lines):
            line = lines[i].strip()
            
            # 跳過空行
            if not line:
                i += 1
                continue
            
            # 處理標題 ## 標題
            if line.startswith('##'):
                title_text = line.replace('##', '').strip()
                blocks.append({
                    "object": "block",
                    "type": "heading_2",
                    "heading_2": {
                        "rich_text": self.parse_rich_text(title_text)
                    }
                })
                i += 1
                continue
            
            # 處理圖片 ![alt](url) - 支援行內或獨立行
            image_match = re.search(r'!\[([^\]]*)\]\(([^)]+)\)', line)
            if image_match:
                alt_text = image_match.group(1)
                image_url = image_match.group(2)
                
                # 如果整行只有圖片，創建獨立的圖片 block
                if line.strip() == image_match.group(0).strip():
                    blocks.append({
                        "object": "block",
                        "type": "image",
                        "image": {
                            "type": "external",
                            "external": {
                                "url": image_url
                            },
                            "caption": self.parse_rich_text(alt_text) if alt_text else []
                        }
                    })
                    i += 1
                    continue
                else:
                    # 行內有圖片，先處理圖片前的文字，再添加圖片
                    before_image = line[:image_match.start()].strip()
                    after_image = line[image_match.end():].strip()
                    
                    if before_image:
                        blocks.append({
                            "object": "block",
                            "type": "paragraph",
                            "paragraph": {
                                "rich_text": self.parse_rich_text(before_image)
                            }
                        })
                    
                    blocks.append({
                        "object": "block",
                        "type": "image",
                        "image": {
                            "type": "external",
                            "external": {
                                "url": image_url
                            },
                            "caption": self.parse_rich_text(alt_text) if alt_text else []
                        }
                    })
                    
                    if after_image:
                        blocks.append({
                            "object": "block",
                            "type": "paragraph",
                            "paragraph": {
                                "rich_text": self.parse_rich_text(after_image)
                            }
                        })
                    
                    i += 1
                    continue
            
            # 處理段落（可能包含連結、粗體等格式）
            paragraph_text = line
            
            # 合併後續空行前的內容為一個段落
            j = i + 1
            while j < len(lines) and lines[j].strip() and not lines[j].strip().startswith('##') and not re.match(r'!\[.*\]\(.*\)', lines[j].strip()):
                paragraph_text += ' ' + lines[j].strip()
                j += 1
            
            rich_text = self.parse_rich_text(paragraph_text)
            if rich_text:
                blocks.append({
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": rich_text
                    }
                })
            
            i = j
        
        return blocks if blocks else [
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": self.parse_rich_text(text)
                }
            }
        ]
    
    def create_toggle_block_with_content(self, title: str, content: str, is_shared: bool = False) -> Dict:
        """創建帶有完整內容的 toggle block"""
        children = self.text_to_blocks(content)
        
        rich_text = {
            "type": "text",
            "text": {
                "content": title
            }
        }
        
        # 如果是 shared，設置為紅色
        if is_shared:
            rich_text["annotations"] = {"color": "red"}
        
        return {
            "object": "block",
            "type": "toggle",
            "toggle": {
                "rich_text": [rich_text],
                "children": children
            }
        }
    
    def get_existing_page(self) -> Optional[str]:
        """取得現有的 Notion 頁面 ID"""
        if self.page_id:
            return self.page_id
        
        if self.database_id:
            try:
                results = self.notion.databases.query(
                    database_id=self.database_id,
                    page_size=1
                )
                
                if results.get('results'):
                    return results['results'][0]['id']
                
                return None
            
            except Exception as e:
                print(f"  ✗ 查詢資料庫失敗: {e}")
                return None
        
        return None
    
    
    def clear_page_content(self, page_id: str) -> bool:
        """清空頁面內容（處理分頁情況）"""
        try:
            all_blocks = []
            next_cursor = None
            
            # 遍歷所有分頁，收集所有 blocks
            while True:
                if next_cursor:
                    blocks = self.notion.blocks.children.list(
                        block_id=page_id,
                        start_cursor=next_cursor
                    )
                else:
                    blocks = self.notion.blocks.children.list(block_id=page_id)
                
                all_blocks.extend(blocks.get('results', []))
                
                next_cursor = blocks.get('next_cursor')
                if not next_cursor:
                    break
            
            # 刪除所有非子頁面的 blocks
            for block in all_blocks:
                if block['type'] != 'child_page':
                    self.notion.blocks.delete(block_id=block['id'])
            
            return True
        
        except Exception as e:
            print(f"  ✗ 清空內容失敗: {e}")
            return False
    
    def sync(self, full_sync: bool = False):
        """執行同步（預設使用增量同步，只更新變動的部分）"""
        print("=" * 60)
        print("同步 Prompt 檔案到 Notion")
        print("=" * 60)
        
        prompts = self.get_all_prompts()
        if not prompts:
            print("✗ 沒有找到任何 prompt 檔案")
            return
        
        print(f"\n找到 {len(prompts)} 個 prompt 檔案")
        print("-" * 60)
        
        for title, _, prompt_type, is_shared, _ in prompts:
            status = "[已分享]" if is_shared else "[未分享]"
            print(f"  • {title} ({prompt_type}) {status}")
        
        print("-" * 60)
        
        if full_sync:
            print("\n執行完整同步（清空後重新同步）...")
            success = self.create_or_update_page_full(prompts)
        else:
            print("\n執行增量同步（只更新變動的部分）...")
            success = self.incremental_sync(prompts)
        
        if success:
            print("\n✓ 同步完成！")
        else:
            print("\n✗ 同步失敗")


def load_config(config_file: str = 'config/notion_config.json') -> Optional[Dict]:
    """載入設定檔"""
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"✗ 找不到設定檔: {config_file}")
        print("請先創建設定檔，參考 config/notion_config.example.json")
        return None


def main():
    parser = argparse.ArgumentParser(
        description='將 Git 中的 prompt 檔案同步到 Notion',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
範例:
  python sync_to_notion.py          # 增量同步（只更新變動的部分，推薦）
  python sync_to_notion.py --full   # 完整同步（清空後重新同步）
  
注意: 
  - 預設使用增量同步，只更新變動的部分，速度更快
  - 使用 --full 參數可強制完整同步（首次同步或狀態損壞時使用）
  - 需要先設定 Notion API Key 和 Database ID
        '''
    )
    parser.add_argument(
        '--full',
        action='store_true',
        help='執行完整同步（清空後重新同步）'
    )
    
    args = parser.parse_args()
    
    config = load_config()
    if not config:
        return
    
    api_key = config.get('api_key')
    database_id = config.get('database_id')
    page_id = config.get('page_id')
    
    if not api_key or api_key == "YOUR_NOTION_API_KEY_HERE":
        print("✗ 請在 config/notion_config.json 中設定有效的 api_key")
        print("  取得方式: https://www.notion.so/my-integrations")
        return
    
    if not database_id and not page_id:
        print("✗ 請在 config/notion_config.json 中設定 database_id 或 page_id")
        print("  Database ID 或 Page ID 可以在 Notion 頁面的 URL 中找到")
        return
    
    syncer = NotionSyncer(api_key, database_id=database_id, page_id=page_id)
    syncer.sync(full_sync=args.full)


if __name__ == "__main__":
    main()

