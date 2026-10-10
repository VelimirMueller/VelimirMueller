#!/usr/bin/env python3
"""Make the social preview images of the flagship repos (1280x640 JPEG).

GitHub shows them when a repo link is shared (LinkedIn, Slack, X). Upload by
hand: repo Settings > General > Social preview. Same look as the profile cards:
full-bleed art (assets/art/social-<key>.jpg), name, label, tagline and the
stats from FLAGSHIPS in make-profile.py, so the numbers stay in one place.
The SVG is built in a temp dir and rasterised with headless Chrome.

Needs: python3 -m pip install fonttools brotli pillow, and Google Chrome
       (macOS path by default, or set CHROME to the binary).
Run:   python3 scripts/make-social.py
"""
import base64
import importlib.util
import io
import os
import subprocess
import tempfile

from PIL import Image

HERE = os.path.dirname(__file__)
ROOT = os.path.normpath(os.path.join(HERE, ".."))
_spec = importlib.util.spec_from_file_location("mp", os.path.join(HERE, "make-profile.py"))
mp = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(mp)
THEMES, MONO, MONO_B, SANS, t, pill = mp.THEMES, mp.MONO, mp.MONO_B, mp.SANS, mp.t, mp.pill
CHROME = os.environ.get("CHROME", "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")
REPOS = {"synthwerk": "synthwerk", "code-context": "vlm-code-context-mcp", "portfolio": "portfolio-website"}
th = THEMES["dark"]  # the preview is always dark art


def preview(fs):
    W, H = 1280, 640
    uid = f"vm-social-{fs['key']}"
    jpg = os.path.join(ROOT, "assets", "art", f"social-{fs['key']}.jpg")
    if not os.path.exists(jpg):
        raise SystemExit(f"missing art: {jpg} (see assets/art/PROMPTS.md)")
    with open(jpg, "rb") as fh:
        data = base64.b64encode(fh.read()).decode()
    parts = [f"""<defs>
<linearGradient id="{uid}-shade" x1="0" x2="1" y1="0" y2="0">
<stop offset="0" stop-color="#0a0a0a" stop-opacity="0.95"/><stop offset="0.45" stop-color="#0a0a0a" stop-opacity="0.78"/>
<stop offset="0.78" stop-color="#0a0a0a" stop-opacity="0.10"/><stop offset="1" stop-color="#0a0a0a" stop-opacity="0.25"/></linearGradient>
<pattern id="{uid}-grid" width="32" height="32" patternUnits="userSpaceOnUse"><path d="M32 0H0V32" fill="none" stroke="#ffffff" stroke-opacity="0.05" stroke-width="1"/></pattern>
<pattern id="{uid}-scan" width="4" height="4" patternUnits="userSpaceOnUse"><rect width="4" height="1" fill="#000000" fill-opacity="0.22"/></pattern>
</defs>""",
             f'<rect width="{W}" height="{H}" fill="#08080a"/>',
             f'<image width="{W}" height="{H}" preserveAspectRatio="xMidYMid slice" href="data:image/jpeg;base64,{data}"/>',
             f'<rect width="{W}" height="{H}" fill="url(#{uid}-scan)"/>',
             f'<rect width="{W}" height="{H}" fill="url(#{uid}-shade)"/>',
             f'<rect width="{W * 0.55:.0f}" height="{H}" fill="url(#{uid}-grid)"/>',
             f'<rect y="{H - 5}" width="{W}" height="5" fill="{th["indigo"]}"/>']

    ix, top = 64, 64
    ms = 48
    parts.append(f'<g transform="translate({ix},{top - 6}) scale({ms / 512})">{mp.ml.mark("dark", 512, uid=f"{uid}-mark")}</g>')
    p, _ = pill(ix + ms + 16, top + 2, fs["status"], th, size=13)
    parts.append(p)

    # Wordmark fills at most ~62 % of the width, so the art keeps the right side.
    size = min(104, (W * 0.62) / MONO_B.width(fs["word"], 1, -0.04))
    y = top + 96 + size * 0.70
    w, _ = t(MONO_B, fs["word"], size, ix - size * 0.04, y, th["text"], track=-size * 0.04)
    parts.append(w)
    y += 50
    parts.append(f'<rect x="{ix}" y="{y - 7:.1f}" width="56" height="3" fill="{th["indigo"]}"/>')
    a, _ = t(MONO, fs["label"], 20, ix + 76, y, th["sub"], track=3.6)
    parts.append(a)
    y += 58
    for line in fs["tagline"]:
        s, _ = t(SANS, line, 24, ix, y, "#d4d4d8")
        parts.append(s)
        y += 34

    sy, sx = H - 72, ix
    for value, name in fs["stats"]:
        v, vw = t(MONO_B, value, 40, sx, sy, th["text"], track=-0.8)
        n, nw = t(MONO, name, 13, sx + vw + 12, sy, th["sub"], track=2.2)
        parts += [v, n]
        sx += vw + nw + 56

    if fs["key"] not in REPOS:
        raise SystemExit(f"no repo for flagship {fs['key']!r}: add it to REPOS")
    url = f"github.com/VelimirMueller/{REPOS[fs['key']]}"
    u, uw = t(MONO, url, 15, W - 64, H - 72, th["text"], track=0.6, anchor="end")
    parts.append(f'<rect x="{W - 64 - uw - 16:.1f}" y="{H - 98}" width="{uw + 32:.1f}" height="38" rx="19" '
                 f'fill="#0a0a0a" fill-opacity="0.78" stroke="{th["card_line"]}"/>')
    parts.append(u)
    return mp.svg_doc(W, H, f"{fs['word']} {fs['label'].lower()}.", parts)


def rasterise(svg, out, W=1280, H=640):
    with tempfile.TemporaryDirectory() as tmp:
        src, png = os.path.join(tmp, "p.svg"), os.path.join(tmp, "p.png")
        with open(src, "w") as fh:
            fh.write(svg)
        subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", f"--window-size={W},{H}",
                        f"--screenshot={png}", f"file://{src}"], check=True, capture_output=True)
        buf = io.BytesIO()
        Image.open(png).convert("RGB").save(buf, "JPEG", quality=88, optimize=True, progressive=True)
    if buf.tell() > 1_000_000:
        raise SystemExit(f"{out} is {buf.tell()} bytes, GitHub allows 1 MB")
    with open(out, "wb") as fh:
        fh.write(buf.getvalue())


def main():
    if not os.path.exists(CHROME):
        raise SystemExit(f"Chrome not found at {CHROME}: set CHROME to the binary")
    os.makedirs(os.path.join(ROOT, "assets", "social"), exist_ok=True)
    for fs in mp.FLAGSHIPS:
        out = os.path.join(ROOT, "assets", "social", f"{fs['key']}.jpg")
        rasterise(preview(fs), out)
        print("wrote", out, os.path.getsize(out), "bytes")


if __name__ == "__main__":
    main()
