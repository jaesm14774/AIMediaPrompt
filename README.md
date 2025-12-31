# AIMediaPrompt

自動上傳圖片到 ImgBB 並插入 URL 到 prompt 檔案的工具。

## 功能說明

- 自動上傳 `Local_Media` 資料夾中的所有圖片到 ImgBB
- 將圖片 URL 插入到指定的 prompt 檔案中
- 支援多種圖片格式：PNG, JPG, JPEG, GIF, WEBP
- 將 Git 中的 prompt 檔案同步到 Notion（可展開列表格式）

## 使用方式

### 1. 設定 API Key

複製 `config/imgbb_config.example.json` 為 `config/imgbb_config.json`，並填入您的 ImgBB API Key。

取得 API Key: https://api.imgbb.com/

### 2. 準備圖片

將要上傳的圖片放入 `Local_Media` 資料夾中。

**注意：`Local_Media` 資料夾一次僅放一種型態的圖片**

### 3. 執行腳本

```bash
python scripts/auto_upload_imgbb.py <prompt檔案名稱>
```

**參數說明：**
- `prompt檔案名稱`: prompt 檔案名稱（不含副檔名，檔案格式為 .md）

**範例：**
```bash
# 中文檔名
python scripts/auto_upload_imgbb.py 貪吃蛇

# 英文檔名（含空格需加引號）
python scripts/auto_upload_imgbb.py "One leaf, one world"
```

### 4. 查看結果

腳本會自動：
- 上傳所有圖片到 ImgBB
- 將圖片 URL 插入到指定的 prompt 檔案末尾
- 第一張圖片會添加 `## 範例圖片` 標題

## 目錄結構

```
AIMediaPrompt/
├── Local_Media/          # 放置要上傳的圖片
├── Prompt/
│   ├── Image/            # prompt 檔案存放位置
│   │   └── shared/       # 已分享的 prompt（會以紅色標記）
│   └── Video/            # prompt 檔案存放位置
│       └── shared/       # 已分享的 prompt（會以紅色標記）
├── scripts/
│   ├── auto_upload_imgbb.py
│   ├── sync_to_notion.py
│   └── requirements.txt
├── config/
│   ├── imgbb_config.json
│   ├── imgbb_config.example.json
│   ├── notion_config.json
│   ├── notion_config.example.json
│   └── notion_sync_state.json
└── README.md
```

## Notion 同步功能

### 1. 設定 Notion API

複製 `config/notion_config.example.json` 為 `config/notion_config.json`，並填入：

- **API Key**: 在 https://www.notion.so/my-integrations 創建整合並取得 API Key
- **Database ID** (選填): 在 Notion 中創建一個 Database，從 URL 中取得 Database ID
  - 方法1：直接貼上完整 URL，腳本會自動提取 ID
    - 例如：`https://www.notion.so/workspace/2dab80218be180faa39efd22aebb31cf`
  - 方法2：從 URL 中手動提取最後一段（32 個字元）
    - URL 格式：`https://www.notion.so/workspace/xxxxxxxxxxxxxxxxxxxxxxxxxxxxx`
    - ID 格式：`xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx` 或 `xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`
- **Page ID** (選填): 如果要同步到現有頁面，提供 Page ID
  - 方法1：直接貼上完整 URL，腳本會自動提取 ID
  - 方法2：從頁面 URL 中取得，格式與 Database ID 相同
  - **如何找到 Page ID**：
    1. 在 Notion 中打開要同步的頁面
    2. 點擊右上角的「分享」或「...」選單
    3. 選擇「複製連結」或查看瀏覽器網址列
    4. URL 格式：`https://www.notion.so/頁面標題-2dab80218be180faa39efd22aebb31cf`
    5. ID 是 URL 中最後的 32 個字元（`2dab80218be180faa39efd22aebb31cf`）
  - **注意**: 必須提供 `database_id` 或 `page_id` 其中一個

### 2. 安裝依賴

```bash
pip install -r scripts/requirements.txt
```

### 3. 執行同步

```bash
# 增量同步（推薦，只更新變動的部分，速度快）
python scripts/sync_to_notion.py

# 完整同步（清空後重新同步，首次同步或狀態損壞時使用）
python scripts/sync_to_notion.py --full
```

**注意**：
- 預設使用增量同步，只更新變動的部分（新增、刪除、狀態變更），速度更快
- 使用 `--full` 參數可強制完整同步（首次同步或狀態檔案損壞時使用）
- 狀態檔案會儲存在 `config/notion_sync_state.json`，用於追蹤同步狀態

### 4. 同步結果

腳本會自動：
- 讀取 `Prompt/Image` 和 `Prompt/Video` 資料夾中的所有 .md 檔案
- 讀取 `Prompt/Image/shared`（或 `Shared`）和 `Prompt/Video/shared`（或 `Shared`）資料夾中的所有 .md 檔案
- 解析每個檔案的標題和內容
- 在 Notion 中創建可展開的列表（Toggle Block）
- 每個 prompt 以標題顯示，點擊可展開查看詳細內容
- **已分享的 prompt**（位於 shared 資料夾中）會以**紅色**標題顯示，方便區分已分享與未分享的內容

### 5. Markdown 格式支援

腳本支援以下 Markdown 格式轉換：

- **圖片**: `![alt](url)` → 顯示為 Notion 圖片 block
- **連結**: `[text](url)` → 轉換為可點擊的連結
- **粗體**: `**text**` → 顯示為粗體文字
- **斜體**: `*text*` → 顯示為斜體文字
- **標題**: `## 標題` → 顯示為二級標題

所有格式會自動轉換為對應的 Notion 格式，圖片會直接顯示，連結可以點擊。

## 注意事項

1. 每次執行時，`Local_Media` 資料夾中應只放置一種型態的圖片
2. 如果圖片 URL 已存在於 prompt 檔案中，會自動跳過
3. 確保 prompt 檔案（.md 格式）存在於 `Image` 或 `Video` 資料夾中
4. 圖片會依檔名排序後依序處理
5. Notion 同步會將所有 prompt 檔案同步到指定的 Database，包括：
   - `Prompt/Image` 和 `Prompt/Video` 資料夾下的檔案
   - `Prompt/Image/shared`（或 `Shared`）和 `Prompt/Video/shared`（或 `Shared`）資料夾下的檔案
6. 已分享的 prompt（位於 shared 資料夾中）會在 Notion 中以紅色標題顯示
7. 預設使用增量同步，只更新變動的部分（新增、刪除、狀態變更），速度更快，適合頻繁同步
8. 狀態檔案 `config/notion_sync_state.json` 會自動生成，用於追蹤同步狀態，請勿手動修改

