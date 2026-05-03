---
name: generate-prompt
description: 生成高創意、可複用的 AI 圖像 Prompt Template，強調強烈印象 × 可渲染性
version: "1.0.0"
---

# Generate Creative Prompt Template

生成高創意、可複用的 AI 圖像 Prompt Template

## 核心哲學

**強烈印象 × 可渲染性 = 值得追求的 Prompt**

將不可能的概念用極度專業的視覺風格呈現，目標不是只做出「不錯的圖」，而是做出讓人想停下來、記住、分享的畫面。

**重要補充：**

- 荒謬不等於好笑
- 可愛不等於有記憶點
- 電影感不等於 S 級
- 生成時就要以 `/evaluate-prompt` 的 S 級標準倒推，不要先做安全牌再期待評估放行

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

---

## 兩條生成路線

| 路線 | 適用場景 | 工具 |
|------|---------|------|
| **路線 A：Claude 手工生成** | 需要高度原創概念、特殊 IP 限定、一次性實驗 | Claude 直接輸出 |
| **路線 B：元件組裝** | 想快速組出結構穩定的模板、想從爆量研究中提取模式、想複用已驗證的高勝率元件 | `assemble_prompt_template.py` |

### 路線 B：元件組裝指引

**步驟 1：查看可用元件**
```bash
python scripts/assemble_prompt_template.py --list-components
```

可用元件類別：`scene` / `shot` / `lighting` / `style` / `emotion` / `hook` / `motion`（僅影片）

**步驟 2：組裝模板**
```bash
python scripts/assemble_prompt_template.py \
  --name "模板名稱" \
  --media-type image \
  --scene [scene_id] \
  --shot [shot_id] \
  --lighting [lighting_id] \
  --style [style_id] \
  --emotion [emotion_id] \
  --hook [hook_id]
```

**搭配爆量研究（路線 B 的最大優勢）**：
若已執行 `/research-keyword` 路線 B 並產出研究簡報，把核心洞察壓縮成一句：
```bash
python scripts/assemble_prompt_template.py \
  --name "寵物療癒陪伴-研究版" \
  --media-type image \
  --scene domestic_emotional_corner \
  --shot cinematic_medium_wide \
  --lighting soft_window_poetry \
  --style storybook_painterly \
  --emotion warm_healing \
  --hook quiet_emotional_reveal \
  --research-note "Tiny companion moment, warm domestic light, one gesture of comfort, no clutter."
```

**輸出**：模板自動寫入 `Test/<模板名稱>.md`，格式與路線 A 相同，可直接進入 `/evaluate-prompt`

## 生成規則

### 1. 必備元素
- **1-3 個填空** - 讓使用者可以自定義核心元素
- **2-4 個範例選項** - 打包成組，選一行就填完
- **風格一致性** - 同一 template 產生的圖片有統一視覺風格
- **多樣性** - 透過少量變化創造豐富內容
- **強印象核心** - 一句話就能說出這個畫面的刺點

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

### 2.5 S 級生成原則

生成前，先用一句話回答：

- 這個畫面最強的記憶點是什麼？
- 觀眾第一反應會是驚嘆、鼻酸，還是會心一笑？
- 為什麼他會想分享，而不是只看過就滑走？

**若答不出來，表示概念還不夠強，不要急著生成。**

**以下類型預設不是 S 級概念：**

- 只是把角色放錯地方
- 只是「可愛角色做日常事」
- 只是常見情緒換成華麗場景
- 只是熟悉 IP + 熟悉題材拼裝
- 只是靠形容詞撐情緒，例如 epic、emotional、bittersweet

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
- 被迫說再見的那一秒
- 差一點接住卻錯過的瞬間
- 撐住不哭的表情
- 終於等到的重逢

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

### Step 0：查重 + 禁用舊模式（MANDATORY，不可跳過）

**目的：強迫跳出「近親繁殖」循環，每次都產出真正的新東西。**

1. 列舉 `Prompt/Image/shared/`、`Prompt/Video/shared/`、`Prompt/Image/`、`Prompt/Video/` 下所有現有 `.md` 檔名
2. 快速閱讀每個 template 的第一行說明，提取：
   - 已用過的 **Type 組合**（如「荒謬專業 + 職場崩潰」「文藝復興 + 現代科技」）
   - 已用過的 **視覺風格關鍵詞**（如「油畫質感」「微縮世界」「扭蛋機」「拆箱」）
   - 已用過的 **核心情境**（如「辦公室」「節日」「食物」「動物擬人」）
3. **明確宣告禁用清單**，格式如下輸出：

```
🚫 已用過，這次禁止重複：
  Type 組合：文藝復興×現代科技 / 荒謬職場×動物 / 微縮世界×食物...
  視覺風格：油畫質感 / 扭蛋機框架 / 立體剖面 / 像素遊戲...
  核心情境：辦公室崩潰 / 聖誕節日 / 珍奶主題...

✅ 本次可用的新方向（至少列出 3 個未被用過的組合）：
  候選 A：[Type X] × [Type Y] → 切入點：...
  候選 B：[Type X] × [Type Z] → 切入點：...
  候選 C：...
```

4. **若指定類型但已大量使用**，主動提示使用者考慮其他組合，或在同類型內找全新切入點

---

### Step 0.5：強制跨類型混搭（CRITICAL）

**規則：每次生成必須融合至少 2 個 Type 的 DNA，不允許只用單一類型。**

混搭方式：
- 從上方「可用新方向」候選中選一組
- 或根據使用者指定主題，找出 **最違反直覺但邏輯自洽** 的兩種 Type 交集
- 生成前先用一句話說出混搭的「化學反應」：

```
💥 本次混搭：[Type A] × [Type B]
   化學反應：[說明為什麼這兩個放在一起會產生新的張力或驚喜]
   概念核心：[一句話描述視覺最強記憶點]
```

**若答不出「化學反應」，表示混搭太普通，換一組。**

混搭靈感快速參考：

| Type A | Type B | 潛在爆點 |
|--------|--------|---------|
| Tiny Epic（微型史詩）| Temporal Displacement（時空錯位）| 古代蚊蟲用三國戰術圍攻漢代蠟燭 |
| Emotion Amplification（情緒放大）| Impossible Architecture（不可能建築）| 考試焦慮蓋成一棟隨時崩塌的起司大樓 |
| Absurd Professionalism（荒謬專業）| Object Soul（舊物之靈）| 退役計算機在法庭上為自己的存在辯護 |
| Mirror World（鏡中世界）| Character Evolution（角色進化）| 鏡子左邊是剛買的公仔，右邊是 30 年後的樣子 |
| Emotional Weather（情緒天氣）| Tiny Epic（微型史詩）| 一隻螞蟻獨自穿越「悲傷」形成的暴風雪地形 |

---

### Step 1：前置檢查與研究

- 如果主題涉及特定 IP、角色或不熟悉的概念
- **建議先使用 `/research-keyword`** 深入了解
- 檢查 `research/<keyword>/` 是否有相關研究報告
- 如果有研究報告，讀取並整合關鍵發現

### Step 2：識別需求 + 確認混搭方向

- 如果指定類型，以該類型為主，**強制搭配第二個 Type**
- 如果指定主題，融入該主題，**選最強的 2 個 Type 組合**
- 如果都沒指定，從 Step 0 的「可用新方向」候選中選最具潛力的一組
- **整合研究結果**中的核心特徵和能力機制

### Step 3：生成 Template（基於研究 + 混搭）

- 先確認概念是否具備 **強烈印象核心**（跑 S 級前置問題）
- 確認混搭的「化學反應」說得出來（說不出來就換組合）
- **CRITICAL: 固定文字 60-80%，填空最多 2-3 個**
- 固定文字應包括：視覺風格、光影、構圖、技術參數
- 填空只用於核心變化元素（場景、角色、物體等）
- 每個選項應簡潔（最多 1-2 句話）
- 使用明確的填空標記（類型 A 或類型 B）
- **確保符合研究報告中的核心特徵**（如有）
- **避免研究報告中標註的常見誤解**（如有）
- **Default character is [IP角色]** (see CLAUDE.md for details)
- 包含完整 Example

### Step 4：保存檔案

- 檔名：`[Template名稱].md`
- 位置：`Test/` 資料夾
- 編碼：UTF-8
- **檔案內容僅包含：Template 名稱、一句話說明、Prompt Template、Example**

### Step 5：輸出確認

- 顯示生成的 template 名稱
- 標註使用的 **Type 混搭組合**
- 說明這組混搭的「化學反應」（為什麼新鮮）
- 標註與現有 template 的差異點
- **如果使用了研究報告，標註關鍵整合點**
- 提供檔案路徑

## 質量標準

每個生成的 prompt template 必須通過：

- ✅ **Strong Impression** - 能讓人停下來、記住、想分享
- ✅ **Surprise** - 有意外的視覺組合，而且不只是廉價錯置
- ✅ **High Fidelity** - 專業攝影/電影級視覺風格
- ✅ **Affect** - 能觸發情感（笑、驚嘆、共鳴）
- ✅ **Relevance** - 與普遍情感/經驗相關
- ✅ **Ease** - 一眼就懂，易於使用

## 範例輸出

### 優秀範例（含查重 + 混搭輸出）

```
🚫 已用過，這次禁止重複：
  Type 組合：文藝復興×現代科技 / 荒謬職場×動物 / 微縮世界×食物
  視覺風格：油畫質感 / 扭蛋機框架 / 立體剖面
  核心情境：辦公室崩潰 / 聖誕節日 / 珍奶主題

✅ 本次可用新方向：
  候選 A：Tiny Epic × Temporal Displacement → 微型生物用古代戰術對抗現代日常威脅
  候選 B：Object Soul × Absurd Professionalism → 退役物品在正式場合捍衛自己的尊嚴
  候選 C：Mirror World × Emotion Amplification → 鏡子兩側是同一人的不同情緒宇宙

💥 本次混搭：Tiny Epic × Temporal Displacement
   化學反應：「宏大敘事感」撞上「時代錯位的荒謬」= 蚊蟲用諸葛亮的空城計騙過電蚊拍
   概念核心：一場古代蚊軍對抗現代電蚊拍的史詩戰役，構圖如《拯救大兵雷恩》

✓ 已生成：蚊蟲三國-空城計對決電蚊拍

Type 混搭：Tiny Epic × Temporal Displacement
化學反應：尺度壓縮（蚊蟲視角的史詩感）× 時代衝突（三國戰術 vs. 現代武器）
填空：2 個（古代名將選擇 + 戰場環境）
固定文字比例：72%
風格：War movie cinematography × 三國志遊戲美術
與現有 template 差異：現有未使用「微型史詩 × 時空錯位」組合；古代戰術 vs. 現代物品角度全新
檔案：Test/蚊蟲三國-空城計對決電蚊拍.md
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

