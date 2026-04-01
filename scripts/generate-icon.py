"""
Generate app icon: blue circular background with gold Greek Gamma (Γ) centered.
Outputs assets/icon.png (1024×1024) and assets/icon.ico (256×256).

Usage: python3 scripts/generate-icon.py
Requires: Pillow
"""

import os
import sys
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("Pillow is required. Run: pip install Pillow")
    sys.exit(1)

# Paths
SCRIPT_DIR = Path(__file__).parent
ASSETS_DIR = SCRIPT_DIR.parent / "assets"
ASSETS_DIR.mkdir(exist_ok=True)

SIZE = 1024
MARGIN_FRAC = 0.08

# Colors
BLUE_BG    = (20, 40, 100)      # navy blue
GOLD_TEXT  = (255, 210, 60)     # gold
WHITE_RING = (255, 255, 255)    # thin ring around circle


def make_icon(size: int) -> Image.Image:
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    cx, cy = size // 2, size // 2
    margin = int(size * MARGIN_FRAC)
    r = cx - margin

    # Outer white ring
    draw.ellipse([cx - r - 6, cy - r - 6, cx + r + 6, cy + r + 6], fill=WHITE_RING + (255,))

    # Blue circle
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=BLUE_BG + (255,))

    # Draw Γ (capital Greek Gamma, U+0393)
    gamma_char = "Γ"
    font_size = int(size * 0.64)

    # Try to find a suitable font with Greek support
    font = None
    font_candidates = [
        "/System/Library/Fonts/Supplemental/Times New Roman.ttf",
        "/System/Library/Fonts/Times.ttc",
        "/usr/share/fonts/truetype/freefont/FreeSerifBold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
        "/usr/share/fonts/truetype/noto/NotoSerif-Bold.ttf",
    ]

    for candidate in font_candidates:
        if os.path.exists(candidate):
            try:
                font = ImageFont.truetype(candidate, font_size)
                break
            except Exception:
                continue

    if font is None:
        # Fallback: use default font (may not render Γ correctly)
        try:
            font = ImageFont.load_default(size=font_size)
        except TypeError:
            font = ImageFont.load_default()

    # Measure text bounding box
    bbox = draw.textbbox((0, 0), gamma_char, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]

    x = cx - text_w // 2 - bbox[0]
    y = cy - text_h // 2 - bbox[1]

    # Draw gold Gamma with slight shadow for depth
    shadow_offset = max(2, size // 80)
    draw.text((x + shadow_offset, y + shadow_offset), gamma_char, font=font,
              fill=(100, 70, 0, 180))
    draw.text((x, y), gamma_char, font=font, fill=GOLD_TEXT + (255,))

    return img


def main():
    print("Generating icon...")
    icon_1024 = make_icon(1024)
    out_png = ASSETS_DIR / "icon.png"
    icon_1024.save(str(out_png), "PNG")
    print(f"  Saved {out_png}")

    # ICO: multiple sizes
    ico_sizes = [16, 24, 32, 48, 64, 128, 256]
    ico_images = [make_icon(s).convert("RGBA") for s in ico_sizes]
    out_ico = ASSETS_DIR / "icon.ico"
    ico_images[0].save(
        str(out_ico),
        format="ICO",
        sizes=[(s, s) for s in ico_sizes],
        append_images=ico_images[1:]
    )
    print(f"  Saved {out_ico}")

    print("Done.")


if __name__ == "__main__":
    main()
