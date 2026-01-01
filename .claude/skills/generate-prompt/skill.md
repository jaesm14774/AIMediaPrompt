# Generate Creative Prompt Template

生成高創意、可複用的 AI 圖像 Prompt Template

## 核心哲學

**荒謬 × 專業 = 會心一笑**

將不可能的概念用極度專業的視覺風格呈現，創造驚喜與共鳴。

## 使用方式

```bash
/generate-prompt [類型] [主題]
```

**參數說明：**
- `[類型]`（可選）：absurd-professional / temporal / emotion / architecture / tiny-epic / mirror / weather / object / evolution-video
- `[主題]`（可選）：具體主題關鍵字

**範例：**
```bash
/generate-prompt                          # 隨機生成圖像 prompt
/generate-prompt absurd-professional      # 指定類型
/generate-prompt emotion "deadline panic" # 指定類型和主題
/generate-prompt evolution-video          # 生成影片 prompt（角色進化）
```

## 生成規則

### 1. 必備元素
- **1-3 個填空** - 讓使用者可以自定義核心元素
- **2-4 個範例選項** - 打包成組，選一行就填完
- **風格一致性** - 同一 template 產生的圖片有統一視覺風格
- **多樣性** - 透過少量變化創造豐富內容

### 2. Template 格式與填空規範

**生成的檔案內容必須嚴格遵循以下格式，不得添加任何額外說明：**

```markdown
### [Template 名稱]

[一句話說明效果]

---

## Prompt Template

[完整 prompt，使用明確的填空標記]

---

## Example

[完整可複製的範例 prompt，所有變量已填好]
```

**CRITICAL: 固定文字 vs 填空比例**
- ✅ **固定文字應占 60-80%**（視覺風格、光影、構圖、技術參數等）
- ✅ **填空最多 2-3 個**，只用於核心變化元素（場景、角色、物體、時間點等）
- ❌ **禁止整段都是填空**，用戶會完全看不懂

**填空標記方式（兩種）：**

**類型 A - 有預設選項的填空（2-4 個選項）：**
```
[變量名稱 with: 簡短說明 / "選項1簡潔描述" / "選項2簡潔描述" / "選項3簡潔描述"]
```
- ✅ 每個選項應簡潔（最多 1-2 句話，不要 3-4 句）
- ✅ 用於場景、情緒、時間點等有限選擇
- ✅ 用戶從選項中選一個複製使用

**類型 B - 自由填入的填空：**
```
**[在此填入角色名]** 或 **[城市名稱]** 或 **[物體：說明 / 範例1 / 範例2]**
```
- ✅ 用 `**[...]**` 標記，視覺上更清楚
- ✅ 用於用戶自定義內容（角色名、地點、物體等）
- ✅ 可加簡短範例幫助理解

**固定文字內容應包括：**
- ✅ 視覺風格定義（"A cinematic IMAX disaster movie poster"、"hyper-realistic mixed-reality photograph"）
- ✅ 光影描述（"volumetric lighting"、"desaturated color grading with selective warm glows"）
- ✅ 構圖指令（"Dramatic low-angle shot, epic composition"）
- ✅ 技術參數（"8K resolution, film grain, anamorphic lens flare"）
- ✅ 特殊元素（文字排版、比例等）

**禁止添加的內容：**
- ❌ 創意核心、驚喜點、情感共鳴等額外說明
- ❌ 使用方式、效果解釋
- ❌ 任何 Template 和 Example 以外的文字

### 3. 創意類型庫

#### Type 1: Absurd Professionalism (荒謬專業)
**公式**: 荒謬主體 + 嚴肅場景 + 專業攝影風格

**範例主題**:
- 動物從事人類工作（職場、專業場景）
- 不可能的專業情境
- 物品擬人化的正經場景

**視覺風格**: National Geographic, 紀實攝影, 35mm film

#### Type 2: Temporal Displacement (時空錯位)
**公式**: 歷史人物/時代 + 現代場景 + 古典藝術風格

**範例主題**:
- 古人使用現代科技
- 現代人在歷史場景
- 時代混搭

**視覺風格**: Rembrandt oil painting, Baroque, 古典繪畫技法應用於現代

#### Type 3: Emotion Amplification (情緒放大)
**公式**: 日常情緒 × 災難級場景 = 電影海報

**範例主題**:
- 週一恐懼症
- 選擇障礙
- 社交焦慮
- Deadline 壓力

**視覺風格**: IMAX poster, 災難片, 史詩電影構圖

#### Type 4: Impossible Architecture (不可能建築)
**公式**: 經典建築 + 食物/軟材質 + 建築攝影

**範例主題**:
- 食物建築（起司、果凍、棉花糖）
- 柔軟材質的堅固結構
- 物理不可能的美學

**視覺風格**: Architectural photography, Unreal Engine 5, 超寫實渲染

#### Type 5: Tiny Epic (微型史詩)
**公式**: 微小生物 + 巨大威脅 + 電影級戰爭場景

**範例主題**:
- 昆蟲的英雄戰役
- 微觀世界的宏大敘事
- 尺度反差的戲劇性

**視覺風格**: War movie cinematography, 微距攝影, Saving Private Ryan aesthetic

#### Type 6: Mirror World (鏡中世界)
**公式**: 鏡子分隔 + 現實 vs 幻想 + 雙重視覺風格

**範例主題**:
- 現實身份 vs 夢想身份
- 外在 vs 內心
- 困境 vs 希望

**視覺風格**: Split composition, 寫實 + 奇幻雙重風格

#### Type 7: Emotional Weather (情緒天氣)
**公式**: 人物 + 情緒化為天氣 + 視覺特效

**範例主題**:
- 焦慮 → 暴風雨
- 希望 → 陽光
- 悲傷 → 雨
- 平靜 → 雪

**視覺風格**: Cinematic portrait, stylized VFX, 情感色調

#### Type 8: Object Soul (舊物之靈)
**公式**: 珍貴舊物 + 靈魂光芒 + 溫馨懷舊

**範例主題**:
- 童年玩具
- 傳家之寶
- 有故事的物品

**視覺風格**: Pixar cinematography, 溫暖色調, 魔幻寫實

#### Type 9: Character Evolution (角色進化) - VIDEO
**公式**: IP 角色 + 遊戲風格進化特效 + 稀有度升級

**範例主題**:
- 遊戲角色稀有度升級（R→SR→SSR→UR）
- 寶可夢風格進化
- 卡牌遊戲抽卡動畫
- 能力覺醒/突破動畫

**視覺風格**: 遊戲進化序列動畫、高幀率粒子特效、動態光影

**Video 專屬規範**:
- ✅ **時長固定 5 秒**（短影音格式）
- ✅ **分段描述**：開場 (0-1s) → 能量聚集 (1-3s) → 爆發轉換 (3-4s) → 結尾展示 (4-5s)
- ✅ **技術參數**：60fps、4K、動態模糊、粒子特效、配樂提示
- ✅ **鏡頭運動**：環繞、推進、震動等動態描述
- ✅ **固定文字占 70%**（視覺風格、特效、轉場、技術參數）
- ✅ **填空 2-3 個**（角色名、進化路徑、外觀變化）

## 執行流程

當用戶調用此 skill 時：

1. **前置檢查與研究**
   - 如果主題涉及特定 IP、角色或不熟悉的概念
   - **建議先使用 `/research-keyword`** 深入了解
   - 檢查 `Test/research/` 是否有相關研究報告
   - 如果有研究報告，讀取並整合關鍵發現

2. **識別需求**
   - 如果指定類型，使用該類型
   - 如果指定主題，融入該主題
   - 如果都沒指定，隨機選擇一個類型
   - **整合研究結果**中的核心特徵和能力機制

3. **生成 Template（基於研究）**
   - **CRITICAL: 固定文字 60-80%，填空最多 2-3 個**
   - 固定文字應包括：視覺風格、光影、構圖、技術參數
   - 填空只用於核心變化元素（場景、角色、物體等）
   - 每個選項應簡潔（最多 1-2 句話）
   - 使用明確的填空標記（類型 A 或類型 B）
   - **確保符合研究報告中的核心特徵**（如有）
   - **避免研究報告中標註的常見誤解**（如有）
   - **範例主角預設規則：如果範例中有主角但未明確指定，預設使用 Kirby作為範例主角**
   - 包含完整 Example

4. **保存檔案**
   - 檔名：`[Template名稱].md`
   - 位置：`Test/` 資料夾
   - 編碼：UTF-8
   - **檔案內容僅包含：Template 名稱、一句話說明、Prompt Template、Example**

5. **輸出確認**
   - 顯示生成的 template 名稱
   - 簡短說明填空數量和風格特點
   - **如果使用了研究報告，標註關鍵整合點**
   - 提供檔案路徑

## 質量標準

每個生成的 prompt template 必須通過：

- ✅ **Surprise** - 有意外的視覺組合
- ✅ **High Fidelity** - 專業攝影/電影級視覺風格
- ✅ **Affect** - 能觸發情感（笑、驚嘆、共鳴）
- ✅ **Relevance** - 與普遍情感/經驗相關
- ✅ **Ease** - 一眼就懂，易於使用

## 範例輸出

### 優秀範例（格式清晰）

```
✓ 已生成：新年決心崩壞

類型：Emotion Amplification
填空：2 個（場景選擇 + 時間點）
固定文字比例：75%
風格：IMAX 災難電影海報
檔案：Test/新年決心崩壞.md

格式特點：
✅ 固定文字包含完整視覺風格、光影、構圖、技術參數
✅ 填空簡潔明確，每個選項 1-2 句話
✅ 用戶一眼就能看出哪些固定、哪些可選
```

### 不良範例（格式混亂）

```
✗ 問題範例：元旦重生之光（初版）

類型：Emotion Amplification
填空：3 個
固定文字比例：20% ← 太低！

問題：
❌ 填空占 80%，整段都是選項
❌ 每個選項 3-4 句話，過於冗長
❌ 用戶看不出哪些是固定文字
❌ 視覺風格、光影、構圖都做成填空（應該固定）

需要重新生成。
```

## 工作流程建議

**完整流程（推薦）：**
1. `/research-keyword [主題]` - 深入研究
2. `/generate-prompt [類型] [主題]` - 基於研究生成
3. `/evaluate-prompt [檔案]` - 評估質量

**快速流程（熟悉主題）：**
1. `/generate-prompt [類型] [主題]` - 直接生成
