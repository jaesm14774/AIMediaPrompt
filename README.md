# AIMediaPrompt

自動上傳圖片與影片到雲端，並同步至 Notion 與 Facebook 的工具。

## 目錄

- [快速開始](#快速開始)
- [支援的媒體格式與服務限制](#支援的媒體格式與服務限制)
- [設定 API 金鑰](#設定-api-金鑰)
- [上傳媒體到雲端](#上傳媒體到雲端)
- [同步內容到 Notion](#同步內容到-notion)
- [使用 Cursor Subagent 執行自動化](#使用-cursor-subagent-執行自動化)
- [設定每日自動發布排程](#設定每日自動發布排程)
- [目錄結構](#目錄結構)
- [常見問題](#常見問題)

---

## 快速開始

```bash
# 1. 安裝依賴
pip install -r requirements.txt

# 2. 設定 API 金鑰（複製範例檔並填入）
cp config/imgbb_config.example.json config/imgbb_config.json
cp config/cloudinary_config.example.json config/cloudinary_config.json

# 3. 將媒體放入 Local_Media/ 資料夾

# 4. 執行上傳
python scripts/auto_upload_media.py <prompt檔案名稱> --type image
```

---

## 支援的媒體格式與服務限制

| 媒體類型 | 支援格式 | 上傳服務 | 大小限制 | 費用 |
|---------|---------|---------|---------|-----|
| 圖片 | PNG, JPG, JPEG, GIF, WEBP, BMP | ImgBB | 32MB | 免費 |
| 影片 | MP4, WEBM, MOV, AVI, MKV | Cloudinary | 100MB, 25GB/月 | 免費 |
| 影片 | MP4, WEBM, MOV, AVI, MKV | Imgur | 200MB（匿名限制） | 免費 |

**影片建議**：解析度 1080p 以下，格式 MP4 (H.264)，長度 5-10 秒。

---

## 設定 API 金鑰

### 圖片上傳需要 ImgBB API Key

1. 前往 https://api.imgbb.com/ 取得 API Key
2. 複製設定檔並填入金鑰：

```bash
cp config/imgbb_config.example.json config/imgbb_config.json
```

### 影片上傳需要 Cloudinary 憑證

1. 註冊帳號：https://cloudinary.com/users/register_free
2. 取得 **Cloud Name**、**API Key**、**API Secret**
3. 複製設定檔並填入：

```bash
cp config/cloudinary_config.example.json config/cloudinary_config.json
```

### Notion 同步需要 Integration Token

1. 前往 [Notion Integrations](https://www.notion.so/my-integrations) 創建 Integration
2. 在目標 Database 或 Page 的「Connections」中加入該 Integration
3. 複製設定檔並填入 `api_key` 與 `database_id`：

```bash
cp config/notion_config.example.json config/notion_config.json
```

---

## 上傳媒體到雲端

### 基本指令

```bash
python scripts/auto_upload_media.py <prompt檔案名稱> [--env <環境>] [--type <類型>]
```

### 參數說明

| 參數 | 說明 | 可選值 |
|-----|------|-------|
| `prompt檔案名稱` | Prompt 檔案名稱（不含 .md 副檔名） | - |
| `--env` | 執行環境 | `dev`, `stg`, `test`, `prod`（預設） |
| `--type` | 媒體類型（移動檔案時必填） | `image`, `video` |

### 環境差異

| 環境 | 檔案搜尋位置 | 處理後行為 |
|-----|------------|----------|
| `dev` / `stg` / `test` | `Test/` 資料夾 | 原地更新，不移動檔案 |
| `prod`（預設） | `Prompt/` 相關資料夾 | 依 `--type` 移動至對應目錄 |

### 使用範例

```bash
# 測試環境：上傳影片並更新 Test/ 中的檔案
python scripts/auto_upload_media.py "午睡危機" --env test --type video

# 正式環境：從 Test/ 移動到 Prompt/Image/ 並上傳
python scripts/auto_upload_media.py "睡眠戰場" --env prod --type image
```

**注意**：`Local_Media/` 處理完成後會自動清空。建議每次僅放同一主題的媒體。

---

## 同步內容到 Notion

### 增量同步（僅更新變動內容）

```bash
python scripts/sync_to_notion.py
```

### 完整同步（清空後重新上傳）

```bash
python scripts/sync_to_notion.py --full
```

同步功能支援可展開列表格式，並以紅色標記已分享內容。

---

## 使用 Cursor Subagent 執行自動化

### 媒體自動化專家 (Media Automation Expert)

在 Cursor 中輸入 `@media-automation-expert` 並描述任務，即可啟動端到端的媒體創作流程。

**工作流程**：

| 階段 | 執行內容 |
|-----|---------|
| Phase 1 內容創作 | Research → Generate → Evaluate → Tutorial |
| Phase 2 圖片處理 | Generate Image（保持原始畫質） |
| Phase 3 發布 | Viral Score → Post to FB → Upload Media → Sync Notion |

**品質標準**：僅 S 級（9.0 分以上）內容才能發布。所有輸出使用繁體中文。

### 每日自動發布指令

```bash
/auto-daily-publish [選項]
```

| 參數 | 說明 | 預設值 |
|-----|------|-------|
| `--generate <主題>` | 生成新內容後發布 | - |
| `--platforms <平台>` | 目標平台（逗號分隔） | `fb,notion` |
| `--min-score <分數>` | 最低發布分數 | `9.0` |
| `--max-posts <數量>` | 每次最多發布數量 | `1` |
| `--page-name <名稱>` | FB 粉絲專頁名稱 | - |
| `--dry-run` | 模擬執行，不實際發布 | - |

**範例**：

```bash
# 生成新主題並發布到 FB 與 Notion
/auto-daily-publish --generate "貓咪辦公" --platforms fb,notion --page-name "AI Art Lab"

# 僅發布 Post/Test/ 中已達標的內容
/auto-daily-publish --platforms fb,notion --page-name "AI Art Lab"

# 模擬執行檢查流程
/auto-daily-publish --dry-run
```

**自動化流程**：

1. 讀取 `Post/Test/` 檔案（或以 `--generate` 即時生成）
2. 調用 `/generate-image` 生成配圖
3. 調用 `/viral-score` 評分，僅 S 級進入發布佇列
4. 發布到 Facebook 與 Notion
5. 完成後將檔案從 `Post/Test/` 移動至 `Post/shared/`

---

## 設定每日自動發布排程

### Windows 排程設定

以管理員身份執行 PowerShell：

```powershell
.\scripts\setup_scheduler.ps1 -Time "10:00" -Theme "AI主題" -Platforms "fb,notion"
```

### 管理排程任務

```powershell
# 查看任務
Get-ScheduledTask -TaskName "AIMediaPrompt-DailyPublish"

# 立即執行
Start-ScheduledTask -TaskName "AIMediaPrompt-DailyPublish"
```

---

## 目錄結構

```
AIMediaPrompt/
├── Local_Media/              # 放置待上傳的媒體
├── Test/                     # 測試用 prompt 檔案
├── Prompt/
│   ├── Image/                # 圖片 prompt
│   └── Video/                # 影片 prompt
├── Post/
│   ├── Test/                 # 待發布內容
│   └── shared/               # 已發布內容
├── scripts/
│   ├── auto_upload_media.py  # 媒體上傳腳本
│   ├── sync_to_notion.py     # Notion 同步腳本
│   └── setup_scheduler.ps1   # 排程設定腳本
├── config/                   # API 設定檔
└── README.md
```

---

## 常見問題

### 媒體上傳失敗

| 問題 | 解決方案 |
|-----|---------|
| API 驗證錯誤 | 檢查 `config/` 下的 API Key 是否正確 |
| 檔案太大 | 圖片需小於 32MB，影片需小於 100MB |
| Cloudinary 錯誤 | 執行 `pip install cloudinary` 確認安裝 |

### Notion 同步失敗

| 問題 | 解決方案 |
|-----|---------|
| 404 / Unauthorized | 確認頁面已在「Connections」中加入 Integration |
| ID 格式錯誤 | 直接貼上 Notion 頁面完整 URL，腳本會自動處理 |
