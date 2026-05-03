# AI Prompt Generation Workflow

完整的 AI Prompt 生成流程，以 `/full-pipeline` 為主。

## 唯一標準流程

`/full-pipeline` 的終點一律是 **媒體上傳完成**，不是自動發布。

```
Phase 1：內容創作
/research-keyword
  → /generate-prompt
  → /evaluate-prompt
  → 未達 S 級：優化後重評，最多 3 次
  → 達 S 級：/create-tutorial

Phase 2：媒體生成
/imagine-prompt
  → image：產生 4 個 Prompt
  → video：產生 2 個 Prompt
  → image：python scripts/generate_media_gemini.py × 4，接受部分成功
  → video：先生 2 張 reference 圖，再生 2 支影片；若只有部分 reference 圖成功，就只繼續成功的項目

Phase 3：成品評估 + 品質關卡 + 媒體上傳
python scripts/evaluate_media_output.py Local_Media/<YYYY-MM-DD-TemplateName>
  → 記錄成品分數（不阻擋流程）
  → reuse_components / reject_components 自動更新 template_components/library.json
/viral-score
  → 未達 S 級：停止，不進入上傳
  → 達 S 級：python scripts/auto_upload_media.py

手動發布
python scripts/publish_to_social.py
```

## Phase 定義

| Phase | 內容 | 結束條件 |
|------|------|---------|
| Phase 1 | 研究、生成、評估、教學文產出 | 產出 `Post/Test/` 教學文 |
| Phase 2 | 以 `imagine-prompt` 依類型產生 Prompt；圖片流程生成 4 張圖，影片流程先生 2 張 reference 圖再生成 2 支影片 | `Local_Media/<YYYY-MM-DD-TemplateName>/` 內有對應媒體 |
| Phase 3 | `evaluate_media_output.py` 成品評估 → `viral-score` → `auto_upload_media.py` 上傳 | URL 寫回檔案，評估報告輸出到 `logs/media_evaluations/` |
| 手動發布 | 使用者自行執行 `publish_to_social.py` | 發布到目標平台 |

## 一鍵自動化

| 使用情境 | 推薦指令 |
|---------|---------|
| 完整主流程：研究到媒體上傳 | `/full-pipeline "主題" --platforms fb` |
| 只生成內容 | `/auto-produce-prompt "主題"` |
| 手動發布已完成內容 | `python scripts/publish_to_social.py "PostFileName" --template "TemplateName" --platforms fb` |
| 批次發布已準備好的內容 | `python scripts/daily_publish.py --platforms fb` |

## 快速參考

| 使用情境 | 推薦指令 |
|---------|---------|
| 研究關鍵字（IP / 角色） | `/research-keyword "主題"` |
| 研究爆量趨勢題材 | `python scripts/synthesize_trend_research.py "主題" --source research/templates/viral-source-template.md` |
| 生成 Prompt Template（手工） | `/generate-prompt [類型] [主題]` |
| 生成 Prompt Template（元件組裝） | `python scripts/assemble_prompt_template.py --name "名稱" --media-type image --scene [id] ...` |
| 列出可用元件 | `python scripts/assemble_prompt_template.py --list-components` |
| 評估 Prompt Template | `/evaluate-prompt "檔案名稱"` |
| 生成教學文 | `/create-tutorial "Template名稱"` |
| 產生衍生 Prompt | `/imagine-prompt "template.md"` |
| 生成圖片 | `python scripts/generate_media_gemini.py --prompt "..." --template "Name" --index 1 --type image` |
| 生成影片（需 reference 圖） | `python scripts/generate_media_gemini.py --prompt "..." --template "Name" --index 1 --type video --reference-image "Local_Media/YYYY-MM-DD-Name/01.png"` |
| **評估實際成品** | `python scripts/evaluate_media_output.py Local_Media/YYYY-MM-DD-模板名稱 --prompt-file Prompt/Image/模板名稱.md` |
| 評估病毒潛力 | `/viral-score "Post/Test/檔案.md" --type image/video --platform fb` |
| 上傳媒體 | `python scripts/auto_upload_media.py "YYYY-MM-DD-名稱" --env prod --type image` |
| 手動發布 | `python scripts/publish_to_social.py "PostFileName" --template "TemplateName" --platforms fb` |

## 進階回饋迴圈（三工具串聯）

這條路線讓 repo 從「寫 prompt」進化為「累積自己的題材判斷與視覺語法資產」：

```
1. 手動填入觀察 → research/templates/viral-source-template.md
2. synthesize_trend_research.py → 抽出爆量共通模式與 5 個可開發概念
3. assemble_prompt_template.py --research-note "..." → 把研究洞察直接壓進模板
4. /evaluate-prompt + 媒體生成
5. evaluate_media_output.py → 得出 reuse_components / reject_components
6. 自動更新 template_components/library.json → 淘汰低分元件，固化高勝率語法，加入新創意
```

每跑一次，元件庫就更精準一點；這是 `/full-pipeline` 沒有的橫向積累能力。

## 強制規則

1. `full-pipeline` 一律只到媒體上傳，不自動發布。
2. `viral-score` 必須達到 S 級（9.0+ 且通過 `/viral-score` 硬門檻）才可繼續上傳。
3. `evaluate-prompt` 的 S 級也不是只有 9.0+，還必須通過概念與強烈印象的硬門檻。
4. `imagine-prompt` 在圖片流程固定產生 4 個 Prompt，在影片流程固定產生 2 個 Prompt。
5. `auto-produce-prompt` 固定產生 2 個主題，不是 3 個。
6. 教學文一律先輸出到 `Post/Test/`。
7. `/指令` 是 Claude skill 呼叫，`python scripts/...` 是直接執行腳本，兩者角色不同，不互相衝突。
8. `--type video` 不可直接用文字生影片，必須先生圖片，再用圖片當 reference。
9. 媒體生成遇到 API 不穩、限速或單筆失敗時，不要回頭重生失敗項；保留成功項繼續，僅在同一階段全部失敗時才再嘗試或標記人工介入。
