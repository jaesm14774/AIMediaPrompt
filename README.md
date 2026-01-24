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
python scripts/auto_upload_imgbb.py <prompt檔案名稱> [--env <環境>] [--type <類型>]
```

**參數說明：**
- `prompt檔案名稱`: prompt 檔案名稱（不含副檔名，檔案格式為 .md）
- `--env`: 環境變數（可選），可選值：`dev`、`stg`、`test`、`prod`
  - `dev/stg/test`: 在 `Test/` 資料夾尋找並更新檔案（不移動檔案）。
  - `prod` 或不指定: 在 `Prompt/` 相關資料夾尋找並更新檔案。
  - 當使用 `--env prod` 且檔案位於 `Test/` 時，會配合 `--type` 自動移動到對應的 Prompt 資料夾。
- `--type`: 類型（可選），可選值：`image`、`video`
  - 當需要從 `Test/` 移動檔案到 `Prompt/` 時（即使用 `--env prod` 且檔案在 `Test/`）為必填。

**範例：**
```bash
# 基本用法（從 Prompt/Image 或 Prompt/Video 找檔案並更新）
python scripts/auto_upload_imgbb.py 睡眠戰場微型史詩

# 使用 prod 環境（如果檔案在 Test/ 則移動到 Prompt/Image 並更新；如果已在 Prompt/ 則直接更新）
python scripts/auto_upload_imgbb.py "睡眠戰場微型史詩" --env prod --type image

# Test 環境用法（僅在 Test/ 資料夾找檔案並更新，不移動）
python scripts/auto_upload_imgbb.py "Kirby-IP-Copy-Ability" --env dev
```

**環境功能說明：**
- **Production (prod 或未指定)**:
  - 優先檢查 `Test/` 是否有同名檔案。如果有，則根據 `--type` 將其移動到 `Prompt/Image` 或 `Prompt/Video`。
  - 如果 `Test/` 沒有，則直接在 `Prompt/` 子資料夾中搜尋並更新。
- **Testing (dev/stg/test)**:
  - 僅在 `Test/` 資料夾中尋找檔案並更新內容，**不會**將檔案移出 `Test/` 資料夾。

### 4. 查看結果

腳本會自動：
- 上傳所有圖片到 ImgBB
- 將圖片 URL 插入到指定的 prompt 檔案末尾
- 第一張圖片會添加 `## 範例圖片` 標題

## Gemini 圖片生成與發布流程

本專案採用高品質圖片生成與發布流程，核心原則如下：

### 1. 原始畫質保證 (Original Quality)
為了確保最佳視覺效果，所有透過 Gemini 生成的圖片**均不進行壓縮處理**。我們保留 Gemini 產出的原始畫質，跳過 WebP 或其他壓縮步驟，直接以 PNG/JPG 原始格式發布。

### 2. 嚴格品質篩選 (S-Grade Only)
我們對內容品質有極高要求，只有達到 **S 級 (9.0-10.0 分)** 的內容才具備發布資格。
- **S 級 (9.0-10.0)**: **唯一通過標準**，立即發布。
- **A 級 (8.0-8.9)**: 優秀但未達標，不予發布，需進一步優化。
- **B 級及以下**: 不予發布，建議重新生成。

### 3. 執行指令

```bash
# 完整自動化流程（自動生成、評估、發布）
/auto-daily-publish --generate "主題" --platforms fb,notion
```

### 4. 目錄結構更新

- `Local_Media/`: 存放原始畫質配圖。
- `.claude/skills/`: 包含各項自動化技能邏輯。
- `Post/shared/`: 僅存放通過 S 級評估並已發布的內容。

---

## 目錄結構

```
AIMediaPrompt/
├── Local_Media/          # 放置要上傳的圖片
├── Test/                 # 測試用的 prompt 檔案（使用 --env 時會從這裡找檔案）
├── Prompt/
│   ├── Image/            # prompt 檔案存放位置
│   │   └── Shared/      # 已分享的 prompt（會以紅色標記）
│   └── Video/            # prompt 檔案存放位置
│       └── Shared/      # 已分享的 prompt（會以紅色標記）
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

#### 步驟 1：創建 Notion Integration

1. 前往 https://www.notion.so/my-integrations
2. 點擊右上角的 **「+ New integration」** 按鈕
3. 填寫整合資訊：
   - **Name**: 輸入整合名稱（例如：`AI Media Prompt Syncer`）
   - **Logo** (選填): 可選擇上傳圖示
   - **Associated workspace**: 選擇要使用的 Notion 工作區
   - **Type**: 選擇 **「Internal」**（內部整合）
   - **Capabilities**: 確保勾選以下權限：
     - ✅ **Read content**
     - ✅ **Update content**
     - ✅ **Insert content**
4. 點擊 **「Submit」** 創建整合
5. 創建完成後，在整合頁面中找到 **「Internal Integration Token」**，複製這個 Token（這就是您的 API Key）
   - Token 格式類似：`secret_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

#### 步驟 2：創建 Notion Database 或選擇現有頁面

您有兩種方式可以選擇：

**方式 A：使用 Database（推薦，適合首次使用）**

1. 在 Notion 中創建一個新的頁面或打開現有頁面
2. 在頁面中輸入 `/database` 或點擊 **「+」** 按鈕，選擇 **「Table - Inline」** 或 **「Table - Full page」**
3. 創建 Database 後，點擊 Database 右上角的 **「...」** 選單
4. 選擇 **「Connections」** → 找到您剛才創建的 Integration → 點擊 **「Connect」** 授權訪問
5. 取得 Database ID：
   - 方法1（推薦）：複製 Database 的完整 URL，腳本會自動提取 ID
     - URL 格式：`https://www.notion.so/workspace/2dab80218be180faa39efd22aebb31cf`
   - 方法2：從 URL 中手動提取 ID
     - URL 格式：`https://www.notion.so/workspace/xxxxxxxxxxxxxxxxxxxxxxxxxxxxx`
     - ID 是 URL 中最後的 32 個字元（`2dab80218be180faa39efd22aebb31cf`）
     - 腳本會自動將 32 字元轉換為標準 UUID 格式（`xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`）

**方式 B：使用現有頁面**

1. 在 Notion 中打開要同步的頁面
2. 點擊頁面右上角的 **「...」** 選單
3. 選擇 **「Connections」** → 找到您創建的 Integration → 點擊 **「Connect」** 授權訪問
4. 取得 Page ID：
   - 方法1（推薦）：複製頁面的完整 URL，腳本會自動提取 ID
     - URL 格式：`https://www.notion.so/頁面標題-2dab80218be180faa39efd22aebb31cf`
   - 方法2：從瀏覽器網址列中取得
     - 打開頁面後，查看瀏覽器網址列
     - ID 是 URL 中最後的 32 個字元（`2dab80218be180faa39efd22aebb31cf`）

**重要提示**：
- 必須提供 `database_id` 或 `page_id` 其中一個（不能兩個都留空）
- 如果提供 `database_id`，腳本會在 Database 中創建新頁面
- 如果提供 `page_id`，腳本會直接更新該頁面的內容
- 無論使用哪種方式，都必須先授權 Integration 訪問該 Database 或 Page

#### 步驟 3：填寫配置文件

1. 複製 `config/notion_config.example.json` 為 `config/notion_config.json`
2. 打開 `config/notion_config.json`，填入以下資訊：

```json
{
  "api_key": "secret_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
  "database_id": "https://www.notion.so/workspace/2dab80218be180faa39efd22aebb31cf",
  "page_id": ""
}
```

**配置說明**：
- **api_key**: 貼上步驟 1 中取得的 Internal Integration Token
- **database_id**: 貼上 Database 的完整 URL 或 ID（如果使用 Database 方式）
- **page_id**: 貼上頁面的完整 URL 或 ID（如果使用 Page 方式）
  - 如果使用 `database_id`，可以將 `page_id` 留空
  - 如果使用 `page_id`，可以將 `database_id` 留空

**範例配置**：

使用 Database：
```json
{
  "api_key": "secret_abc123def456ghi789jkl012mno345pqr678stu901vwx234yz",
  "database_id": "https://www.notion.so/myworkspace/2dab80218be180faa39efd22aebb31cf",
  "page_id": ""
}
```

使用 Page：
```json
{
  "api_key": "secret_abc123def456ghi789jkl012mno345pqr678stu901vwx234yz",
  "database_id": "",
  "page_id": "https://www.notion.so/myworkspace/AI-Prompts-2dab80218be180faa39efd22aebb31cf"
}
```

**注意**：
- 可以直接貼上完整 URL，腳本會自動提取 ID
- ID 格式可以是 32 字元（無連字號）或標準 UUID 格式（有連字號），腳本會自動處理
- 確保 Integration 已經授權訪問對應的 Database 或 Page

#### 步驟 4：驗證設定

在執行同步前，請確認：
- ✅ API Key 已正確填入（以 `secret_` 開頭）
- ✅ Database ID 或 Page ID 已正確填入（至少填寫一個）
- ✅ Integration 已授權訪問對應的 Database 或 Page

如果設定有誤，執行同步時會顯示錯誤訊息，請根據錯誤訊息修正配置。

### 2. 安裝依賴

確保已安裝所需的 Python 套件：

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

**同步模式說明**：
- **增量同步**（預設）：只更新變動的部分（新增、刪除、內容變更、狀態變更），速度更快，適合頻繁同步
- **完整同步**（`--full`）：清空現有內容後重新同步所有檔案，適合首次同步或狀態檔案損壞時使用

**狀態檔案**：
- 狀態檔案會自動儲存在 `config/notion_sync_state.json`
- 用於追蹤每個檔案的同步狀態，包括內容雜湊值、是否已分享等
- 請勿手動修改此檔案，以免造成同步錯誤

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

## 常見問題與疑難排解

### ImgBB 上傳相關

**Q: 上傳失敗怎麼辦？**
- 檢查 API Key 是否正確
- 確認網路連線正常
- 檢查圖片檔案是否損壞
- 確認圖片格式是否支援（PNG, JPG, JPEG, GIF, WEBP）

**Q: 圖片 URL 重複插入怎麼辦？**
- 腳本會自動檢查，如果 URL 已存在會跳過
- 如需重新上傳，請先手動刪除檔案中的舊 URL

### Notion 同步相關

**Q: 出現 "should be a valid uuid" 錯誤？**
- 檢查 Database ID 或 Page ID 格式是否正確
- 可以直接貼上完整 URL，腳本會自動提取 ID
- 確認 ID 是 32 個字元（可能包含連字號）

**Q: 出現 "object_not_found" 或 "unauthorized" 錯誤？**
- 確認 Integration 已授權訪問對應的 Database 或 Page
- 在 Notion 中打開 Database/Page → 點擊右上角「...」→ 「Connections」→ 確認 Integration 已連接

**Q: 同步後 Notion 中沒有內容？**
- 確認 prompt 檔案存在於正確的資料夾中
- 檢查檔案格式是否為 `.md`
- 確認檔案內容不為空
- 嘗試使用 `--full` 參數執行完整同步

**Q: 已分享的 prompt 沒有顯示為紅色？**
- 確認檔案位於 `shared` 或 `Shared` 資料夾中
- 執行增量同步以更新顏色狀態

**Q: 如何重新同步所有內容？**
- 使用 `--full` 參數執行完整同步
- 或刪除 `config/notion_sync_state.json` 後重新執行同步

## 注意事項

### ImgBB 上傳功能

1. 每次執行時，`Local_Media` 資料夾中應只放置一種型態的圖片
2. 如果圖片 URL 已存在於 prompt 檔案中，會自動跳過
3. 確保 prompt 檔案（.md 格式）存在於以下位置之一：
   - `Prompt/Image` 或 `Prompt/Video` 資料夾
   - `Prompt/Image/Shared` 或 `Prompt/Video/Shared` 資料夾
   - `Test/` 資料夾（使用 `--env` 參數時）
4. 使用 `--env prod` 和 `--type` 參數時，檔案會自動從 `Test/` 移動到對應的 Prompt 資料夾
5. 圖片會依檔名排序後依序處理
6. 支援的圖片格式：PNG, JPG, JPEG, GIF, WEBP

### Notion 同步功能

1. Notion 同步會將所有 prompt 檔案同步到指定的 Database 或 Page，包括：
   - `Prompt/Image` 和 `Prompt/Video` 資料夾下的檔案
   - `Prompt/Image/shared`（或 `Shared`）和 `Prompt/Video/shared`（或 `Shared`）資料夾下的檔案
2. 已分享的 prompt（位於 shared 資料夾中）會在 Notion 中以**紅色**標題顯示
3. 預設使用增量同步，只更新變動的部分（新增、刪除、內容變更、狀態變更），速度更快，適合頻繁同步
4. 狀態檔案 `config/notion_sync_state.json` 會自動生成，用於追蹤同步狀態，請勿手動修改
5. 如果檔案從未分享移動到 shared 資料夾（或相反），會自動更新顏色標記
6. 支援的 Markdown 格式會自動轉換為 Notion 格式（圖片、連結、粗體、斜體、標題）

## Gemini 圖片生成功能

此工具可以使用 Gemini Web 介面自動生成圖片。

### 執行方式

```bash
npx -y bun .claude/skills/generate-image/scripts/main.ts --prompt "你的圖片描述" --image "輸出路徑.png"
```

**參數說明：**
- `--prompt`, `-p`: 圖片描述。
- `--image`: 輸出路徑（預設為 `generated.png`）。

**主要更新：**
- **修正圖片定位邏輯**：不再依賴不穩定的 CSS 選擇器，改為直接使用偵測到的圖片 URL 定位元素，提高截圖成功率。
- **優化捲動行為**：使用 `instant` 捲動模式，避免動畫延遲導致的截圖偏差。
- **增強渲染檢查**：加入寬高偵測，確保圖片完全渲染後才進行截圖。

### Facebook 自動發文功能 (post-to-fb)

此工具使用 Chrome DevTools Protocol (CDP) 自動發布內容到 Facebook 粉專或個人頁面，可繞過反自動化機制並保持登入狀態。

#### 執行方式

```bash
# 基本發布（預覽模式）
npx -y bun .claude/skills/post-to-fb/scripts/fb-browser.ts "貼文內容" --target personal

# 發布到粉專並上傳圖片（正式發布）
npx -y bun .claude/skills/post-to-fb/scripts/fb-browser.ts "貼文內容" --image "path/to/img.png" --target page --page-name "你的粉專名稱" --submit
```

**參數說明：**
- `[內容]`: 貼文文字內容。
- `--image`: 配圖路徑（可多次使用，最多 4 張）。
- `--target`: `page` (粉專) 或 `personal` (個人)。
- `--page-name`: 當 target 為 page 時，指定粉專名稱或 ID。
- `--submit`: 實際執行點擊「發布」按鈕。如果不加此參數，則停留在發布預覽介面。
- `--profile`: 指定自定義 Chrome Profile 路徑（預設儲存於 AppData）。

**主要特點：**
- **繞過偵測**：連接真實 Chrome 瀏覽器，非無頭模式 (Headless)，安全性更高。
- **自動上傳**：修正了 CDP 檔案上傳邏輯，支援自動附加圖片。
- **持久化登入**：第一次手動登入後，後續執行會自動載入 Session。


