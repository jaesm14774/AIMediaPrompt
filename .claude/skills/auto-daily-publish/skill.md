---
name: auto-daily-publish
description: 每日自動化發布工具。這是獨立的發布流程，不是 full-pipeline 的一部分；full-pipeline 一律只到媒體上傳為止。
---

# Auto Daily Publish

每日內容發布流程。**推薦直接用 Python 腳本**，不需要開啟 Claude session。

> 這個工具是「發布階段」的獨立流程。`/full-pipeline` 的標準終點仍然是 `auto_upload_media.py`，不包含自動發布。

---

## 推薦：直接執行 Python 腳本

```bash
# 掃描 Post/Test/，評分 + 發布最高分內容
python scripts/daily_publish.py --platforms fb

# 預覽不發布
python scripts/daily_publish.py --dry-run

# 最多發布 3 篇
python scripts/daily_publish.py --max-posts 3 --platforms fb,notion

# 指定最低分數（仍需同時通過 `viral-score` 的 S 級硬門檻）
python scripts/daily_publish.py --min-score 9.0
```

腳本功能：
- 掃描 `Post/Test/` 找所有待發布 `.md`
- 對每個檔案呼叫 `claude -p "/viral-score ..."` 取得分數
- 排序，只發布達 S 級的內容（不是只有分數 ≥ 9.0）
- 呼叫 `scripts/publish_to_social.py` 執行實際發布
- 更新 `config/publish_queue.json` 狀態
- 自動執行頻率限制（30 分鐘間隔、每日上限 5 篇）

---

## Claude 輔助模式（當需要補齊配圖時）

若 Post 沒有配圖，可在 Claude session 中執行：

```bash
/auto-daily-publish [選項]
```

**參數說明：**
- `--generate <關鍵字>`：先生成新內容再發布（調用 `/auto-produce-prompt`）
- `--platforms <平台>`：目標平台（預設：`fb`）
- `--max-posts <數量>`：最多發布數量（預設：1）
- `--dry-run`：模擬執行

**範例：**
```bash
/auto-daily-publish --platforms fb --page-name "AI Art Lab"
/auto-daily-publish --generate "Kirby" --platforms fb,notion
/auto-daily-publish --dry-run
```

---

## 執行流程（Claude 輔助模式）

```
Step 1: 準備內容
  ├─ 若有 --generate：調用 /auto-produce-prompt [關鍵字]
  └─ 讀取 Post/Test/ 所有待發布檔案

Step 2: 對每個待發布檔案，生成配圖
  └─ 調用 /generate-image [Post 檔案] --auto

Step 3: 評估 + 篩選
  └─ 對每個有配圖的檔案：
      /viral-score [Post 檔案] --image [配圖]
      → 達 S 級：加入發布佇列
      → 未達 S 級：標記「未達標」，跳過

Step 4: 排序佇列（分數高到低），取前 --max-posts 個

Step 5: 發布
  └─ 對佇列中每個內容：
      python scripts/publish_to_social.py [file] --platforms [platforms]
      python scripts/sync_to_notion.py
      移動 Post/Test/ → Post/shared/
```

---

## 品質控制（MANDATORY）

- **最低標準：S 級（9.0+ 且通過 `/viral-score` 硬門檻）**，A 級及以下一律不發布
- 這是 CLAUDE.md 的強制規則，任何情況下不得繞過
- 腳本模式和 Claude 模式均適用
- 此規則與 `full-pipeline` 相同：未達 S 級就停止，不是只做紀錄

---

## 頻率限制

- 每次發布間隔至少 **30 分鐘**
- 每日上限 **5 篇**
- 最佳發布時段（台灣）：10:00–12:00、19:00–21:00

---

## 輸出報告範例

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Auto Daily Publish 完成報告
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
執行時間：2026-03-31 10:00
目標平台：FB
最低分數：S 級 (9.0)

掃描：3 個  |  達標：1 個  |  發布：1 個

✅ 已發布
  Kirby-文藝復興油畫 — S 級 (9.3)，FB ✓，Notion ✓

⏸️ 未達標（不發布）
  Kirby-辦公室 — A 級 (8.7) → 保留 Post/Test/
  Mario-場景 — B 級 (7.5) → 保留 Post/Test/
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 錯誤處理

| 錯誤 | 處理方式 |
|------|---------|
| 配圖生成失敗 | 跳過，繼續其他 |
| Viral Score 未達標 | 保留在 Post/Test/，不計入失敗 |
| FB 發布失敗 | 標記 failed，Notion 仍繼續 |
| Notion 同步失敗 | 記錄，不影響 FB 發布 |
