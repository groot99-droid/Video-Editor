"""Find the best moments in long dialogue video and cut them as standalone clips (vertical or not)."""
from videoeditor.recipes import Recipe, register


def steps(b: dict) -> list[str]:
    src = b["sources"][0]
    out = ["# highlight_clips: dialogue -> several short clips",
           f"ve transcribe {src}",
           "ve pack --edit-dir <edit>            # writes takes_packed.md; read it and pick 3-5 candidates (10-25s each)",
           "# confirm the candidate list (start, end, why, title) with the user before cutting"]
    out.append(f"ve cut {src} --start S --end E -o <edit>/clips/clip_N.mp4   # once per chosen clip")
    if b["deliverable"] == "vertical":
        if b.get("source_orientation") == "landscape":
            mode = b.get("reframe", "center")
            roi = " --left-roi x,y,w,h --right-roi x,y,w,h" if mode in ("pan", "split") else ""
            out.append(f"ve reframe <edit>/clips/clip_N.mp4 --mode {mode}{roi} -o <edit>/clips/clip_N_v.mp4")
            if mode in ("pan", "split"):
                out.append("# place ROIs over each face's mouth+chin from one sample frame; at most 2 tuning passes")
        else:
            out.append("# source is already vertical; no reframe needed")
    cap = b.get("captions", "none")
    final = "<edit>/clips/clip_N_v.mp4" if b["deliverable"] == "vertical" and b.get("source_orientation") == "landscape" else "<edit>/clips/clip_N.mp4"
    flags = []
    if cap != "none":
        flags.append(f"--captions {cap}")
    if b.get("grade", "none") != "none":
        flags.append(f"--grade {b['grade']}")
    finish = " ".join(["ve finish", final, *flags, "-o <out>/clip_N_final.mp4"])
    out.append(f"{finish}   # transcribes the clip, captions, grade, loudnorm")
    out.append("ve timeline <final> START END      # self-check cut boundaries and caption readability")
    return out


register(Recipe("highlight_clips", "Highlight clips", "Pick the best moments from long dialogue and cut standalone clips.", steps))
