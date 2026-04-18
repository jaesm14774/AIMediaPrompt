---
name: generate-image
description: 呼叫 Gemini API 生成圖片，或以 reference 圖生影片，存入 Local_Media/
version: "1.0.0"
---

# Generate Image / Video

使用 Gemini API 生成圖片，或以已生成圖片作為 reference 生成影片，存入 `Local_Media/<TemplateName>/`。

- **圖片**：`gemini-3.1-flash-image-preview`
- **影片**：`veo-3.1-lite-generate-preview`（以 reference image 生影片）

## 使用方式

```bash
/generate-image [描述或檔案路徑] [選項]
```

**參數說明：**
- `[描述或檔案路徑]`：圖片/影片描述文字，或 Prompt 檔案路徑
- `--template <名稱>`：Prompt Template 名稱（決定存入 `Local_Media/<名稱>/`）
- `--type <類型>`：`image`（預設）或 `video`
- `--index <序號>`：第幾張/支，用於命名（預設：1）
- `--reference-image <路徑>`：生成影片時必填；若省略，會優先嘗試使用 `Local_Media/<名稱>/<序號>.png`
- `--style <風格>`：指定視覺風格，附加到 prompt（見下方風格列表）
- `--aspect <比例>`：圖片比例（`1:1`、`16:9`、`2.35:1`），附加到 prompt
- `--auto`：從檔案自動分析內容生成描述

**範例：**
```bash
# 生成圖片，存入 Local_Media/KirbyTemplate/01.png
/generate-image "Kirby 在辦公室認真工作，穿著西裝打領帶" --template "KirbyTemplate" --index 1

# 影片：先有 reference 圖，再生成影片
/generate-image "Kirby 跳舞" --template "KirbyTemplate" --index 1
python scripts/generate_media_gemini.py --prompt "Kirby 跳舞" --template "KirbyTemplate" --index 1 --type video --reference-image "Local_Media/KirbyTemplate/01.png"

# 從教學文自動分析並生成
/generate-image "Post/Test/2026-01-20-Kirby-Office.md" --template "KirbyOffice" --auto
```

## 前置需求

**設定 Gemini API Key（二擇一）：**
```bash
# 方式一：環境變數
set GEMINI_API_KEY=YOUR_KEY

# 方式二：設定檔
# 建立 config/gemini_config.json：
# {"api_key": "YOUR_KEY"}
```

**安裝 Python SDK：**
```bash
pip install google-genai
```

---

## 風格系統

### 可用風格

| 風格 | 說明 | 適用場景 |
|-----|------|---------|
| `notion` | 極簡手繪線條，SaaS 儀表板美學 | 產品介紹、生產力工具、B2B 內容 |
| `warm` | 溫暖友善，橙黃暖色調 | 個人成長、生活風格、教育內容 |
| `playful` | 活潑創意，粉彩色調 | 教學、入門指南、輕鬆主題 |
| `tech` | 科技藍圖，工程精確 | 系統架構、技術文件 |
| `watercolor` | 水彩柔和，自然溫暖 | 生活、旅遊、美食 |
| `minimal` | 極度乾淨，禪意聚焦 | 簡約內容、高端品牌 |
| `pixel-art` | 復古 8-bit，懷舊遊戲風 | 遊戲、開發者內容 |
| `sketch` | 手繪筆記風，教育溫暖 | 知識分享、教學 |
| `editorial` | 雜誌風格資訊圖 | 科技解說、新聞 |
| `vintage` | 復古老舊紙張質感 | 歷史、傳記 |

風格定義檔存於 `styles/` 目錄。若指定風格，讀取對應檔案並附加風格描述到 prompt 結尾。

---

## 執行流程

### Step 1: 分析輸入

1. **判斷輸入類型**：
   - 如果是檔案路徑 → 讀取檔案，提取核心視覺描述
   - 如果是描述文字 → 直接使用

2. **決定媒體類型**：
   - 副檔名 `.mp4/.mov/.webm` 或 `--type video` → 影片
   - 否則 → 圖片

### Step 2: 建構完整 Prompt

```
[用戶描述]

[風格描述（若指定 --style）]

[比例指令（若指定 --aspect）]
```

### Step 3: 決定輸出路徑

- 若指定 `--template <名稱>` 和 `--index <序號>`：
  - 圖片：`Local_Media/<名稱>/<序號，補零2位>.png`（例：`Local_Media/KirbyTemplate/01.png`）
  - 影片：`Local_Media/<名稱>/<序號，補零2位>.mp4`
- 若指定完整路徑 → 直接使用

### Step 4: 呼叫 Gemini API

```bash
python scripts/generate_media_gemini.py \
  --prompt "[建構的 prompt]" \
  --template "[Template 名稱]" \
  --index [序號] \
  --type image
```

若要生成影片，必須先有 reference image，再執行：

```bash
python scripts/generate_media_gemini.py \
  --prompt "[建構的 prompt]" \
  --template "[Template 名稱]" \
  --index [序號] \
  --type video \
  --reference-image "Local_Media/[Template 名稱]/0[序號].png"
```

### Step 5: 輸出結果

```
✓ 媒體生成完成！

類型：[image / video]
模型：[gemini-3.1-flash-image-preview / veo-3.1-lite-generate-preview]
位置：Local_Media/<TemplateName>/<序號>.png 或 .mp4

下一步建議：
- 圖片流程：生成全部 4 張後，執行 /viral-score 評估
- 影片流程：先確認 2 張 reference 圖，再生成 2 支影片後執行 /viral-score
- 確認已達 S 級後執行 python scripts/auto_upload_media.py "TemplateName" --folder "TemplateName"
```

---

## 批量生成（搭配 /imagine-prompt）

典型使用情境：一個 Template 依媒體類型生成不同數量的媒體。

```
1. /imagine-prompt "TemplateName.md"
   - 圖片流程 → 產生 4 個 Prompt
   - 影片流程 → 產生 2 個 Prompt
2. 若是圖片流程，對每個 Prompt 呼叫 /generate-image：
   - Prompt 1 → Local_Media/TemplateName/01.png
   - Prompt 2 → Local_Media/TemplateName/02.png
   - Prompt 3 → Local_Media/TemplateName/03.png
   - Prompt 4 → Local_Media/TemplateName/04.png
3. 若是影片流程，先生成 01.png、02.png，再各自生成 01.mp4、02.mp4
4. /viral-score 評估
5. 分數達 S 級後，再執行 python scripts/auto_upload_media.py "TemplateName" --folder "TemplateName"
   （僅上傳，不刪除本機檔案）
```

---

## 注意事項

- **API Key 必填**：請先設定 `GEMINI_API_KEY` 或 `config/gemini_config.json`
- **影片生成較慢**：Veo API 通常需要 1-3 分鐘
- **影片禁止文字直出**：必須先生成圖片，再用圖片當 reference 生成影片
- **資料夾隔離**：每個 Template 使用獨立的 `Local_Media/<TemplateName>/`，不互相干擾
- **不自動發布**：生成後僅儲存到 Local_Media，不會自動呼叫 publish_to_social.py

## 與其他 Skills 整合

```
/auto-produce-prompt → /imagine-prompt (image ×4 / video ×2)
                     → 圖片流程：/generate-image (×4)
                     → 影片流程：先生圖 (×2) → 再生影片 (×2)
                     → /viral-score
                        ├─ 未達 S 級（不是只有分數不足，也包含未通過硬門檻）：停止
                        └─ 達 S 級：auto_upload_media.py
                                           ↓（手動）
                                publish_to_social.py
```
