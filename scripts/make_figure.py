#!/usr/bin/env python3
"""Generate templates/figure.svg: a voxel image segmented by a readable spatial-logic specification.

Deterministic (fixed seed). Colours come from the page's CSS variables, so the figure follows the theme.
Run once after changing it; build.py inlines the result.
"""
import math
import pathlib
import random

ROOT = pathlib.Path(__file__).resolve().parent.parent
N, CELL, GAP = 16, 15, 2
STEP = CELL + GAP
OX, OY = 8, 14
CORE, CORE_R = (9.6, 6.4), 2.1
EDEMA_R = 3.7

rnd = random.Random(7)
cells = []
for y in range(N):
    for x in range(N):
        # brain-like mask: an ellipse with a soft, irregular border
        dx, dy = (x + .5 - N / 2) / 7.6, (y + .5 - N / 2) / 7.0
        r = math.hypot(dx, dy) + rnd.uniform(-.06, .06)
        if r > 1:
            continue
        d = math.hypot(x + .5 - CORE[0], y + .5 - CORE[1])
        if d <= CORE_R:
            kind = "core"
        elif d <= EDEMA_R + rnd.uniform(-.4, .4):
            kind = "edema"
        else:
            kind = "tissue"
        cells.append((x, y, kind, d, r))

out = []
for x, y, kind, d, r in cells:
    px, py = OX + x * STEP, OY + y * STEP
    if kind == "tissue":
        op = .10 + .16 * (1 - r) + rnd.uniform(0, .10)
        out.append(f'<rect x="{px}" y="{py}" width="{CELL}" height="{CELL}" rx="3" fill="var(--fg)" opacity="{op:.2f}"/>')
    else:
        cls = "c" if kind == "core" else "e"
        delay = .25 + d * .12
        out.append(f'<rect class="seg {cls}" style="animation-delay:{delay:.2f}s" x="{px}" y="{py}" '
                   f'width="{CELL}" height="{CELL}" rx="3"/>')

grid_w = N * STEP
fx = OX + grid_w + 34  # formula panel
code = [
    ("let", "core", "=", "bright & homogeneous"),
    ("let", "edema", "=", "hyperintense & near(core)"),
    ("let", "tumour", "=", "touch(edema, core)"),
]
lines = []
for i, (kw, name, eq, rhs) in enumerate(code):
    yy = OY + 62 + i * 30
    colour = {"core": "var(--accent)", "edema": "var(--accent2)", "tumour": "var(--fg)"}[name]
    lines.append(
        f'<text x="{fx + 18}" y="{yy}" class="code"><tspan fill="var(--muted)">{kw} </tspan>'
        f'<tspan fill="{colour}" font-weight="600">{name}</tspan><tspan fill="var(--muted)"> {eq} </tspan>'
        f'<tspan fill="var(--fg)">{rhs}</tspan></text>'
    )

# The box fits its longest line: 13px monospace is about 0.62em, so 8.1px a character, plus 18px padding each side.
longest = max(len(f"{kw} {name} {eq} {rhs}") for kw, name, eq, rhs in code)
BOX_W = math.ceil(36 + longest * 8.1)
W = fx + BOX_W + 10
H = OY + grid_w + 14
svg = f'''<svg class="figure" viewBox="0 0 {W} {H}" role="img" aria-labelledby="fig-title fig-desc" xmlns="http://www.w3.org/2000/svg">
<title id="fig-title">Spatial model checking</title>
<desc id="fig-desc">A grid of voxels from a brain scan. A short logical specification defines core and edema; the voxels that satisfy it are coloured.</desc>
<style>
.figure .seg {{ opacity: 0; animation: segin .5s ease-out forwards; }}
.figure .c {{ fill: var(--accent); }}
.figure .e {{ fill: var(--accent2); }}
.figure .code {{ font: 500 13px ui-monospace, "SF Mono", Menlo, Consolas, monospace; }}
.figure .lbl {{ font: 600 10.5px Inter, system-ui, sans-serif; letter-spacing: .12em; fill: var(--muted); }}
@keyframes segin {{ from {{ opacity: 0; transform: scale(.4); }} to {{ opacity: .92; transform: none; }} }}
.figure .seg {{ transform-box: fill-box; transform-origin: center; }}
@media (prefers-reduced-motion: reduce) {{ .figure .seg {{ animation: none; opacity: .92; }} }}
</style>
{chr(10).join(out)}
<rect x="{fx}" y="{OY + 30}" width="{BOX_W}" height="118" rx="10" fill="var(--soft)" stroke="var(--rule)"/>
{chr(10).join(lines)}
<path d="M {fx - 4} {OY + 89} C {fx - 22} {OY + 89}, {fx - 18} {OY + 105}, {OX + grid_w - 6} {OY + 105}" fill="none" stroke="var(--muted)" stroke-width="1.3" stroke-dasharray="3 4"/>
<g transform="translate({fx + 18} {OY + 168})" class="code" font-size="12">
  <rect width="11" height="11" rx="2.5" fill="var(--accent)"/><text x="18" y="10" fill="var(--fg)">core</text>
  <rect x="70" width="11" height="11" rx="2.5" fill="var(--accent2)"/><text x="88" y="10" fill="var(--fg)">edema</text>
</g>
</svg>
'''
(ROOT / "templates" / "figure.svg").write_text(svg, encoding="utf-8")
print(f"figure.svg written ({len(svg)} bytes, {len(cells)} voxels)")
