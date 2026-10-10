#!/usr/bin/env python3
"""Make the README's section dividers (dark + light): a wide art strip with the
section index and title. They replace the plain ASCII rules between sections.
One file per section serves both themes: the strip is dark art with its own
border, so a light variant would only duplicate the embedded image.
Same rules as make-profile.py: text outlined to paths, no fonts, no <text>, no
external references. The art (assets/art/strip-<key>.jpg) is embedded as a data
URI.

Needs: python3 -m pip install fonttools brotli
Run:   python3 scripts/make-dividers.py [--version v1] [--motion]
--motion adds a slow light sweep (SMIL, hidden for prefers-reduced-motion).
"""
import argparse
import base64
import importlib.util
import os

HERE = os.path.dirname(__file__)
ROOT = os.path.normpath(os.path.join(HERE, ".."))
_spec = importlib.util.spec_from_file_location("mp", os.path.join(HERE, "make-profile.py"))
mp = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(mp)
THEMES, MONO, MONO_B, t = mp.THEMES, mp.MONO, mp.MONO_B, mp.t

# key, index, title, caption. Order = order in the README.
SECTIONS = [
    ("profile", "00", "PROFILE", "WHO BUILDS THIS"),
    ("flagships", "01", "FLAGSHIPS", "WHAT I SHIP IN PUBLIC"),
    ("rig", "02", "THE RIG", "HOW THE WORK GETS DONE"),
    ("work", "03", "WORK", "GALVANY · ENERGY · BERLIN"),
    ("built", "04", "ALSO BUILT", "SIDE PROJECTS AND EXPERIMENTS"),
]
INK = THEMES["dark"]  # the strip is dark art in both themes


# Light sweep: one pass of SWEEP_S seconds, then a pause, every LOOP_S seconds.
SWEEP_S, LOOP_S, SWEEP_A = 1.8, 9, 0.12


def sweep(uid, W, H):
    """A soft diagonal band of light that crosses the strip once per loop.
    SMIL moves it (the animation kind GitHub README SVGs use); CSS hides it
    for prefers-reduced-motion."""
    k = SWEEP_S / LOOP_S
    return [f'<style>@media (prefers-reduced-motion: reduce) {{ .{uid}-sw {{ display: none }} }}</style>',
            f'<linearGradient id="{uid}-band" x1="0" x2="1" y1="0" y2="0"><stop offset="0" stop-color="#ffffff" stop-opacity="0"/>'
            f'<stop offset="0.5" stop-color="#c7d2fe" stop-opacity="{SWEEP_A}"/><stop offset="1" stop-color="#ffffff" stop-opacity="0"/></linearGradient>',
            f'<g class="{uid}-sw"><g>'
            f'<animateTransform attributeName="transform" type="translate" values="-420 0;{W + 220} 0;{W + 220} 0" '
            f'keyTimes="0;{k:.3f};1" calcMode="spline" keySplines=".45 0 .25 1;0 0 1 1" dur="{LOOP_S}s" repeatCount="indefinite"/>'
            f'<rect x="0" y="-40" width="260" height="{H + 80}" fill="url(#{uid}-band)" transform="skewX(-22)"/></g></g>']


def strip(key, index, title, caption, motion=False):
    W, H, r = 1280, 200, 24
    uid = f"vm-div-{key}"
    jpg = os.path.join(ROOT, "assets", "art", f"strip-{key}.jpg")
    if not os.path.exists(jpg):
        raise SystemExit(f"missing art: {jpg} (see assets/art/PROMPTS.md)")
    with open(jpg, "rb") as fh:
        data = base64.b64encode(fh.read()).decode()
    parts = [f"""<defs>
<clipPath id="{uid}-clip"><rect width="{W}" height="{H}" rx="{r}"/></clipPath>
<linearGradient id="{uid}-shade" x1="0" x2="1" y1="0" y2="0">
<stop offset="0" stop-color="#0a0a0a" stop-opacity="0.94"/><stop offset="0.38" stop-color="#0a0a0a" stop-opacity="0.72"/>
<stop offset="0.7" stop-color="#0a0a0a" stop-opacity="0.12"/><stop offset="1" stop-color="#0a0a0a" stop-opacity="0.30"/></linearGradient>
<pattern id="{uid}-grid" width="32" height="32" patternUnits="userSpaceOnUse"><path d="M32 0H0V32" fill="none" stroke="#ffffff" stroke-opacity="0.05" stroke-width="1"/></pattern>
<pattern id="{uid}-scan" width="4" height="4" patternUnits="userSpaceOnUse"><rect width="4" height="1" fill="#000000" fill-opacity="0.22"/></pattern>
</defs>""",
             f'<g clip-path="url(#{uid}-clip)">',
             f'<rect width="{W}" height="{H}" fill="#08080a"/>',
             f'<image width="{W}" height="{H}" preserveAspectRatio="xMidYMid slice" href="data:image/jpeg;base64,{data}"/>',
             f'<rect width="{W}" height="{H}" fill="url(#{uid}-scan)"/>',
             f'<rect width="{W}" height="{H}" fill="url(#{uid}-shade)"/>',
             f'<rect width="{W * 0.5:.0f}" height="{H}" fill="url(#{uid}-grid)"/>',
             f'<rect y="{H - 3}" width="{W}" height="3" fill="{INK["indigo"]}" fill-opacity="0.85"/>',
             *(sweep(uid, W, H) if motion else []),
             "</g>",
             f'<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="{r - 0.5}" fill="none" stroke="{INK["card_line"]}"/>']

    ix, base = 40, 118
    n, nw = t(MONO_B, index, 64, ix, base, INK["indigo"], track=-2.5)
    s, sw = t(MONO, "/", 40, ix + nw + 14, base - 4, INK["faint"])
    w, _ = t(MONO_B, title, 48, ix + nw + 14 + sw + 14, base - 4, INK["text"], track=-1.2)
    parts += [n, s, w]
    parts.append(f'<rect x="{ix}" y="{base + 26}" width="44" height="2" fill="{INK["indigo"]}"/>')
    c, _ = t(MONO, caption, 12, ix + 62, base + 32, INK["sub"], track=2.6)
    parts.append(c)
    # Corner tag on a dark plate, so it stays readable on bright art.
    e, ew = t(MONO, f"SECTION {index} / {SECTIONS[-1][1]}", 10.5, W - 40, 40, INK["sub"], track=2.2, anchor="end")
    parts.append(f'<rect x="{W - 40 - ew - 12:.1f}" y="24" width="{ew + 24:.1f}" height="24" rx="12" '
                 f'fill="#0a0a0a" fill-opacity="0.78" stroke="{INK["card_line"]}"/>')
    parts.append(e)
    svg = mp.svg_doc(W, H, f"{index} {title.title()}. {caption.capitalize()}.", parts)
    return svg.replace("scripts/make-profile.py", "scripts/make-dividers.py", 1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--version", default="v1", help="file name suffix. Use a new one for each change.")
    ap.add_argument("--motion", action="store_true", help="add the light sweep")
    opt = ap.parse_args()
    for key, index, title, caption in SECTIONS:
        fn = os.path.join(ROOT, "assets", "dividers", f"{key}-{opt.version}.svg")
        os.makedirs(os.path.dirname(fn), exist_ok=True)
        with open(fn, "w") as fh:
            fh.write(strip(key, index, title, caption, opt.motion))
        print("wrote", fn, os.path.getsize(fn), "bytes")


if __name__ == "__main__":
    main()
