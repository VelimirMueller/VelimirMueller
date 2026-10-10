#!/usr/bin/env python3
"""Make the link preview image of velimir-mueller.de (1200x630 JPEG).

Shown when the site is shared (LinkedIn, Slack, X). Same look as the profile:
art on the right (assets/art/og.jpg), name, role and stance on the left.
Copy the output to portfolio-website as src/app/opengraph-image.jpg.

Needs: python3 -m pip install fonttools brotli pillow, and Google Chrome.
Run:   python3 scripts/make-og.py
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
MONO, MONO_B, SANS, t, pill = mp.MONO, mp.MONO_B, mp.SANS, mp.t, mp.pill
th = mp.THEMES["dark"]

W, H = 1200, 630
NAME = "VELIMIR MÜLLER."
ROLE = "SENIOR PRODUCT ENGINEER"
SUB = "FULL-STACK · INFRASTRUCTURE · AI TOOLING"
STANCE = "Models propose. Rules gate. I decide."
TAG = "BERLIN · BUILDING WITH AI, NOT BY AI"
URL = "velimir-mueller.de"


def og():
    uid = "vm-og"
    jpg = os.path.join(ROOT, "assets", "art", "og.jpg")
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
    msz = 48
    parts.append(f'<g transform="translate({ix},{top - 6}) scale({msz / 512})">{mp.ml.mark("dark", 512, uid=f"{uid}-mark")}</g>')
    p, _ = pill(ix + msz + 16, top + 2, TAG, th, size=13)
    parts.append(p)

    size = 76
    y = top + 120 + size * 0.70
    n, _ = t(MONO_B, NAME, size, ix - size * 0.04, y, th["text"], track=-size * 0.04)
    parts.append(n)
    y += 56
    parts.append(f'<rect x="{ix}" y="{y - 7}" width="56" height="3" fill="{th["indigo"]}"/>')
    a, _ = t(MONO, ROLE, 22, ix + 76, y, th["sub"], track=4.0)
    b, _ = t(MONO, SUB, 13, ix + 76, y + 28, th["faint"], track=2.4)
    parts += [a, b]
    y += 100
    s, _ = t(MONO_B, STANCE, 30, ix, y, th["text"], track=-0.6)
    parts.append(s)

    u, uw = t(MONO_B, URL, 16, ix, H - 64, th["text"], track=0.6)
    parts += [u, f'<rect x="{ix}" y="{H - 57}" width="{uw:.1f}" height="1.4" fill="{th["text"]}"/>']
    return mp.svg_doc(W, H, "Velimir Müller. Senior Product Engineer. Models propose, rules gate, I decide.", parts)


def main():
    if not os.path.exists(ms.CHROME):
        raise SystemExit(f"Chrome not found at {ms.CHROME}: set CHROME to the binary")
    out = os.path.join(ROOT, "assets", "site", "opengraph-image.jpg")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    ms.rasterise(og(), out, W, H)
    print("wrote", out, os.path.getsize(out), "bytes")


if __name__ == "__main__":
    main()
