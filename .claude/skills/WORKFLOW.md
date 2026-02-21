# AI Prompt Generation Workflow

完整的 AI 圖像 Prompt 生成與自動發布工作流程。

## 完整工作流程概覽

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                            Phase 1: 內容創作                                   │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐        │
│  │  1. Research    │────▶│  2. Generate    │────▶│  3. Evaluate    │        │
│  │ /research-keyword│     │ /generate-prompt│     │ /evaluate-prompt│        │
│  └─────────────────┘     └─────────────────┘     └────────┬────────┘        │
│                                                           │                  │
│                                                           ▼                  │
│                                                  ┌─────────────────┐        │
│                                                  │  4. Tutorial    │        │
│                                                  │ /create-tutorial│        │
│                                                  └─────────────────┘        │
└──────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                            Phase 2: 圖片處理                                   │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────┐                                                         │
│  │  5. Generate    │                                                         │
│  │ /generate-image │ (保持原始畫質，不壓縮)                                     │
│  └─────────────────┘                                                         │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                            Phase 3: 品質評估與發布                             │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐        │
│  │  7. Viral Score │────▶│  8. Post to FB  │────▶│ 9. Upload Media│        │
│  │   /viral-score  │     │   /post-to-fb   │     │auto_upload_media│        │
│  └─────────────────┘     └─────────────────┘     └────────┬────────┘        │
│                                                           │                  │
│                                                           ▼                  │
│                                                  ┌─────────────────┐        │
│                                                  │ 10. Sync Notion │        │
│                                                  │  sync_to_notion │        │
│                                                  └─────────────────┘        │
└──────────────────────────────────────────────────────────────────────────────┘
```

## 一鍵自動化

使用 `/auto-produce-prompt` 自動完成 Phase 1，使用 `/auto-daily-publish` 自動完成 Phase 2 和 3。

```bash
# 完整自動化（生成 + 發布）
/auto-daily-publish --generate "Kirby" --platforms fb,notion --page-name "AI Art Lab"
```

---

## Phase 1: 內容創作 Skills

### 🔍 1. Research Keyword

**目的**: 深入了解關鍵字背後的含義、特徵和能力

**使用時機**:
- 涉及特定 IP 角色（如：Kirby、Mario、宮崎駿角色）
- 不熟悉的概念或風格（如：Steampunk、Vaporwave）
- 需要準確理解能力機制（如：Copy Ability、Stand Power）

**範例**:
```bash
/research-keyword "kirby copy ability"
```

### 🎨 2. Generate Prompt

**目的**: 生成高創意、可複用的 AI 圖像 Prompt Template

**使用方式**:
```bash
/generate-prompt [類型] [主題]
```

**範例**:
```bash
/generate-prompt mirror-world "kirby copy ability"
/generate-prompt absurd-professional "workplace animals"
```

### 📊 3. Evaluate Prompt

**目的**: 評估 template 的創意性、可複用性和準確性

**評級** (僅 S 級通過):
- **S級** (9.0-10.0) - **唯一通過標準**，可直接使用
- **A級** (8.0-8.9) - 優秀但未達標，需進一步優化
- **B級** (7.0-7.9) - 良好，需大幅優化
- **C級** (6.0-6.9) - 及格，建議重新生成
- **D級** (<6.0) - 不合格，必須重新生成

**範例**:
```bash
/evaluate-prompt "Kirby-Copy-Ability-Transformation.md"
```

### 📝 4. Create Tutorial

**目的**: 將 Prompt Template 轉換為雙語教學文

**範例**:
```bash
/create-tutorial "萬物皆Kirby-日常物體顯現"
```

### 🚀 Auto-Produce Prompt（一鍵完成 Phase 1）

**目的**: 自動完成研究、生成、評估、教學文的完整流程

**範例**:
```bash
/auto-produce-prompt "Kirby"
```

---

## Phase 2: 圖片處理 Skills

### 🖼️ 5. Generate Image

**目的**: 使用 AI（Gemini Web API）生成高品質配圖，保持原始原始畫質不壓縮

**風格系統**:
| 風格 | 說明 |
|-----|------|
| `notion` | 極簡手繪線條 |
| `warm` | 溫暖友善插畫 |
| `playful` | 活潑創意卡通 |
| `tech` | 科技藍圖風格 |
| `watercolor` | 水彩柔和自然 |

**範例**:
```bash
/generate-image "Kirby 在辦公室工作" --style notion --output cover.png
/generate-image "Post/Test/2026-01-20-Kirby.md" --auto
```

---

## Phase 3: 品質評估與發布 Skills

### 📈 7. Viral Score

**目的**: 評估內容的病毒傳播潛力

**評估維度**:
- 視覺衝擊力 (25%)
- 情感共鳴度 (20%)
- 創意獨特性 (20%)
- 可分享性 (20%)
- 平台適配度 (15%)

**範例**:
```bash
/viral-score "Post/Test/2026-01-20-Kirby.md" --image cover.png
```

### 📱 8. Post to FB

**目的**: 自動發布內容到 Facebook

**範例**:
```bash
# 發到粉專
/post-to-fb "教學文內容" --image cover.png --target page --page-name "AI Art Lab" --submit

# 發到個人頁面
/post-to-fb "分享內容" --image art.png --target personal --submit
```

### ☁️ 9. Upload Media

**目的**: 將 Local_Media 的圖片上傳到 ImgBB，並將產出的 URL 插入到對應的 Prompt Markdown 檔案中。這是同步到 Notion 前的必要步驟。

**範例**:
```bash
python scripts/auto_upload_media.py "Prompt名稱" --env dev --type image
```

### 🔄 10. Sync to Notion

**目的**: 同步 Prompt 到 Notion 資料庫（包含已插入的 ImgBB 圖片 URL）

**範例**:
```bash
python scripts/sync_to_notion.py
```

### 📤 Auto-Daily-Publish（一鍵完成 Phase 2 + 3）

**目的**: 自動完成配圖生成、品質評估、發布、上傳圖片、同步 Notion 的完整流程

**範例**:
```bash
/auto-daily-publish --platforms fb,notion --page-name "AI Art Lab"
/auto-daily-publish --generate "Kirby" --platforms fb,notion
```

---

## 使用場景

### 場景 1：完整自動化（推薦）

```bash
# 一鍵完成所有流程
/auto-daily-publish --generate "Kirby" --platforms fb,notion --page-name "AI Art Lab"
```

### 場景 2：分階段執行

```bash
# Phase 1: 內容創作
/auto-produce-prompt "Kirby"

# Phase 2: 圖片處理
/generate-image "Post/Test/2026-01-20-Kirby-Office.md" --auto --style playful

# Phase 3: 評估與發布
/viral-score "Post/Test/2026-01-20-Kirby-Office.md" --image cover.png
/post-to-fb "Post/Test/2026-01-20-Kirby-Office.md" --image cover.webp --target page --page-name "AI Art Lab" --submit
python scripts/sync_to_notion.py
```

### 場景 3：只發布已準備好的內容

```bash
/auto-daily-publish --platforms fb,notion --page-name "AI Art Lab"
```

---

## 文件結構

```
AIMediaPrompt/
├── .claude/skills/
│   ├── WORKFLOW.md                    # 本文件
│   ├── auto-produce-prompt/           # 自動化內容生成
│   ├── research-keyword/              # 關鍵字研究
│   ├── generate-prompt/               # Prompt 生成
│   ├── evaluate-prompt/               # Prompt 評估
│   ├── create-tutorial/               # 教學文生成
│   ├── generate-image/                # AI 圖片生成
│   ├── compress-image/                # 圖片壓縮
│   ├── viral-score/                   # 病毒潛力評估
│   ├── post-to-fb/                    # FB 自動發文
│   └── auto-daily-publish/            # 每日自動發布
│
├── Test/                              # 測試用檔案
│   ├── research/                      # 研究報告
│   └── evaluations/                   # 評估報告
│
├── Prompt/
│   ├── Image/                         # 圖片 Prompt
│   │   └── shared/                    # 已發布
│   └── Video/                         # 影片 Prompt
│       └── shared/                    # 已發布
│
├── Post/
│   ├── Test/                          # 待發布教學文
│   └── shared/                        # 已發布教學文
│
├── Local_Media/                       # 本地圖片（上傳前）
│
├── scripts/
│   ├── auto_upload_media.py           # 上傳到 ImgBB
│   └── sync_to_notion.py              # 同步到 Notion
│
└── config/
    ├── imgbb_config.json
    ├── notion_config.json
    └── publish_queue.json             # 發布佇列
```

---

## 快速參考

| 使用情境 | 推薦指令 |
|---------|---------|
| 完整自動化 | `/auto-daily-publish --generate "主題" --platforms fb,notion` |
| 只生成內容 | `/auto-produce-prompt "主題"` |
| 只生成配圖 | `/generate-image "描述" --style 風格` |
| 只評估品質 | `/viral-score "Post 檔案" --image 圖片` |
| 只發布到 FB | `/post-to-fb "內容" --image 圖片 --submit` |
| 只同步 Notion | `python scripts/sync_to_notion.py` |

---

## 最佳實踐

1. **首次使用特定 IP 時**，先執行 `/research-keyword` 建立知識庫
2. **生成後務必評估**，確保品質達到 S 級以上再發布
3. **使用 `--dry-run`** 預覽發布內容，避免錯誤
4. **控制發布頻率**，每天不超過 3-5 篇，每篇間隔至少 30 分鐘
5. **追蹤實際效果**，根據互動數據調整內容策略
