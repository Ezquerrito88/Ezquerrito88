"""Prepara una foto para el retrato ASCII:
1) quita el fondo (rembg), 2) sube el contraste local (CLAHE),
3) la pone sobre blanco y la recorta al sujeto. Salida: source-prepped.png

Uso: python scripts/prep_photo.py foto.jpg"""
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image
from rembg import remove

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "source-prepped.png"


def main() -> None:
    if len(sys.argv) < 2:
        raise SystemExit("Uso: python scripts/prep_photo.py foto.jpg")
    img = Image.open(sys.argv[1]).convert("RGB")
    img.thumbnail((1200, 1200))

    cut = np.array(remove(img))  # RGBA con el fondo transparente
    rgb, alpha = cut[..., :3], cut[..., 3].astype(np.float32) / 255.0

    gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
    clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
    gray = clahe.apply(gray).astype(np.float32)

    # Sobre blanco puro: el fondo acabará como espacios en el ASCII
    out = gray * alpha + 255.0 * (1.0 - alpha)

    ys, xs = np.where(alpha > 0.1)
    if len(xs):
        pad = int(0.04 * max(out.shape))
        y0, y1 = max(ys.min() - pad, 0), min(ys.max() + pad, out.shape[0])
        x0, x1 = max(xs.min() - pad, 0), min(xs.max() + pad, out.shape[1])
        out = out[y0:y1, x0:x1]

    Image.fromarray(out.clip(0, 255).astype(np.uint8)).save(OUT)
    print(f"-> {OUT}")


if __name__ == "__main__":
    main()
