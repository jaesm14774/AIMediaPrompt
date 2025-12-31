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
- `[類型]`（可選）：absurd-professional / temporal / emotion / architecture / tiny-epic / mirror / weather / object
- `[主題]`（可選）：具體主題關鍵字

**範例：**
```bash
/generate-prompt                          # 隨機生成
/generate-prompt absurd-professional      # 指定類型
/generate-prompt emotion "deadline panic" # 指定類型和主題
```

## 生成規則

### 1. 必備元素
- **1-3 個填空** - 讓使用者可以自定義核心元素
- **2-4 個範例選項** - 打包成組，選一行就填完
- **風格一致性** - 同一 template 產生的圖片有統一視覺風格
- **多樣性** - 透過少量變化創造豐富內容

### 2. Template 格式

```markdown
### [Template 名稱]

[一句話說明效果]

---

## Prompt Template

[完整 prompt，用 [變量ith: 詳細說明/ 選項1 / 選項2 / 選項3 / 選項4] 標記填空位置]
---

## Example

[完整可複製的範例 prompt，所有變量已填好]
```

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

## 執行流程

當用戶調用此 skill 時：

1. **識別需求**
   - 如果指定類型，使用該類型
   - 如果指定主題，融入該主題
   - 如果都沒指定，隨機選擇一個類型

2. **生成 Template**
   - 遵循格式規範
   - 確保 1-3 個填空
   - 提供 2-4 個範例選項（打包成組）
   - 包含完整 Example

3. **保存檔案**
   - 檔名：`[Template名稱].md`
   - 位置：`Test/` 資料夾
   - 編碼：UTF-8

4. **輸出確認**
   - 顯示生成的 template 名稱
   - 簡短說明填空數量和風格特點
   - 提供檔案路徑

## 質量標準

每個生成的 prompt template 必須通過：

- ✅ **Surprise** - 有意外的視覺組合
- ✅ **High Fidelity** - 專業攝影/電影級視覺風格
- ✅ **Affect** - 能觸發情感（笑、驚嘆、共鳴）
- ✅ **Relevance** - 與普遍情感/經驗相關
- ✅ **Ease** - 一眼就懂，易於使用

## 範例輸出

生成成功後應顯示：

```
✓ 已生成：職場動物崩潰

類型：Absurd Professionalism
填空：1 個（選擇動物）
風格：National Geographic 紀實攝影
檔案：Test/職場動物崩潰.md

驚喜點：用動物的無辜表情演繹週五被加班的心情
使用：複製 Template → 選一個動物 → 完成
```
