# Imagine Prompt - 基於 Template 的超級想像力 Prompt 生成器

根據使用者指定的 Prompt Template MD 檔案，僅替換 `[...]` 中的內容，其餘所有文字一字不改，發揮超級想像力生成至少 5 個令人驚嘆的 Prompt 描述。

## 核心目標

讓每個生成的 Prompt 都能讓人發出「挖塞，這個 prompt template 也太讚了吧！」的驚嘆，吸引大量觀眾，富有情感、美學、震撼力，讓人看完就想馬上自己嘗試。

## 使用方式

```bash
/imagine-prompt [prompt md 檔案名稱]
```

**參數說明：**
- `[prompt md 檔案名稱]`：Prompt Template 的 MD 檔名（不需完整路徑，自動搜尋）

**範例：**
```bash
/imagine-prompt "微縮世界.md"
/imagine-prompt "扭蛋機裡的擠壓角色.md"
/imagine-prompt "馬力歐.md"
```

## 執行流程

### 1. 搜尋並讀取 Prompt Template

**搜尋優先順序：**
1. `Prompt/Image/shared/` 資料夾
2. `Prompt/Video/shared/` 資料夾
3. `Prompt/Image/` 資料夾
4. `Prompt/Video/` 資料夾
5. `Test/` 資料夾

**執行步驟：**
- 根據使用者提供的檔名，在上述路徑中搜尋
- 讀取完整的 MD 檔案內容
- 解析出 Prompt Template 部分（主要是 `## Prompt Template` 區塊，如果沒有此標記則取整個 prompt 正文）
- 識別所有 `[...]` 填空位置（包含 `**[...]**` 格式）
- 識別所有 `<...>` 填空位置（部分舊模板使用此格式）

**輸出確認：**
```
✓ 找到 Template：Prompt/Image/shared/微縮世界.md
  - 填空數量：3 個
  - 填空位置：<地上世界>、<上面的細節>、<地下的秘密>
```

---

### 2. 精準解析 Template 結構

**CRITICAL 規則 - 絕對不可違反：**

- **只修改 `[...]` 或 `<...>` 中的內容**
- **所有非填空的文字必須一模一樣，一個字、一個標點、一個空格都不能改**
- **不得增刪任何固定文字**
- **不得調整段落順序或格式**
- **不得修改 Markdown 標記（如 `**`、`##` 等）**

**解析步驟：**
1. 將 Template 拆分為「固定文字」和「填空區塊」
2. 標記每個填空的位置索引
3. 確認填空的類型：
   - **類型 A**：`[變量名稱 with: 說明 / "選項1" / "選項2" / "選項3"]` → 可從選項中選或自創
   - **類型 B**：`**[在此填入...]**` → 自由填入
   - **類型 C**：`<描述說明：例如...>` → 自由填入（舊格式）
4. 驗證：將填空替換回原文後，必須與原 Template 100% 吻合

---

### 3. 發揮超級想像力生成 5+ 個 Prompt

**CRITICAL - 想像力準則：**

每個生成的 Prompt 必須達到以下標準：

#### 驚嘆感檢查（全部必須 YES）
- **「挖塞！」反應**：看到描述時會不由自主驚嘆嗎？
- **視覺震撼**：腦海中浮現的畫面是否令人屏息？
- **情感共鳴**：是否觸動某種情感（溫暖、壯觀、幽默、奇幻、懷舊）？
- **想嘗試慾望**：是否讓人想立刻複製這個 prompt 去生成圖片？
- **分享衝動**：是否讓人想立刻分享給朋友？

#### 創意多樣性要求
5 個 Prompt 必須涵蓋**完全不同的主題方向**，避免雷同：

**建議涵蓋的維度（從中選 5 個不同方向）：**
1. **奇幻史詩** - 魔法、龍、古老文明、神話傳說
2. **溫暖治癒** - 童年回憶、家的溫馨、自然擁抱
3. **科幻未來** - 太空、賽博朋克、未來都市、AI 世界
4. **荒謬幽默** - 反差萌、不可能的組合、黑色幽默
5. **東方美學** - 水墨、禪意、武俠、傳統節慶
6. **暗黑奇幻** - 哥德風、廢墟美學、神秘詭譎
7. **自然壯觀** - 極光、深海、火山、雨林
8. **復古懷舊** - 80年代、蒸汽龐克、老照片、膠片
9. **美食藝術** - 食物的極致美學、料理即藝術
10. **運動動感** - 極限運動、舞蹈、武術的瞬間定格

#### 描述品質要求
- **具體而生動**：不是「美麗的花園」而是「月光下盛開的夜來香花園，螢火蟲在花瓣間穿梭，露珠映射出微型星空」
- **感官豐富**：讓人彷彿能看到、聽到、聞到、觸摸到場景
- **細節驚喜**：藏有讓人細看才發現的小巧思
- **情緒渲染**：每個場景都有獨特的情感氛圍

#### 禁止事項
- **禁止抄襲原 MD 檔中的 Example**：必須完全原創，不得使用原檔案範例中的任何主題或描述
- **禁止平庸描述**：如「一隻可愛的貓」、「美麗的風景」→ 太無聊
- **禁止雷同主題**：5 個 prompt 之間不能有相似主題
- **禁止修改固定文字**：Template 中非 `[...]` / `<...>` 的部分絕對不動

---

### 4. 輸出格式

**每個 Prompt 的輸出格式：**

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Prompt [編號] - [簡短主題標籤]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[完整的 Prompt，所有填空已替換為精心設計的內容，固定文字完全不動]

---
💡 創意亮點：[一句話說明這個 prompt 的驚喜之處]
```

**最終輸出格式：**

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✓ Imagine Prompt 完成
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Template：[檔案名稱]
來源：[檔案路徑]
填空數量：[N] 個
生成 Prompt 數量：[N] 個

[依序列出所有生成的 Prompt]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
使用方式
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

複製任一 Prompt，貼到 AI 圖像生成工具中即可使用。
每個 Prompt 都可以直接使用，不需要額外修改。
```

---

## 範例執行

### 輸入
```bash
/imagine-prompt "微縮世界.md"
```

### 分析過程
```
✓ 找到 Template：Prompt/Image/shared/微縮世界.md

Template 結構解析：
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
固定文字（不可修改）：
  "Isometric 3D diorama of a floating cube, cutaway view."
  "**TOP LEVEL (Surface):** "
  ", featuring "
  "."
  "**BOTTOM LEVEL (Underground Cross-section):** The soil cross-section reveals "
  "."
  "**STYLE:** High-quality clay render, miniature toy aesthetic..."
  "**LIGHTING:** Warm and cozy sunlight on top..."

填空位置（需替換）：
  1. <地上世界：例如熱帶島嶼、充滿霓虹燈的城市>
  2. <上面的細節：例如棕櫚樹和小屋、招牌和行人>
  3. <地下的秘密：例如埋藏的海盜寶箱、恐龍化石、神秘實驗室>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 輸出示範（僅展示 2 個作為格式參考）

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Prompt 1 - 深海龍宮奇境
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

### 微縮世界

Isometric 3D diorama of a floating cube, cutaway view.

**TOP LEVEL (Surface):** a moonlit Japanese fishing village perched on rocky cliffs, with paper lanterns glowing along the shore and a lone torii gate half-submerged in silver tide, featuring weathered wooden boats tied to the pier, an elderly fisherman mending nets, tiny crabs scuttling across wet stones, and wisps of sea fog curling around the lantern light.

**BOTTOM LEVEL (Underground Cross-section):** The soil cross-section reveals a magnificent Dragon Palace (Ryugu-jo) carved from luminous coral and pearl, with a grand throne room where the Sea King entertains a bewildered turtle messenger, treasure rooms overflowing with glowing jellyfish lanterns, and ancient scrolls floating in underwater currents alongside schools of golden koi.

**STYLE:** High-quality clay render, miniature toy aesthetic, tilt-shift photography, shallow depth of field, incredible details, C4D style, volumetric lighting.

**LIGHTING:** Warm and cozy sunlight on top, slightly darker and mysterious underground.

---
💡 創意亮點：日本民間故事「浦島太郎」的龍宮場景藏在漁村地底，水面上的寧靜與海底的奢華形成夢幻反差

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Prompt 2 - 末日種子方舟
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

### 微縮世界

Isometric 3D diorama of a floating cube, cutaway view.

**TOP LEVEL (Surface):** a post-apocalyptic wasteland of cracked earth and rusted machinery, with a single enormous ancient tree breaking through the concrete, its canopy sheltering a tiny makeshift greenhouse, featuring scrap-metal wind turbines spinning slowly, a faded road sign half-buried in sand, scattered remnants of civilization, and one small figure in a hazmat suit carefully watering a seedling.

**BOTTOM LEVEL (Underground Cross-section):** The soil cross-section reveals a thriving underground biodome — a secret seed vault transformed into a living garden paradise, with cascading hydroponic terraces of fruits and flowers in full bloom, bio-luminescent mushroom groves illuminating winding stone pathways, a crystal-clear underground spring feeding into a waterfall, and tiny robotic pollinators tending to rare orchids.

**STYLE:** High-quality clay render, miniature toy aesthetic, tilt-shift photography, shallow depth of field, incredible details, C4D style, volumetric lighting.

**LIGHTING:** Warm and cozy sunlight on top, slightly darker and mysterious underground.

---
💡 創意亮點：地表荒蕪絕望 vs 地下生機盎然，末日中的希望藏在腳下，一個人的堅持守護著人類最後的伊甸園
```

---

## 質量檢查清單

每個生成的 Prompt 必須通過以下檢查：

### 格式正確性（CRITICAL）
- [ ] 所有固定文字與原 Template 100% 一致
- [ ] 只有 `[...]` / `<...>` 中的內容被替換
- [ ] Markdown 格式完全保留
- [ ] 段落順序未被調整

### 內容品質
- [ ] 每個描述都具體、生動、有畫面感
- [ ] 5 個 Prompt 主題方向完全不同
- [ ] 沒有抄襲原 MD 中的 Example
- [ ] 每個都能觸發「挖塞！」的驚嘆
- [ ] 細節豐富，有意想不到的小巧思

### 想像力等級
- [ ] **S 級想像力**：讓人想立刻嘗試生成圖片
- [ ] **情感觸動**：每個場景都有獨特的情感色彩
- [ ] **視覺震撼**：腦海中能清晰浮現壯觀畫面
- [ ] **原創性**：完全原創，非陳腔濫調

## 注意事項

- **CRITICAL**：固定文字一字不改，這是最高優先級的鐵律
- **CRITICAL**：禁止參考或抄襲原 MD 中的 Example 內容
- **CRITICAL**：所有中文輸出使用繁體中文
- 如果 Template 中的填空有提供選項（類型 A），可以從選項中選擇，也可以自創全新的描述
- 自創描述時，要符合填空的語境和角色（如填空要求「角色名」就填角色名，要求「場景」就填場景）
- 生成的內容應該與 Template 的整體風格和意圖協調
- 每次執行至少生成 5 個不同的 Prompt，如果使用者要求更多則配合
