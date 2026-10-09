#!/usr/bin/env python3
"""Make the README's diagram panels (dark + light) in the D-41 look: what I do,
the Synthwerk map and the rig. They replace ASCII diagrams that were too busy.
Same rules as make-profile.py: text outlined to paths, no fonts, no <text>, no
external references, so GitHub's <img> sandbox renders them.
Needs: python3 -m pip install fonttools brotli
Run:   python3 scripts/make-panels.py [--version v1]
"""
import argparse
import importlib.util
import os

HERE = os.path.dirname(__file__)
ROOT = os.path.normpath(os.path.join(HERE, ".."))
_spec = importlib.util.spec_from_file_location("mp", os.path.join(HERE, "make-profile.py"))
mp = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(mp)
THEMES, MONO, MONO_B, SANS, t, pill, defs, page, card, svg_doc = (
    mp.THEMES, mp.MONO, mp.MONO_B, mp.SANS, mp.t, mp.pill, mp.defs, mp.page, mp.card, mp.svg_doc)

VIOLET = {"dark": "#8b5cf6", "light": "#7c3aed"}


def frame(uid, th, W, H):
    return [defs(uid, th, W, H), page(uid, th, W, H)]


def heading(x, y, index, title, th):
    """'01 / TITLE' in the card corner, like the flagship cards."""
    a, aw = t(MONO, index, 11, x, y, th["faint"], track=2.0)
    b, _ = t(MONO, " / " + title, 11, x + aw, y, th["faint"], track=2.0)
    return [a, b]


def node(x, y, w, h, title, sub, th, status=None, dashed=False):
    """A service box: rounded card, indigo accent tick, bold title, mono sub, optional status dot."""
    dash = ' stroke-dasharray="6 5"' if dashed else ""
    out = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="14" fill="{th["card"]}" '
           f'stroke="{th["card_line"]}" stroke-width="1.2"{dash}/>',
           f'<rect x="{x + 18}" y="{y + 16}" width="22" height="2" fill="{th["indigo"]}"/>']
    a, _ = t(MONO_B, title, 19, x + 18, y + 46, th["text"], track=0.4)
    b, _ = t(MONO, sub, 11.5, x + 18, y + 68, th["sub"], track=1.2)
    out += [a, b]
    if status:
        color = th["green"] if status == "ok" else th["indigo"]
        out.append(f'<circle cx="{x + w - 20}" cy="{y + 20}" r="5" fill="{color}"/>')
    return out


def arrow(x1, y1, x2, y2, th, color=None):
    c = color or th["indigo"]
    out = [f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{c}" stroke-width="2"/>']
    if y1 == y2:  # horizontal, head at x2
        s = 1 if x2 > x1 else -1
        out.append(f'<path d="M{x2} {y2} L{x2 - 9 * s} {y2 - 5} L{x2 - 9 * s} {y2 + 5} Z" fill="{c}"/>')
    else:  # vertical, head at y2
        s = 1 if y2 > y1 else -1
        out.append(f'<path d="M{x2} {y2} L{x2 - 5} {y2 - 9 * s} L{x2 + 5} {y2 - 9 * s} Z" fill="{c}"/>')
    return out


# ---------------------------------------------------------------- what I do
CAPS = [
    ("01", "PRODUCT ENGINEERING", ["Requirements to release:", "UX/UI, full-stack code,", "tests and rollout."],
     "NEXT.JS · LARAVEL · VUE · KOTLIN"),
    ("02", "AI TOOLING", ["Agent pipelines with gated", "reviews, MCP servers and", "local models."],
     "MCP · CLAUDE CODE · MLX"),
    ("03", "PLATFORM", ["Vercel, Supabase, AWS, Azure,", "Terraform, and CI that", "blocks bad merges."],
     "TERRAFORM · DOCKER · CI"),
]


def capabilities(theme):
    th = THEMES[theme]
    W, H, pad, gap = 1280, 300, 32, 20
    uid = f"vm-caps-{theme}"
    parts = frame(uid, th, W, H)
    cw = (W - 2 * pad - 2 * gap) / 3
    for i, (idx, title, lines, tags) in enumerate(CAPS):
        x = pad + i * (cw + gap)
        parts.append(card(x, pad, cw, H - 2 * pad, th))
        parts += heading(x + 28, pad + 34, idx, "WHAT I DO", th)
        parts.append(f'<rect x="{x + 28}" y="{pad + 58}" width="44" height="2" fill="{th["indigo"]}"/>')
        a, _ = t(MONO_B, title, 22, x + 28, pad + 92, th["text"], track=0.6)
        parts.append(a)
        for j, line in enumerate(lines):
            p, _ = t(SANS, line, 15.5, x + 28, pad + 126 + j * 22, th["sub"])
            parts.append(p)
        g, _ = t(MONO, tags, 10, x + 28, H - pad - 26, th["faint"], track=1.8)
        parts.append(g)
    return svg_doc(W, H, "What I do: product engineering, AI tooling, platform.", parts)


# ---------------------------------------------------------------- synthwerk map
TOP = [("STUDIO", "NUXT 4", "plan"), ("WIDGETS", "VUE CE", "plan"), ("SDK", "TOKENS", "ok")]
BOTTOM = [("IDENTITY", "GO · ZITADEL", "plan"), ("LLM", "GO · SSE", "plan"), ("VISION", "PYTHON · ONNX", "ok")]


def synthwerk_map(theme):
    th = THEMES[theme]
    W, H, pad = 1280, 520, 32
    uid = f"vm-map-{theme}"
    parts = frame(uid, th, W, H)
    parts.append(card(pad, pad, W - 2 * pad, H - 2 * pad, th, uid, grid=True))
    parts += heading(pad + 32, pad + 40, "MAP", "SYNTHWERK · ONE REPO PER ROLE", th)
    p, _ = pill(W - pad - 250, pad + 22, "SELF-HOSTED · MIT", th)
    parts.append(p)

    bw, bh, x0, gap = 240, 92, pad + 60, 48
    ty, by = pad + 90, pad + 300
    bus_y = ty + bh + 58
    xs = [x0 + i * (bw + gap) for i in range(4)]
    # the shared contract between clients and services
    parts.append(f'<rect x="{xs[0]}" y="{bus_y - 3}" width="{xs[2] + bw - xs[0]}" height="6" rx="3" '
                 f'fill="{th["indigo"]}" fill-opacity="0.85"/>')
    lbl, _ = t(MONO, "ONE API CONTRACT · SDK TYPES", 10.5, xs[0] + bw / 2 + 18, bus_y - 14, th["faint"], track=1.8)
    parts.append(lbl)
    for i, (name, sub, st) in enumerate(TOP):
        parts += node(xs[i], ty, bw, bh, name, sub, th, st)
        parts += arrow(xs[i] + bw / 2, ty + bh, xs[i] + bw / 2, bus_y - 4, th)
    for i, (name, sub, st) in enumerate(BOTTOM):
        parts += arrow(xs[i] + bw / 2, bus_y + 4, xs[i] + bw / 2, by, th)
        parts += node(xs[i], by, bw, bh, name, sub, th, st)
    # blueprint: shared by every repo, so it sits apart, dashed
    parts += node(xs[3], ty, bw, bh, "BLUEPRINT", "CI · LINT · TEMPLATES", th, "ok", dashed=True)
    s, _ = t(MONO, "SHARED BY ALL REPOS", 10.5, xs[3], ty + bh + 26, th["faint"], track=1.8)
    parts.append(s)
    # legend
    lx, ly = xs[3], by + 30
    for k, (label, color) in enumerate((("WORKING", th["green"]), ("REWRITE PLANNED", th["indigo"]))):
        parts.append(f'<circle cx="{lx + 6}" cy="{ly + k * 26 - 4}" r="5" fill="{color}"/>')
        a, _ = t(MONO, label, 11, lx + 20, ly + k * 26, th["sub"], track=1.6)
        parts.append(a)
    return svg_doc(W, H, "Synthwerk map: studio, widgets and SDK on one API contract over identity, LLM and vision; "
                         "blueprint shared by all repos.", parts)


# ---------------------------------------------------------------- the rig
STEPS = [("TICKET", "ME", "human"), ("SPEC", "MODEL + ME", "both"), ("IMPLEMENT", "MODELS", "model"),
         ("2 REVIEWS", "BOTH MUST APPROVE", "model"), ("SHIP", "ME", "human")]


def rig(theme):
    th = THEMES[theme]
    W, H, pad = 1280, 470, 32
    uid = f"vm-rig-{theme}"
    parts = frame(uid, th, W, H)
    parts.append(card(pad, pad, W - 2 * pad, H - 2 * pad, th, uid, grid=True))
    parts += heading(pad + 32, pad + 40, "RIG", "HOW A CHANGE SHIPS", th)
    p, _ = pill(W - pad - 236, pad + 22, "HUMAN IN THE LOOP", th)
    parts.append(p)

    n, bw, bh, gap = len(STEPS), 196, 104, 36
    x0 = (W - (n * bw + (n - 1) * gap)) / 2
    y = pad + 92
    for i, (name, who, kind) in enumerate(STEPS):
        x = x0 + i * (bw + gap)
        parts += node(x, y, bw, bh, name, who, th)
        tag_color = {"human": th["green"], "model": th["indigo"], "both": VIOLET[theme]}[kind]
        tag = {"human": "HUMAN", "model": "MODEL", "both": "MODEL + HUMAN"}[kind]
        tg, _ = t(MONO, tag, 9.5, x + 18, y + bh - 14, tag_color, track=1.6)
        parts.append(tg)
        if i < n - 1:
            parts += arrow(x + bw + 4, y + bh / 2, x + bw + gap - 4, y + bh / 2, th)
    # reviews -> memory
    rx = x0 + 3 * (bw + gap) + bw / 2
    my = y + bh + 70
    parts += arrow(rx, y + bh + 2, rx, my - 2, th, VIOLET[theme])
    mw = 236
    parts += node(rx - mw / 2, my, mw, 92, "MEMORY", "LESSONS · PITFALLS", th, "ok")
    for k, line in enumerate(("A model can flag a risk. It cannot clear one.",
                              "A missing reviewer means BLOCKED, not skipped.",
                              "When a model and a rule disagree, the rule wins.")):
        a, _ = t(SANS, line, 16, x0, my + 28 + k * 28, th["sub"])
        parts.append(a)
    return svg_doc(W, H, "The rig: ticket by me, spec by model and me, implement by models, two reviews that both "
                         "must approve, ship by me; reviews feed a memory of lessons.", parts)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--version", default="v1")
    opt = ap.parse_args()
    for theme in ("dark", "light"):
        for key, fn in (("capabilities", capabilities), ("synthwerk-map", synthwerk_map), ("rig", rig)):
            out = os.path.join(ROOT, "assets", "panels", f"{key}-{opt.version}-{theme}.svg")
            os.makedirs(os.path.dirname(out), exist_ok=True)
            with open(out, "w") as fh:
                fh.write(fn(theme))
            print("wrote", out, os.path.getsize(out), "bytes")


if __name__ == "__main__":
    main()
