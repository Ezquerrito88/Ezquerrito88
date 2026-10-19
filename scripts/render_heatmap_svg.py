"""Convierte data/contributions.json en contrib-heatmap.svg:
calendario de 53 semanas que aparece en diagonal casilla a casilla.
STATIC=1 genera un fotograma fijo (útil para previsualizar)."""
import json
import os
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "contributions.json"
OUT = ROOT / "contrib-heatmap.svg"
STATIC = os.environ.get("STATIC") == "1"

PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#69f0a0"]
BG, BORDER, TEXT, MUTED, ACCENT = "#0d1117", "#30363d", "#e6edf3", "#7d8590", "#39d353"
FONT = "ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace"
MONTHS = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"]

W, H = 860, 214
CELL, GAP = 12, 3
STEP = CELL + GAP
LEFT, TOP = 47, 62


def level_for(count: int, maxc: int, gh_level: int) -> int:
    if count <= 0:
        return 0
    # Nivel 5 (neón) para los días excepcionales; el resto respeta el nivel de GitHub
    if maxc and count >= max(maxc * 0.85, 1) and gh_level >= 4:
        return 5
    return max(1, min(gh_level or 1, 4))


def fmt(n: int) -> str:
    return f"{n:,}".replace(",", ".")


def main() -> None:
    data = json.loads(DATA.read_text())
    days = data["days"]
    first = date.fromisoformat(days[0]["date"])
    start = first - timedelta(days=(first.weekday() + 1) % 7)  # domingo anterior
    maxc = max(d["count"] for d in days)

    cells, months, last_month = [], [], None
    for d in days:
        dt = date.fromisoformat(d["date"])
        col = (dt - start).days // 7
        row = (dt.weekday() + 1) % 7
        x, y = LEFT + col * STEP, TOP + row * STEP
        lvl = level_for(d["count"], maxc, d.get("level", 0))
        anim = "" if STATIC else f' style="animation-delay:{(col + row) * 0.018:.3f}s"'
        tip = f'{d["count"]} contribuciones el {d["date"]}'
        cells.append(
            f'<rect class="c" x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2.5" '
            f'fill="{PALETTE[lvl]}"{anim}><title>{tip}</title></rect>'
        )
        if row == 0 and dt.month != last_month and dt.day <= 7:
            if col < 52:
                months.append(f'<text x="{x}" y="{TOP - 9}" class="m">{MONTHS[dt.month - 1]}</text>')
            last_month = dt.month

    wd = "".join(
        f'<text x="{LEFT - 8}" y="{TOP + r * STEP + 10}" class="m" text-anchor="end">{t}</text>'
        for r, t in ((1, "lun"), (3, "mié"), (5, "vie"))
    )

    lx = W - 50 - 6 * STEP
    legend = (
        f'<text x="{lx - 8}" y="31" class="m" text-anchor="end">menos</text>'
        + "".join(
            f'<rect x="{lx + i * STEP}" y="21" width="{CELL}" height="{CELL}" rx="2.5" fill="{c}"/>'
            for i, c in enumerate(PALETTE)
        )
        + f'<text x="{lx + 6 * STEP + 2}" y="31" class="m">más</text>'
    )

    best = data["best_day"]
    footer_y = TOP + 7 * STEP + 30
    footer = (
        f'<text x="22" y="{footer_y}" class="s">'
        f'<tspan class="k">racha actual</tspan> {data["current_streak"]} días  '
        f'<tspan class="dim">·</tspan>  <tspan class="k">racha máx.</tspan> {data["longest_streak"]} días  '
        f'<tspan class="dim">·</tspan>  <tspan class="k">mejor día</tspan> {best["count"]} ({best["date"]})</text>'
    )

    css = f"""
    text{{font-family:{FONT};}}
    .t{{fill:{TEXT};font-size:15px;font-weight:700}}
    .t tspan.g{{fill:{ACCENT}}}
    .m{{fill:{MUTED};font-size:10px}}
    .s{{fill:{TEXT};font-size:12px}}
    .k{{fill:{ACCENT}}} .dim{{fill:{MUTED}}}
    """
    if not STATIC:
        css += """
    .c{opacity:0;transform-box:fill-box;transform-origin:center;
       animation:drop .45s cubic-bezier(.2,.8,.3,1) forwards}
    @keyframes drop{from{opacity:0;transform:translateY(-7px) scale(.6)}
                    to{opacity:1;transform:none}}
    .fade{opacity:0;animation:fade .6s ease-out 1.3s forwards}
    @keyframes fade{to{opacity:1}}
    """

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Mapa de contribuciones de {data['username']}">
<style>{css}</style>
<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="10" fill="{BG}" stroke="{BORDER}"/>
<text x="22" y="32" class="t"><tspan class="g">{fmt(data['total'])}</tspan> contribuciones en el último año</text>
{legend}
{''.join(months)}
{wd}
{''.join(cells)}
<g class="fade">{footer}</g>
</svg>
"""
    OUT.write_text(svg)
    print(f"-> {OUT}")


if __name__ == "__main__":
    main()
