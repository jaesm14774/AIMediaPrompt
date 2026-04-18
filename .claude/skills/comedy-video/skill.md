---
name: comedy-video
description: 從角色 + 道具 + 喜劇概念生成 9:16 豎版喜劇短片（含品質分析與優化）
---

# Comedy Video — 喜劇短片生成器

從一句話概念出發，生成 9:16 豎版喜劇短片。

**核心原則：Claude 是喜劇編導。目標是帶來快樂、創意與感動——不限定手法，誇張只是其中一種選擇。**

> **Reference image 就是角色說明書。Prompt 的職責是描述動作與情感，不是解釋角色長什麼樣。**

---

## API 已確認限制

| 參數 | 狀態 | 說明 |
|------|------|------|
| `--aspect-ratio 9:16` | ✅ 已支援 | generate_media_gemini.py 已加入此參數 |
| `--duration 4/6/8` | ✅ 支援 | Veo API 僅支援 **4/6/8** 三種時長 |
| `--negative-prompt` | ❌ API 回傳 400 | 禁用 |
| `duration=8s` | ⚠️ 不穩定 | 較易觸發 code 13；優先 6s，必要才用 8s |

---

## 鐵律

| # | 規則 |
|---|------|
| 1 | **先設計後生成** — Beat 骨架 + 完整 Prompt 草稿完成後才生成媒體 |
| 2 | **情感自然優先** — 讓反應感覺必然（"Of course!" 感）；誇張、細膩、反差、溫柔都可以帶來笑點 |
| 3 | **畫風統一是唯一鎖定項** — 全片唯一需要保持一致的是視覺風格；背景、鏡頭、角度皆可隨劇情變化 |
| 4 | **reference 接力** — 每段影片生成後，擷取「給下一幕用的接力幀」時**必須**使用 `--diverge-from`（比對對象＝**本段生成時用的那張 reference**），避免短片段仍卡在片頭、導致下一幕再度從同一構圖起跑；Prompt 首句仍描述該接力幀的畫面狀態 |
| 5 | **禁止文字直出影片** — 所有影片必須搭配 reference image |
| 6 | **時長由動作密度決定** — 先列動詞鏈，數動作數，再對應時長；禁止先設定時長再填內容 |
| 7 | **禁止所有 Beat 同一時長** — 節奏感來自快慢對比 |
| 8 | **繁體中文輸出** — 所有狀態回報使用繁體中文 |
| 9 | **每拍空間錨點（防重複場景）** — `Scene opens with` 必須寫入**與上一拍可區分的地景／構圖錨點**（例如：小徑與草坡交界、木柵欄與花箱、大樹樹蔭邊緣、淺水邊、門廊階前）；**STYLE 仍全片一行鎖定**。`--diverge-from` 只解決「與本段 reference 像素差」，不解決「每拍語意上仍是同一座草坡大合照」—錨點由編導在 Prompt 主動給 |
| 10 | **接點預算（防斷點堆疊）** — 每個 Beat = 一次 Veo 獨立生成 + 合併時一處**硬切**。在故事與動作密度夠用的前提下，**優先較少 Beat**（常見：3 段：8s+8s+6s 或 6s+6s+6s），總長相近時 **少一個 Beat 就少一個 Join**；分段過細會放大斷點感 |

---

## 銜接與多樣性（為何必做）

| 現象 | 成因 | 與本 skill 的對應 |
|------|------|-------------------|
| 畫面重複 | 每拍 Prompt 都只有「陽光草地 + 角色」，模型易回到類似構圖 | **鐵律 9**：每拍強制不同**空間錨點**；`scene_01.png` 的圖生圖 Prompt 也應帶入第一拍錨點 |
| 斷點感強 | 多段硬接；Veo 每段從靜態 reference「重開機」敘事 | **鐵律 10**：減少 Beat；Phase 3 依評級修剪接點（⚠️／❌） |

> **English:** Spatial anchors reduce repeated establishing shots; fewer beats mean fewer hard cuts between independently generated clips.

---

## 【PHASE 0：喜劇設計】

### Step 0 — 解析輸入

提取：角色、道具（若有）、喜劇概念

```
✓ 角色：<名稱>
✓ 道具：<名稱，無則填「無」>
✓ 喜劇概念：<一句話>
✓ TemplateName：<儲存用名稱>
```

---

### Step 1 — 喜劇密度評估 + 節拍設計

#### A. 密度評估

| 輸入密度 | 判斷標準 | 最少 Beat | 策略 |
|---------|---------|----------|------|
| **極薄** | 只說了結果 | 3 | 補鋪陳與期待建立 |
| **標準** | 設定→反應→結果 | 3 | 確保每拍有視覺升級；**優先 3 beats** 以控制接點數（見鐵律 10） |
| **分層** | 反應可再拆 | 4 | 拆分：意識到 → 完全崩潰 |
| **豐富** | 多笑點或有 callback | 4-5 | 完整設計 |

```
笑點密度：[極薄/標準/分層/豐富]
笑點核心機制：<為什麼好笑，一句話>
規劃 Beat 數：<N>
喜劇手法：<選用哪種手法：誇張反應 / 細膩對比 / 反差萌 / 意外收尾 / 其他>
```

#### B. 時長分配（動作密度法）

| Action sequence 動詞數 | 時長 |
|-----------------------|------|
| 1–2 個動作 | **4s** |
| 3–4 個動作 | **6s** |
| 5+ 個動作 | **8s** ⚠️，或**拆成兩個 6s Beat**（會多一處接點）|

> 決策順序：先列動詞鏈 → 數動作數 → 對應時長。**禁止反向。**  
> **與鐵律 10 並行：**若「拆成兩段 6s」僅為了動作數，但會多一個 Join，可優先評估 **單段 8s**（API 穩定時）或**刪減次要動作**，避免接點不必要的堆疊。

#### C. 節拍骨架

```
━━━ <N>拍喜劇骨架 ━━━
角色：<角色名>  |  道具：<道具>  |  喜劇手法：<手法>
笑點核心：<一句話>  |  預估總時長：~<Xs>

Beat 1｜<功能>（<N>個動作 → <Xs>）
  動詞鏈：<動作A> → <動作B> → <情感頂點>
  鏡頭/環境：<鏡頭角度或環境描述，可自由發揮>

Beat 2｜<功能>（<N>個動作 → <Xs>）
  動詞鏈：...
  鏡頭/環境：...
（依 Beat 數繼續）
━━━━━━━━━━━━━━━━━━━━━━━
規劃說明：<為何選此 Beat 數與手法>
```

---

### Step 2 — 風格鎖定

確定角色的視覺風格，全片所有 Prompt 使用**完全相同**的一行風格描述。

```
STYLE: <IP 所屬風格 + 設計語言>
範例：Nintendo Kirby game art style, soft rounded 3D, vibrant pastel colors
範例：Nintendo Pokémon game art, soft rounded 3D, vibrant saturated colors
範例：Disney animated movie style, expressive 3D characters, warm lighting
```

> ✅ **STYLE** 是全片唯一鎖定的一行畫風描述。  
> ✅ **空間與構圖** 不鎖死同一背景，但**每一拍**須在 Prompt（及節拍骨架的「鏡頭/環境」）中**主動規劃不同錨點**（見鐵律 9），避免模型每段都生成同一類「中央團圓」畫面。

---

### Step 3 — 完整 Prompt 草稿

**在生成任何媒體前，輸出所有 Beat 的完整 Prompt。**

```
Beat 1 Prompt（reference：scene_01.png，時長：<Xs>）：
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
<完整 Prompt>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Beat 2 Prompt（reference：frame_01_relay.png，時長：<Xs>）：
...
```

> ✅ 草稿完成後輸出：「✓ 分鏡草稿完成，共 N beats，預計總時長 ~<Xs>。開始媒體生成...」

---

## 【Prompt 格式】

每 Beat 只需四個元素，自然描述即可：

```
[STYLE: <全片統一風格描述>]

Scene opens with <reference 幀的畫面狀態：人物 + 當前動作/表情 + **本拍專屬空間錨點** + 環境>,
<動詞鏈展開：A → B → C，描述角色做了什麼、如何變化、情感如何推進>,
<喜劇/情感落點：這個時刻帶來什麼感受、為什麼好笑或感人>,

[portrait orientation 9:16, <Ns>, seamless continuation]（Beat 2+ 加 seamless continuation）
```

**寫作原則：**
- 用**動詞**描述動作，不解釋角色外觀（reference image 已處理）
- **每一拍**第一句就要讓讀者看出「和上一拍不是同一個無差別廣場」— 空間錨點與動作同級重要（鐵律 9）
- 每個 Beat 只有一個情感核心，不要堆砌多個笑點
- 環境、鏡頭角度、光線可以隨劇情演變，且**每拍應有明確差異**（至少一個地景元素或主構圖軸線不同）
- 最後落點（好笑/感動/意外）要明確說出來，讓模型理解目標情緒

**範例對比：**

❌ 舊式寫法（描述角色外觀、鎖死背景）：
```
[CHARACTER ANATOMY: Kirby perfectly round pink ball body, tiny arms, large blue eyes...]
[POSTURE LOCK: Kirby remains standing. DO NOT walk...]
[BACKGROUND LOCK: pure white background, NO gradient...]
```

✅ 新式寫法（專注動作與情感）：
```
[STYLE: Nintendo Kirby game art style, soft rounded 3D, vibrant pastel colors]

Scene opens with Kirby facing camera with a mischievous gleam in eyes,
mischievous gleam building → corner of mouth curling into a slow smug smirk → one tiny arm rising to point directly at the camera with complete confidence,
the whole expression radiating "you're about to see something incredible" — pure comedic anticipation,

[portrait orientation 9:16, 4s]
```

---

## 【PHASE 1：逐 Beat 媒體生成】

### Step 4 — Beat 1（圖片 → 影片 → 接力幀，diverge-from）

**4a. 生成初始參考圖：**
```bash
export PYTHONIOENCODING=utf-8
python scripts/generate_media_gemini.py \
  --prompt "<開場畫面描述 + 角色情緒 + 環境，強調豎版構圖>" \
  --output "Local_Media/<TemplateName>/comedy/scene_01.png" \
  --type image
```

> 📌 加入：`portrait vertical composition, character centered, 9:16 aspect ratio`  
> 📌 **並帶入 Beat 1 的空間錨點**（與 `Scene opens with` 一致），避免初始圖已是「泛用草地大合照」、後續每段更難拉開差異。

**4b. 生成 Beat 1 影片：**
```bash
export PYTHONIOENCODING=utf-8
python scripts/generate_media_gemini.py \
  --prompt "<完整 Beat 1 Prompt>" \
  --output "Local_Media/<TemplateName>/comedy/clip_01.mp4" \
  --type video \
  --reference-image "Local_Media/<TemplateName>/comedy/scene_01.png" \
  --duration <時長> \
  --aspect-ratio 9:16
```

> ⚠️ code 400（時長不支援）→ 升級：4→6→8s
> ⚠️ code 13（內部錯誤）→ 降級：8→6→4s；同一時長重試 1 次；全失敗才跳過

**4c. 擷取接力幀（與 `scene_01.png` 足夠區隔）：**
```bash
export PYTHONIOENCODING=utf-8
python scripts/concat_video_clips.py \
  --extract-last-frame "Local_Media/<TemplateName>/comedy/clip_01.mp4" \
  --diverge-from "Local_Media/<TemplateName>/comedy/scene_01.png" \
  --output "Local_Media/<TemplateName>/comedy/frame_01_relay.png"
```

> 📌 **為何不用固定 30%？** 短片段（例如 4s）的 30% 僅約 1.2s，畫面仍極接近「本段起始 reference」，下一幕等於重複同一張構圖。`--diverge-from` 會以本段使用的 reference 為基準，在片內多個時間點試擷，直到像素差異足夠（預設 MAE 門檻），仍失敗則改取接近片尾之幀。  
> 📌 **English:** Fixed 30% on short clips stays near the starting keyframe; use `--diverge-from` so the relay frame is visually advanced from the reference image.

```
Beat 1 完成 ✅  [<功能>] (<Xs>)
  scene_01.png → clip_01.mp4 → frame_01_relay.png
```

---

### Step 5 — Beat 2–N（reference 幀接力）

```bash
export PYTHONIOENCODING=utf-8
python scripts/generate_media_gemini.py \
  --prompt "<完整 Beat N Prompt>" \
  --output "Local_Media/<TemplateName>/comedy/clip_0N.mp4" \
  --type video \
  --reference-image "Local_Media/<TemplateName>/comedy/frame_{N-1}_relay.png" \
  --duration <時長> \
  --aspect-ratio 9:16
```

擷取接力幀（最後 Beat 不需要；**diverge-from＝生成本段時用的 reference**）：
```bash
export PYTHONIOENCODING=utf-8
python scripts/concat_video_clips.py \
  --extract-last-frame "Local_Media/<TemplateName>/comedy/clip_0N.mp4" \
  --diverge-from "Local_Media/<TemplateName>/comedy/frame_{N-1}_relay.png" \
  --output "Local_Media/<TemplateName>/comedy/frame_0N_relay.png"
```

> **若前 Beat 失敗**：改用 `frame_{N-2}_relay.png` 作為 **影片** 的 reference；擷取接力幀時 `--diverge-from` 仍須對應「該段實際使用的 reference 圖」，Prompt 首句更新描述該幀狀態

```
Beat N 完成 ✅  [<功能>] (<Xs>)
  frame_{N-1}_relay.png → clip_0N.mp4 → frame_0N_relay.png
```

---

## 【PHASE 2：合併】

### Step 6 — 合併所有成功片段

```bash
export PYTHONIOENCODING=utf-8
python scripts/concat_video_clips.py \
  --clips Local_Media/<TemplateName>/comedy/clip_01.mp4 \
          Local_Media/<TemplateName>/comedy/clip_02.mp4 \
          （依實際成功片段列出）\
  --trim-overlap \
  --trim-prev-end 0.4 \
  --trim-next-start 0.3 \
  --output Local_Media/<TemplateName>/comedy/final_optimized.mp4
```

> **English:** Always trim overlap before the delivery export. Raw concat keeps the last motion of Beat N and the first repeated motion of Beat N+1, which creates the "just finished, then did it again" feeling.

---

## 【PHASE 3：品質分析與優化（video-frames）】

### Step 7 — 接合點分析

**計算接合時間戳：**
```
Join 1 = Beat 1 時長
Join 2 = Beat 1 + Beat 2 時長
...
```

**擷取每個接合點前後幀：**
```bash
export PYTHONIOENCODING=utf-8
mkdir -p "Local_Media/<TemplateName>/comedy/transitions"

# 每個接合點：before = 接合點 - 0.3s，after = 接合點 + 0.2s
ffmpeg -y -ss <接合點 - 0.3> \
  -i "Local_Media/<TemplateName>/comedy/final_comedy.mp4" \
  -frames:v 1 "Local_Media/<TemplateName>/comedy/transitions/join_N_before.jpg"

ffmpeg -y -ss <接合點 + 0.2> \
  -i "Local_Media/<TemplateName>/comedy/final_comedy.mp4" \
  -frames:v 1 "Local_Media/<TemplateName>/comedy/transitions/join_N_after.jpg"
```

**視覺分析（讀取每對 before/after 幀）：**

| 評級 | 症狀 | 處理 |
|------|------|------|
| ✅ 流暢 | 畫面銜接自然 | 無需處理 |
| ⚠️ 輕微 | 輕微位移或表情跳變 | 修剪前 clip 末尾 0.3s |
| ❌ 跳幀 | 角色突變 / 背景閃爍 / 明顯跳切 | 修剪前 clip 末尾 0.5s + 後 clip 開頭 0.3s |

```
━━━ 接合點分析 ━━━
Join 1（Beat 1→2，<Xs>）：[✅/⚠️/❌]  <描述或「流暢」>
Join 2（Beat 2→3，<Xs>）：[✅/⚠️/❌]  <描述>
需修剪：<N 個 / 全部流暢>
━━━━━━━━━━━━━━━━━━
```

> 若全部 ✅，跳過 Step 8-9，final_comedy.mp4 即為最終成品。

---

### Step 8 — 修剪

```bash
# ⚠️ 輕微：剪前 clip 末尾 0.3s
ffmpeg -y -i "clip_N.mp4" -t <原時長 - 0.3> -c copy "clip_N_trim.mp4"

# ❌ 跳幀：剪前 clip 末尾 0.5s + 後 clip 開頭 0.3s
ffmpeg -y -i "clip_N.mp4" -t <原時長 - 0.5> -c copy "clip_N_trim.mp4"
ffmpeg -y -ss 0.3 -i "clip_N+1.mp4" -c copy "clip_N+1_trim.mp4"
```

> 若修剪後 clip 時長低於 2s，保留原始並標記「需人工確認」。

---

### Step 9 — 重合並

```bash
export PYTHONIOENCODING=utf-8
python scripts/concat_video_clips.py \
  --clips Local_Media/<TemplateName>/comedy/clip_01[_trim].mp4 \
          Local_Media/<TemplateName>/comedy/clip_02[_trim].mp4 \
          （有修剪用 _trim 版，無修剪用原始）\
  --output Local_Media/<TemplateName>/comedy/final_optimized.mp4
```

---

### Step 10 — 最終報告

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Comedy Video 完成報告
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Template：<TemplateName>  |  格式：9:16 豎版  |  成功：<N>/<N> beats

Beat 1｜<功能>  ✅  clip_01.mp4（<Xs>）
...
Beat N｜<功能>  ✅  clip_0N.mp4（<Xs>）

接合點品質：
  Join 1：✅/⚠️/❌  <描述>
  ...
  修剪執行：<N 個 / 無>

最終成品：Local_Media/<TemplateName>/comedy/final_optimized.mp4（<Xs>）
（若無需修剪：final_comedy.mp4）

喜劇節拍回顧：
  Beat 1（<功能>）：<動詞鏈核心>
  ...
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 失敗處理

| 情況 | 處理 |
|------|------|
| `scene_01.png` 失敗 | 重試 1 次；仍失敗停止 |
| code 400（時長不支援）| 升級：4→6→8s |
| code 13（內部錯誤）| 降級：8→6→4s；全失敗重試 1 次；仍失敗跳過 |
| 429 / RESOURCE_EXHAUSTED（配額或限速）| 冷卻後重試；必要時改**較短時長**或**減少剩餘 Beat**，避免短時間連續消耗 |
| 接力幀與 reference 太像 | 已內建於 `--diverge-from` 多點試擷；仍不足則改接近片尾；手動備援：`--extract-at "last"` |
| 只有 1 Beat 成功 | 不合併，輸出單幕路徑 |
| 前 Beat 失敗 | 改用 `frame_{N-2}_relay.png`，更新 Prompt 首句 |
| 修剪後時長 < 2s | 保留原始，標記人工確認 |

---

## 儲存結構

```
Local_Media/<TemplateName>/
  comedy/
    scene_01.png             ← Beat 1 參考圖
    clip_01.mp4              ← Beat 1 影片
    frame_01_relay.png       ← Beat 1 接力幀（與 scene_01 足夠區隔）
    clip_02.mp4 / _trim.mp4  ← Beat 2（有修剪則有 _trim）
    frame_02_relay.png
    ...
    final_comedy.mp4         ← 原始合併
    transitions/
      join_1_before.jpg
      join_1_after.jpg
      ...
    final_optimized.mp4      ← 優化成品（若有修剪）
```

---

## 完整範例（卡比獸量體重 — 4 beats）

### 密度評估

```
笑點密度：分層
笑點核心機制：自我認知的荒謬落差 + 逃避行為
喜劇手法：分層反應（半信半疑 → 完全崩潰）+ 反差萌收尾
規劃 Beat 數：4 beats
```

### 節拍骨架

```
━━━ 4拍喜劇骨架 ━━━
角色：Snorlax  |  道具：黑色數位體重計  |  喜劇手法：分層反應 + 反差萌
笑點核心：看到真實體重後分階段崩潰，最後抱著「罪證」逃跑
預估總時長：~20s

Beat 1｜Setup（3個動作 → 6s）
  動詞鏈：踏上體重計 → 閉眼愜意等待 → LED 數字慢慢點亮
  鏡頭/環境：正面中景，溫暖柔光，乾淨背景

Beat 2｜Escalation（3個動作 → 6s）
  動詞鏈：一隻眼半開瞄向數字 → 眉頭微蹙 → 表情從滿足轉向狐疑
  鏡頭/環境：輕微推近，聚焦臉部

Beat 3｜Punchline（3個動作 → 6s）
  動詞鏈：雙眼全開看清數字 → 嘴巴張到最大 → 小手舉起全身顫抖
  鏡頭/環境：維持臉部特寫

Beat 4｜Gag Exit（2個動作 → 4s）
  動詞鏈：抱起體重計貼緊肚子 → 轉身搖擺走遠消失
  鏡頭/環境：鏡頭拉開，看著身影越來越小直到消失
━━━━━━━━━━━━━━━━━━━━━━━━━
規劃說明：崩潰拆兩拍讓笑點層次更豐富；出走 4s 快速收尾。
```

### Beat 1 Prompt（Setup，6s）

```
[STYLE: Nintendo Pokémon game art, soft rounded 3D, vibrant colors, cheerful animation quality]

Scene opens with Snorlax stepping confidently onto a black digital weight scale,
strutting on with smug self-satisfaction → settling into relaxed standing pose as eyes close contentedly → swaying gently while the LED display slowly lights up with a very large number,
the complete absence of self-awareness is the joke — Snorlax has no idea what's coming,

[portrait orientation 9:16, 6s]
```

### Beat 2 Prompt（Escalation，6s）

```
[STYLE: Nintendo Pokémon game art, soft rounded 3D, vibrant colors, cheerful animation quality]

Scene opens with Snorlax standing on scale, eyes closed in blissful satisfaction,
continuing from previous beat, one eye slowly cracks half-open and drifts sideways toward the display → brow furrows slightly as the number registers but doesn't compute → expression shifts from satisfied to suspicious, as if the scale must be broken,
the internal negotiation — "that can't be right" — is written all over the face,

[portrait orientation 9:16, 6s, seamless continuation]
```

### Beat 3 Prompt（Punchline，6s）

```
[STYLE: Nintendo Pokémon game art, soft rounded 3D, vibrant colors, cheerful animation quality]

Scene opens with Snorlax squinting at the scale with one skeptical eye,
continuing from previous beat, both eyes fly fully open as the number truly sinks in → mouth drops to maximum open in pure shock → tiny arms shoot straight up and the whole round body trembles,
it's exactly the number you'd expect for Snorlax — the joke is that Snorlax is the only one surprised,

[portrait orientation 9:16, 6s, seamless continuation]
```

### Beat 4 Prompt（Gag Exit，4s）

```
[STYLE: Nintendo Pokémon game art, soft rounded 3D, vibrant colors, cheerful animation quality]

Scene opens with Snorlax arms raised in full shock pose,
continuing from previous beat, Snorlax snatches the scale and hugs it tightly against belly → turns and waddles away from camera getting smaller and smaller until disappearing into the distance,
taking the evidence with it — the most dignified possible response to an undignified number,

[portrait orientation 9:16, 4s, seamless continuation]
```
