#!/usr/bin/env python3
"""
animate_architecture.py
Creates an animated GIF from lab5-architecture.png by drawing
moving dots along the data-flow arrows and compositing squirrel icons on top.

Arrow positions are derived from the .excalidraw JSON via a verified
affine mapping: PNG_x = ex_x * 2.0056 + 575.2, PNG_y = ex_y * 1.9831 - 5728.3

Usage:
    uv run python3 scripts/animate_architecture.py             # produce GIF
    uv run python3 scripts/animate_architecture.py --calibrate # verify arrow paths
"""

import base64
import io
import json
import math
import sys
from pathlib import Path
from PIL import Image, ImageDraw

# ── Paths ─────────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).parent.parent
IMG_PATH = BASE_DIR / "assets/lab5/lab5-architecture.png"
EXCALIDRAW_PATH = BASE_DIR / "assets/lab5/lab5-architecture.excalidraw"
OUT_PATH = BASE_DIR / "assets/lab5/lab5-architecture-animated.gif"
CAL_PATH = BASE_DIR / "assets/lab5/lab5-architecture-calibration.png"

# ── Animation parameters ──────────────────────────────────────────────────────
NUM_FRAMES = 10
FRAME_DELAY_MS = 80
DOT_RADIUS = 5
DOT_SPACING = 70
DOT_COLOR = (255, 255, 255, 255)

# ── Squirrel (Flink logo) ─────────────────────────────────────────────────────
SQUIRREL_FILE_ID = "90ecbeecc2a22af649ea0c61e2e487e64e778e19"
# Rendered size in PNG pixels (matches existing diagram usage)
SQUIRREL_W = 84
SQUIRREL_H = 83
# Centers of squirrel placements (x, y) in PNG pixel space.
# Placed on top of everything else (composited last).
#   1. Below "Anomaly detection" (existing position, redrawn on top)
#   2. Midpoint of A2: claims_anomalies → Flink Agent arrow
#   3. Midpoint of A3: Flink Agent → claims_reviewed arrow
SQUIRREL_CENTERS = [
    (660, 500),    # below "Anomaly detection" (existing squirrel, now on top)
    (1452, 512),   # midpoint of A2 arrow
    (2357, 512),   # midpoint of A3 arrow
]

# ── Arrow paths ───────────────────────────────────────────────────────────────
# ONE-DIRECTIONAL arrows: dots travel from start → end.
# BIDIRECTIONAL arrows: stored separately — dots radiate from midpoint outward in both directions.

ONE_WAY_PATHS = [
    # A1: claims → claims_anomalies
    [(497, 554), (852, 554)],
    # A2: claims_anomalies → Flink Agent
    [(1299, 553), (1606, 553)],
    # A3: Flink Agent → claims_reviewed
    [(2224, 554), (2491, 554)],
    # A4: claims_reviewed → Regulatory reviewers
    [(2938, 554), (3205, 554)],
    # A7: claims_reviewed → iceberg (Confluent Tableflow, vertical)
    [(2723, 667), (2729, 1008)],
    # A8: IBM MQ Source Connector (bottom → top)
    [(283, 1014), (283, 649)],
]

# BIDIRECTIONAL arrows: dots start at midpoint and radiate both ways each frame.
# Each entry is (start, end) — midpoint is computed automatically.
BIDIRECTIONAL_PATHS = [
    # A5: Flink → WatsonX Agent (HTTP Post Sink Connector)
    ((1919, 788), (1919, 1002)),
    # A6: WatsonX → CIS
    ((1933, 1371), (1933, 1569)),
]

# Calibration colors
CAL_COLORS = [
    (220, 30, 30, 220),
    (30, 160, 30, 220),
    (30, 30, 220, 220),
    (180, 0, 180, 220),
    (140, 0, 200, 220),
    (180, 160, 0, 220),
    (220, 130, 0, 220),
    (0, 180, 180, 220),
]


def load_squirrel() -> Image.Image:
    """Extract squirrel PNG from the excalidraw file and return as RGBA Image."""
    with open(EXCALIDRAW_PATH) as f:
        data = json.load(f)
    files = data.get("files", {})
    file_data = files.get(SQUIRREL_FILE_ID, {})
    dataurl = file_data.get("dataURL", "")
    if not dataurl:
        raise RuntimeError(f"Squirrel fileId {SQUIRREL_FILE_ID} not found in excalidraw")
    b64 = dataurl.split(",", 1)[1]
    img_bytes = base64.b64decode(b64)
    img = Image.open(io.BytesIO(img_bytes)).convert("RGBA")
    return img.resize((SQUIRREL_W, SQUIRREL_H), Image.LANCZOS)


def composite_squirrels(base: Image.Image, squirrel: Image.Image) -> Image.Image:
    """Paste squirrel icon on top of base at each center position."""
    result = base.copy()
    for cx, cy in SQUIRREL_CENTERS:
        x = cx - SQUIRREL_W // 2
        y = cy - SQUIRREL_H // 2
        result.paste(squirrel, (x, y), mask=squirrel.split()[3])
    return result


def interpolate_path(points: list[tuple[int, int]]) -> list[tuple[int, int]]:
    """Return every (x, y) along a polyline at ~1px resolution."""
    result = []
    for i in range(len(points) - 1):
        x0, y0 = points[i]
        x1, y1 = points[i + 1]
        dist = math.hypot(x1 - x0, y1 - y0)
        n = max(1, int(dist))
        for j in range(n):
            t = j / n
            result.append((round(x0 + t * (x1 - x0)), round(y0 + t * (y1 - y0))))
    result.append(points[-1])
    return result


def draw_one_way(draw: ImageDraw.ImageDraw, path: list[tuple[int, int]], offset: int) -> None:
    """Draw moving dots along a one-directional path."""
    pixels = interpolate_path(path)
    r = DOT_RADIUS
    pos = offset % DOT_SPACING  # wrap so dots enter from start each cycle
    while pos < len(pixels):
        x, y = pixels[pos]
        draw.ellipse([x - r, y - r, x + r, y + r], fill=DOT_COLOR)
        pos += DOT_SPACING


def draw_bidirectional(draw: ImageDraw.ImageDraw, start: tuple, end: tuple, offset: int) -> None:
    """Draw dots radiating from midpoint in both directions simultaneously."""
    pixels = interpolate_path([start, end])
    total = len(pixels)
    mid = total // 2
    r = DOT_RADIUS

    # Upward half: from mid toward start (index mid down to 0)
    pos = offset % DOT_SPACING
    while pos <= mid:
        idx = mid - pos
        x, y = pixels[idx]
        draw.ellipse([x - r, y - r, x + r, y + r], fill=DOT_COLOR)
        pos += DOT_SPACING

    # Downward half: from mid toward end (index mid up to total-1)
    pos = offset % DOT_SPACING
    while pos <= total - 1 - mid:
        idx = mid + pos
        x, y = pixels[idx]
        draw.ellipse([x - r, y - r, x + r, y + r], fill=DOT_COLOR)
        pos += DOT_SPACING


def make_frame(base_with_squirrels: Image.Image, frame_index: int) -> Image.Image:
    """Render one animation frame."""
    frame = base_with_squirrels.convert("RGBA").copy()
    overlay = Image.new("RGBA", frame.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    offset = int(frame_index * DOT_SPACING / NUM_FRAMES)

    for path in ONE_WAY_PATHS:
        draw_one_way(draw, path, offset)

    for start, end in BIDIRECTIONAL_PATHS:
        draw_bidirectional(draw, start, end, offset)

    composited = Image.alpha_composite(frame, overlay)
    rgb = Image.new("RGB", composited.size, (255, 255, 255))
    rgb.paste(composited, mask=composited.split()[3])
    return rgb


def run_calibrate(base_img: Image.Image, squirrel: Image.Image) -> None:
    """Draw all arrow paths as colored lines and show squirrel positions."""
    img = composite_squirrels(base_img.convert("RGBA"), squirrel)
    draw = ImageDraw.Draw(img)
    r = DOT_RADIUS + 1

    all_paths = ONE_WAY_PATHS + [list(p) for p in BIDIRECTIONAL_PATHS]
    for idx, path in enumerate(all_paths):
        color = CAL_COLORS[idx % len(CAL_COLORS)]
        pixels = interpolate_path(path if isinstance(path[0], tuple) else [path[0], path[1]])
        for x, y in pixels:
            draw.ellipse([x - r, y - r, x + r, y + r], fill=color)
        sx, sy = pixels[0]
        draw.text((sx + 6, sy - 22), f"P{idx+1}", fill=color)

    rgb = Image.new("RGB", img.size, (255, 255, 255))
    rgb.paste(img, mask=img.split()[3])
    rgb.save(CAL_PATH)
    print(f"Calibration image saved → {CAL_PATH}")


def main() -> None:
    calibrate = "--calibrate" in sys.argv

    print(f"Loading {IMG_PATH} ...")
    base_img = Image.open(IMG_PATH)
    print(f"  Size: {base_img.size}, mode: {base_img.mode}")

    print("Loading squirrel from excalidraw ...")
    squirrel = load_squirrel()

    # Composite squirrels onto the base once — reused for every frame
    base_with_squirrels = composite_squirrels(base_img.convert("RGBA"), squirrel)

    if calibrate:
        run_calibrate(base_img, squirrel)
        return

    print(f"Generating {NUM_FRAMES} frames ...")
    frames = []
    for f in range(NUM_FRAMES):
        print(f"  Frame {f + 1}/{NUM_FRAMES}", end="\r")
        frames.append(make_frame(base_with_squirrels, f))
    print()

    print(f"Saving GIF → {OUT_PATH}")
    frames[0].save(
        OUT_PATH,
        format="GIF",
        save_all=True,
        append_images=frames[1:],
        loop=0,
        duration=FRAME_DELAY_MS,
        optimize=False,
    )
    print("Done.")


if __name__ == "__main__":
    main()
