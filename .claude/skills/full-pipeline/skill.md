---
name: full-pipeline
description: 一鍵完成從關鍵字到媒體上傳的完整流程。Phase 1 由 /auto-produce-prompt 處理；Phase 2 的 imagine-prompt 依類型輸出，圖片流程產生 4 個衍生 Prompt 並生成 4 張圖，影片流程產生 2 個衍生 Prompt，且必須先生 2 張 reference 圖，再用圖生 2 支影片。Phase 3 只有通過統一 S 級硬門檻的內容才能上傳媒體。發布需由使用者手動執行 publish_to_social.py。
disable-model-invocation: true
---

# Full Pipeline - End-to-End Automation

一鍵完成從關鍵字到媒體上傳的完整流程：
Research → Generate Prompt (通過 S 級硬門檻) → Imagine (image ×4 / video ×2) → Gemini API 生成媒體 → Viral Score → Upload URL

> **發布流程由使用者手動執行**：`python scripts/publish_to_social.py`

## 使用方式

```bash
/full-pipeline [主題] [選項]
```

**參數說明：**
- `[主題]`：核心 IP 或關鍵字（如 "Kirby", "Mario"）
- `--platforms <平台>`：Viral Score 評估目標平台（預設：`fb`）
- `--type <類型>`：媒體類型 `image`（預設）或 `video`
- `--dry-run`：預覽模式，不實際呼叫 API

**範例：**
```bash
/full-pipeline "Kirby"
/full-pipeline "Kirby" --type image --platforms fb
/full-pipeline "水彩告白" --type video
/full-pipeline "Mario" --dry-run
```

---

## 執行架構

```
/full-pipeline "Kirby"
  │
  ├─ Phase 1（委派給 subagent）
  │   └─ /auto-produce-prompt "Kirby"
  │       ├─ /research-keyword          → research/<keyword>/<date>.md
  │       └─ 每個主題獨立 subagent
  │           ├─ /generate-prompt
  │           ├─ /evaluate-prompt（最多 3 次優化）
  │           └─ /create-tutorial（S 級才執行）
  │
  └─ Phase 2+3（每個 S 級 Template 獨立處理）
      └─ 對每個 S 級 Prompt Template：
          ├─ /imagine-prompt → image 產生 4 個 Prompt；video 產生 2 個 Prompt
          ├─ image 模式：python scripts/generate_media_gemini.py × 4
          │   → 存入 Local_Media/<TemplateName>/01~04.png
          ├─ video 模式：先生成 2 張 reference 圖，再生成 2 支影片
          │   → Local_Media/<TemplateName>/01~02.png
          │   → Local_Media/<TemplateName>/01~02.mp4
          ├─ /viral-score
          │   → 未達 S 級即停止，不上傳
          └─ python scripts/auto_upload_media.py "TemplateName" --folder "TemplateName"
              → 僅在 S 級時執行，上傳 URL 到檔案（不刪除本機媒體）
```

---

## Phase 1：內容創作（委派給 subagent）

啟動一個 subagent 執行 Phase 1：

```
執行 /auto-produce-prompt "[主題]"
固定生成 2 個不同創意類型的 S 級 Prompt + 教學文
輸出到 Post/Test/
回報：{成功數量, S 級 Template 清單（含 Template 名稱）, 需人工介入清單}
```

**品質門檻：**
- Prompt 評估必須達 S 級（9.0+ 且通過 `/evaluate-prompt` 硬門檻）才生成教學文
- 最多 3 次優化迭代
- 主題數量固定為 2

---

## Phase 2+3：媒體生成 + URL 上傳（每個 S 級 Template）

### ⚠️ 架構重要說明：必須用 Agent subagent，禁止用 Skill tool

**Skill tool 呼叫會產生 human-turn 邊界**：每次 `Skill: imagine-prompt` 結束後，
assistant turn 就結束，流程停住等待用戶輸入，導致無法自動繼續到 Gemini API。

**正確做法**：對每個 S 級 Template，啟動一個 **`Agent` subagent** 執行完整 Phase 2+3，
subagent 內部直接讀取 Template 檔案並 inline 生成 Prompt，不使用 Skill tool。

對每個 Phase 1 產出的 S 級 Prompt Template，啟動 Agent subagent，指令如下：

```
Template 名稱：<TemplateName>

Step 1: 直接讀取 Prompt/Image/<TemplateName>.md（或 Prompt/Video/）
  → 找出所有 [佔位符] 和 <佔位符>
  → 若 --type image：inline 生成 4 個完全不同主題的完整 Prompt（替換佔位符）
  → 若 --type video：inline 生成 2 個完全不同主題的完整 Prompt（替換佔位符）
  → IP角色規則：1~2 個可使用具名著名 IP（Kirby/皮卡丘/Hello Kitty 等），
               其餘用廣義描述（"a tiny round cartoon creature"）
  → 直接繼續 Step 2，不停頓、不輸出摘要等待確認

Step 2A: 若 --type image，逐一呼叫 Gemini API（4 次）
  python scripts/generate_media_gemini.py \
    --prompt "[Prompt N]" \
    --template "<TemplateName>" \
    --index N \
    --type image
  → 存入 Local_Media/<TemplateName>/01.png ~ 04.png
  → API 不穩、限速、單筆失敗時直接記錄，保留成功張數繼續
  → 僅在 4 / 4 全部失敗時才重試或標記需人工介入

Step 2B: 若 --type video，必須走 image-to-video 流程（禁止文字直出影片）
  先生成 2 張 reference 圖：
  python scripts/generate_media_gemini.py \
    --prompt "[Prompt N]" \
    --template "<TemplateName>" \
    --index N \
    --type image

  再用同一張圖生成對應影片：
  python scripts/generate_media_gemini.py \
    --prompt "[Prompt N]" \
    --template "<TemplateName>" \
    --index N \
    --type video \
    --reference-image "Local_Media/<TemplateName>/0N.png"

  → 存入 Local_Media/<TemplateName>/01.png ~ 02.png 與 01.mp4 ~ 02.mp4
  → 若 reference 圖只成功部分，僅對成功的 reference 圖繼續生成影片
  → API 不穩、限速、單筆失敗時直接記錄，不回頭補生失敗項
  → 僅在 reference 圖 2 / 2 全失敗，或可執行的影片生成全失敗時才重試或標記需人工介入

Step 3: /viral-score "Post/Test/[file].md" --type [image|video] --platform fb
  → 若未達 S 級（不是只有分數不足，也包含未通過硬門檻）：立即停止，不進入上傳
  → 若達 S 級：繼續 Step 4

Step 4: python scripts/auto_upload_media.py "<TemplateName>" --folder "<TemplateName>"
  → 上傳 Local_Media/<TemplateName>/ 內的媒體到 ImgBB/Cloudinary
  → 將 URL 插入相關檔案
  → ⚠️ 不刪除本機媒體檔案

Step 5: 輸出完成報告，提示使用者手動發布
```

**發布（手動執行）：**
```bash
python scripts/publish_to_social.py "PostFileName" \
  --template "<TemplateName>" \
  --platforms fb
```

---

## 品質門檻總覽

| 門檻 | 標準 | 未達標行為 |
|------|------|-----------|
| Prompt 評估 | S 級（9.0+ + `/evaluate-prompt` 硬門檻） | 自動優化，最多 3 次 |
| Viral Score | S 級（9.0+ + `/viral-score` 硬門檻） | 立即停止，不進入上傳 |
| 最大優化次數 | 3 次/主題 | 標記「需人工介入」 |

---

## 輸出報告

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Full Pipeline 完成報告
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

主題：Kirby
媒體類型：image
平台評估：FB

━━━ Phase 1 結果 ━━━
生成主題數：2
達 S 級：2 / 2
教學文產出：2 篇

━━━ Phase 2+3 結果 ━━━
Template 1：Kirby-文藝復興油畫
  ├─ 媒體生成：4 / 4 張
  ├─ Viral Score：S 級 (9.3)
  └─ URL 上傳：✅ 已插入 Prompt 檔案
  📁 Local_Media/Kirby-文藝復興油畫/ (4 張圖保留中)

Template 2：Kirby-荒謬職場
  ├─ 媒體生成：4 / 4 張
  ├─ Viral Score：S 級 (9.1)
  └─ URL 上傳：✅ 已插入 Prompt 檔案
  📁 Local_Media/Kirby-荒謬職場/ (4 張圖保留中)

━━━ 下一步：手動發布 ━━━
確認媒體後執行：
  python scripts/publish_to_social.py "2026-01-07-Kirby-文藝復興油畫" --template "Kirby-文藝復興油畫" --platforms fb
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 快速替代方案

| 場景 | 指令 |
|------|------|
| 只生成內容（不生成媒體） | `/auto-produce-prompt "主題"` |
| 只生成圖片（已有 Template） | `python scripts/generate_media_gemini.py --prompt "..." --template "Name" --index 1 --type image` |
| 只生成影片（已有 reference 圖） | `python scripts/generate_media_gemini.py --prompt "..." --template "Name" --index 1 --type video --reference-image "Local_Media/Name/01.png"` |
| 手動發布 | `python scripts/publish_to_social.py "Post" --template "Name" --platforms fb` |

---

## 錯誤處理

| 情況 | 處理方式 |
|------|---------|
| Phase 1 subagent 失敗 | 記錄錯誤，若有部分成品仍繼續 Phase 2+3 |
| 3 次優化後未達 S 級 | 標記「需人工介入」，繼續下一個主題 |
| 圖片或影片生成部分失敗 | 標記失敗，保留成功成果並繼續，在報告中說明 |
| 圖片或影片生成全部失敗 | 才重試一次；若仍失敗，標記「需人工介入」 |
| Viral Score 未達 S 級 | 立即停止該 Template 的上傳流程，保留本機媒體供人工檢查 |
| URL 上傳失敗 | 記錄，媒體仍保留在 Local_Media，可手動重試 |
