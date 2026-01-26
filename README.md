# AIMediaPrompt

自動上傳圖片與影片並插入 URL 到 prompt 檔案的工具。

## 功能說明

- **媒體上傳**：自動上傳 `Local_Media` 資料夾中的圖片到 ImgBB，影片到 Cloudinary。
- **自動插入**：將媒體 URL 插入到指定的 prompt 檔案中（支援 .md 格式）。
- **格式支援**：
  - 圖片：PNG, JPG, JPEG, GIF, WEBP, BMP
  - 影片：MP4, WEBM, MOV, AVI, MKV
- **Notion 同步**：將 Git 中的 prompt 檔案同步到 Notion（支援可展開列表格式與紅色標記已分享內容）。
- **自動發布**：整合 Facebook 自動發文功能與每日定時排程。

## 使用方式

### 1. 設定 API Key

#### 圖片上傳 (ImgBB)
1. 取得 API Key: https://api.imgbb.com/
2. 複製 `config/imgbb_config.example.json` 為 `config/imgbb_config.json` 並填入 Key。

#### 影片上傳 (Cloudinary)
1. 註冊帳號：https://cloudinary.com/users/register_free
2. 取得 **Cloud Name**, **API Key**, **API Secret**。
3. 複製 `config/cloudinary_config.example.json` 為 `config/cloudinary_config.json` 並填入資訊。

### 2. 安裝依賴

```bash
pip install -r requirements.txt
# 或手動安裝必要套件
pip install cloudinary requests
```

### 3. 準備媒體檔案

將要上傳的圖片或影片放入 `Local_Media` 資料夾中。
**注意：建議每次執行僅放一種型態或一個主題的媒體。**

### 4. 執行上傳腳本

```bash
# 上傳圖片或影片（腳本會自動偵測類型）
python scripts/auto_upload_media.py <prompt檔案名稱> [--env <環境>] [--type <類型>]
```

**參數說明：**
- `prompt檔案名稱`: prompt 檔案名稱（不含副檔名，檔案格式為 .md）
- `--env`: 環境變數，可選值：`dev`、`stg`、`test`、`prod`
  - `dev/stg/test`: 在 `Test/` 資料夾尋找並更新檔案（不移動檔案）。
  - `prod` 或不指定: 在 `Prompt/` 相關資料夾尋找並更新。若檔案在 `Test/` 會配合 `--type` 移動到對應目錄。
- `--type`: 類型，可選值：`image`、`video`（移動檔案時必填）。

**範例：**
```bash
# 上傳影片並更新 Test 中的檔案
python scripts/auto_upload_media.py "午睡危機" --env test --type video

# 正常發布流程（從 Test 移動到 Prompt/Image）
python scripts/auto_upload_media.py "睡眠戰場" --env prod --type image
```

---

## 🎯 支援的服務與限制

| 媒體類型 | 服務 | 限制 | 成本 |
|---------|-----|------|-----|
| **圖片** | ImgBB | 單檔 32MB | 免費 |
| **影片** | Cloudinary | 單檔 100MB, 25GB/月 | 免費 |
| **影片** | Imgur | 單檔 200MB (匿名限制) | 免費 |

---

## Gemini 圖片生成與發布流程

本專案採用高品質圖片生成與發布流程：

### 1. 原始畫質保證 (Original Quality)
所有透過 Gemini 生成的圖片**均不進行壓縮處理**，保留原始 PNG/JPG 畫質。

### 2. 嚴格品質篩選 (S-Grade Only)
只有達到 **S 級 (9.0-10.0 分)** 的內容才具備發布資格。

### 3. 執行指令
```bash
# 手動生成與發布
/auto-daily-publish --generate "主題" --platforms fb,notion
```

---

## 📅 每日自動發布排程 (Windows)

**1. 以管理員身份執行 PowerShell**
**2. 執行設定腳本**
```powershell
.\scripts\setup_scheduler.ps1 -Time "10:00" -Theme "AI主題" -Platforms "fb,notion"
```
**3. 管理任務**
- 查看：`Get-ScheduledTask -TaskName "AIMediaPrompt-DailyPublish"`
- 立即執行：`Start-ScheduledTask -TaskName "AIMediaPrompt-DailyPublish"`

---

## 📋 目錄結構

```
AIMediaPrompt/
├── Local_Media/          # 放置要上傳的媒體 (圖片/影片)
├── Test/                 # 測試用的 prompt 檔案
├── Prompt/
│   ├── Image/            # 圖片 prompt 存放位置
│   └── Video/            # 影片 prompt 存放位置
├── scripts/
│   ├── auto_upload_media.py  # 核心媒體上傳腳本
│   ├── sync_to_notion.py     # Notion 同步腳本
│   └── setup_scheduler.ps1   # 排程設定腳本
├── config/               # 配置文件 (ImgBB, Cloudinary, Notion)
└── README.md
```

---

## 🔗 Notion 同步功能

### 1. 設定 Notion API
1. 前往 [Notion Integrations](https://www.notion.so/my-integrations) 創建 Integration 並取得 Token。
2. 授權該 Integration 訪問您的 Database 或 Page。
3. 複製 `config/notion_config.example.json` 為 `config/notion_config.json` 並填入 `api_key` 與 `database_id` (或 `page_id`)。

### 2. 執行同步
```bash
# 增量同步（僅更新變動內容，速度快）
python scripts/sync_to_notion.py

# 完整同步（清空後重新上傳）
python scripts/sync_to_notion.py --full
```

---

## 🔍 常見問題與故障排除

### 媒體上傳問題
- **上傳失敗**：檢查 API Key、網路連線、以及檔案是否超過大小限制 (圖片 32MB / 影片 100MB)。
- **Cloudinary 錯誤**：確認 `pip install cloudinary` 已執行且配置正確。

### Notion 同步問題
- **404/Unauthorized**：確認 Notion 頁面已在「Connections」中加入該 Integration。
- **ID 格式錯誤**：直接貼上 Notion 頁面的完整 URL 即可，腳本會自動處理。

---

## ⚠️ 注意事項

1. **品質第一**：僅發布 S 級內容。
2. **自動清理**：`Local_Media` 處理完後會自動清空本機檔案。
3. **影片建議**：解析度 1080p 以下，格式 MP4 (H.264)，長度 5-10 秒為佳。

詳細內容請參閱代碼註釋與各腳本說明。
