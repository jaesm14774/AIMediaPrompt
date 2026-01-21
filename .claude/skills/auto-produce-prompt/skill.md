# Auto-Produce High-Quality Prompts

完全自動化生產高質量 AI Prompt 的工作流程：研究 → 多樣化生成 → 自動優化 → 教學文產出。

## 核心目標

一鍵自動執行完整流程，確保產出的 Prompt 都達到 A 級或 S 級標準。

## 語言要求

**CRITICAL**：所有中文輸出必須使用**繁體中文**，嚴禁使用簡體中文。

- ✅ 正確：關鍵字、執行、確保、產出、優化
- ❌ 錯誤：关键字、执行、确保、产出、优化

這包括：
- 所有控制台輸出訊息
- 生成的 Prompt 內容
- 評估報告
- 教學文章內容
- 檔案名稱中的中文部分

## 使用方式

```bash
/auto-produce-prompt [IP 或關鍵字]
```

**參數說明：**
- `[IP 或關鍵字]`：核心主題（如 "Kirby", "Mario", "office anxiety"）

**範例：**
```bash
/auto-produce-prompt "Kirby"
/auto-produce-prompt "Ghibli style"
/auto-produce-prompt "workplace stress"
```

## 執行流程

### 1. Research 階段（深入理解關鍵字）

**目的**：確保生成的 prompt 準確理解 IP 特徵、能力機制、視覺風格。

**執行步驟**：
- 調用 `/research-keyword [用戶關鍵字]`
- 等待研究完成
- 讀取生成的研究報告（`Test/research/research_[關鍵字].md`）
- 提取核心特徵、能力機制、常見誤解

**輸出確認**：
```
✓ Research 完成：Kirby
  - 核心特徵：粉紅圓球、Copy Ability、純真可愛
  - 能力機制：吸入敵人 → 造型與能力轉換
  - 常見誤解：不是隨機選擇能力
```

---

### 2. 主題生成階段（創造 3 個差異極大的主題）

**CRITICAL 規則**：
- ✅ **保持用戶提供的 IP/關鍵字**（如 Kirby 永遠是 Kirby）
- ✅ **隨機選擇 3 個完全不同的創意類型**
- ✅ **確保類型之間差異極大**（不是場景變化，而是概念維度不同）

**可用創意類型（從中隨機選 3 個）**：
1. `absurd-professional` - 荒謬專業（職場、正經場景）
2. `temporal` - 時空錯位（歷史 × 現代）
3. `emotion` - 情緒放大（日常情緒 → 災難級場景）
4. `architecture` - 不可能建築（食物建築、軟材質結構）
5. `tiny-epic` - 微型史詩（微小生物的宏大戰役）
6. `mirror` - 鏡中世界（現實 vs 幻想）
7. `weather` - 情緒天氣（情緒化為天氣視覺）
8. `object` - 舊物之靈（珍貴舊物的靈魂光芒）
9. `evolution-video` - 角色進化（遊戲風格進化動畫）

**範例組合（確保類型差異極大）**：
```
用戶關鍵字：Kirby

生成的 3 個主題：
├─ 主題 1：Kirby + absurd-professional
│   → "Kirby 認真工作於科技公司辦公室"（職場荒謬）
│
├─ 主題 2：Kirby + temporal
│   → "Kirby 出現在文藝復興油畫中"（時空錯位）
│
└─ 主題 3：Kirby + emotion
    → "週一恐懼症變成 Kirby 災難電影海報"（情緒放大）
```

**輸出確認**：
```
✓ 主題生成完成（3 個差異極大的方向）：
  1. Kirby + absurd-professional（荒謬職場）
  2. Kirby + temporal（時空錯位）
  3. Kirby + weather（情緒天氣）
```

---

### 3. 批量生成與自動優化循環（對每個主題執行）

**對每個主題執行以下步驟**：

#### 3.1 Generate Prompt（整合 research 結果）

**調用**：
```bash
/generate-prompt [類型] [用戶關鍵字]
```

**範例**：
```bash
/generate-prompt absurd-professional "Kirby"
```

**CRITICAL**：
- 整合步驟 1 的研究結果
- 確保符合核心特徵
- 避免研究報告標註的常見誤解

---

#### 3.2 Evaluate Prompt（評估質量）

**調用**：
```bash
/evaluate-prompt [生成的檔案名稱]
```

**評估標準**：
- **S 級** (9.0-10.0) - 卓越，可直接使用
- **A 級** (8.0-8.9) - 優秀，小幅調整
- **B 級** (7.0-7.9) - 良好，需優化
- **C 級** (6.0-6.9) - 及格，需大幅改進
- **D 級** (<6.0) - 不合格，建議重新生成

---

#### 3.3 自動優化循環（如果評分 < A 級）

**循環邏輯**：
```python
MAX_ITERATIONS = 3
current_iteration = 0

while 評分 < 8.0 and current_iteration < MAX_ITERATIONS:
    1. 從 evaluate 結果提取改進建議
    2. 將改進建議整合到新的 generate 請求中
    3. 重新調用 /generate-prompt（帶上改進要求）
    4. 重新調用 /evaluate-prompt
    5. current_iteration += 1

if 評分 >= 8.0:
    → 進入步驟 3.4
else:
    → 標記為「需人工介入」，繼續處理下一個主題
```

**改進建議整合範例**：
```
Evaluate 結果：
  - 概念創意 5/10：只是 Kirby 穿西裝，缺乏視覺衝擊
  - 建議：加入「吸入辦公室」或「身體變形成辦公椅」的荒謬元素

整合到新的 generate 請求：
  /generate-prompt absurd-professional "Kirby"
  + 額外指令：「強調荒謬視覺衝擊，如 Kirby 正在吸入整個辦公室，或身體變形成傢俱」
```

**輸出確認**：
```
✓ 自動優化循環完成：
  - 初次生成：C 級 (6.5/10)
  - 第 1 次優化：B 級 (7.8/10) - 整合建議：加入荒謬元素
  - 第 2 次優化：A 級 (8.5/10) - 整合建議：強化視覺反差
  → 達到 A 級，進入教學文生成
```

---

#### 3.4 Create Tutorial（生成教學文）

**CRITICAL**：只有達到 **A 級或 S 級** 才執行此步驟。

**調用**：
```bash
/create-tutorial [生成的檔案名稱]
```

**輸出**：
- 生成雙語教學文章
- 保存到 `Post/` 資料夾（臨時）

---

#### 3.5 移動到 Post/Test/ 資料夾

**執行**：
```bash
move "Post/[檔名].md" "Post/Test/[檔名].md"
```

**目的**：
- `Post/Test/` - 待審核發布的成品
- `Post/shared/` - 已發布的文章（用戶手動移動）

**輸出確認**：
```
✓ 教學文已移動：Post/Test/2026-01-07-Kirby-Absurd-Professional.md
```

---

### 4. 總結報告（顯示所有結果）

**統計信息**：
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✓ Auto-Produce 完成報告
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

關鍵字：Kirby
生成主題數：3
成功達標：3 / 3
總優化次數：5 次

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 詳細結果
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Kirby + absurd-professional（荒謬職場）
   ├─ 初次評分：C 級 (6.5/10)
   ├─ 優化次數：2 次
   ├─ 最終評分：A 級 (8.5/10)
   ├─ 檔案：Post/Test/2026-01-07-Kirby-Office-Chaos.md
   └─ 狀態：✅ 已完成

2. Kirby + temporal（時空錯位）
   ├─ 初次評分：B 級 (7.5/10)
   ├─ 優化次數：1 次
   ├─ 最終評分：S 級 (9.2/10)
   ├─ 檔案：Post/Test/2026-01-07-Kirby-Renaissance-Painting.md
   └─ 狀態：✅ 已完成

3. Kirby + weather（情緒天氣）
   ├─ 初次評分：A 級 (8.0/10)
   ├─ 優化次數：0 次
   ├─ 最終評分：A 級 (8.0/10)
   ├─ 檔案：Post/Test/2026-01-07-Kirby-Emotional-Weather.md
   └─ 狀態：✅ 已完成

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 質量統計
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

S 級：1 個（33%）
A 級：2 個（67%）
B 級：0 個（0%）
需人工介入：0 個

平均評分：8.6/10
平均優化次數：1 次

所有成品已保存至 Post/Test/ 資料夾，請審核後移至 Post/shared/ 發布。
```

---

## 錯誤處理與邊界情況

### 情況 1：Research 失敗

**處理**：
- 顯示警告訊息
- 嘗試使用通用知識繼續執行
- 標記「未經研究，可能不準確」

### 情況 2：3 次優化後仍未達 A 級

**處理**：
- 標記為「需人工介入」
- 保留最佳版本（最高分數版本）
- 繼續處理下一個主題
- 在最終報告中標註問題

**範例輸出**：
```
⚠️ 主題 1 需人工介入
   ├─ 初次評分：D 級 (5.0/10)
   ├─ 優化 3 次後：C 級 (6.8/10)
   ├─ 檔案：Test/Kirby-Absurd-Professional.md（未生成教學文）
   └─ 建議：概念層面問題，建議手動調整創意方向
```

### 情況 3：生成的檔案格式錯誤

**處理**：
- 嘗試修復格式
- 如果無法修復，重新生成
- 如果 2 次都失敗，標記為「格式錯誤」並跳過

---

## 質量標準

每個成品必須：

- ✅ **Research-Based** - 基於深入研究，避免誤解
- ✅ **Diverse** - 3 個主題類型完全不同
- ✅ **High-Quality** - 最終評分 ≥ A 級（8.0/10）
- ✅ **Automated** - 全程自動，無需人工介入（除非 3 次優化後仍失敗）
- ✅ **Production-Ready** - 附帶雙語教學文，可直接發布

---

## 與其他 Skills 的整合

**完整依賴鏈**：
```
/auto-produce-prompt
  ├─ 調用 /research-keyword
  ├─ 調用 /generate-prompt（3 次，不同類型）
  ├─ 調用 /evaluate-prompt（3-12 次，含優化循環）
  └─ 調用 /create-tutorial（3 次）
```

**文件流向**：
```
Test/research/
  └─ research_[關鍵字].md（研究報告）

Test/
  ├─ [生成的 Prompt Template].md（原始 prompt）
  └─ evaluations/
      └─ evaluation_[檔名].md（評估報告，可選）

Post/Test/
  └─ [日期]-[檔名].md（待發布教學文）

Post/shared/
  └─ [日期]-[檔名].md（已發布教學文，用戶手動移動）
```

---

## 範例輸出（完整流程）

```bash
/auto-produce-prompt "Kirby"
```

**控制台輸出**：
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🚀 Auto-Produce 啟動
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

關鍵字：Kirby
目標：生成 3 個差異極大的高質量 Prompts

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔍 Step 1: Research 階段
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

正在調用 /research-keyword "Kirby"...
✓ Research 完成：Test/research/research_kirby.md
  - 核心特徵：粉紅圓球、Copy Ability、純真表情
  - 能力機制：吸入 → 造型與能力完全轉換
  - 常見誤解：不是隨機選擇能力

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎨 Step 2: 主題生成階段
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

隨機選擇 3 個創意類型：
✓ 主題 1：Kirby + absurd-professional
✓ 主題 2：Kirby + temporal
✓ 主題 3：Kirby + weather

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📦 Step 3: 批量生成與優化
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[主題 1/3] Kirby + absurd-professional
  ├─ 正在生成 prompt...
  ✓ 生成完成：Test/Kirby-Office-Chaos.md
  ├─ 正在評估...
  ✓ 評估結果：C 級 (6.5/10)
  ├─ 概念問題：缺乏荒謬視覺衝擊
  ├─ 觸發自動優化循環...
  │
  ├─ [優化 1/3] 整合建議：加入「吸入辦公室」元素
  │   ├─ 重新生成...
  │   ✓ 評估結果：B 級 (7.8/10)
  │
  ├─ [優化 2/3] 整合建議：強化視覺反差
  │   ├─ 重新生成...
  │   ✓ 評估結果：A 級 (8.5/10)
  │   └─ 達標！停止優化
  │
  ├─ 正在生成教學文...
  ✓ 教學文完成：Post/2026-01-07-Kirby-Office-Chaos.md
  ├─ 正在移動到 Post/Test/...
  ✓ 已移動：Post/Test/2026-01-07-Kirby-Office-Chaos.md
  └─ 狀態：✅ 完成

[主題 2/3] Kirby + temporal
  ├─ 正在生成 prompt...
  ✓ 生成完成：Test/Kirby-Renaissance-Painting.md
  ├─ 正在評估...
  ✓ 評估結果：B 級 (7.5/10)
  ├─ 觸發自動優化循環...
  │
  ├─ [優化 1/3] 整合建議：強化油畫技法描述
  │   ├─ 重新生成...
  │   ✓ 評估結果：S 級 (9.2/10)
  │   └─ 達標！停止優化
  │
  ├─ 正在生成教學文...
  ✓ 教學文完成：Post/2026-01-07-Kirby-Renaissance-Painting.md
  ├─ 正在移動到 Post/Test/...
  ✓ 已移動：Post/Test/2026-01-07-Kirby-Renaissance-Painting.md
  └─ 狀態：✅ 完成

[主題 3/3] Kirby + weather
  ├─ 正在生成 prompt...
  ✓ 生成完成：Test/Kirby-Emotional-Weather.md
  ├─ 正在評估...
  ✓ 評估結果：A 級 (8.0/10)
  ├─ 無需優化，直接生成教學文
  │
  ├─ 正在生成教學文...
  ✓ 教學文完成：Post/2026-01-07-Kirby-Emotional-Weather.md
  ├─ 正在移動到 Post/Test/...
  ✓ 已移動：Post/Test/2026-01-07-Kirby-Emotional-Weather.md
  └─ 狀態：✅ 完成

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✓ Auto-Produce 完成報告
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

關鍵字：Kirby
生成主題數：3
成功達標：3 / 3
總優化次數：3 次

質量統計：
  S 級：1 個（33%）
  A 級：2 個（67%）
  平均評分：8.6/10

所有成品已保存至 Post/Test/ 資料夾。
請審核後移至 Post/shared/ 發布。
```

---

## 注意事項

- **CRITICAL**: 所有中文內容必須使用繁體中文，嚴禁簡體中文
- **CRITICAL**: 此 skill 會執行多次 API 調用，建議在穩定網路環境下使用
- 每次執行約需 5-15 分鐘（取決於優化次數）
- 如果某個主題 3 次優化後仍未達標，會自動跳過並繼續處理下一個
- 生成的檔案會自動命名，避免覆蓋舊檔案
- 所有中間檔案（prompt template、評估報告）都會保留在 `Test/` 資料夾供參考
