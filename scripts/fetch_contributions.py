"""Descarga el calendario público de contribuciones de GitHub (sin token)
y lo guarda en data/contributions.json con estadísticas derivadas."""
import json
import os
import re
from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path

import requests
from bs4 import BeautifulSoup

USERNAME = os.environ.get("GH_USER", "Ezquerrito88")
URL = f"https://github.com/users/{USERNAME}/contributions"
ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "contributions.json"


def parse_count(text: str) -> int:
    text = (text or "").strip()
    if not text or text.lower().startswith("no "):
        return 0
    m = re.match(r"([\d,]+)", text)
    return int(m.group(1).replace(",", "")) if m else 0


def main() -> None:
    resp = requests.get(URL, headers={"User-Agent": "profile-readme-bot"}, timeout=30)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    # Los recuentos están en <tool-tip for="<id de la celda>">N contributions on ...</tool-tip>
    tips = {t.get("for"): t.get_text(" ", strip=True) for t in soup.find_all("tool-tip")}

    days = []
    for cell in soup.select("[data-date]"):
        d = cell.get("data-date")
        level = int(cell.get("data-level", 0) or 0)
        count = parse_count(tips.get(cell.get("id"), ""))
        if count == 0 and level > 0:
            count = level  # respaldo si GitHub cambia el formato del tooltip
        days.append({"date": d, "count": count, "level": level})

    if not days:
        raise SystemExit("No se encontraron días: ¿ha cambiado el HTML de GitHub?")

    days.sort(key=lambda x: x["date"])

    total = sum(x["count"] for x in days)
    h2 = soup.find("h2")
    if h2:
        m = re.search(r"([\d,]+)\s+contribution", h2.get_text(" ", strip=True))
        if m:
            total = int(m.group(1).replace(",", ""))

    # Rachas
    longest = cur = 0
    for x in days:
        cur = cur + 1 if x["count"] > 0 else 0
        longest = max(longest, cur)
    current = 0
    today = date.today().isoformat()
    for x in reversed(days):
        if x["date"] == today and x["count"] == 0:
            continue  # hoy todavía puede sumar
        if x["count"] > 0:
            current += 1
        else:
            break

    best = max(days, key=lambda x: x["count"])
    monthly = defaultdict(int)
    for x in days:
        monthly[x["date"][:7]] += x["count"]

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({
        "username": USERNAME,
        "total": total,
        "current_streak": current,
        "longest_streak": longest,
        "best_day": best,
        "monthly": dict(monthly),
        "days": days,
    }, indent=1))
    print(f"{len(days)} días, {total} contribuciones -> {OUT}")


if __name__ == "__main__":
    main()
