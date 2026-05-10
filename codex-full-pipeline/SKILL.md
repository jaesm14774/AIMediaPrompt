---
name: codex-full-pipeline
description: Run the AIMediaPrompt end-to-end content pipeline in Codex. Use when the user asks for codex-full-pipeline, full-pipeline, one-click AIMediaPrompt production, or prompt plus media generation. This workflow must use the Codex built-in `$imagegen` skill for image generation and must not use Gemini API for image generation, prompt scoring, viral scoring, or media evaluation unless the user explicitly overrides this project rule.
---

# Codex Full Pipeline

Use this skill to execute the AIMediaPrompt pipeline continuously without pausing between routine phases. All Chinese output must use Traditional Chinese.

Do not publish to social media automatically. End by reporting generated files, prompt scores, media paths, upload results, and the manual publish command.

## Core Rules

- Default character placeholder: `[IP角色]`
- Default page/platform: `AI Art Lab`, Facebook
- Publish threshold: S-grade, 9.0/10+
- Maximum prompt optimization iterations: 3
- Gemini API is prohibited by default in this Codex workflow.
- Image generation must use the Codex built-in `$imagegen` skill.
- Do not call `scripts/generate_media_gemini.py --type image`.
- Do not call Gemini-based viral scoring or media evaluation unless the user explicitly allows Gemini.
- If built-in imagegen is unavailable, stop at the media generation phase and report the blocker. Do not silently switch to API fallback.

## Supported Options

- `--type image|video`: default `image`
- `--platforms fb|...`: default `fb`
- `--auto-trend`: discover a timely topic before Phase 1
- `--dry-run`: generate prompt/post assets only; do not create media or upload

## Phase 1 - Prompt Production

Produce two distinct S-grade prompt concepts.

1. Research or infer the strongest content angle from the user request.
2. Generate prompt templates under `Prompt/Image/`, `Prompt/Video/`, or `Test/` according to project conventions.
3. Evaluate each template with the project S-grade rubric. Use non-API/manual rubric scoring unless the user explicitly allows an API evaluator.
4. If a template is below S-grade, optimize and re-evaluate up to 3 times.
5. For each S-grade template, create the tutorial/post file under `Post/Test/`.

Expected outputs:

- Prompt template files
- Tutorial/post files
- S-grade score records
- A list of template names and post paths for Phase 2

## Phase 2 - Imagine Prompts

For each S-grade template, read the template file directly and produce concrete prompts.

- Image mode: create 4 materially different image prompts.
- Video mode: create 2 reference image prompts and 2 video prompts.
- Replace placeholders with concrete visual details while preserving `[IP角色]` when the user did not name a specific character.
- Vary scene, emotion, composition, lighting, and visual hook.

## Phase 3A - Image Mode With `$imagegen`

Use the `$imagegen` skill in default built-in mode. Do not use Gemini or project Gemini scripts for image generation.

For each of the 4 image prompts:

1. Call the Codex built-in image generation path through `$imagegen`.
2. Save successful images to:

```text
Local_Media/<YYYY-MM-DD-TemplateName>/01.png
Local_Media/<YYYY-MM-DD-TemplateName>/02.png
Local_Media/<YYYY-MM-DD-TemplateName>/03.png
Local_Media/<YYYY-MM-DD-TemplateName>/04.png
```

Continue if at least one image succeeds. Stop only if all image generations fail or the built-in imagegen tool is unavailable.

## Phase 3B - Video Mode

Video mode still starts with `$imagegen` for reference images.

1. Generate 2 reference images with `$imagegen`.
2. Save them as:

```text
Local_Media/<YYYY-MM-DD-TemplateName>/01.png
Local_Media/<YYYY-MM-DD-TemplateName>/02.png
```

3. Do not call Gemini video generation unless the user explicitly allows Gemini. If Gemini remains disallowed, stop after reference images and report that video generation requires a non-Gemini video backend.

## Phase 4 - Media Evaluation

Use non-Gemini evaluation by default:

- Local file existence and count check
- Visual spot-check when images can be viewed
- Manual rubric score for subject clarity, composition, emotional impact, technical quality, and social thumbstop

Do not call `scripts/evaluate_media_output.py` when it uses Gemini, unless the user explicitly allows Gemini.

## Phase 5 - Viral Score

Use a non-API/manual rubric by default:

- Copy hook
- Visual impact
- Emotional resonance
- Shareability
- Platform fit

Record but do not block upload unless the user asks for strict publish gating. Any score below S-grade must be marked `Not publish-ready`.

## Phase 6 - Upload URLs

When generated media exists, upload and insert URLs:

```powershell
$env:PYTHONIOENCODING='utf-8'
python scripts/auto_upload_media.py "<YYYY-MM-DD-TemplateName>" --env prod --type image
```

For video:

```powershell
$env:PYTHONIOENCODING='utf-8'
python scripts/auto_upload_media.py "<YYYY-MM-DD-TemplateName>" --env prod --type video
```

Do not delete local media. Do not run `publish_to_social.py` unless the user explicitly asks to publish.

## Stop Conditions

Ask or stop only when:

- Required non-Gemini media generation capability is unavailable.
- Prompt evaluation still fails S-grade after 3 optimization iterations.
- The current media generation stage fully fails.
- Upload credentials or network access are missing.

## Final Report

Report in Traditional Chinese:

- Topic and options used
- S-grade template count and manual-review items
- For each template: prompt path, post path, media folder, successful media count, media score, viral score, upload result
- Failed or skipped items
- Whether anything is not publish-ready
- Manual publish command when content is publish-ready
