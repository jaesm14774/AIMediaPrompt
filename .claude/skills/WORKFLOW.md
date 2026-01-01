# AI Prompt Generation Workflow

完整的三階段 AI 圖像 Prompt 生成工作流程。

## 工作流程概覽

```
┌─────────────────────┐
│  1. Research        │  深入研究關鍵字含義
│  /research-keyword  │  避免誤判和表面理解
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  2. Generate        │  基於研究結果生成
│  /generate-prompt   │  確保準確且有創意
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  3. Evaluate        │  多維度評估質量
│  /evaluate-prompt   │  給出改進建議
└─────────────────────┘
```

## 三個核心 Skills

### 🔍 1. Research Keyword
**目的**: 深入了解關鍵字背後的含義、特徵和能力

**使用時機**:
- 涉及特定 IP 角色（如：Kirby、Mario、宮崎駿角色）
- 不熟悉的概念或風格（如：Steampunk、Vaporwave）
- 需要準確理解能力機制（如：Copy Ability、Stand Power）

**輸出**:
- 視覺特徵分析
- 核心能力機制說明
- 常見誤解標註
- 創意應用建議

**範例**:
```bash
/research-keyword "kirby copy ability"
```

### 🎨 2. Generate Prompt
**目的**: 生成高創意、可複用的 AI 圖像 Prompt Template

**改進點**:
- ✅ 整合研究報告的關鍵發現
- ✅ 確保符合核心特徵
- ✅ 避免常見誤解
- ✅ 標註研究來源

**使用方式**:
```bash
/generate-prompt [類型] [主題]
```

**範例**:
```bash
# 有研究基礎（推薦）
/generate-prompt mirror-world "kirby copy ability"

# 快速生成（熟悉主題）
/generate-prompt absurd-professional
```

### 📊 3. Evaluate Prompt
**目的**: 評估 template 的創意性、可複用性和準確性

**評估維度**:
- **創意性** (30%) - 是否有驚喜的視覺組合
- **可複用性** (35%) - 填空設計是否靈活
- **準確性** (25%) - 是否符合研究報告特徵
- **情感共鳴** (10%) - 是否能觸發情感反應

**評級**:
- **S級** (9.0-10.0) - 卓越，可直接使用
- **A級** (8.0-8.9) - 優秀，小幅調整
- **B級** (7.0-7.9) - 良好，需優化
- **C級** (6.0-6.9) - 及格，需大幅改進
- **D級** (<6.0) - 不合格，建議重新生成

**範例**:
```bash
/evaluate-prompt "Kirby-Copy-Ability-Transformation.md"
```

## 使用場景

### 場景 1：特定 IP 角色 Prompt（完整流程）

**問題**: 想為 Kirby 的 Copy Ability 生成 prompt，但不確定機制細節

**流程**:
```bash
# Step 1: 研究 Kirby Copy Ability
/research-keyword "kirby copy ability"

# 輸出：了解到 Kirby 吸收能力時，造型和能力都會改變

# Step 2: 基於研究生成 prompt
/generate-prompt mirror-world "kirby copy ability"

# 輸出：生成了包含「造型轉換」機制的 template

# Step 3: 評估質量
/evaluate-prompt "Kirby-Copy-Ability-Transformation.md"

# 輸出：A級評分，確認準確性和創意性都很好
```

**結果**: 生成的 prompt 準確反映了 Kirby 的 Copy Ability 機制，不會出現誤解。

### 場景 2：熟悉主題的快速生成（簡化流程）

**問題**: 想生成職場動物系列 prompt，主題已經很熟悉

**流程**:
```bash
# Step 1: 直接生成（跳過研究）
/generate-prompt absurd-professional "workplace animals"

# Step 2: 評估質量
/evaluate-prompt "職場動物崩潰.md"

# 輸出：C級評分，建議改進填空設計

# Step 3: 根據建議重新生成
/generate-prompt absurd-professional "workplace animals in tech industry"

# Step 4: 再次評估
/evaluate-prompt "科技業動物工程師.md"

# 輸出：B級評分，可以使用
```

### 場景 3：不熟悉的藝術風格（需要研究）

**問題**: 想使用「賽博朋克 Cyberpunk」風格，但不確定視覺要素

**流程**:
```bash
# Step 1: 研究風格特徵
/research-keyword "cyberpunk visual style"

# 輸出：了解霓虹燈、高科技低生活、雨夜城市等元素

# Step 2: 生成 template
/generate-prompt temporal "cyberpunk aesthetic"

# Step 3: 評估
/evaluate-prompt "賽博朋克時空錯位.md"
```

## 為什麼需要這個工作流程？

### ❌ 沒有研究階段的問題

**錯誤案例：Kirby Copy Ability**

沒有研究，可能生成：
```
"Kirby 吸入一個角色，然後隨機選擇一個能力使用"
```

**問題**:
- ❌ 誤解：Kirby 不是「隨機選擇」能力
- ❌ 遺漏：沒有提到造型會改變
- ❌ 不準確：破壞了 Copy Ability 的核心機制

### ✅ 有研究階段的正確做法

經過研究，生成：
```
"Kirby 吸入 [對象]，造型和能力完全轉換成 [對象] 的樣子，
展示吸收前（粉紅圓球）和吸收後（[能力] 造型）的對比"
```

**優點**:
- ✅ 準確：正確呈現 Copy Ability 機制
- ✅ 完整：包含造型轉換的視覺重點
- ✅ 有趣：強調前後對比的視覺效果

## 文件結構

```
Test/
├── research/                          # 研究報告目錄
│   ├── research_kirby-copy-ability.md
│   ├── research_studio-ghibli.md
│   └── ...
│
├── evaluations/                       # 評估報告目錄
│   ├── evaluation_Kirby-Copy-Ability-Transformation.md
│   └── ...
│
└── [生成的 Prompt Templates]          # Prompt 模板
    ├── Kirby-Copy-Ability-Transformation.md
    ├── 職場動物崩潰.md
    └── ...
```

## 快速參考

| 使用情境 | 推薦流程 | 跳過步驟 |
|---------|---------|---------|
| 不熟悉的 IP 角色 | Research → Generate → Evaluate | 無 |
| 不熟悉的藝術風格 | Research → Generate → Evaluate | 無 |
| 熟悉的主題 | Generate → Evaluate | Research |
| 快速原型測試 | Generate | Research, Evaluate |

## 最佳實踐

1. **第一次接觸特定 IP/概念時，務必先研究**
   - 避免基於表面理解產生錯誤 prompt
   - 建立知識庫供未來使用

2. **生成後一定要評估**
   - 確保創意性和可複用性
   - 根據評分決定是否需要重新生成

3. **保存研究報告**
   - 研究結果可重複使用
   - 建立個人的 IP/概念知識庫

4. **迭代改進**
   - C/D 級評分 → 根據建議重新生成
   - A 級評分 → 小幅調整細節
   - S 級評分 → 可直接使用並分享

## 目標：高質量 Prompt Template

通過這個三階段工作流程，確保每個生成的 prompt template：

✅ **準確** - 符合角色/概念的核心特徵
✅ **有創意** - 驚喜的視覺組合
✅ **可複用** - 靈活的填空設計
✅ **有共鳴** - 觸發情感反應

讓使用者一用就滿意，不需要反覆修改！
