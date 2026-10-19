"""Prepara una foto para el retrato ASCII:
1) quita el fondo (rembg), 2) sube el contraste local (CLAHE),
3) la pone sobre blanco y la recorta al sujeto. Salida: source-prepped.png

Uso: python scripts/prep_photo.py foto.jpg"""
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "source-prepped.png"


def white_bg_alpha(rgb: np.ndarray) -> np.ndarray:
    """Máscara del sujeto para fotos que ya tienen fondo blanco:
    rellena desde los bordes las zonas casi blancas conectadas."""
    near_white = (rgb.min(axis=2) > 235).astype(np.uint8)
    h, w = near_white.shape
    bg = np.zeros((h + 2, w + 2), np.uint8)
    flood = near_white.copy()
    for x, y in [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1), (w // 2, 0)]:
        if near_white[y, x]:
            cv2.floodFill(flood, bg, (x, y), 2)
    alpha = (flood != 2).astype(np.float32)
    return cv2.GaussianBlur(alpha, (5, 5), 0)


def main() -> None:
    if len(sys.argv) < 2:
        raise SystemExit("Uso: python scripts/prep_photo.py foto.jpg")
    img = Image.open(sys.argv[1]).convert("RGB")
    img.thumbnail((1200, 1200))

    try:
        from rembg import remove
        cut = np.array(remove(img))  # RGBA con el fondo transparente
        rgb, alpha = cut[..., :3], cut[..., 3].astype(np.float32) / 255.0
    except ImportError:
        print("rembg no instalado: asumo que la foto ya tiene fondo blanco")
        rgb = np.array(img)
        alpha = white_bg_alpha(rgb)

    gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
    clahe = cv2.createCLAHE(clipLimit=3.5, tileGridSize=(6, 6))
    gray = clahe.apply(gray).astype(np.float32)
    # Enfoque (unsharp mask) para marcar ojos, cejas y boca
    blur = cv2.GaussianBlur(gray, (0, 0), 3)
    gray = cv2.addWeighted(gray, 1.8, blur, -0.8, 0).clip(0, 255)

    # Sobre blanco puro: el fondo acabará como espacios en el ASCII
    out = gray * alpha + 255.0 * (1.0 - alpha)

    ys, xs = np.where(alpha > 0.1)
    if len(xs):
        pad = int(0.04 * max(out.shape))
        y0, y1 = max(ys.min() - pad, 0), min(ys.max() + pad, out.shape[0])
        x0, x1 = max(xs.min() - pad, 0), min(xs.max() + pad, out.shape[1])
        out = out[y0:y1, x0:x1]
        alpha = alpha[y0:y1, x0:x1]

    # Guardamos la máscara en el canal alfa para que el ASCII deje el fondo vacío
    la = np.dstack([out.clip(0, 255), alpha * 255]).astype(np.uint8)
    Image.fromarray(la, "LA").save(OUT)
    print(f"-> {OUT}")


if __name__ == "__main__":
    main()
