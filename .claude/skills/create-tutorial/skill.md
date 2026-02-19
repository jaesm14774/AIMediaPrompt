# Create Tutorial Post

將 AI Prompt Template 轉換為雙語教學文，搭配三語 SEO Discovery Block，最大化 Instagram 內部搜尋與 Google 外部索引的雙平台可發現性。

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
5. **TRILINGUAL SEO BLOCK**: 教學文末尾附加三語 SEO Discovery Block（emojis + alt text + 15-20 個三語 hashtags）

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

🔍 **SEO Discovery Block**

[Line 1: 3-5 個代表核心主題的 emoji]
[Line 2: 15-20 個三語策略性 hashtags，空格分隔]
```

## SEO Discovery Block 生成策略

### 核心原則

**Keyword Primacy（關鍵字優先）**
Caption 和 alt text 中的自然語言關鍵字是搜尋發現的主要驅動力，hashtags 是次要分類工具。

**Trilingual Parallelism（三語平行）**
用英文、繁體中文、日文的在地化關鍵字表達核心概念。不是直接翻譯，而是使用各語言母語者「實際會搜尋」的詞彙。
- 範例：英文 "cafe hopping" = 日文 #カフェ巡り = 繁中 #咖啡廳打卡

**Dual Optimization（雙平台優化）**
同時針對 Instagram AI 排名系統和 Google 外部索引進行優化，將每篇貼文視為長期 SEO 資產。

**AI Signal Optimization（AI 信號優化）**
Instagram 的 AI 系統會分析 caption、alt text、圖片元資料和圖上文字，所有元素之間需要語義一致性。

---

### SEO Discovery Block 格式（嚴格三行）

**Line 1 — Emoji（3-5 個）**
代表核心主題的 emoji，與 alt text 和 hashtags 語義一致。

**Line 2 — Hashtags（15-20 個）**
空格分隔，三語策略性分佈：

### 標籤策略性分佈（15-20 個）

1. **Primary Keywords（3-4 個）** - 核心主題直接描述詞
   - 三語覆蓋主要概念
   - 範例：#KirbyArt #AI繪圖 #カービィイラスト

2. **Niche Long-tail（5-7 個）** - 多詞組長尾精準搜尋
   - 代表單一可搜尋概念的多字組合
   - 範例：#ChibiCharacterDesign #AI角色生成教學 #ゲームキャラクターアート
   - 目標：高意圖、低競爭的特定搜尋

3. **Community/Style（3-5 個）** - 興趣社群與美學風格連接器
   - 連接既有高互動利基社群
   - 範例：#kawaiiaesthetic #ドット絵好きと繋がりたい #像素藝術

4. **Trending/Seasonal（1-2 個）** - 時效性趨勢標籤
   - 結合當前熱門趨勢提升即時曝光
   - 範例：#AIArt2026 #GenerativeArtTrend

5. **Tool-Specific（1-2 個）** - 工具專屬標籤
   - 範例：#NanoBananaPro #Midjourney #Veo3

### 標籤品質標準

- ✅ **語義一致性**：hashtags 與 alt text 關鍵字對齊，強化 AI 信號
- ✅ **文化在地化**：每個語言版本反映真實使用者搜尋行為，不是直譯
- ✅ **長尾優先**：優先使用多字組合 hashtag 而非單字泛用標籤
- ✅ **無冗餘跨語翻譯**：除非文化上有特殊意義，否則不重複翻譯同一概念
- ✅ **每個標籤有獨立策略目的**：質量優於數量
- ❌ 禁止過度通用標籤（如 #AI #Art #cute）
- ❌ 禁止三個語言都翻譯同一個意思（選擇最適合該語言的不同面向）

### 三語分配建議

| 語言 | 佔比 | 用途 |
|------|------|------|
| English | 50-60% (3-8 個) | 全球搜尋覆蓋、Google SEO 主力 |
| 繁體中文 | 20-30% (3-5 個) | 華語圈社群連接、在地 SEO |
| 日文 | 15-20% (2-4 個) | 日本市場滲透、動漫/遊戲文化圈 |

### 範例 SEO Discovery Block

```
🎮🩷✨🕹️😆
#NanoBananaPro #RetroConsoleKawaii #ChibiSqueezeArt #KirbyFanArt #AIイラスト #GameBoyAesthetic #AI繪圖教學 #ゲームボーイアート #CharacterDesignChallenge #可愛角色插畫 #ドット絵風 #PromptEngineering #SqueezableArt #AIArtTutorial #復古遊戲機萌圖 #カービィ #GenerativeArt2026
```

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

- **CRITICAL：檔名語言必須與 Prompt Template 檔名一致**
- 如果 Prompt 檔名是中文，Post 檔名也用中文
- 如果 Prompt 檔名是英文，Post 檔名也用英文
- **禁止自行翻譯語言**（中文 Prompt 不要翻成英文 Post）
- 移除特殊字元
- 保留核心關鍵字
- 使用連字號分隔
- 最多 3-5 個關鍵字

### 範例

- `萬物皆Kirby-日常物體顯現.md` → `2026-01-03-萬物皆Kirby-日常物體顯現.md`
- `午睡危機.md` → `2026-01-24-午睡危機.md`
- `被逐出年假伊甸園.md` → `2026-02-19-被逐出年假伊甸園.md`
- `StoneAge-Dino-Ride.md` → `2026-02-15-StoneAge-Dino-Ride.md`

## 質量標準

每個生成的教學文必須：

- ✅ **Engagement** - Hook 要能在 3 秒內抓住注意力
- ✅ **Clarity** - Template 和 Example 清晰易懂
- ✅ **Actionable** - 參數解析和專家建議具體可操作
- ✅ **Trilingual SEO** - SEO Discovery Block 涵蓋英文/繁中/日文三語，alt text 100-125 字元
- ✅ **Semantic Coherence** - Emoji、alt text、hashtags 之間語義一致，強化 AI 排名信號
- ✅ **Bilingual Content** - 教學文本體中英文內容完整且自然
- ✅ **Long-tail Focus** - Hashtags 以多字組長尾標籤為主，避免泛用單字標籤
- ✅ **Cultural Localization** - 三語標籤各自反映在地搜尋行為，不是直譯
- ✅ **Original** - Hashtags 和互動問題根據具體內容客製化

## 範例輸出

```
✓ 已生成教學文：萬物皆 Kirby 的魔法變身術 | Everything Turns Kirby Magic

類型：Video Tutorial
主題：Character Transformation Animation
風格：Nintendo Game Style
檔案：Post/2026-01-03-萬物皆Kirby-日常物體顯現.md

SEO Discovery Block:
🩷🎮✨🌟🫧
 #NanoBananaPro #KirbyTransformation #AIキャラクター変身 #AI角色變身教學 #GameArtAnimation #NintendoFanArt #PromptEngineering #カービィ変身アニメ #AIVideoPrompts2026 #GenerativeAnimation #ゲームアート #ChibiTransformation #AIArtCommunity #AI繪圖教學 #CharacterMorphing #可愛動畫教學
```

## 注意事項

- **CRITICAL**: Template 和 Example 段落必須 100% 保留原始內容，不做任何修改
- 讀取檔案時，準確識別 `## Prompt Template` 和 `## Example` 段落
- 如果檔案格式不符合預期，提示用戶檢查檔案結構
- Hashtags 必須根據具體內容生成，不使用通用模板
- 中英文內容應自然流暢，避免機翻感
- 每個教學文都應該是獨特的，根據 Template 的特性客製化
- **SEO Discovery Block 是必要區塊**，必須出現在教學文最末尾
- **日文標籤必須使用母語者的自然搜尋習慣**，不是英文或中文的直譯（例：用 #カフェ巡り 而非 #カフェホッピング）
- **三語標籤應各自涵蓋主題的不同面向**，避免同一個概念翻譯三次
