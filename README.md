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

## Publishing (`ve publish`)

A safer rebuild of the idea behind browser-automation posters. It uses **official platform APIs only**: OAuth or app
tokens, no passwords, no cookies, no headless browser, no user-agent spoofing. Install: `pip install -e '.[publish]'`.

```bash
ve publish prepare --video final.mp4 --caption "..." --platforms youtube,mastodon --not-made-for-kids   # checks only
ve publish plan                                  # dry run: what each platform would get, in which mode
ve publish init youtube                          # one-time login (tokens go to the OS keyring or env vars, never a file)
ve publish send --platform youtube --yes         # sends as PRIVATE; add --public to post publicly
ve publish handoff                               # no API at all: where to upload + the caption to paste
```

Rules enforced in code (and tested): nothing is sent without `--yes`, one platform per command; **private/draft is the
default** wherever a platform has one; platforms with no private mode (Bluesky, X) refuse unless you pass `--public`; X
also needs `--accept-cost` (pay-per-post); validation errors block sending; the same video + platform + mode + text is
sent once (an idempotency ledger in `<edit>/publish_ledger.jsonl`, `--force` to repeat); secrets are never written to a
file (without a keyring, use `VE_<PLATFORM>_<NAME>` environment variables); the "made for kids" declaration for YouTube is
never defaulted; `--ai-generated` / `--branded` are passed to platforms that have a field for them.

| Platform | Default (no `--public`) | `--public` | Notes |
|---|---|---|---|
| YouTube | private upload | public | official docs say unverified API projects are not forced private; 1 quota unit per upload, 100/day |
| Mastodon | followers-only | public | token from your instance; limits read from the instance |
| LinkedIn | connections-only | public | no draft state exists for API posts; 60-day tokens, no refresh for self-serve apps (`init --manual` if localhost redirects are refused) |
| TikTok | inbox upload (finish in the app; caption not sent) | Direct Post | non-private posting needs an audited app |
| Instagram Reels | container prepared, **not published** (expires in 24 h) | publish | professional account + Meta app; token and user id supplied by you |
| Bluesky | refused | public | no private posts exist |
| X | refused | public + `--accept-cost` | pay-per-use pricing |

**Verified against official docs, but never run against a live account** (no accounts or app approvals exist in the
build environment): request shapes are unit-tested against a fake network and, for the trickiest transports
(multipart, streamed files, Content-Range, basic auth), against a local HTTP server. Details that the docs left open
and that may need adjusting on first real use: Bluesky's service-auth audience/method for video upload (taken from
Bluesky's own client), whether LinkedIn's userinfo `sub` equals the id in `urn:li:person` (override with
`VE_LINKEDIN_PERSON_ID`), whether Instagram resumable upload is available to your login type (or host the file and set
`VE_INSTAGRAM_VIDEO_URL`), TikTok's scope separator, X's billing of media-upload calls, and what YouTube counts as a Short.

## Known limits

- Local Whisper normalizes fillers ("um", "uh"), so filler removal is best-effort.
- Speaker-follow reframing uses motion inside two hand-placed face regions by default and needs a static camera; real speaker turns need the optional whisperX diarization (not testable without a Hugging Face token).
- Manim needs LaTeX; HyperFrames needs Node 22.

See `NOTICE` for attribution.
