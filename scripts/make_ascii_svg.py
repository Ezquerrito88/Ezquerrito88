"""Convierte source-prepped.png en ascii-portrait.svg: retrato ASCII
monocromo que se "teclea" fila a fila (SMIL, se reproduce una vez y se queda fijo).
STATIC=1 genera un fotograma fijo."""
import os
from pathlib import Path
from xml.sax.saxutils import escape

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "source-prepped.png"
OUT = ROOT / "ascii-portrait.svg"
STATIC = os.environ.get("STATIC") == "1"

RAMP = " .`:-=+*cs#%@"  # claro (disperso) -> oscuro (denso); el espacio limpia el fondo
COLS = 110
W = 370
PAD = 14
BG, BORDER, FG, CURSOR = "#0d1117", "#30363d", "#c9d1d9", "#39d353"
FONT = "ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace"
GAMMA = 0.9  # <1 aclara medios tonos, >1 los oscurece


def main() -> None:
    img = Image.open(SRC).convert("LA")
    char_w = (W - 2 * PAD) / COLS
    line_h = char_w * 1.75          # ~proporción de una celda monoespaciada
    rows = round(COLS * img.height / img.width * char_w / line_h)
    small = np.asarray(img.resize((COLS, rows), Image.LANCZOS), dtype=np.float32) / 255.0
    a, mask = small[..., 0], small[..., 1] > 0.5

    # Estira el rango de brillo del sujeto
    subj = a[mask]
    if subj.size:
        lo, hi = np.percentile(subj, 2), np.percentile(subj, 99)
        a = ((a - lo) / max(hi - lo, 1e-3)).clip(0, 1)
    a = a ** GAMMA

    # Texto claro sobre fondo oscuro: zonas claras -> caracteres densos.
    # El sujeto nunca baja de "." para que el pelo oscuro siga marcando el contorno.
    idx = (1 + a * (len(RAMP) - 2)).round().astype(int)
    idx[~mask] = 0
    lines = ["".join(RAMP[i] for i in row).rstrip() for row in idx]

    H = round(rows * line_h + 2 * PAD)
    font_size = char_w / 0.6
    text_w = W - 2 * PAD
    parts, defs = [], []
    for r, line in enumerate(lines):
        if not line.strip():
            continue
        y = PAD + (r + 0.8) * line_h
        tl = f' textLength="{len(line) * char_w:.2f}" lengthAdjust="spacingAndGlyphs"'
        text = f'<text x="{PAD}" y="{y:.2f}"{tl}>{escape(line)}</text>'
        if STATIC:
            parts.append(text)
            continue
        begin, dur = 0.3 + r * 0.045, 0.28
        cy = PAD + r * line_h
        defs.append(
            f'<clipPath id="r{r}"><rect x="{PAD}" y="{cy:.2f}" width="0" height="{line_h + 1:.2f}">'
            f'<animate attributeName="width" from="0" to="{text_w}" begin="{begin:.3f}s" dur="{dur}s" fill="freeze"/>'
            f'</rect></clipPath>'
        )
        parts.append(
            f'<g clip-path="url(#r{r})">{text}</g>'
            f'<rect x="{PAD}" y="{cy + 1:.2f}" width="{char_w * 1.4:.2f}" height="{line_h - 1:.2f}" fill="{CURSOR}" opacity="0">'
            f'<set attributeName="opacity" to="1" begin="{begin:.3f}s"/>'
            f'<animate attributeName="x" from="{PAD}" to="{PAD + text_w}" begin="{begin:.3f}s" dur="{dur}s" fill="freeze"/>'
            f'<set attributeName="opacity" to="0" begin="{begin + dur:.3f}s"/></rect>'
        )

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Retrato ASCII">
<style>text{{font-family:{FONT};font-size:{font_size:.2f}px;fill:{FG};white-space:pre}}</style>
<defs>{''.join(defs)}</defs>
<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="10" fill="{BG}" stroke="{BORDER}"/>
<g xml:space="preserve">{''.join(parts)}</g>
</svg>
"""
    OUT.write_text(svg)
    print(f"-> {OUT} ({W}x{H}, {COLS}x{rows} caracteres)")


if __name__ == "__main__":
    main()
