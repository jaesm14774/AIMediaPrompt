# Full Pipeline - End-to-End Automation

一鍵完成從研究到發布的完整流程：Research -> Generate -> Evaluate -> Tutorial -> Image -> Viral Score -> Publish -> Upload -> Sync。

## 使用方式

```bash
/full-pipeline [主題] [選項]
```

**參數說明：**
- `[主題]`：核心 IP 或關鍵字（如 "Kirby", "Mario", "office anxiety"）
- `--platforms <平台>`：目標平台，逗號分隔（預設：`fb,notion`）
- `--page-name <名稱>`：FB 粉專名稱（預設：`"AI Art Lab"`）
- `--count <數量>`：生成主題數量（預設：3）
- `--style <風格>`：圖片風格覆蓋（預設：自動選擇）
- `--dry-run`：預覽模式，不實際發布
- `--skip-research`：跳過研究階段（適用於已熟悉的主題）

**範例：**
```bash
# 完整自動化（預設設定）
/full-pipeline "Kirby"

# 指定平台和粉專
/full-pipeline "Kirby" --platforms fb,notion --page-name "AI Art Lab"

# 只生成 1 個主題，預覽不發布
/full-pipeline "Mario" --count 1 --dry-run

# 跳過研究，指定圖片風格
/full-pipeline "Ghibli style" --skip-research --style watercolor

# 只同步到 Notion
/full-pipeline "workplace stress" --platforms notion
```

## 執行流程

### Phase 1: 內容創作（委派給 `/auto-produce-prompt`）

```
1. /research-keyword [主題]          （除非 --skip-research）
2. /generate-prompt [類型] [主題]     x [count] 個不同主題
3. /evaluate-prompt [檔案]            評估 + 自動優化循環（最多 3 次）
4. /create-tutorial [檔案]            僅 S 級（9.0+）才生成教學文
5. 移動到 Post/Test/                  待審核
```

**調用方式**：
```bash
/auto-produce-prompt [主題]
```

**Phase 1 品質門檻**：
- Prompt 必須達到 **S 級（9.0+）** 才進入教學文生成
- 最多 3 次優化迭代，超過則標記為「需人工介入」

---

### Phase 2+3: 圖片處理 + 發布（對每個 S 級 Post 執行）

**對 Post/Test/ 中每個 S 級教學文執行以下流程**：

```
1. /generate-image [Post 檔案] --auto    生成配圖（原始畫質）
   如果指定 --style，使用指定風格

2. /viral-score [Post 檔案] --image [配圖]
   品質門檻：S 級（9.0+）才發布

3. 如果 platforms 包含 fb：
   /post-to-fb [Post 檔案] --image [配圖]
     --target page --page-name [粉專名] --submit
   （--dry-run 模式下不加 --submit）

4. 如果 platforms 包含 notion：
   python scripts/auto_upload_media.py [Prompt名稱] --env prod --type image
   python scripts/sync_to_notion.py

5. 移動到正式區：
   Post/Test/[檔案].md -> Post/shared/[檔案].md
   Prompt 移動到對應 shared/ 資料夾
```

**Phase 2+3 品質門檻**：
- Viral Score 必須達到 **S 級（9.0+）** 才實際發布
- 未達標的跳過發布，保留在 Post/Test/ 等待優化

---

## 品質門檻總覽

| 門檻 | 標準 | 未達標行為 |
|------|------|-----------|
| Prompt 評估 | S 級（9.0+） | 自動優化，最多 3 次 |
| Viral Score | S 級（9.0+） | 跳過發布，保留待優化 |
| 最大優化次數 | 3 次/主題 | 標記為「需人工介入」 |

---

## 輸出報告

執行完成後顯示完整報告：

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Full Pipeline 完成報告
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

主題：[主題]
平台：[平台列表]
模式：[正式發布 / 預覽模式]

━━━ Phase 1 結果 ━━━
生成主題數：[N]
達 S 級：[N] / [total]
教學文產出：[N] 篇

━━━ Phase 2+3 結果 ━━━
配圖生成：[N] 張
Viral Score 達標：[N] / [total]
已發布：[N] 篇
  - FB：[N] 篇
  - Notion：[N] 筆

━━━ 未達標項目 ━━━
[列出需人工介入的項目]

━━━ 檔案清單 ━━━
[列出所有產出的檔案路徑]
```

---

## 錯誤處理

| 情況 | 處理方式 |
|------|---------|
| Research 失敗 | 使用通用知識繼續，標記警告 |
| 3 次優化後未達 S 級 | 標記為「需人工介入」，繼續下一個主題 |
| 配圖生成失敗 | 跳過該內容，繼續處理其他 |
| Viral Score 未達 S 級 | 跳過發布，保留在 Post/Test/ |
| FB 發布失敗 | 標記為 failed，繼續其他平台 |
| Notion 同步失敗 | 記錄錯誤，不影響其他操作 |

## 注意事項

- 此 skill 會執行大量 API 調用，建議在穩定網路環境下使用
- `--dry-run` 模式下會執行完整流程但不實際發布，用於預覽和驗證
- 每篇 FB 發文間隔至少 30 分鐘，避免觸發安全機制
- 所有中間檔案保留在 `Test/` 資料夾供參考
