---
name: story-video
description: 從故事概念生成 3-7 幕連續影片（24-56 秒），reference 幀接力確保跨幕一致性
---

# Story Video — 分鏡連續影片生成器

從故事概念出發，先評估敘事豐富度並主動補足創意，設計 3-7 幕動態故事弧（每幕 4/6/8s 依情緒份量決定）；reference 幀接力 + 三重文字鎖定確保跨幕連續性，最後合併完整成片。

**核心原則：Claude 是故事設計師，不是輸入複製機。使用者給的是主線，你負責設計完整影片。**

## 使用方式

```bash
# 方式 A：從 Prompt Template 檔案生成
/story-video "TemplateName"
/story-video "TemplateName" --topic "追趕場景"

# 方式 B：直接提供故事概念（skill 自行完成評估與規劃）
/story-video [直接貼入場景概念或故事描述]
```

---

## API 已確認限制（禁止重試）

| 參數 | 狀態 | 替代策略 |
|------|------|---------|
| `--negative-prompt` | ❌ API 回傳 400 | 改用 Anatomy Block 內 FORBIDDEN 清單 |
| `--character-anchor` | ✅ 已支援 | `generate_media_gemini.py` 會自動改用 `veo-3.1-generate-preview`（Lite 不支援 referenceImages） |
| `--aspect-ratio` | ✅ `16:9` / `9:16` | 與 comedy-video 相同，請在指令加上 `--aspect-ratio` |
| duration | ✅ 支援 4/6/8s | 依每幕敘事份量動態指定；若 API 拒絕較短時長，升級到下一檔（4→6→8s）|

---

## 鐵律（CRITICAL — 違反即失敗）

| # | 規則 |
|---|------|
| 1 | **先評估再規劃再生成** — 必須完成敘事評估 + 動態幕數/時長規劃 + 完整 N 幕 Prompt 草稿後，才能開始任何媒體生成 |
| 2 | **三重文字鎖定必填** — 每幕 Prompt 最前端必須含 Anatomy Block + Posture Lock + Background Lock |
| 3 | **reference 接力** — 幕 N 用前幕 30% 幀作為 reference；Prompt 首句精確描述該幀的視覺狀態 |
| 4 | **禁止文字直出影片** — 所有影片必須搭配 reference image |
| 5 | **每幕單一動作** — 每個 clip 只描述 ONE 主要動作；動作必須與 Posture Lock 兼容 |
| 6 | **嚴格序列** — 每幕必須等前幕的 30% 幀擷取完畢後才能繼續，不可跳步 |
| 7 | **失敗時更新 Prompt** — 若幕 N 失敗，幕 N+1 的 "Scene opens with..." 必須改為描述幕 N-1 的 relay 幀狀態 |
| 8 | **繁體中文輸出** — 所有狀態回報、報告、說明使用繁體中文 |
| 9 | **禁止全部同一時長** — 若所有幕時長完全一致（如全8s），必須重新評估是否合理，除非有明確理由 |

---

## 【完整執行流程】

### ── PHASE 0：故事設計（生成任何媒體前必須完成） ──

---

### Step 0 — 解析輸入

**若輸入為 Template 名稱：**
搜尋順序：`Prompt/Image/` → `Prompt/Video/` → `Prompt/Image/shared/` → `Prompt/Video/shared/`
提取：視覺風格 block、角色清單、場景基調。

**若輸入為直接概念/分鏡：**
從輸入中提取：視覺風格、角色清單（含外觀特徵）、場景基調。

**確認後輸出：**
```
✓ 輸入類型：[Template / 直接概念]
✓ TemplateName（儲存路徑用）：<name>
✓ 角色清單：<character 1>, <character 2>...
✓ 視覺風格（已鎖定）：<style keywords>
```

---

### Step 1 — 敘事豐富度評估 + 故事骨架設計

**⚠️ 這是最關鍵的步驟。不要直接把使用者輸入轉成幕；先評估深度，薄的故事必須延伸。**

#### A. 敘事豐富度評估

分析輸入：以現有描述能自然填充多少秒的影片？

| 輸入密度 | 標準 | 幕數下限 | 必做創意策略 |
|---------|------|---------|------------|
| **極薄**（一個瞬間 / 只描述結果）| < 8s | 4 幕 | 補足前因 + 醞釀過程 + 細節放大 + 情感後效 |
| **偏薄**（1-2 個動作，無轉折）| 8-16s | 4 幕 | 加入情緒轉折、反應節拍、環境變化 |
| **適中**（有起承轉合）| 16-32s | 4 幕 | 正常規劃，酌情強化情緒層次 |
| **豐富**（完整多層故事）| 32s+ | 5-7 幕 | 如實規劃，確保每幕節奏有差異 |

**輸出評估結果：**
```
敘事密度：[極薄/偏薄/適中/豐富]
估計輸入可填充時長：~<Xs>
規劃幕數：<N> 幕
創意延伸策略：<具體說明補足了哪些幕、加了什麼創意元素>
```

#### B. 每幕時長分配原則（禁止全部一律 8s）

| 幕的敘事功能 | 建議時長 | 說明 |
|-------------|---------|------|
| 快速 Hook / 高潮爆發 / 視覺衝擊 | **4-6s** | 短促有力，節奏快，讓觀眾第一眼就被抓住 |
| 情感醞釀 / 緊張積累 / 場景過渡 | **6-8s** | 需要呼吸空間，讓情緒發展 |
| 日常開場建立 / 情感收尾回味 | **6-8s** | 給觀眾足夠時間代入情境 |
| 快速反應 / 轉場節拍 | **4s** | 純粹過渡，不拖長 |

#### C. 敘事弧設計（根據評估結果動態選擇）

從以下弧型中選擇，或自由組合適合的結構：

**3 幕極速弧**（適合單一情緒轉折、快節奏概念）：
```
Hook(4-6s) → Climax(6-8s) → End(4-6s)  ≈ 14-20s
```

**4 幕短篇弧**（適合輕鬆日常、有一個轉折的小故事）：
```
Hook(4-6s) → Setup(6-8s) → Climax(6-8s) → End(4-6s)  ≈ 20-28s
```

**5 幕標準弧**（適合有起承轉合的完整故事）：
```
Hook(4-6s) → Setup(6-8s) → Rising(6-8s) → Climax(4-8s) → End(6-8s)  ≈ 26-38s
```

**6-7 幕史詩弧**（適合情節豐富、多層次情緒故事）：
```
Hook → Setup → Rising → Twist → Climax → Aftermath → End
```

**輸出完整故事骨架：**
```
━━━ <N>幕故事骨架 ━━━
主題：<一句話主題>
情緒弧：<開場情緒> → <中段變化> → <結尾情緒>
預估總時長：~<Xs>

幕 1｜<功能>：   <一句話描述>  [<時長>s]
幕 2｜<功能>：   <一句話描述>  [<時長>s]
幕 3｜<功能>：   <一句話描述>  [<時長>s]
（依幕數繼續...）
幕 N｜End：      <結局收尾>    [<時長>s]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
規劃說明：<1-2句說明為何選擇此幕數與時長分配>
```

> ⚠️ 幕的功能標籤可自由命名，不限 Hook/Setup/Rising/Climax/End。
> 依故事需要用：`Discovery`、`Reaction`、`Escalation`、`Transition`、`Reveal`、`Callback`、`Aftermath` 等。

**創意延伸實例：**
> 輸入：「卡比跑去吃蛋糕」（約 5s 就說完了）
>
> 補足後：
> - 幕 1｜Hook(4s)：遠處聞到香氣，眼睛瞬間放光
> - 幕 2｜Reaction(6s)：鏡頭拉遠，卡比目瞪口呆盯著遠處蛋糕
> - 幕 3｜Rising(6s)：飛奔衝刺，留下一道粉色氣流
> - 幕 4｜Climax(8s)：第一口大口咬下，滿臉幸福 close-up
> - 幕 5｜End(6s)：吃完後摸著圓滾滾的肚子，心滿意足
>
> → 5 幕，預估 ~30s（從輸入的 5s 延伸為 30s 完整影片）

---

### Step 2 — 三重鎖定 Block 定義（全片共用）

**確定故事骨架後，定義三個全片共用的 Block。生成過程中逐字不變（除 Posture Lock 的「Only allowed movement」欄位）。**

#### Block A — Anatomy Lock（角色外觀，全片逐字不變）

```
[CHARACTER ANATOMY - NEVER CHANGE:
角色名：<精確形狀描述>, <精確顏色>, <比例>, <五官特徵>;
FORBIDDEN: <最常出現的錯誤特徵，逐條列出>]
```

> 📌 常見 FORBIDDEN 範例：beak（尖嘴）、wings（翅膀）、human proportions（人體比例）、red feet（腳變色）

#### Block B — Posture Lock 模板（每幕只改「Only allowed movement」）

```
[POSTURE LOCK: <角色名> remains <基礎姿勢> throughout entire clip.
DO NOT <禁止動作 1>. DO NOT <禁止動作 2>.
Only allowed movement: <本幕唯一動作>.]
```

#### Block C — Background Lock 模板（每幕依顏色轉場調整）

```
[BACKGROUND LOCK: <背景類型描述>, NO ground texture, NO environment props.
Background color: <本幕起始色> [gradually shifting to <結束色>]. Camera FIXED, <鏡頭角度>.]
```

> 📌 若背景顏色不改變，直接寫：`same <顏色> gradient background as reference frame, NO change.`

---

### Step 3 — 完整分鏡草稿（所有 N 幕 Prompt 預覽）

**在開始生成任何媒體之前，輸出完整分鏡表和所有 N 幕的完整 Prompt。**

#### 分鏡狀態總表

```
━━━ 分鏡狀態總表 ━━━
幕 | 功能     | 時長 | 基礎姿勢 | 背景顏色          | 唯一動作 | 30%幀預期狀態
────────────────────────────────────────────────────────────────────────────────────
1  | <功能>   | <Xs> | <姿勢>  | <起始色>→<結束色> | <動作>  | <顏色>背景，角色<狀態>
2  | <功能>   | <Xs> | <姿勢>  | <起始色>→<結束色> | <動作>  | ...
（依幕數繼續...）
N  | End      | <Xs> | <姿勢>  | <起始色>          | <動作>  | （無需 relay 幀）
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**動作-姿勢相容性核查（通過後才繼續）：**
- 姿勢鎖定為「坐姿」→ 動作只能是手部/表情/頭部動作；禁止出現「走路」「跳起」「站立」
- 姿勢鎖定為「站姿」→ 動作可以是手部/頭部/小幅身體轉動；禁止出現「飛翔」「躺下」
- 核查通過後才繼續

#### 完整 Prompt 草稿（APB-SEC 格式）

對每幕輸出完整 Prompt，標示接力來源與時長：

```
幕 1 Prompt（reference：新生成 scene_01.png，時長：<N>s）：
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
<完整 Prompt 1>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

幕 2 Prompt（reference：frame_01_relay.png，時長：<N>s）：
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
<完整 Prompt 2>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

...（幕 3 至幕 N 同格式）
```

> ✅ 草稿完成後輸出：「✓ 分鏡草稿完成，共 N 幕，預計總時長 ~<Xs>。開始媒體生成...」

---

## 【APB-SEC Prompt 格式說明】

每幕 Prompt 固定分為 6 段，順序不可調換：

```
段 A（Anatomy Lock）：[CHARACTER ANATOMY - NEVER CHANGE: ...]
段 B（Posture Lock）：[POSTURE LOCK: ...]
段 C（Background Lock）：[BACKGROUND LOCK: ...]

段 S（Scene State）：Scene opens with <精確描述 reference 幀的視覺狀態：背景顏色 + 角色姿勢 + 物件位置>,
段 E（Event/Action）：<continuing from previous scene,> <ONE 主要動作（與 Posture Lock 兼容）>,

段 V（Visual Style）：[視覺風格 block（全片逐字不變）],
                      [鏡頭指示（建議 fixed camera）],

段 C2（Continuity）：maintain consistent character anatomy throughout clip,
                     stable proportions from first to last frame,
                     [seamless continuation,]（幕 2+ 加此句）
                     <本幕規劃時長>s
```

> ⚠️ **段 S（Scene State）的關鍵**：必須同時描述背景顏色 + 角色姿勢，缺一不可。
> 例：「Scene opens with Kirby seated cross-legged, open book in tiny nub arms, on a warm golden-yellow gradient background」

---

### ── PHASE 1：逐幕媒體生成 ──

---

### Step 4 — 生成幕 1（圖片 → 影片 → 30% 幀）

**4a. 生成初始參考圖（幕 1 的 reference image）：**
```bash
export PYTHONIOENCODING=utf-8
python scripts/generate_media_gemini.py \
  --prompt "<Block A> + <Block B（幕1版本）> + <Block C（幕1版本）> + <幕1場景描述> + <視覺風格>" \
  --output "Local_Media/<YYYY-MM-DD-TemplateName>/story/scene_01.png" \
  --type image
```

**4b. 生成 Clip 1（依規劃時長）：**
```bash
export PYTHONIOENCODING=utf-8
python scripts/generate_media_gemini.py \
  --prompt "<完整幕1 Prompt（APB-SEC 格式）>" \
  --output "Local_Media/<YYYY-MM-DD-TemplateName>/story/clip_01.mp4" \
  --type video \
  --reference-image "Local_Media/<YYYY-MM-DD-TemplateName>/story/scene_01.png" \
  --duration <幕1規劃時長>
```

> ⚠️ 若 API 拒絕指定時長，升級至下一檔：4s → 6s → 8s

**4c. 擷取 30% 幀（幕 1 relay → 幕 2 reference）：**
```bash
export PYTHONIOENCODING=utf-8
python scripts/concat_video_clips.py \
  --extract-last-frame "Local_Media/<YYYY-MM-DD-TemplateName>/story/clip_01.mp4" \
  --extract-at "30%" \
  --output "Local_Media/<YYYY-MM-DD-TemplateName>/story/frame_01_relay.png"
```

> 📌 30% 對應秒數：4s→1.2s，6s→1.8s，8s→2.4s
> 📌 若 30% 擷取失敗，改用對應秒數重試；仍失敗改用 `--extract-at "last"`

**完成後輸出：**
```
幕 1 完成 ✅  [<敘事功能標籤>] (<實際時長>s)
  scene_01.png → clip_01.mp4 → frame_01_relay.png
```

---

### Step 5 — 生成幕 2–N（reference 幀接力 + 三重鎖定）

對每幕 N（N = 2, 3, ..., 最後幕）：

**5a. 確認 reference 幀狀態：**
- 正常情況：使用 `frame_{N-1}_relay.png`，Prompt 段 S 描述「幕 N-1 的 30% 幀視覺狀態」
- **若幕 N-1 失敗跳過**：使用 `frame_{N-2}_relay.png`，Prompt 段 S 必須更新為描述「幕 N-2 的 30% 幀視覺狀態」

```
⚠️  幕 {N-1} 已跳過 → 幕 {N} 改用 frame_{N-2}_relay.png
    更新 Prompt 段 S：Scene opens with <幕 N-2 的 relay 幀狀態描述>
```

**5b. 生成 Clip N（依規劃時長）：**
```bash
export PYTHONIOENCODING=utf-8
python scripts/generate_media_gemini.py \
  --prompt "<完整幕N Prompt（APB-SEC continuity 格式）>" \
  --output "Local_Media/<YYYY-MM-DD-TemplateName>/story/clip_0N.mp4" \
  --type video \
  --reference-image "Local_Media/<YYYY-MM-DD-TemplateName>/story/frame_0{實際使用的relay幀}_relay.png" \
  --duration <幕N規劃時長>
```

> ⚠️ 若 API 拒絕指定時長，升級至下一檔：4s → 6s → 8s

**5c. 擷取 30% 幀（最後幕不需要）：**
```bash
export PYTHONIOENCODING=utf-8
python scripts/concat_video_clips.py \
  --extract-last-frame "Local_Media/<YYYY-MM-DD-TemplateName>/story/clip_0N.mp4" \
  --extract-at "30%" \
  --output "Local_Media/<YYYY-MM-DD-TemplateName>/story/frame_0N_relay.png"
```

**完成後輸出：**
```
幕 N 完成 ✅  [<敘事功能標籤>] (<實際時長>s)
  frame_{N-1}_relay.png → clip_0N.mp4 → frame_0N_relay.png
```

---

### ── PHASE 2：合併 + 最終報告 ──

---

### Step 6 — 合併所有成功片段

```bash
export PYTHONIOENCODING=utf-8
python scripts/concat_video_clips.py \
  --template "<TemplateName>" \
  --output "Local_Media/<YYYY-MM-DD-TemplateName>/story/final_story.mp4"
```

若有跳過的幕，改用 `--clips` 明確列出成功片段：
```bash
python scripts/concat_video_clips.py \
  --clips Local_Media/<YYYY-MM-DD-TemplateName>/story/clip_01.mp4 \
          Local_Media/<YYYY-MM-DD-TemplateName>/story/clip_03.mp4 \
          Local_Media/<YYYY-MM-DD-TemplateName>/story/clip_05.mp4 \
  --output Local_Media/<YYYY-MM-DD-TemplateName>/story/final_story.mp4
```

---

### Step 7 — 輸出完成報告

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Story Video 完成報告
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Template：<TemplateName>
總成功幕數：<成功N> / <規劃N> 幕
實際總時長：~<各幕時長加總> 秒

幕 1｜<功能>    ✅  clip_01.mp4（<Xs>）
幕 2｜<功能>    ✅  clip_02.mp4（<Xs>）
幕 3｜<功能>    ✅  clip_03.mp4（<Xs>）
（依實際幕數輸出...）
幕 N｜End       ✅  clip_0N.mp4（<Xs>）

合併成品：Local_Media/<YYYY-MM-DD-TemplateName>/story/final_story.mp4

━━━ 故事回顧 ━━━
幕 1（<功能>）：   <敘事一句話>
幕 2（<功能>）：   <敘事一句話>
（依實際幕數輸出...）
幕 N（End）：      <敘事一句話>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 失敗處理

| 情況 | 處理方式 |
|------|---------|
| `scene_01.png` 生成失敗 | 重試 1 次；仍失敗則停止整個流程（無初始 reference 無法繼續）|
| `clip_N` 時長被 API 拒絕 | 升級至下一檔（4→6→8s）重試 |
| `clip_N` 生成失敗（API 錯誤）| 重試 1 次；仍失敗則記錄跳過；**下一幕 Prompt 段 S 必須更新為描述跳過幕的前一幕 relay 幀狀態** |
| 30% 幀擷取失敗 | 改用對應秒數（4s幕→1.2s，6s幕→1.8s，8s幕→2.4s）重試；仍失敗改用 `--extract-at "last"` |
| 連續 3 幕全失敗 | 停止，標記「需人工介入」|
| 最終只有 1 幕成功 | 不合併，直接輸出單幕路徑 |
| 最終有 2+ 幕成功 | 用 `--clips` 明確列出成功片段合併 |

---

## 儲存結構

```
Local_Media/<YYYY-MM-DD-TemplateName>/
  story/
    scene_01.png           ← 幕 1 初始參考圖（Gemini 生圖）
    clip_01.mp4            ← 幕 1 影片（依規劃時長）
    frame_01_relay.png     ← 幕 1 的 30% 幀 → 幕 2 reference
    clip_02.mp4            ← 幕 2 影片（依規劃時長）
    frame_02_relay.png     ← 幕 2 的 30% 幀 → 幕 3 reference
    ...（依幕數擴展）
    clip_0N.mp4            ← 最後幕影片（不需 relay 幀）
    final_story.mp4        ← 合併成品（時長 = 各幕時長加總）
```

---

## IP 角色視覺描述速查

| 角色 | Anatomy Block 關鍵詞 | 基礎姿勢選項 | 足部顏色（易出錯）|
|------|---------------------|------------|-----------------|
| Kirby（卡比） | perfectly round pink ball body, no neck, dark-blue oval eyes, tiny pink nub arms, tiny PINK feet | seated cross-legged / standing still | **PINK**（易被生成為紅色，FORBIDDEN 必須寫 red feet）|
| King Dedede（迪迪迪） | large rotund dark blue penguin-king, red robe, gold crown, wooden mallet, small orange beak | standing upright holding mallet | 黃色爪足 |
| Waddle Dee（瓦豆魯迪） | small round peach ball, large dot eyes, NO mouth, simple feet | walking / standing | 淡橙色 |
| Meta Knight（魅塔騎士） | dark blue round body, silver mask, blue bat wings, purple cape | standing / flying | 黃色爪足 |

---

## 完整範例（卡比從白天到夜晚讀書）

### 敘事豐富度評估

```
敘事密度：偏薄（「卡比讀書」只是一個靜態動作）
估計輸入可填充時長：~8s
規劃幕數：5 幕
創意延伸策略：
  加入「翻開書的儀式感鉤子」、「翻頁建立沉浸感」、「書中情節觸動眼睛發光」、
  「書中文字飛出的情感頂點」、「合書微笑的溫柔收尾」
  + 背景從天藍到深夜藍，以色彩敘述時間流逝
```

### 故事骨架

```
━━━ 5幕故事骨架 ━━━
主題：卡比從白天讀到夜晚，書中世界觸動了他
情緒弧：好奇期待 → 投入沉浸 → 情感共鳴 → 情緒頂點 → 滿足落幕
預估總時長：~38s

幕 1｜Hook（鉤子）：    卡比翻開繪本，強烈視覺開場     [6s]
幕 2｜Setup（建立）：   投入翻頁，背景開始轉暖          [8s]
幕 3｜Rising（轉折）：  眼睛閃光，情感被觸動            [6s]
幕 4｜Climax（高潮）：  書中文字飛出環繞，情緒最高點    [8s]
幕 5｜End（落幕）：     輕輕合書微笑，背景轉深夜        [10s→8s 使用8s]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
規劃說明：5幕提供完整情緒弧；時長有快有慢（6-8s），避免單調節奏。
```

### 分鏡狀態總表

```
幕 | 功能    | 時長 | 姿勢      | 背景顏色           | 唯一動作          | 30%幀預期
───────────────────────────────────────────────────────────────────────────────
1  | Hook    | 6s   | 坐姿盤腿  | 亮天藍             | 翻開繪本          | 天藍背景，卡比剛展開書
2  | Setup   | 8s   | 坐姿盤腿  | 天藍→暖金黃        | 翻一頁            | 金黃背景，卡比執書翻頁中
3  | Rising  | 6s   | 坐姿盤腿  | 暖金黃→橙紅        | 眼睛閃閃發光       | 橙紅背景，卡比眼睛開始發光
4  | Climax  | 8s   | 坐姿盤腿  | 橙紅→深暮紫        | 書中文字飛出環繞   | 暮紫背景，卡比被光包圍
5  | End     | 8s   | 坐姿盤腿  | 深暮紫→深夜藍      | 輕輕合上書，微笑   | （無需 relay）
```

### 幕 1 完整 Prompt（Hook — 開書，6s）

```
[CHARACTER ANATOMY - NEVER CHANGE:
Kirby: perfectly round pink ball body (no neck), tiny pink nub arms on both sides,
tiny PINK feet (NOT red, NOT dark), large round dark-blue oval eyes with white highlights,
simple curved open smile mouth, NO beak, NO wings, NO yellow features, NO human proportions],

[POSTURE LOCK: Kirby remains seated cross-legged on the ground throughout entire clip.
DO NOT stand up. DO NOT walk. DO NOT change sitting position.
Only allowed movement: Kirby opens a colorful picture book with tiny nub arms.],

[BACKGROUND LOCK: simple flat gradient background only, NO ground texture, NO environment props.
Background color: bright sky blue. Camera FIXED, front view, no movement.],

Scene opens with Kirby sitting cross-legged on a simple bright sky-blue gradient background,
book closed on Kirby's lap,
Kirby slowly lifts the book and opens it with tiny nub arms, morning daylight atmosphere,

Nintendo Kirby game art style, vibrant saturated colors, soft rounded 3D character design,
cheerful playful animation, simple flat gradient background, game cutscene quality,
fixed front camera, medium shot,

maintain consistent character anatomy throughout clip,
stable proportions from first to last frame,
6 seconds
```

### 幕 2 完整 Prompt（Setup — 翻頁，背景轉金黃，8s）

```
[CHARACTER ANATOMY - NEVER CHANGE:
Kirby: perfectly round pink ball body (no neck), tiny pink nub arms on both sides,
tiny PINK feet (NOT red, NOT dark), large round dark-blue oval eyes with white highlights,
simple curved open smile mouth, NO beak, NO wings, NO yellow features, NO human proportions],

[POSTURE LOCK: Kirby remains seated cross-legged on the ground throughout entire clip.
DO NOT stand up. DO NOT walk. DO NOT change sitting position.
Only allowed movement: Kirby's tiny nub arms slowly turn one page of the open book.],

[BACKGROUND LOCK: simple flat gradient background only, NO ground texture, NO environment props.
Background color: bright sky blue gradually shifting to warm golden yellow. Camera FIXED, front view.],

Scene opens with Kirby seated cross-legged, colorful picture book open in tiny nub arms, on a bright sky-blue gradient background,
continuing from previous scene, Kirby slowly turns one page of the book, background gradually warms to golden yellow,

Nintendo Kirby game art style, vibrant saturated colors, soft rounded 3D character design,
cheerful playful animation, simple flat gradient background, game cutscene quality,
fixed front camera, medium shot,

maintain consistent character anatomy throughout clip,
stable proportions from first to last frame,
seamless continuation, 8 seconds
```
