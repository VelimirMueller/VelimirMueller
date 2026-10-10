#!/usr/bin/env python3
"""Make the LinkedIn profile banner (1584x396 JPEG) in the profile look.

LinkedIn lays the profile photo over the bottom-left of the banner and prints
the name below it, so the banner carries the stance, right-aligned, and the art
fills the left. Upload by hand: LinkedIn profile > edit background photo.
Art: assets/art/linkedin.jpg (prompt in assets/art/PROMPTS.md).

Needs: python3 -m pip install fonttools brotli pillow, and Google Chrome.
Run:   python3 scripts/make-linkedin.py
"""
import base64
import importlib.util
import os

HERE = os.path.dirname(__file__)
ROOT = os.path.normpath(os.path.join(HERE, ".."))
_spec = importlib.util.spec_from_file_location("ms", os.path.join(HERE, "make-social.py"))
ms = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ms)
mp = ms.mp
MONO, MONO_B, t, pill = mp.MONO, mp.MONO_B, mp.t, mp.pill
th = mp.THEMES["dark"]

W, H = 1584, 396
STANCE = ["Models propose.", "Rules gate.", "I decide."]
ROLE = "SENIOR PRODUCT ENGINEER · FULL-STACK · AI TOOLING"
TAG = "BERLIN · BUILDING WITH AI, NOT BY AI"
URL = "velimir-mueller.de"


def banner():
    uid = "vm-linkedin"
    jpg = os.path.join(ROOT, "assets", "art", "linkedin.jpg")
    if not os.path.exists(jpg):
        raise SystemExit(f"missing art: {jpg} (see assets/art/PROMPTS.md)")
    with open(jpg, "rb") as fh:
        data = base64.b64encode(fh.read()).decode()
    parts = [f"""<defs>
<linearGradient id="{uid}-shade" x1="1" x2="0" y1="0" y2="0">
<stop offset="0" stop-color="#0a0a0a" stop-opacity="0.94"/><stop offset="0.42" stop-color="#0a0a0a" stop-opacity="0.74"/>
<stop offset="0.72" stop-color="#0a0a0a" stop-opacity="0.08"/><stop offset="1" stop-color="#0a0a0a" stop-opacity="0.2"/></linearGradient>
<pattern id="{uid}-grid" width="32" height="32" patternUnits="userSpaceOnUse"><path d="M32 0H0V32" fill="none" stroke="#ffffff" stroke-opacity="0.05" stroke-width="1"/></pattern>
<pattern id="{uid}-scan" width="4" height="4" patternUnits="userSpaceOnUse"><rect width="4" height="1" fill="#000000" fill-opacity="0.22"/></pattern>
</defs>""",
             f'<rect width="{W}" height="{H}" fill="#08080a"/>',
             f'<image width="{W}" height="{H}" preserveAspectRatio="xMidYMid slice" href="data:image/jpeg;base64,{data}"/>',
             f'<rect width="{W}" height="{H}" fill="url(#{uid}-scan)"/>',
             f'<rect width="{W}" height="{H}" fill="url(#{uid}-shade)"/>',
             f'<rect x="{W * 0.5:.0f}" width="{W * 0.5:.0f}" height="{H}" fill="url(#{uid}-grid)"/>',
             f'<rect y="{H - 4}" width="{W}" height="4" fill="{th["indigo"]}"/>']

    rx = W - 80  # right edge of the text block
    _, pw = pill(0, 0, TAG, th, size=12)  # measure first, the pill has no right anchor
    ms_ = 40
    p, _ = pill(rx - pw, 64, TAG, th, size=12)
    parts.append(f'<g transform="translate({rx - pw - ms_ - 14},{58}) scale({ms_ / 512})">'
                 f'{mp.ml.mark("dark", 512, uid=f"{uid}-mark")}</g>')
    parts.append(p)

    y = 160
    for line in STANCE:
        s, _ = t(MONO_B, line, 44, rx, y, th["text"], track=-1.0, anchor="end")
        parts.append(s)
        y += 50
    y += 14
    r, rw = t(MONO, ROLE, 14, rx, y, th["sub"], track=2.6, anchor="end")
    parts += [f'<rect x="{rx - rw - 64:.1f}" y="{y - 6}" width="44" height="2" fill="{th["indigo"]}"/>', r]
    u, uw = t(MONO_B, URL, 14, rx, y + 40, th["text"], track=0.6, anchor="end")
    parts += [u, f'<rect x="{rx - uw:.1f}" y="{y + 46}" width="{uw:.1f}" height="1.2" fill="{th["text"]}"/>']
    return mp.svg_doc(W, H, "Models propose. Rules gate. I decide. Senior Product Engineer, Berlin.", parts)


def main():
    if not os.path.exists(ms.CHROME):
        raise SystemExit(f"Chrome not found at {ms.CHROME}: set CHROME to the binary")
    out = os.path.join(ROOT, "assets", "linkedin", "banner.jpg")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    ms.rasterise(banner(), out, W, H)
    print("wrote", out, os.path.getsize(out), "bytes")


if __name__ == "__main__":
    main()
