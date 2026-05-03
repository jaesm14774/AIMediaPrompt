---
name: research-keyword
description: 在生成 Prompt 前深度研究關鍵字（IP 角色、概念、主題），確保準確性
version: "1.0.0"
---

# Research Keyword

深入研究關鍵字背後的含義、特徵和能力，避免誤判和表面理解。

## 核心目標

當用戶提供 IP 角色、概念或主題時，進行深度研究以確保生成的 prompt 準確且符合預期。

## 使用方式

```bash
/research-keyword [關鍵字或主題]
```

**範例：**
```bash
/research-keyword "kirby copy ability"
/research-keyword "Studio Ghibli art style"
/research-keyword "steampunk"
```

---

## 三條研究路線

**在執行前，先判斷關鍵字類型，選擇對應路線：**

| 類型 | 判斷標準 | 使用路線 |
|------|---------|---------|
| **IP / 角色 / 風格** | 有具體名字、設定、版權歸屬 | 路線 A：WebSearch 研究 |
| **爆量題材 / 情緒主題** | 是趨勢、情感、場景類主題（如「療癒陪伴」「辦公室崩潰」），使用者已提供觀察資料 | 路線 B：`synthesize_trend_research.py` |
| **無指定主題 / 模糊輸入** | 使用者沒給具體主題，或只說「隨便」「你決定」「找個有趣的」 | 路線 C：`/auto-trend-scout` 自動偵測 |

### 路線 A：IP / 角色研究（原流程）

使用 WebSearch 工具，按下方「研究維度」進行，輸出研究報告。

### 路線 B：爆量題材研究（使用者有提供觀察資料）

**前置條件**：使用者需先手動蒐集 3 筆以上的爆量 Reel / Post 觀察，填入：
```
research/templates/viral-source-template.md
```

**執行指令**：
```bash
export PYTHONIOENCODING=utf-8
python scripts/synthesize_trend_research.py "主題關鍵字" \
  --source research/templates/viral-source-template.md
```

**輸出路徑**：`research/<keyword>/<今日日期>-viral-research.md`

**輸出結構**（Gemini 自動生成）：
- 來源摘要 / 爆量共通點 / 視覺 Hook
- 情緒與敘事機制 / 可回收 Prompt 元件 / 反模式
- **5 個可直接進入 `/generate-prompt` 的概念方向**

**後續銜接**：
- 把「可回收 Prompt 元件」區塊的核心洞察壓成一句 `--research-note`
- 餵給 `assemble_prompt_template.py` 或 `/generate-prompt` 使用

### 路線 C：自動趨勢偵測（無主題 / 模糊輸入）

**觸發條件**：使用者沒有給出具體主題，或明示「你來決定」「找個當下最有趣的」。

**執行方式**：直接呼叫 `/auto-trend-scout`，不需要使用者準備任何資料。

```bash
/auto-trend-scout                      # 全自動偵測台灣今日趨勢
/auto-trend-scout --focus "科技"       # 可選：聚焦特定領域
```

**輸出**：今日熱門話題 Top 5 + 每個話題的創意切入角度，可直接選一個繼續執行。

**銜接 generate-prompt**：
- 從 `/auto-trend-scout` 輸出中選出「推薦優先開發」的話題
- 將話題 + 推薦的 Type 混搭方向直接傳給 `/generate-prompt`

**路線 C 完整銜接範例：**
```
使用者輸入：「幫我生個有意思的 prompt，你決定主題」

Step 1: /auto-trend-scout → 偵測到「今日台灣氣溫飆升 35 度」是熱門話題
Step 2: 推薦切入：Absurd Professionalism × Tiny Epic
         概念：「野生台灣人在 35 度高溫等捷運的 National Geographic 紀錄片特輯」
Step 3: /generate-prompt 接收此方向 → 執行 Step 0 查重 → 生成 Template
```

## 研究維度

### 1. 視覺特徵 (Visual Features)
- 外觀描述（形狀、顏色、質感）
- 造型變化（不同狀態、形態）
- 經典視覺元素
- 色彩配置

### 2. 核心能力/特性 (Core Abilities)
- 主要能力機制
- 特殊技能或功能
- 能力的視覺表現
- 能力的限制或規則

### 3. 背景設定 (Context)
- 來源/出處
- 世界觀設定
- 相關角色或元素
- 經典場景或情境

### 4. 創意應用點 (Creative Points)
- 可延伸的視覺概念
- 適合的風格搭配
- 常見的誤解（需避免）
- 獨特的識別特徵

## 執行流程

當用戶調用此 skill 時：

1. **接收關鍵字並判斷路線**
   - 識別關鍵字類型（角色/風格/概念/主題/無主題）
   - 有具體 IP 名或版權歸屬 → **路線 A（WebSearch）**
   - 是趨勢、情緒或場景型主題，且使用者已有觀察資料 → **路線 B（synthesize_trend_research.py）**
   - 主題模糊、使用者說「你決定」、或完全沒給主題 → **路線 C（/auto-trend-scout 自動偵測）**，立即執行不需等待使用者準備

2. **路線 A：深度搜尋（IP / 角色 / 風格）**
   - 使用 WebSearch 工具搜尋相關資訊
   - 查找官方設定、wiki、粉絲討論
   - 收集視覺參考和能力說明
   - 注意特殊機制或規則

3. **路線 A：資訊整理**
   - 提取關鍵視覺特徵
   - 整理核心能力機制
   - 標註常見誤解
   - 歸納創意應用點

4. **路線 A：輸出摘要**
   - 顯示關鍵發現
   - 標註重要機制
   - 提醒注意事項
   - 建議後續應用方向

5. **是否落地保存**
   - 路線 A 預設：不強制落地成檔；若後續 subagent 需讀取，保存到 `research/<keyword>/<日期>.md`
   - 路線 B：`synthesize_trend_research.py` 自動落地到 `research/<keyword>/<日期>-viral-research.md`
   - 檔案用途是跨階段共享，不是暫存垃圾檔

## 研究報告格式

```markdown
# [關鍵字] 研究報告

## 基本資訊
- **來源**: [出處/IP名稱]
- **類型**: [角色/風格/概念]
- **研究日期**: [日期]

## 視覺特徵
- [詳細視覺描述]
- [造型變化說明]
- [色彩配置]

## 核心能力/特性
- [能力名稱]: [詳細機制說明]
- [視覺表現]: [能力的視覺特徵]
- [重要規則]: [需要注意的機制]

## 常見誤解 ⚠️
- ❌ [錯誤理解]
- ✅ [正確理解]

## 創意應用建議
- [適合的 prompt 類型]
- [推薦的風格搭配]
- [獨特的視覺角度]

## 參考來源
- [來源1]
- [來源2]
```

## 範例輸出

搜尋 "kirby copy ability" 後應顯示：

```
✓ 研究完成：Kirby Copy Ability

核心發現：
• Copy Ability 不只是獲得技能，造型也會改變
• 吸入敵人後，Kirby 會變成對應能力的外觀
• 每種能力都有獨特的帽子/造型變化
• 目前有 100+ 種不同的 Copy Abilities

常見誤解：
❌ Kirby 只是獲得能力，外觀不變
✅ Kirby 吸收後會完全轉換成該能力的專屬造型

創意應用：
• Prompt 重點：強調造型轉換過程
• 視覺亮點：展示吸收前後的對比
• 推薦類型：Transformation / Before-After

```

## 質量標準

每個研究報告必須：

- ✅ **Accuracy** - 資訊正確，來源可靠
- ✅ **Depth** - 深入機制，不只表面描述
- ✅ **Clarity** - 清晰標註常見誤解
- ✅ **Actionable** - 提供具體的創意應用建議
- ✅ **Visual Focus** - 強調視覺化的重點特徵

## 與其他 Skill 的整合

此 skill 的輸出會被用於：
- `generate-prompt`: 基於研究結果生成更準確的 prompt template
- `evaluate-prompt`: 評估時參考是否符合角色/概念的核心特徵
- `auto-produce-prompt` / `full-pipeline`: 若涉及 subagent 接力，應保存到 `research/<keyword>/<日期>.md`

## 注意事項

- 對於不熟悉的 IP 或角色，**必須**先使用此 skill 研究
- 搜尋時優先查找官方設定和可靠來源
- 標註不確定的資訊，避免誤導
- 重點關注「視覺化」相關的特徵和機制
- 預設不必落地保存研究檔
- 若後續流程使用 subagent 串接，應保存到 `research/<keyword>/<日期>.md`
- 不要再使用 `Test/research/` 作為研究檔案目錄
