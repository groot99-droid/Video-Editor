---
name: video-editor
description: Edit video by conversation. Use when the user wants to cut clips from long video, make vertical/9:16 shorts, edit a talking-head or interview into one polished video, cut an action/rhythm montage on impacts, or add animated overlays and captions. Starts with a short questionnaire so only the relevant tools are used.
---

# video-editor

All work goes through the `ve` CLI (install: `pip install -e .` in this repo; `pip install -e .[speech]` for
local Whisper). ffmpeg and ffprobe must be on PATH. Outputs live in `<videos_dir>/edit/`, never in this repo.

## 1. Ask first (this is what keeps competing tools out)

Run `ve ask --schema` to get the questions as JSON, then ask the USER those questions (batch them in one
AskUserQuestion call where possible; skip the ones that clearly do not apply). Then:

```bash
ve ask <source.mp4> [more sources] --answers '{"deliverable":"vertical","content":"dialogue","goal":"highlights","captions":"opus"}'
ve plan --edit-dir <videos_dir>/edit
```

`ve ask` probes the source, prunes questions that do not apply (for example no reframe question when the source
is already vertical, no captions or goal questions for action footage), saves `brief.json`, and selects ONE
recipe. `ve plan` prints that recipe's concrete steps and the path to its playbook. Read the playbook, then follow
the steps. Do not use tools from other recipes.

| Recipe | Chosen when | Core tools |
|---|---|---|
| `highlight_clips` | dialogue + goal=highlights | transcribe, pack, cut, reframe, finish |
| `long_form` | dialogue + goal=single_edit | transcribe, pack, edl, captions, render, timeline |
| `action_montage` | content=action (no Whisper, no captions) | find, verify, edl, render |
| `explainer` (add-on) | overlays != none | overlay (PIL) or Manim/HyperFrames/Remotion slots |

## 2. Rules that apply in every recipe

1. Confirm the plan with the user in plain English before cutting.
2. Never cut inside a word; pad every cut edge 30-200 ms; 30 ms audio fades at every cut (render.py does the fades).
3. Captions are applied LAST in the filter chain; caption times are on the output timeline.
4. Cache transcripts; never re-transcribe an unchanged source.
5. Verify your own output before showing it: `ve timeline` on the RENDERED file at each cut boundary; measure loudness
   rather than guessing; cap self-eval at 3 passes.
6. Local Whisper normalizes fillers ("um", "uh"), so filler removal is best-effort. Say so.
7. Action footage: always `ve verify` strikes visually before rendering; audio finds the sound, not the picture.
8. Never skip a recipe step silently; if something cannot be tested or done, tell the user.

## 3. Command reference

`ve ask | plan | transcribe | pack | find | verify | cut | reframe | edl | captions | render | grade | timeline | overlay | finish`
(`ve <cmd> --help` for flags; `render`, `grade`, `timeline` pass extra flags through, e.g. `ve render edl.json -o out.mp4 --preview`).

Manim overlays: read `skills/manim-video/SKILL.md` (needs LaTeX + `pip install manim`).
Adding a use case: add a recipe module in `src/videoeditor/recipes/`, a playbook, and a branch in
`questionnaire.select_recipes`.
