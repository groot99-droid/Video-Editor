# Video-Editor

One questionnaire-driven video editor, merged from [video-use](https://github.com/browser-use/video-use) and
[clipify](https://github.com/louisedesadeleer/clipify). You answer a few questions first; the answers select a single
use-case recipe, so vertical-vs-landscape, dialogue-vs-action and similar choices never compete.

## Use cases (recipes)

| Recipe | For |
|---|---|
| `highlight_clips` | pull the best moments from long dialogue; optional 9:16 reframe (center / speaker-pan / split-screen) and captions |
| `long_form` | one polished edit: cut retakes, grade, caption, QA |
| `action_montage` | cut on every strike/beat via audio transients; no speech needed |
| `explainer` (add-on) | animated overlays: PIL cards built in, Manim/HyperFrames/Remotion on demand |

More recipes can be added: a module in `src/videoeditor/recipes/`, a playbook, and one branch in the questionnaire.

## Install (Linux)

```bash
sudo apt-get install ffmpeg          # ffmpeg + ffprobe
pip install -e '.[speech,dev]'       # faster-whisper (local transcription) and pytest
```

## Use

```bash
ve ask my_video.mp4                  # interactive questionnaire -> edit/brief.json -> recipe
ve plan --edit-dir edit              # the recipe's concrete steps + playbook path
```

Agents: copy or symlink `skills/video-editor` into your skills directory; it drives the same CLI.
Run `ve --help` for every command. Tests: `pytest`.

## Known limits

- Local Whisper normalizes fillers ("um", "uh"), so filler removal is best-effort.
- No speaker diarization; speaker-follow reframing uses motion inside two hand-placed face regions and needs a static camera.
- Manim needs LaTeX; HyperFrames needs Node 22.

See `NOTICE` for attribution.
