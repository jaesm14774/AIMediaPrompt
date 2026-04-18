---
name: auto-produce-prompt
description: 完整自動化生產高質量 AI Prompt：研究 → 多樣化生成 → 自動優化 → 教學文產出。使用 subagent 隔離每個主題，避免 context 污染。
---

# Auto-Produce High-Quality Prompts

完全自動化生產高質量 AI Prompt 的工作流程：研究 → 2 個主題生成 → 自動優化 → 教學文產出。

## 核心目標

一鍵自動執行完整流程，確保產出的 Prompt 都達到 **統一 S 級標準**：**9.0/10 以上，且通過 `/evaluate-prompt` 的硬門檻**。

## 使用方式

```bash
/auto-produce-prompt [IP、關鍵字]
```

**範例：**
```bash
/auto-produce-prompt "Kirby 御守 傳統神社風格 中國水墨風"
/auto-produce-prompt "Ghibli style with kirby warm story"
```

---

## 執行流程

### 1. Research 階段

調用 `/research-keyword [用戶關鍵字]`。

- 若後續流程需要由 subagent 讀取研究內容，則將研究結果落地保存到 `research/<keyword>/<日期>.md`
- 若沒有跨 subagent 共享需求，可只保留在當前上下文

**輸出確認：**
```
✓ Research 完成：Kirby
  - 核心特徵：粉紅色、圓形、Copy Ability、純真可愛、無牙齒
```

---

### 2. 主題生成階段（2 個差異極大的主題）

**CRITICAL 規則**：
- ✅ 保持用戶提供的 IP/關鍵字
- ✅ 隨機選 2 個完全不同的創意類型（差異極大，不只場景變化而是迥異的核心內容）

**可用創意類型：**
`absurd-professional` | `temporal` | `emotion` | `architecture` | `tiny-epic` | `mirror` | `weather` | `object` | `evolution-video`

**將主題清單寫入 `config/tmp/topics_[關鍵字].json`：**
```json
{
  "keyword": "Kirby",
  "topics": [
    {"type": "absurd-professional", "description": "Kirby 認真工作於科技公司"},
    {"type": "temporal", "description": "Kirby 出現在文藝復興油畫中"}
  ]
}
```

---

### 3. 批量生成（每個主題用獨立 subagent 處理）

**CRITICAL：每個主題必須用獨立 subagent 處理，避免主 context 污染！**

對每個主題，啟動一個 subagent，指令如下：

```
處理主題：[IP] + [type]

1. 若存在研究檔案，讀取：research/[IP]/[日期].md
2. 調用 /generate-prompt [type] "[IP]"
3. 調用 /evaluate-prompt [生成的檔案名]
4. 如果未達 S 級，執行優化循環（最多 3 次）：
   a. 在每次迭代開始前，將狀態寫入 config/tmp/produce_[IP]_[type].json：
      {"iteration": N, "best_score": X, "best_file": "路徑", "status": "optimizing"}
   b. 從 evaluate 結果提取具體改進建議
   c. 重新調用 /generate-prompt 並附上改進要求
   d. 重新調用 /evaluate-prompt
   e. 更新狀態檔（iteration += 1）
   f. 如果達到 S 級或迭代達 3 次，停止循環
5. 如果最終達到 S 級：調用 /create-tutorial [最佳檔案]
6. 回報結果：{topic, final_score, file_path, iterations, status}
```

**為什麼用 subagent：**
- 每個主題的生成+優化會消耗大量 context（多次讀寫大型 prompt 檔案）
- Subagent 在獨立 context window 中執行，完成後只回傳摘要
- 主 context 保持乾淨，避免「context 污染導致性能下降」

---

### 4. 總結報告

收集所有 subagent 的結果，輸出：

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✓ Auto-Produce 完成報告
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

關鍵字：Kirby
生成主題數：2
成功達標：2 / 2

1. Kirby + temporal（時空錯位）
   ├─ 最終評分：S 級 (9.2/10)
   ├─ 優化次數：1 次
   ├─ 檔案：Post/Test/2026-01-07-Kirby-文藝復興油畫.md
   └─ 狀態：✅ 教學文已生成

2. Kirby + absurd-professional（荒謬職場）
   ├─ 最終評分：S 級 (9.0/10)
   ├─ 優化次數：2 次
   ├─ 檔案：Post/Test/2026-01-07-Kirby-荒謬職場.md
   └─ 狀態：✅ 教學文已生成

所有成品已保存至 Post/Test/，後續可交由 /full-pipeline 繼續處理，或手動發布。
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 防止無限循環的保護機制

1. **MAX_ITERATIONS = 3**：每個主題最多優化 3 次，超過即停止
2. **狀態持久化**：每次迭代前後寫入 `config/tmp/produce_[IP]_[type].json`，即使 context 被壓縮也能從狀態檔恢復
3. **Subagent 隔離**：每個主題的循環在獨立 context 中執行，不會互相影響
4. **明確停止條件**：`達到 S 級（不是只有 9.0 分）` 或 `迭代次數 >= 3`，兩者任一即停止——不設任何例外

---

## 錯誤處理

| 情況 | 處理方式 |
|------|---------|
| Research 失敗 | 使用通用知識繼續，標記「未經研究」 |
| 3 次後仍未達 S 級 | 標記「需人工介入」，繼續下一主題 |
| 格式錯誤 | 嘗試修復，若 2 次失敗則跳過 |
| Subagent 失敗 | 記錄錯誤，繼續其他主題 |
