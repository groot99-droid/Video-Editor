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

Optional extras (each is lazy-loaded; the base install stays light):

| Extra | Adds | Improves |
|---|---|---|
| `speech-plus` | [whisperX](https://github.com/m-bain/whisperX): forced word alignment, optional speaker labels (`ve transcribe --backend whisperx [--diarize]`) | tighter cut edges and captions; `ve reframe --turns` follows real speaker turns. Several GB (torch). Diarization needs a Hugging Face token and the pyannote terms; NLTK `punkt_tab` is downloaded once |
| `stems` | [Demucs](https://github.com/adefossez/demucs) (maintained fork, v4.1): `ve separate`, `ve transcribe --clean-speech`, `ve find --stem drums` | music under speech; action montages with a soundtrack. About 1.5x track length on CPU |
| (Node) | Remotion overlay template: `ve overlay --engine remotion` | titles and caption pages as overlays, opaque MP4 or transparent WebM. Needs Node 20.19+/22.13+; Remotion has its own [licence](https://www.remotion.pro/license) (free for individuals, for-profit orgs up to 3 people, non-profits) |

## Use

```bash
ve ask my_video.mp4                  # interactive questionnaire -> edit/brief.json -> recipe
ve plan --edit-dir edit              # the recipe's concrete steps + playbook path
```

Agents: copy or symlink `skills/video-editor` into your skills directory; it drives the same CLI.
Run `ve --help` for every command. Tests: `pytest`.

## Known limits

- Local Whisper normalizes fillers ("um", "uh"), so filler removal is best-effort.
- Speaker-follow reframing uses motion inside two hand-placed face regions by default and needs a static camera; real speaker turns need the optional whisperX diarization (not testable without a Hugging Face token).
- Manim needs LaTeX; HyperFrames needs Node 22.

See `NOTICE` for attribution.
