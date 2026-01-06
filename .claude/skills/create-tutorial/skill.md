# Create Tutorial Post

將 AI Prompt Template 轉換為雙語教學文，優化 Instagram 演算法與 Google SEO。

## 核心目標

從 `Prompt/` 資料夾讀取驗證過的 Prompt Template，生成高互動、雙語（繁體中文 + 英文）的教學文章，並保存到 `Post/` 資料夾。

## 使用方式

```bash
/create-tutorial [Template 檔案名稱或路徑]
```

**範例：**
```bash
/create-tutorial "萬物皆Kirby-日常物體顯現"
/create-tutorial "Test/Office-Paradise-Escape.md"
```

## 執行流程

當用戶調用此 skill 時：

1. **讀取 Template 檔案**
   - 如果提供完整路徑，直接讀取
   - 如果只提供檔名，在 `Prompt/Image` or `Prompt/Video` 資料夾中尋找
   - 提取以下內容：
     - Template 名稱（第一個標題）
     - Template 說明（第一句話）
     - Prompt Template 段落（完整保留）
     - Example 段落（完整保留）

2. **分析內容特性**
   - 識別主題類型（Video / Image）
   - 識別風格（遊戲風格、寫實、卡通等）
   - 識別核心概念（轉換、情緒、荒謬專業等）
   - 提取關鍵技術參數（4K, 60fps, cel-shading 等）

3. **生成教學文章**
   - 按照「教學文格式規範」（見下方）生成內容
   - **CRITICAL**: Prompt Template 和 Example 必須**原封不動**使用，不得修改
   - 生成雙語標題、Hook、參數解析、專家建議等
   - 創建動態 Hashtags

4. **保存檔案**
   - 檔名：`[日期]-[Template名稱].md`（如：`2026-01-03-萬物皆Kirby.md`）
   - 位置：`Post/` 資料夾
   - 編碼：UTF-8

5. **輸出確認**
   - 顯示生成的教學文標題
   - 提供檔案路徑
   - 顯示生成的 Hashtags

## 教學文格式規範

**CRITICAL RULES:**
1. **NO META LABELS**: 不使用 [Title], [Hook] 等標籤，直接輸出內容
2. **BILINGUAL**: 標題格式為「繁體中文 | English」，內文中文先、英文後
3. **CORE CONTENT**: Template 和 Example 必須完整保留，不得修改
4. **VISUAL HIERARCHY**: 使用 emoji 作為區塊分隔
5. **DYNAMIC HASHTAGS**: 根據具體主題生成 5-8 個標籤

### 完整格式結構

```markdown
(Emoji) **[吸睛中文標題] | [Catchy English Headline]**

[中文 Hook：高衝擊力的心理觸發或價值主張]
[English Hook: Mirroring the hook to stop the scroll]

👇 **Prompt Template / 指令模板**

> 提供可重複使用的結構，讓用戶可以自定義。

`(原封不動貼上 Prompt Template 段落)`

📝 **Example / 指令範例**

> 提供高質量、完整填寫的範例版本。

`(原封不動貼上 Example 段落)`

💡 **Key Parameters / 關鍵參數解析**

- **[關鍵詞/參數]**: [中文解釋] ([English Context/SEO Value])
- **[關鍵詞/參數]**: [中文解釋] ([English Context/SEO Value])
（提取 3-5 個最重要的技術參數或創意概念）

🎨 **Pro Tips / 專家建議**
❌ [常見錯誤 中文] ([Common Mistake EN])
✅ [更好的做法/SEO 秘訣 中文] ([Better Approach EN])

✨ **Try This Variation / 延伸挑戰**
👉 [提升分享度的變化建議 中文] ([Variation Idea EN])

💬 [提升留言的互動問題 中文？]
[Engagement Question to boost comments EN?]

---

(生成 5-8 個獨特標籤：2 個利基主題、2 個 SEO/趨勢、2 個社群特定、1 個工具特定)
```

## Hashtag 生成策略

### 標籤分類（5-8 個）

1. **Niche Tags (2個)** - 精確定位核心主題
   - 範例：#Kirby #GameArtAnimation

2. **SEO/Trending Tags (2個)** - 搜尋優化與趨勢
   - 範例：#AIVideoPrompts #GenerativeArtTutorial

3. **Community Tags (2個)** - 社群互動
   - 範例：#AIArtCommunity #PromptEngineering

4. **Tool-Specific Tag (1個)** - 工具專屬
   - 範例：#NanoBananaPro #Midjourney #Veo3

5. **Optional Bilingual Tag (1個)** - 雙語標籤
   - 範例：#AI繪圖教學 #AI藝術

### 標籤品質標準

- ✅ 每個標籤都與內容高度相關
- ✅ 混合高流量（trending）和低競爭（niche）標籤
- ✅ 避免過度通用的標籤（如 #AI #Art）
- ✅ 使用駝峰式命名（#AIArtTutorial）而非全小寫

## Hook 撰寫策略

### 心理觸發類型

1. **驚喜感（Surprise）**
   - 中文：「你絕對想不到一滴水也能變成卡比！」
   - English: "You won't believe what happens to ordinary water drops!"

2. **價值主張（Value）**
   - 中文：「5 秒學會讓萬物變 Kirby 的魔法動畫技巧」
   - English: "Master the magic of transforming anything into Kirby in 5 seconds"

3. **解決痛點（Problem-Solution）**
   - 中文：「角色轉換動畫總是很突兀？這個方法讓變化超流暢！」
   - English: "Tired of abrupt character transformations? This makes it seamless!"

4. **FOMO（Fear of Missing Out）**
   - 中文：「這個 Kirby 變身技巧在 AI 藝術圈爆紅，你還沒試過？」
   - English: "This Kirby transformation technique is trending in AI art—don't miss out!"

5. **好奇心（Curiosity）**
   - 中文：「為什麼粉紅色小圓球能讓人看了就想笑？」
   - English: "Why does a pink sphere make everyone smile? The science behind Kirby!"

## 參數解析撰寫指南

### 必須包含的參數類型

1. **視覺風格參數**
   - 範例：`Nintendo game animation style`, `cel-shading rendering`
   - 解析：說明為何選擇這種風格、對 SEO 的價值

2. **技術規格參數**
   - 範例：`60fps`, `4K resolution`, `motion blur`
   - 解析：說明這些參數如何影響輸出品質

3. **創意概念參數**
   - 範例：`gradual transformation`, `watercolor spreading effect`
   - 解析：說明創意邏輯和為何有效

4. **填空變量**
   - 範例：`[物體]`, `[場景環境]`
   - 解析：說明如何選擇替換內容

### 撰寫格式

```markdown
💡 **Key Parameters / 關鍵參數解析**

- **60fps smooth motion**: 每秒 60 幀讓轉換動畫極度流暢，避免卡頓感 (High frame rate ensures silky-smooth transformation, critical for viewer retention and Instagram algorithm favor)

- **Gradual color shift (1-2s)**: 從一個小點擴散的粉紅漸變，模擬水彩暈染效果 (Watercolor-like spreading creates organic, believable magic—SEO keywords: "gradual transformation", "color morphing animation")

- **Feature emergence (2-3s)**: 五官像水印般若隱若現，而非突然出現 (Subtle facial feature reveal mimics real-world perception, avoiding jarring transitions—"natural animation flow" is a trending search term)
```

## 專家建議撰寫指南

### 常見錯誤 ❌

聚焦於新手最容易犯的 1-2 個錯誤：
- 技術錯誤（參數設置不當）
- 創意錯誤（概念不清）
- 執行錯誤（流程順序錯誤）

### 更好的做法 ✅

提供可操作的改進建議：
- 具體的參數調整
- 創意優化方向
- SEO 秘訣（關鍵字使用）

### 範例

```markdown
🎨 **Pro Tips / 專家建議**

❌ 直接從水滴跳到完整 Kirby，變化太突兀 (Jumping straight from droplet to full Kirby feels jarring and unnatural)

✅ 用「粉紅點擴散 → 五官浮現 → 形狀變圓 → 手腳長出」四階段，讓轉換有邏輯且吸睛 (Use 4-stage transformation: color spread → facial features emerge → shape rounds → limbs appear. This logical flow keeps viewers engaged and boosts watch time—key for Instagram Reels algorithm!)

💡 **SEO 秘訣**: 在生成後的檔名加上 "smooth-transformation" 或 "character-morphing" 等關鍵字，提升 Google 搜尋排名 (Adding "smooth-transformation" to your file names improves Google Images SEO ranking)
```

## 延伸挑戰撰寫指南

### 目標

激發用戶創意，提升內容分享度和二次創作。

### 策略

1. **變化主題** - 建議不同的物體或場景
2. **風格混搭** - 建議結合其他藝術風格
3. **進階技巧** - 建議加入更複雜的元素
4. **跨平台應用** - 建議如何用於不同平台

### 範例

```markdown
✨ **Try This Variation / 延伸挑戰**

👉 試試用「雪花 → Kirby」、「星星 → Kirby」或「咖啡拉花 → Kirby」！每個物體的材質和運動方式不同，會創造出獨特的轉換效果。分享你的創作並標記 #EverythingIsKirby 讓更多人看到！

(Try "snowflake → Kirby", "star → Kirby", or "latte art → Kirby"! Different materials and motion create unique transformation effects. Share your creation with #EverythingIsKirby for maximum visibility!)

🔥 **進階挑戰**: 結合「萬物皆 Kirby」+ 你最喜歡的遊戲角色，創造專屬的角色轉換動畫 (Advanced: Combine this with your favorite game character to create custom transformation animations—huge potential for viral content!)
```

## 互動問題撰寫指南

### 目標

提升留言數，觸發 Instagram 演算法推薦。

### 問題類型

1. **選擇題** - 提供 2-3 個選項讓用戶選擇
2. **開放式創意** - 鼓勵用戶分享自己的想法
3. **挑戰邀請** - 邀請用戶嘗試並回報結果
4. **意見徵求** - 詢問用戶想看什麼主題

### 範例

```markdown
💬 你最想看什麼變成 Kirby？留言告訴我：A) 食物 B) 動物 C) 交通工具！

What would you transform into Kirby? Comment: A) Food B) Animals C) Vehicles!

---

💬 你成功做出來了嗎？分享你遇到的最大挑戰！

Did you succeed? Share the biggest challenge you faced!

---

💬 下一篇教學想看什麼主題？Pokemon 進化？Disney 風格？

What tutorial next? Pokemon evolution? Disney style?
```

## 檔案命名規則

### 格式

```
YYYY-MM-DD-[Template名稱簡化].md
```

### 簡化規則

- 移除特殊字元
- 保留核心關鍵字
- 使用連字號分隔
- 最多 3-4 個關鍵字

### 範例

- `萬物皆Kirby-日常物體顯現.md` → `2026-01-03-Everything-Kirby-Transformation.md`
- `角色進化序列-遊戲風格.md` → `2026-01-03-Character-Evolution-Game-Style.md`
- `Office-Paradise-Escape.md` → `2026-01-03-Office-Paradise-Escape.md`

## 質量標準

每個生成的教學文必須：

- ✅ **Engagement** - Hook 要能在 3 秒內抓住注意力
- ✅ **Clarity** - Template 和 Example 清晰易懂
- ✅ **Actionable** - 參數解析和專家建議具體可操作
- ✅ **SEO-Optimized** - 包含相關關鍵字和 2026 趨勢標籤
- ✅ **Bilingual** - 中英文內容完整且自然
- ✅ **Original** - Hashtags 和互動問題根據具體內容客製化

## 範例輸出

```
✓ 已生成教學文：萬物皆 Kirby 的魔法變身術 | Everything Turns Kirby Magic

類型：Video Tutorial
主題：Character Transformation Animation
風格：Nintendo Game Style
檔案：Post/2026-01-03-Everything-Kirby-Transformation.md

生成的 Hashtags:
#KirbyTransformation #AIVideoPrompts2026 #GameArtAnimation
#SoraAI #AIArtCommunity #PromptEngineering #萬物皆Kirby
```

## 注意事項

- **CRITICAL**: Template 和 Example 段落必須 100% 保留原始內容，不做任何修改
- 讀取檔案時，準確識別 `## Prompt Template` 和 `## Example` 段落
- 如果檔案格式不符合預期，提示用戶檢查檔案結構
- Hashtags 必須根據具體內容生成，不使用通用模板
- 中英文內容應自然流暢，避免機翻感
- 每個教學文都應該是獨特的，根據 Template 的特性客製化
