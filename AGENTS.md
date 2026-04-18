# AIMediaPrompt - Project Rules

## Language Rules

**CRITICAL**: All Chinese output MUST use **Traditional Chinese (繁體中文)**. Simplified Chinese is strictly forbidden.

- All console output, generated prompts, evaluations, tutorials, and filenames
- Bilingual format: Traditional Chinese first, English second
- When unsure about a character, use the Traditional variant

## Default Behaviors

- **Default character**: Use `[IP角色]` as a variable placeholder in prompt templates — keep characters flexible and interchangeable. Only hardcode a specific character when the scene/concept is **inseparable** from that character's unique traits (e.g., Copy Ability mechanics must be Kirby). When user specifies a character, use it; otherwise default to `[IP角色]` to maximize template reusability.
- **Default FB page**: "AI Art Lab"
- **Quality gate**: Only **S-grade (9.0/10+)** content may be published. A-grade and below must be optimized further.
- **Max optimization iterations**: 3 per prompt before flagging for manual review
- **Publishing frequency**: Max 3-5 posts/day, at least 30 min apart

## Key Commands

```bash
# Upload media to ImgBB and insert URLs into Prompt files
python scripts/auto_upload_media.py "PromptName" --env prod --type image

# Sync prompts to Notion
python scripts/sync_to_notion.py
```

## Workflow Pipeline

See @.Codex/skills/WORKFLOW.md for the complete pipeline and quick reference commands.

## File Naming Conventions

- **Post files**: `YYYY-MM-DD-[Name].md` (e.g., `2026-01-07-Kirby-Office.md`)
- **Post filename language must match Prompt filename language** (no translation)
- **Prompt templates**: `[TemplateName].md` saved to `Test/`

## Quality Gates

| Gate | Threshold | Action if below |
|------|-----------|-----------------|
| Prompt evaluation | S-grade (9.0+) | Re-optimize (max 3 iterations) |
| Viral score | S-grade (9.0+) | Do not publish, optimize |
| Concept creativity | 5/10 | Cap overall at C-grade regardless of technical score |

**IMPORTANT**: Never skip quality gates. Use subagent `quality-reviewer` for pre-publish checks, and subagent `content-publisher` to execute Phase 3 safely.

## Full Pipeline 自動執行規則

**CRITICAL：所有多步驟 Pipeline 必須自動連續執行，不得在每個步驟後停下來等待用戶確認。**

### /full-pipeline 自動執行順序（不中斷）

```
Phase 1（完全自動）：
  1. /research-keyword → 立即繼續
  2. /generate-prompt → 立即繼續
  3. /evaluate-prompt → 未達 S 級立即優化（最多 3 次），達標立即繼續
  4. /create-tutorial → 完成立即進入 Phase 2

Phase 2+3（完全自動）：
  5. /imagine-prompt → image 生成 4 個 Prompt；video 生成 2 個 Prompt，立即繼續
  6. image 流程：generate_media_gemini.py × 4（背景並行）→ 接受部分成功，僅在 4/4 全失敗時才重試或停下
     video 流程：先生成 2 張圖片，再用圖片當 reference 生成 2 支影片
     - API 不穩定、限速、單筆報錯時，不要回頭重生該筆；保留成功項直接繼續
     - video reference 圖階段若至少 1 張成功，就只對成功的項目繼續生成影片
     - 僅在當前階段全部失敗時才需要再嘗試或標記人工介入
     - 必須使用 `export PYTHONIOENCODING=utf-8` 避免 Windows cp950 編碼錯誤
  7. /viral-score → 僅記錄，不阻擋流程，立即繼續
  8. auto_upload_media.py --type image → 完成後輸出最終報告
```

### 僅在以下情況才停下來詢問用戶
- API 金鑰遺失或無法連線
- Prompt 評估 3 次迭代後仍未達 S 級（標記「需人工介入」）
- 媒體生成當前階段全部失敗（image 4/4 失敗，或 video reference 圖 2/2 失敗，或可執行的 video 生成全失敗）

### 已知技術注意事項
- Windows 環境執行 Python 腳本必須加 `export PYTHONIOENCODING=utf-8`（bash）
- `auto_upload_media.py` 需加 `--type image` 或 `--type video` 參數
- `generate_media_gemini.py --type video` 必須搭配 reference image，不可直接文字生影片
- `publish_to_social.py` 刪除範圍：僅 `Local_Media/{template名稱}/`，不影響其他 Template

## Context Management

When compressing, always preserve: current pipeline phase, quality gate results, and paths of files being worked on.
