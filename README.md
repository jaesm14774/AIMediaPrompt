# AIMediaPrompt

`AIMediaPrompt` 用 Claude skills 與本機 Python 腳本，把一個主題一路轉成 `Prompt`、`Post`、圖片或影片、雲端 URL，最後再手動發布到社群平台。

這份 README 是專案的單一入口。你可以用它快速理解三件事：什麼時候該用 `/skill`、什麼時候該跑 `python scripts/...`、以及檔案會在專案中如何流動。

## 先看最重要的 6 件事

- `/full-pipeline` 是標準主流程，負責從主題走到**媒體上傳完成**。
- `/full-pipeline` 的終點**不是自動發布**。發布要另外執行 `python scripts/publish_to_social.py`。
- `/xxx` 是在 Cursor / Claude 內執行的 **skill**。`python scripts/...` 是本機直接執行的 **腳本**。
- 圖片流程固定產生 **4 個** imagine prompts；影片流程固定產生 **2 個** imagine prompts。
- 影片不可直接文字生影片。標準做法是 **先生成 reference 圖，再用圖生影片**。
- 品質門檻以 **S 級 9.0+** 為準。未達標就繼續優化，不直接發布。

## 目錄

- [先選擇你要走哪一條入口](#先選擇你要走哪一條入口)
- [用 5 分鐘完成環境設定](#用-5-分鐘完成環境設定)
- [理解完整流程最不容易用錯](#理解完整流程最不容易用錯)
- [在 Cursor 中使用這些 skills](#在-cursor-中使用這些-skills)
- [直接執行這些 Python 腳本](#直接執行這些-python-腳本)
- [知道資料夾如何流動最不容易出錯](#知道資料夾如何流動最不容易出錯)
- [遵守這些品質與命名規則](#遵守這些品質與命名規則)
- [支援格式與服務限制](#支援格式與服務限制)
- [常見問題先從這裡排查](#常見問題先從這裡排查)

## 先選擇你要走哪一條入口

先決定你現在要解的是哪一類問題，再選指令會最快。

| 你的目標 | 建議入口 | 你會得到什麼 |
|------|------|------|
| 從主題一路做到媒體上傳 | `/full-pipeline "主題"` | 研究、Prompt、Post、媒體、URL |
| 只先把內容做出來 | `/auto-produce-prompt "主題"` | 2 個達標主題與教學文 |
| 已有 Template，想展開成多個生成 prompt | `/imagine-prompt "Template.md"` | 圖片 4 個 / 影片 2 個衍生 prompt |
| 已有 prompt，想直接生圖或生影片 | `python scripts/generate_media_gemini.py ...` | `Local_Media/<Template>/` 下的媒體 |
| 已有媒體，想把 URL 寫回 Prompt | `python scripts/auto_upload_media.py ...` | 上傳後的雲端 URL |
| 已有 Post 與媒體，想發布到社群 | `python scripts/publish_to_social.py ...` | 發布結果與 shared 歸檔 |
| 想同步 Prompt 到 Notion | `python scripts/sync_to_notion.py` | Notion 資料庫或頁面內容 |

## 用 5 分鐘完成環境設定

先安裝依賴，再把需要的設定檔複製出來。

```bash
pip install -r requirements.txt

cp config/imgbb_config.example.json config/imgbb_config.json
cp config/cloudinary_config.example.json config/cloudinary_config.json
cp config/notion_config.example.json config/notion_config.json
cp config/gemini_config.example.json config/gemini_config.json
```

把設定檔中的範例值改成真實金鑰後，再開始跑流程。

### 你需要準備哪些金鑰

| 功能 | 設定檔或來源 | 必要欄位 |
|------|------|------|
| Gemini 圖片 / 影片生成 | `config/gemini_config.json` 或 `GEMINI_API_KEY` 環境變數 | `api_key` |
| 圖片上傳到 ImgBB | `config/imgbb_config.json` | `api_key` |
| 影片上傳到 Cloudinary | `config/cloudinary_config.json` | `cloud_name`、`api_key`、`api_secret` |
| Notion 同步 | `config/notion_config.json` | `api_key`、`database_id` 或 `page_id` |

### Windows 使用者先設定 UTF-8 會比較穩

Windows 執行 Python 腳本時，建議先設定 UTF-8，避免繁體中文輸出遇到編碼問題。

```powershell
$env:PYTHONIOENCODING="utf-8"
```

如果你使用 bash，等價做法如下：

```bash
export PYTHONIOENCODING=utf-8
```

## 理解完整流程最不容易用錯

`/full-pipeline` 是專案的主流程。它負責把主題變成可用內容與媒體，但**社群發布仍是手動步驟**。

```mermaid
graph TD
    A[輸入主題] --> B[/research-keyword]
    B --> C[/generate-prompt]
    C --> D{/evaluate-prompt<br/>是否達 9.0+}
    D -- 否 --> E[依建議優化後重跑<br/>最多 3 次]
    E --> D
    D -- 是 --> F[/create-tutorial]
    F --> G[/imagine-prompt]
    G --> H{媒體類型}
    H -- image --> I[generate_media_gemini.py x 4]
    H -- video --> J[先生成 2 張 reference 圖]
    J --> K[再生成 2 支影片]
    I --> L[/viral-score]
    K --> L
    L --> M[auto_upload_media.py]
    M --> N[手動執行 publish_to_social.py]
```

### Phase 1 先把內容做對

Phase 1 的責任是產出高品質 Prompt 與教學文。

1. `/research-keyword` 研究主題，必要時將結果存到 `research/<keyword>/<date>.md`。
2. `/generate-prompt` 產出 Prompt Template。
3. `/evaluate-prompt` 評估 Template。未達 S 級就優化，最多 3 次。
4. `/create-tutorial` 把達標內容整理成 Post / 教學文。

如果你不想手動逐步跑，直接用 `/auto-produce-prompt "主題"` 即可。這個 skill 會自動生成 **2 個差異明顯的主題方向**，並各自完成評估與優化。

### Phase 2 再把媒體做出來

Phase 2 的責任是把 Template 展開成可直接餵給模型的生成 prompt，並產出媒體。

- 圖片流程：`/imagine-prompt` 固定生成 **4 個** prompt，再執行 `generate_media_gemini.py` 四次。
- 影片流程：`/imagine-prompt` 固定生成 **2 個** prompt，先生成 **2 張 reference 圖**，再各自生成 **2 支影片**。
- `generate_media_gemini.py --type video` 必須搭配 reference image。腳本也會檢查這件事。

### Phase 3 先過品質關卡，再寫回 URL

Phase 3 會評估 Post 的社群潛力，再把媒體上傳並回填 URL。

- `/viral-score` 評估的是 **Post 成品**，不是 Prompt Template。
- `auto_upload_media.py` 會把圖片上傳到 ImgBB、影片上傳到 Cloudinary，然後把 URL 插回對應 Prompt 檔。
- README 以專案品質規則為準：**S 級內容才是正式發布標準**。

### 媒體流程允許部分成功

媒體生成遇到 API 限速、暫時錯誤或單筆失敗時，流程不應回頭卡死。

- 圖片流程只要有部分圖片成功，就保留成功結果並繼續。
- 影片流程只要有部分 reference 圖成功，就只對成功的項目繼續生影片。
- 只有當前階段**全部失敗**時，才需要重試或改為人工介入。

## 在 Cursor 中使用這些 skills

如果你主要在 Cursor / Claude 內工作，先記住下表就夠了。

| Skill | 用途 | 典型輸入 | 典型輸出 |
|------|------|------|------|
| `/research-keyword` | 研究主題、整理背景資訊 | 主題或 IP | `research/` 研究筆記 |
| `/generate-prompt` | 產出 Prompt Template | 類型 + 主題 | Template 草稿 |
| `/evaluate-prompt` | 評估 Template 品質 | Template 檔名 | 分數與優化建議 |
| `/create-tutorial` | 產出教學文 / Post | 達標 Template | `Post/` 內容 |
| `/auto-produce-prompt` | 自動跑完研究到教學文 | 主題 | 2 個達標方向 |
| `/imagine-prompt` | 只替換 Template 佔位符 | `Template.md` | 圖片 4 個 / 影片 2 個 prompt |
| `/viral-score` | 評估 Post 的傳播潛力 | `Post/...md` | S/A/B/C/D 分級 |
| `/full-pipeline` | 跑完整主流程到媒體上傳 | 主題 | Prompt、Post、媒體、URL |
| `/video-frames` | 用 ffmpeg 抽幀或短片段 | 影片檔案 | 影格或片段 |

### 另外還有幾個輔助型 skill

這些 skill 不是每天都會用到，但在補流程或維運時很有幫助。

| Skill | 主要用途 |
|------|------|
| `/generate-image` | 從描述或檔案自動產圖，必要時再接影片流程 |
| `publish_to_social.py` | 手動發布已完成內容到社群平台（需先通過 viral-score S 級） |
| `/auto-daily-publish` | 處理待發布內容的篩選、評分與發布流程 |
| `/health` | 檢查專案的 Claude Code 設定健康度 |

### `imagine-prompt` 的規則要特別記住

`/imagine-prompt` 不是重寫整份 Template，而是**只替換佔位符**。

- 來源在 `Prompt/Image*` 時，固定產生 4 個不同方向的 prompt。
- 來源在 `Prompt/Video*` 時，固定產生 2 個不同方向的 prompt。
- Template 中佔位符以外的固定文字，應維持不變。

### `viral-score` 和 `evaluate-prompt` 不是同一件事

這兩個 skill 很容易混淆，但職責不同。

| Skill | 評估對象 | 所在階段 | 核心問題 |
|------|------|------|------|
| `/evaluate-prompt` | Prompt Template | Phase 1 | 這個 Template 能不能穩定產出好作品 |
| `/viral-score` | Post 成品 | Phase 3 | 這篇內容發出去有沒有擴散潛力 |

## 直接執行這些 Python 腳本

如果你已經知道自己要做哪一步，直接跑腳本通常最快。

### 用 `generate_media_gemini.py` 生成圖片或影片

這支腳本會使用 Gemini 生成圖片，或使用 Veo 類模型生成影片。

```bash
# 生成圖片
python scripts/generate_media_gemini.py --prompt "..." --template "TemplateName" --index 1 --type image

# 先有 reference 圖後，再生成影片
python scripts/generate_media_gemini.py --prompt "..." --template "TemplateName" --index 1 --type video --reference-image "Local_Media/TemplateName/01.png"
```

重點規則如下：

- `--template` 會自動把輸出放到 `Local_Media/<TemplateName>/`。
- 圖片預設輸出為 `01.png`、`02.png` 這種序號命名。
- 影片預設輸出為 `01.mp4`、`02.mp4`。
- 若沒有 reference image，影片生成會直接報錯停止。

### 用 `auto_upload_media.py` 把 URL 寫回 Prompt

```bash
# 正式環境：若來源在 Test/，需要指定 --type 才能移到 Prompt/
python scripts/auto_upload_media.py "TemplateName" --env prod --type image --folder "TemplateName"

# 測試環境：只更新 Test/ 內檔案，不移動
python scripts/auto_upload_media.py "TemplateName" --env test --type video --folder "TemplateName"
```

這支腳本的行為重點如下：

- 圖片上傳到 ImgBB，影片上傳到 Cloudinary。
- `--folder` 很重要。它能把操作範圍限制在 `Local_Media/<folder>/`，避免不同 Template 互相干擾。
- `--env prod` 且來源檔在 `Test/` 時，必須加 `--type image` 或 `--type video`，腳本才能決定移到哪個目錄。
- 這支腳本會把 URL 插入檔案，但不以「清空整個 `Local_Media/`」為前提。

### 用 `publish_to_social.py` 手動發布到社群

```bash
# 推薦：用 --template 鎖定對應媒體資料夾
python scripts/publish_to_social.py "2026-04-03-Kirby-越南大戰坦克兵" --template "Kirby-越南大戰坦克兵" --platforms fb

# 同時發 Facebook 與 Twitter
python scripts/publish_to_social.py "PostFile" --template "TemplateName" --platforms fb,twitter

# 先看結果，不實際發布
python scripts/publish_to_social.py "PostFile" --template "TemplateName" --dry-run
```

這支腳本的行為重點如下：

- 預設平台是 `fb,twitter`。
- `--template` 優先於 `--media-dir`，也是更安全的寫法。
- 發布成功後，只會清理指定 Template 對應的媒體資料夾，不會動到其他 Template 的媒體。
- 若未指定 `--no-move`，發布後會把 Post / Prompt 移到對應的 `shared/` 目錄。

### 用 `sync_to_notion.py` 同步 Prompt 到 Notion

```bash
# 增量同步
python scripts/sync_to_notion.py

# 完整同步
python scripts/sync_to_notion.py --full
```

第一次接 Notion 時，先確認目標頁面或資料庫已經加上你的 Integration。

## 知道資料夾如何流動最不容易出錯

專案最常見的錯誤不是指令寫錯，而是搞錯檔案現在應該在哪裡。

### 核心資料夾

```text
AIMediaPrompt/
├── Prompt/
│   ├── Image/
│   ├── Video/
│   ├── Image/shared/
│   └── Video/shared/
├── Post/
│   ├── Test/
│   └── shared/
├── Test/
├── Local_Media/
├── research/
├── scripts/
├── config/
└── .claude/skills/
```

### 檔案在流程中如何移動

| 類型 | 起點 | 後續位置 | 說明 |
|------|------|------|------|
| 研究結果 | `research/<keyword>/<date>.md` | 通常保留原地 | 提供後續生成參考 |
| Prompt Template 測試稿 | `Test/*.md` | `Prompt/Image/` 或 `Prompt/Video/` | `auto_upload_media.py --env prod --type ...` 會處理移動 |
| 媒體檔 | `Local_Media/<TemplateName>/` | 依流程上傳 / 發布後清理 | 建議每個 Template 分資料夾 |
| Post | `Post/*.md` 或 `Post/Test/*.md` | `Post/shared/` | 發布成功後歸檔 |
| 已發布 Prompt | `Prompt/Image/*.md` 或 `Prompt/Video/*.md` | 對應 `shared/` | 發布成功後歸檔 |

## 遵守這些品質與命名規則

這些規則不是裝飾。它們會直接影響檔案命名、skill 行為和發布品質。

### 內容品質以 S 級為準

- Prompt 評估門檻：`9.0+`
- Viral Score 門檻：`9.0+`
- 單一主題最多優化：`3` 次
- 未達標時：繼續優化，必要時標記人工介入

### 檔名與語言要一致

- 所有中文輸出一律使用**繁體中文**。
- Post 檔名格式：`YYYY-MM-DD-[Name].md`
- Prompt 與 Post 的檔名語言要一致，不要一個中文、一個英文。
- Template 預設應保留 `[IP角色]` 這種可替換寫法。只有當主題與某個 IP 高度綁定時，才直接寫死角色。

### 發布節奏也有規則

- 預設 Facebook 粉專名稱：`AI Art Lab`
- 每日建議發布量：`3-5` 篇
- 兩篇之間至少間隔：`30` 分鐘

### 專案內建檢查腳本

`scripts/hooks/` 內已有基礎檢查腳本：

- `validate-filename.py`：檢查 Post 檔名格式

## 支援格式與服務限制

| 類型 | 支援格式 | 主要服務 | 備註 |
|------|------|------|------|
| 圖片 | `png`、`jpg`、`jpeg`、`webp` | ImgBB | 單檔建議小於 32MB |
| 影片 | `mp4`、`webm`、`mov` | Cloudinary | 影片上傳需先完成本機生成 |

影片生成的實務建議如下：

- 優先使用 `mp4`
- 解析度控制在 `1080p` 以下會更穩
- 長度以 `5-10 秒` 最容易控場

## 常見問題先從這裡排查

### 找不到 Gemini API Key

先檢查以下兩件事：

1. 是否已設定 `GEMINI_API_KEY`
2. 或是否已建立 `config/gemini_config.json` 並填入 `api_key`

### 影片生成一直失敗

先確認這幾件事：

- 是否真的有 reference image
- `--reference-image` 路徑是否正確
- `Local_Media/<TemplateName>/01.png` 之類的圖檔是否已存在

如果 reference 圖只有部分成功，不需要整批重跑。只繼續成功的項目即可。

### `auto_upload_media.py` 找不到 Prompt

常見原因有三個：

- 檔案其實在 `Test/`，但你用的是 `prod` 流程卻沒加 `--type`
- 檔名少了空格或標點
- 你以為檔案還在 `Prompt/`，但其實已經被移到 `shared/`

### Notion 回傳 404 或 Unauthorized

先檢查以下兩件事：

1. Notion Integration 是否已加到目標頁面或資料庫的 `Connections`
2. `config/notion_config.json` 中是否提供了正確的 `database_id` 或 `page_id`

### 社群發布後媒體被清掉了

這通常不是 bug，而是正常行為。`publish_to_social.py` 會清理你指定的 Template 媒體資料夾。

如果你只想測試流程，先加 `--dry-run`。如果你只想保留檔案不搬移，再加 `--no-move`。
