#!/usr/bin/env python3
"""Make the synthwerk banner (dark + light) and the social-preview SVG.

Look: velimir-mueller.de + code-context dashboard family (decision D-41).
All text is outlined to paths from Space Mono and Inter (SIL OFL 1.1, see assets/fonts/).
The SVGs contain no <text>, no fonts and no external references, so they render
inside GitHub's <img> sandbox.

Needs: python3 -m pip install fonttools brotli

Overview repo (default):
  python3 scripts/make-banner.py
Per-repo variant (run in any synthwerk-* repo that has a copy of this script and the fonts):
  python3 scripts/make-banner.py --repo vision --status "WORKING" \
      --tagline "Image labels with an open vocabulary." --snippet "$ docker compose up vision"
"""
import argparse
import os
from xml.sax.saxutils import escape, quoteattr
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen

ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
FONTS = os.path.join(ROOT, "assets", "fonts")

# Tokens. Keep in sync with docs/presence-style.md.
THEMES = {
    "dark": dict(
        page="#0a0a0a", page_line="#1f1f23", card="#111111", card_line="#26262b",
        text="#fafafa", sub="#a1a1aa", faint="#71717a", grid="#ffffff", grid_a=0.045,
        green="#10b981", green_bg=0.10, green_line=0.40, indigo="#6366f1",
        snip_bg="#fafafa", snip_text="#18181b", snip_dim="#71717a",
        glow=[("#14b8a6", 0.22), ("#ef4444", 0.14), ("#8b5cf6", 0.22)],
    ),
    "light": dict(
        page="#fafafa", page_line="#e4e4e7", card="#ffffff", card_line="#e4e4e7",
        text="#18181b", sub="#52525b", faint="#71717a", grid="#18181b", grid_a=0.05,
        green="#059669", green_bg=0.08, green_line=0.35, indigo="#4f46e5",
        snip_bg="#18181b", snip_text="#fafafa", snip_dim="#a1a1aa",
        glow=[("#14b8a6", 0.14), ("#ef4444", 0.08), ("#8b5cf6", 0.14)],
    ),
}


class Face:
    def __init__(self, name):
        self.font = TTFont(os.path.join(FONTS, name))
        self.gs = self.font.getGlyphSet()
        self.cmap = self.font.getBestCmap()
        self.upem = self.font["head"].unitsPerEm
        self.hmtx = self.font["hmtx"]
        self.cap = self.font["OS/2"].sCapHeight / self.upem

    def width(self, text, size, track=0.0):
        s = size / self.upem
        w = 0.0
        for ch in text:
            g = self.cmap.get(ord(ch))
            if g is None:
                raise SystemExit(f"glyph missing for {ch!r}")
            w += self.hmtx[g][0] * s + track
        return w - track if text else 0.0

    def path(self, text, size, x, y, track=0.0):
        """Outline text with the baseline at y. Returns (svg path d, width)."""
        s = size / self.upem
        pen = SVGPathPen(self.gs, ntos=lambda v: f"{v:.1f}".rstrip("0").rstrip("."))
        cx = x
        for ch in text:
            g = self.cmap.get(ord(ch))
            if g is None:
                raise SystemExit(f"glyph missing for {ch!r}")
            self.gs[g].draw(TransformPen(pen, (s, 0, 0, -s, cx, y)))
            cx += self.hmtx[g][0] * s + track
        return pen.getCommands(), cx - x - track


MONO = Face("space-mono-latin-400-normal.woff2")
MONO_B = Face("space-mono-latin-700-normal.woff2")
SANS = Face("inter-latin-400-normal.woff2")
SANS_B = Face("inter-latin-600-normal.woff2")


def t(face, text, size, x, y, fill, track=0.0, anchor="start", opacity=None):
    w = face.width(text, size, track)
    if anchor == "middle":
        x -= w / 2
    elif anchor == "end":
        x -= w
    d, _ = face.path(text, size, x, y, track)
    op = f' fill-opacity="{opacity}"' if opacity is not None else ""
    return f'<path fill="{fill}"{op} d="{d}"/>', w


def pill(x, y, label, th, size=11.5, center=False):
    """Green status pill like '● VERFUEGBAR FUER PROJEKTE'. y is the top edge."""
    track = size * 0.12
    tw = MONO.width(label, size, track)
    h = size * 2.3
    w = tw + h * 0.62 + size * 1.9
    if center:
        x -= w / 2
    r = h / 2
    dot_x = x + h * 0.55
    out = [
        f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{r:.1f}" '
        f'fill="{th["green"]}" fill-opacity="{th["green_bg"]}" stroke="{th["green"]}" '
        f'stroke-opacity="{th["green_line"]}" stroke-width="1"/>',
        f'<circle cx="{dot_x:.1f}" cy="{y + r:.1f}" r="{size * 0.26:.1f}" fill="{th["green"]}"/>',
    ]
    p, _ = t(MONO, label, size, dot_x + size * 0.9, y + r + size * 0.35, th["green"], track)
    out.append(p)
    return "\n".join(out), w


def defs(uid, th, W, H, r=32):
    g = th["glow"]
    glows = "".join(
        f'<radialGradient id="{uid}-g{i}"><stop offset="0" stop-color="{c}" stop-opacity="{a}"/>'
        f'<stop offset="1" stop-color="{c}" stop-opacity="0"/></radialGradient>'
        for i, (c, a) in enumerate(g)
    )
    return f"""<defs>
{glows}
<pattern id="{uid}-grid" width="32" height="32" patternUnits="userSpaceOnUse"><path d="M32 0H0V32" fill="none" stroke="{th['grid']}" stroke-opacity="{th['grid_a']}" stroke-width="1"/></pattern>
<radialGradient id="{uid}-fade" cx="0.5" cy="0.35" r="0.75"><stop offset="0" stop-color="#fff" stop-opacity="1"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></radialGradient>
<mask id="{uid}-m"><rect width="{W}" height="{H}" fill="url(#{uid}-fade)"/></mask>
<clipPath id="{uid}-clip"><rect width="{W}" height="{H}" rx="{r}"/></clipPath>
</defs>"""


def page(uid, th, W, H, r=32):
    return f"""<g clip-path="url(#{uid}-clip)">
<rect width="{W}" height="{H}" fill="{th['page']}"/>
<rect width="{W}" height="{H}" fill="url(#{uid}-grid)" mask="url(#{uid}-m)"/>
<ellipse cx="{W * 0.16:.0f}" cy="0" rx="{W * 0.32:.0f}" ry="{H * 0.55:.0f}" fill="url(#{uid}-g0)"/>
<ellipse cx="{W * 0.52:.0f}" cy="0" rx="{W * 0.26:.0f}" ry="{H * 0.40:.0f}" fill="url(#{uid}-g1)"/>
<ellipse cx="{W * 0.90:.0f}" cy="{H * 0.05:.0f}" rx="{W * 0.30:.0f}" ry="{H * 0.60:.0f}" fill="url(#{uid}-g2)"/>
<ellipse cx="{W * 0.70:.0f}" cy="{H:.0f}" rx="{W * 0.30:.0f}" ry="{H * 0.35:.0f}" fill="url(#{uid}-g0)" opacity="0.6"/>
</g>
<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="{max(r - 0.5, 0)}" fill="none" stroke="{th['page_line']}"/>"""


def card(x, y, w, h, th, uid=None, grid=False):
    out = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="24" fill="{th["card"]}" fill-opacity="0.92" '
           f'stroke="{th["card_line"]}" stroke-width="1"/>']
    if grid:
        out.append(f'<rect x="{x + 16}" y="{y + 16}" width="{w - 32}" height="{h - 32}" rx="12" '
                   f'fill="url(#{uid}-grid)" opacity="0.9"/>')
    return "\n".join(out)


def build(theme, opt, W, H, social=False):
    th = THEMES[theme]
    uid = f"sw-{'s' if social else 'b'}-{theme}"
    pad = 32 if not social else 48
    gap = 20
    rw = 400 if not social else 404
    lx, ly, lh = pad, pad, H - 2 * pad
    lw = W - 2 * pad - gap - rw
    rx = lx + lw + gap
    r = 0 if social else 32
    parts = [defs(uid, th, W, H, r), page(uid, th, W, H, r), card(lx, ly, lw, lh, th), card(rx, ly, rw, lh, th, uid, grid=True)]

    # ---- left card ------------------------------------------------------
    ix = lx + 36
    wm_size = 112 if len(opt.word) <= 10 else max(64, int(112 * 10 / len(opt.word)))
    wm_size = min(wm_size, int((lw - 72) / (len(opt.word) * 0.612 - 0.04 * len(opt.word))))
    block_h = 30 + 28 + wm_size * 0.70 + 34 + 46 + (58 if opt.tagline2 else 36) + (56 if social else 0)
    top = ly + (lh - block_h) / 2 + 2
    p, _ = pill(ix, top, opt.status, th)
    parts.append(p)
    y = top + 30 + 28
    if opt.eyebrow:
        e, _ = t(MONO, opt.eyebrow, 14, ix + 2, y - 6, th["faint"], track=2.0)
        parts.append(e)
        y += 10
    y += wm_size * 0.70
    w, _ = t(MONO_B, opt.word, wm_size, ix - wm_size * 0.04, y, th["text"], track=-wm_size * 0.04)
    parts.append(w)
    y += 34
    parts.append(f'<rect x="{ix}" y="{y - 6:.1f}" width="44" height="2" fill="{th["indigo"]}"/>')
    a, _ = t(MONO, opt.label, 17, ix + 62, y, th["sub"], track=3.2)
    parts.append(a)
    b, _ = t(MONO, opt.sublabel, 11, ix + 62, y + 22, th["faint"], track=2.2)
    parts.append(b)
    y += 46 + 16
    parts.append(f'<rect x="{ix}" y="{y - 18:.1f}" width="2" height="{(48 if opt.tagline2 else 26)}" fill="{th["card_line"]}"/>')
    tg, _ = t(SANS, opt.tagline, 17, ix + 18, y, th["sub"])
    parts.append(tg)
    if opt.tagline2:
        tg2, _ = t(SANS, opt.tagline2, 17, ix + 18, y + 23, th["sub"])
        parts.append(tg2)
    if social:
        cy = y + (23 if opt.tagline2 else 0) + 44
        cx = ix
        for chip in opt.chips:
            cw = MONO.width(chip, 12, 1.0) + 28
            parts.append(f'<rect x="{cx:.1f}" y="{cy:.1f}" width="{cw:.1f}" height="28" rx="14" fill="none" '
                         f'stroke="{th["card_line"]}" stroke-width="1.2"/>')
            c, _ = t(MONO, chip, 12, cx + 14, cy + 18.5, th["sub"], track=1.0)
            parts.append(c)
            cx += cw + 8

    # ---- right card -----------------------------------------------------
    mx = rx + rw / 2
    rblock = 28 + 26 + 36 + 36 + 30 + 46 + 34 + 16
    ry = ly + (lh - rblock) / 2
    p, _ = pill(mx, ry, opt.badge, th, size=10.5, center=True)
    parts.append(p)
    yy = ry + 26 + 54
    for line in opt.title:
        s, _ = t(MONO_B, line, 28, mx, yy, th["text"], track=-0.6, anchor="middle")
        parts.append(s)
        yy += 36
    yy += 12
    sw = rw - 64
    parts.append(f'<rect x="{rx + 32}" y="{yy:.1f}" width="{sw}" height="46" rx="10" fill="{th["snip_bg"]}"/>')
    dollar, dw = t(MONO, "$", 12.5, rx + 48, yy + 27.5, th["snip_dim"])
    parts.append(dollar)
    cmd = opt.snippet.lstrip("$ ").strip()
    size = 12.5
    while MONO.width(cmd, size) > sw - 48 and size > 9:
        size -= 0.25
    if MONO.width(cmd, size) > sw - 48:
        raise SystemExit(f"--snippet is too long for the card: {cmd!r}")
    s, _ = t(MONO, cmd, size, rx + 48 + dw + 9, yy + 27.5, th["snip_text"])
    parts.append(s)
    yy += 46 + 34
    f, fw = t(MONO_B, opt.foot, 12, mx, yy, th["text"], track=0.6, anchor="middle")
    parts.append(f)
    parts.append(f'<rect x="{mx - fw / 2:.1f}" y="{yy + 6:.1f}" width="{fw:.1f}" height="1.2" fill="{th["text"]}"/>')

    label = f"{opt.word} {opt.label.lower()}. {opt.status.lower()}."
    head = ("<!-- synthwerk presence v2 (D-41). Text outlined from Space Mono and Inter "
            "(SIL OFL 1.1). No live text, no fonts, no external references. "
            "Generated by scripts/make-banner.py. Do not edit by hand. -->")
    svg = (f'{head}\n<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
           f'role="img" aria-label={quoteattr(label)}><title>{escape(label)}</title>\n' + "\n".join(parts) + "\n</svg>\n")
    return svg


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default="", help="role name, e.g. vision. Empty = overview repo.")
    ap.add_argument("--status", default="IN DEVELOPMENT · M0")
    ap.add_argument("--label", default="MODULAR AI SERVICES")
    ap.add_argument("--sublabel", default="CHAT · VISION · PAGE BUILDER · SELF-HOSTED")
    ap.add_argument("--tagline", default="Small services for AI chat, image recognition and page building.")
    ap.add_argument("--tagline2", default="You run all of it yourself.")
    ap.add_argument("--badge", default="OPEN SOURCE · MIT")
    ap.add_argument("--title", default="One map.|Run it yourself.", help="right card title, | separates lines")
    ap.add_argument("--snippet", default="$ gh repo clone VelimirMueller/synthwerk")
    ap.add_argument("--foot", default="github.com/VelimirMueller")
    ap.add_argument("--chips", default="edge identity llm vision pulse widgets studio sdk")
    ap.add_argument("--version", default="v2", help="file name suffix. Use a new one for each change.")
    ap.add_argument("--out", default=os.path.join(ROOT, "assets"))
    opt = ap.parse_args()
    opt.word = (opt.repo.upper() if opt.repo else "SYNTHWERK") + "."
    opt.eyebrow = "SYNTHWERK /" if opt.repo else ""
    opt.title = opt.title.split("|")
    opt.chips = opt.chips.split()

    os.makedirs(os.path.join(opt.out, "banner"), exist_ok=True)
    os.makedirs(os.path.join(opt.out, "social"), exist_ok=True)
    for theme in ("dark", "light"):
        fn = os.path.join(opt.out, "banner", f"banner-{opt.version}-{theme}.svg")
        with open(fn, "w") as fh:
            fh.write(build(theme, opt, 1280, 400))
        print("wrote", fn, os.path.getsize(fn), "bytes")
    fn = os.path.join(opt.out, "social", f"social-preview-{opt.version}.svg")
    with open(fn, "w") as fh:
        fh.write(build("dark", opt, 1280, 640, social=True))
    print("wrote", fn, os.path.getsize(fn), "bytes")


if __name__ == "__main__":
    main()
