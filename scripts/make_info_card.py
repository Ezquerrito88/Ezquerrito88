"""Genera info-card.svg: panel estilo `neofetch` cuyas líneas aparecen una a una.
Edita INFO para cambiar el contenido. STATIC=1 genera un fotograma fijo."""
import os
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "info-card.svg"
STATIC = os.environ.get("STATIC") == "1"

USER, HOST = "adrian", "ezquerrito88"
INFO = [
    ("OS", "Logroño, La Rioja · ES"),
    ("Rol", "Full-Stack Developer"),
    ("Ahora", "Construyendo AgroConecta"),
    ("Lenguajes", "Java · PHP · TypeScript · JS · SQL"),
    ("Frameworks", "Laravel · Angular · Spring Boot"),
    ("DevOps", "Docker · Azure · Git"),
    ("Foco", "Arquitectura · Cloud · APIs"),
    None,
    ("Proyecto", "AgroConecta: marketplace agrícola"),
    ("", "pagos · panel admin · chat en vivo"),
    ("", "deploy con Docker en Azure"),
    ("Otros", "wine-connect-microservices"),
    None,
    ("LinkedIn", "in/adrianezquerro"),
    ("Lema", "Build fast, build clean, build real"),
]

W = 490
BG, BAR, BORDER = "#0d1117", "#161b22", "#30363d"
TEXT, MUTED, GREEN, BLUE, YELLOW = "#e6edf3", "#7d8590", "#39d353", "#58a6ff", "#e3b341"
FONT = "ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace"
LH, X0, XV = 22, 24, 132
BLOCKS = ["#f85149", "#e3b341", "#39d353", "#58a6ff", "#bc8cff", "#39c5cf", "#e6edf3"]


def main() -> None:
    lines, y, i = [], 72, 0

    def line(content: str) -> None:
        nonlocal i
        delay = "" if STATIC else f' style="animation-delay:{0.25 + i * 0.09:.2f}s"'
        lines.append(f'<g class="l"{delay}>{content}</g>')
        i += 1

    line(f'<text x="{X0}" y="{y}" class="b"><tspan fill="{GREEN}">{USER}</tspan>'
         f'<tspan fill="{TEXT}">@</tspan><tspan fill="{BLUE}">{HOST}</tspan></text>')
    y += LH
    line(f'<text x="{X0}" y="{y}" fill="{MUTED}">{"─" * (len(USER) + len(HOST) + 1)}</text>')
    y += LH
    for item in INFO:
        if item is None:
            y += LH // 2
            continue
        k, v = item
        key = f'<text x="{X0}" y="{y}" class="b" fill="{YELLOW}">{escape(k)}</text>' if k else ""
        line(key + f'<text x="{XV}" y="{y}" fill="{TEXT}">{escape(v)}</text>')
        y += LH

    y += 6
    blocks = "".join(
        f'<rect x="{X0 + n * 30}" y="{y - 12}" width="26" height="14" rx="2" fill="{c}"/>'
        for n, c in enumerate(BLOCKS)
    )
    line(blocks)
    y += LH + 8
    cursor_cls = "" if STATIC else ' class="cur"'
    line(f'<text x="{X0}" y="{y}" fill="{GREEN}" class="b">$</text>'
         f'<rect{cursor_cls} x="{X0 + 16}" y="{y - 12}" width="8" height="15" fill="{TEXT}"/>')
    H = y + 22

    css = f"text{{font-family:{FONT};font-size:13px}} .b{{font-weight:700}}"
    if not STATIC:
        css += """
  .l{opacity:0;animation:in .4s ease-out forwards}
  @keyframes in{from{opacity:0;transform:translateX(-8px)}to{opacity:1;transform:none}}
  .cur{animation:blink 1.1s steps(1) infinite}
  @keyframes blink{50%{opacity:0}}"""

    dots = "".join(
        f'<circle cx="{20 + n * 18}" cy="17" r="5.5" fill="{c}"/>'
        for n, c in enumerate(["#f85149", "#e3b341", "#39d353"])
    )
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Info de {USER}">
<style>{css}</style>
<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="10" fill="{BG}" stroke="{BORDER}"/>
<path d="M0.5 34 V10.5 a10 10 0 0 1 10 -10 H{W - 10.5} a10 10 0 0 1 10 10 V34 Z" fill="{BAR}"/>
<line x1="0.5" y1="34" x2="{W - 0.5}" y2="34" stroke="{BORDER}"/>
{dots}
<text x="{W / 2}" y="21" text-anchor="middle" fill="{MUTED}" font-size="12">{USER}@{HOST}: ~ — neofetch</text>
{''.join(lines)}
</svg>
"""
    OUT.write_text(svg)
    print(f"-> {OUT} ({W}x{H})")


if __name__ == "__main__":
    main()
