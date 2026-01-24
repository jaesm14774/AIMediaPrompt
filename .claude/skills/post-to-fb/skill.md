# Post to Facebook

自動發布內容到 Facebook 粉專或個人頁面，使用 Chrome DevTools Protocol 繞過反自動化機制。

## 語言要求

**CRITICAL**：所有中文輸出必須使用**繁體中文**，嚴禁使用簡體中文。

## 使用方式

```bash
/post-to-fb [內容] [選項]
```

**參數說明：**
- `[內容]`：貼文內容（文字）或 Post 檔案路徑
- `--image <路徑>`：配圖路徑（可重複使用，最多 4 張）
- `--target <目標>`：發布目標 `page`（粉專）或 `personal`（個人）
- `--page-name <名稱>`：粉專名稱（當 target=page 時必填）
- `--submit`：實際發布（預設為預覽模式）
- `--preview`：僅預覽，不發布

**範例：**
```bash
# 發到粉專（預覽模式）
/post-to-fb "今日教學：Kirby 變身術！🎮" --image cover.png --target page --page-name "AI Art Lab"

# 發到個人頁面（實際發布）
/post-to-fb "分享我的 AI 創作" --image art.png --target personal --submit

# 從 Post 檔案讀取內容
/post-to-fb "Post/shared/2026-01-20-Kirby-Office.md" --image cover.png --target page --page-name "AI Art Lab" --submit

# 多張圖片
/post-to-fb "系列創作分享" --image img1.png --image img2.png --image img3.png --target personal
```

## 執行流程

### Step 1: 準備內容

1. **解析輸入**：
   - 如果是檔案路徑 → 讀取檔案內容
   - 如果是文字 → 直接使用

2. **提取貼文內容**（從 Post 檔案）：
   - 標題（中英文）
   - Hook 段落
   - Hashtags
   - 互動問題

3. **格式化貼文**：
```markdown
[標題]

[Hook 內容]

📝 Prompt Template 連結：[連結]

[互動問題]

[Hashtags]
```

### Step 2: 啟動瀏覽器

1. **尋找 Chrome**：
   - Windows：`C:\Program Files\Google\Chrome\Application\chrome.exe`
   - macOS：`/Applications/Google Chrome.app/Contents/MacOS/Google Chrome`
   - Linux：`/usr/bin/google-chrome`

2. **啟動帶有 Debug Port 的 Chrome**：
```bash
chrome --remote-debugging-port=[port] --user-data-dir=[profile] [FB_URL]
```

3. **連線到 CDP**：
   - 等待 Chrome 啟動
   - 透過 WebSocket 連線到 Debug Port

### Step 3: 登入檢查

1. **檢查登入狀態**：
   - 嘗試訪問 Facebook 發文頁面
   - 檢查是否有發文編輯器

2. **如果需要登入**：
   - 顯示提示訊息
   - 等待使用者手動登入
   - Session 會被保存供下次使用

### Step 4: 發布內容

#### 發布到粉專

1. 導航到粉專管理頁面
2. 找到發文按鈕
3. 輸入文字內容
4. 上傳圖片（如果有）
5. 點擊發布（如果 --submit）

#### 發布到個人頁面

1. 導航到 Facebook 首頁
2. 找到「你在想什麼？」輸入框
3. 輸入文字內容
4. 上傳圖片（如果有）
5. 點擊發布（如果 --submit）

### Step 5: 結果確認

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✓ Facebook 發文完成
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

目標：粉專 - AI Art Lab
內容：今日教學：Kirby 變身術！🎮...
圖片：1 張
狀態：已發布

瀏覽器將在 10 秒後關閉...
```

## Script Directory

**Important**: 所有腳本位於 `scripts/` 子目錄。

**Script Reference**:
| Script | Purpose |
|--------|---------|
| `scripts/fb-browser.ts` | Facebook 瀏覽器自動化主程式 |
| `scripts/copy-to-clipboard.ts` | 複製內容到剪貼簿 |
| `scripts/paste-from-clipboard.ts` | 模擬貼上操作 |

**執行方式**：
```bash
npx -y bun ${SKILL_DIR}/scripts/fb-browser.ts [options] [text]
```

## 技術細節

### Chrome DevTools Protocol (CDP)

使用 CDP 而非 Puppeteer/Playwright 的原因：
- **繞過反自動化**：CDP 連接真實 Chrome，不會被偵測為自動化
- **保持登入狀態**：使用獨立 profile 保存 session
- **減少依賴**：不需要額外安裝 browser driver

### 圖片上傳方式

1. **剪貼簿方式**（優先）：
   - 將圖片複製到系統剪貼簿
   - 在編輯器中模擬 Ctrl+V / Cmd+V
   - 更接近真實使用者行為

2. **File Input 方式**（備用）：
   - 找到隱藏的 file input 元素
   - 直接設定檔案路徑

### Profile 目錄

- **Windows**：`%APPDATA%\fb-browser-profile`
- **macOS**：`~/Library/Application Support/fb-browser-profile`
- **Linux**：`~/.local/share/fb-browser-profile`

首次使用會建立新的 profile，登入後 session 會被保存。

## 注意事項

### 安全性

- **Cookie 安全**：Profile 目錄包含登入 cookie，請勿分享
- **帳號風險**：頻繁自動發文可能觸發 Facebook 安全機制
- **建議做法**：
  - 每次發文間隔至少 30 分鐘
  - 不要發布垃圾內容
  - 保持正常使用者行為模式

### 限制

- **圖片數量**：單次發文最多 4 張圖片
- **發文頻率**：建議每天不超過 5 篇
- **內容長度**：過長的內容可能需要分段

### 錯誤處理

| 錯誤 | 可能原因 | 解決方式 |
|-----|---------|---------|
| Chrome 找不到 | 未安裝 Chrome | 安裝 Google Chrome |
| 連線超時 | Chrome 啟動失敗 | 檢查 profile 權限 |
| 編輯器找不到 | 未登入或頁面變更 | 手動登入或更新選擇器 |
| 上傳失敗 | 圖片格式不支援 | 使用 PNG/JPG 格式 |

## 與其他 Skills 整合

```
/create-tutorial → /generate-image → /viral-score → /post-to-fb
                                                              │
                                                              ▼
                                                    (若 >= S 級且 --submit)
                                                              │
                                                              ▼
                                                       實際發布到 FB
```

建議工作流程：
1. 先使用 `/viral-score` 評估內容品質
2. 達到 S 級（9.0+）以上再使用 `/post-to-fb --submit`
3. 低於 S 級使用預覽模式檢視，然後優化內容

