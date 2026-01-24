# Generate Image

使用 AI（Gemini Web API）生成高品質圖片，支援多種視覺風格。

## 語言要求

**CRITICAL**：所有中文輸出必須使用**繁體中文**，嚴禁使用簡體中文。

## 使用方式

```bash
/generate-image [描述或檔案路徑] [選項]
```

**參數說明：**
- `[描述或檔案路徑]`：圖片描述文字，或 Post/Prompt 檔案路徑
- `--style <風格>`：指定視覺風格（見下方風格列表）
- `--output <路徑>`：輸出圖片路徑（預設：`Local_Media/generated.png`）
- `--aspect <比例>`：圖片比例（`1:1`、`16:9`、`2.35:1`）
- `--auto`：從檔案自動分析內容生成配圖

**範例：**
```bash
# 直接描述生成
/generate-image "Kirby 在辦公室認真工作，穿著西裝打領帶" --style notion

# 從教學文自動生成配圖
/generate-image "Post/Test/2026-01-20-Kirby-Office.md" --auto --style warm

# 指定輸出路徑和比例
/generate-image "水彩風格的櫻花樹" --style watercolor --output cover.png --aspect 16:9
```

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

### 風格自動選擇

當未指定 `--style` 時，系統會根據內容自動選擇最適合的風格：

| 內容關鍵字 | 自動選擇風格 |
|-----------|-------------|
| 遊戲、角色、IP、卡通 | `playful` |
| 技術、架構、系統 | `tech` |
| 教學、知識、學習 | `sketch` |
| 生活、旅遊、美食 | `watercolor` |
| 產品、SaaS、工具 | `notion` |
| 個人、成長、情感 | `warm` |
| 其他 | `notion`（預設）|

## 執行流程

### Step 1: 分析輸入

1. **判斷輸入類型**：
   - 如果是檔案路徑 → 讀取檔案內容
   - 如果是描述文字 → 直接使用

2. **提取關鍵資訊**：
   - 主題：圖片要呈現什麼？
   - 風格訊號：內容中的風格暗示
   - 情緒：嚴肅、活潑、溫暖？

### Step 2: 確定風格

1. 如果指定 `--style` → 使用該風格
2. 如果使用 `--auto` → 根據內容自動選擇
3. 否則 → 詢問用戶選擇

### Step 3: 建構 Prompt

根據選定風格的特性，建構完整的圖片生成 prompt：

```markdown
[風格基礎描述]

主題：[用戶描述或從檔案提取的主題]

視覺元素：
- [風格特定的視覺元素]
- [主題相關的元素]

色彩：
- 主色：[風格主色]
- 背景：[風格背景色]
- 強調色：[風格強調色]

構圖：[根據 aspect ratio 調整]

技術規格：高品質、清晰、[aspect ratio]
```

### Step 4: 生成圖片

**呼叫 Gemini Web API**：

```bash
npx -y bun ${SKILL_DIR}/scripts/main.ts --prompt "[建構的 prompt]" --image "[輸出路徑]"
```

### Step 5: 輸出結果

```
✓ 圖片生成完成！

主題：[主題描述]
風格：[使用的風格]
比例：[aspect ratio]
位置：[輸出檔案路徑] (保持原始畫質)

下一步建議：
- 使用 /viral-score 評估病毒潛力
```

## 風格定義檔

每個風格的詳細定義存放在 `styles/` 目錄：

```
.claude/skills/generate-image/
├── skill.md
├── scripts/
│   └── main.ts
└── styles/
    ├── notion.md
    ├── warm.md
    ├── playful.md
    └── ...
```

## Script Directory

**Important**: 所有腳本位於 `scripts/` 子目錄。

**Script Reference**:
| Script | Purpose |
|--------|---------|
| `scripts/main.ts` | Gemini Web API 圖片生成主程式 |

**執行方式**：
```bash
npx -y bun ${SKILL_DIR}/scripts/main.ts --prompt "描述" --image output.png
```

## 注意事項

- **首次使用需登入**：第一次執行會開啟瀏覽器要求登入 Google 帳號
- **生成時間**：通常需要 10-30 秒
- **圖片格式**：預設輸出 PNG 格式
- **Cookie 快取**：登入後 cookie 會被快取，後續使用無需重新登入
- **網路需求**：需要能夠存取 Google 服務

## 與其他 Skills 整合

```
/auto-produce-prompt → /create-tutorial → /generate-image → /viral-score → /post-to-fb
```

