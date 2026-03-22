# AIMediaPrompt - Project Rules

## Language Rules

**CRITICAL**: All Chinese output MUST use **Traditional Chinese (繁體中文)**. Simplified Chinese is strictly forbidden.

- All console output, generated prompts, evaluations, tutorials, and filenames
- Bilingual format: Traditional Chinese first, English second
- When unsure about a character, use the Traditional variant

## Default Behaviors

- **Default character**: Kirby (unless user explicitly specifies another character or the theme is incompatible)
- **Default FB page**: "AI Art Lab"
- **Quality gate**: Only **S-grade (9.0/10+)** content may be published. A-grade and below must be optimized further.
- **Max optimization iterations**: 3 per prompt before flagging for manual review
- **Publishing frequency**: Max 3-5 posts/day, at least 30 min apart

## Project Architecture

```
AIMediaPrompt/
├── CLAUDE.md                    # This file - universal rules
├── .claudeignore                # Context exclusions
├── .claude/
│   ├── settings.local.json      # Permissions & hooks
│   └── skills/                  # All skills (see WORKFLOW.md)
│       ├── WORKFLOW.md          # Pipeline overview
│       ├── auto-produce-prompt/ # Phase 1 automation
│       ├── auto-daily-publish/  # Phase 2+3 automation
│       ├── full-pipeline/       # End-to-end automation
│       ├── research-keyword/    # Keyword research
│       ├── generate-prompt/     # Prompt generation
│       ├── evaluate-prompt/     # Quality evaluation
│       ├── create-tutorial/     # Tutorial post creation
│       ├── generate-image/      # AI image generation (Gemini)
│       ├── imagine-prompt/      # Batch fill templates
│       ├── viral-score/         # Viral potential scoring
│       └── post-to-fb/          # Facebook auto-posting
├── Test/                        # Working area for prompts & research
│   ├── research/                # Research reports
│   └── evaluations/             # Evaluation reports
├── Prompt/
│   ├── Image/shared/            # Published image prompts
│   └── Video/shared/            # Published video prompts
├── Post/
│   ├── Test/                    # Pending review posts
│   └── shared/                  # Published posts
├── Local_Media/                 # Local images (pre-upload)
├── scripts/                     # Python & TS automation scripts
│   ├── hooks/                   # Claude Code hook scripts
│   ├── auto_upload_media.py     # Upload to ImgBB/Cloudinary
│   └── sync_to_notion.py        # Sync to Notion DB
└── config/                      # Config files (gitignored)
```

## Key Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Upload media to ImgBB and insert URLs into Prompt files
python scripts/auto_upload_media.py "PromptName" --env prod --type image

# Sync prompts to Notion
python scripts/sync_to_notion.py
```

## Workflow Pipeline

```
Phase 1: Content Creation
  /research-keyword -> /generate-prompt x3 -> /evaluate-prompt loop -> /create-tutorial

Phase 2: Image Processing
  /generate-image (Gemini Web API, original quality)

Phase 3: Quality & Publishing
  /viral-score -> /post-to-fb -> upload media -> sync Notion -> archive

One-key commands:
  /auto-produce-prompt "topic"     # Phase 1 only
  /auto-daily-publish              # Phase 2+3 only
  /full-pipeline "topic"           # All phases end-to-end
```

## File Naming Conventions

- **Post files**: `YYYY-MM-DD-[Name].md` (e.g., `2026-01-07-Kirby-Office.md`)
- **Post filename language must match Prompt filename language** (no translation)
- **Prompt templates**: `[TemplateName].md` saved to `Test/`
- **Research reports**: `research_[keyword].md` in `Test/research/`

## Quality Gates

| Gate | Threshold | Action if below |
|------|-----------|-----------------|
| Prompt evaluation | S-grade (9.0+) | Re-optimize (max 3 iterations) |
| Viral score | S-grade (9.0+) | Do not publish, optimize |
| Concept creativity | 5/10 | Cap overall at C-grade regardless of technical score |

## Hooks

Deterministic rules are enforced via hook scripts in `scripts/hooks/`:
- `validate-chinese.py`: Blocks simplified Chinese in `.md` files under `Post/`, `Prompt/`, `Test/`
- `validate-filename.py`: Blocks Post files that don't match `YYYY-MM-DD-[Name].md` format
