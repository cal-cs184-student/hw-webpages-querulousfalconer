#!/usr/bin/env python3
"""
Procedurally generates docs/competition.svg for the CS184/284A HW1 rasterizer.
Output uses only: <polygon>, <texture>, <textri> (no paths/curves).
Run from repo root: python3 src/generate_competition_svg.py
"""

import math
import os

W, H = 800, 800
CENTER_X, CENTER_Y = W / 2, H / 2
OUT_PATH = os.path.join(os.path.dirname(__file__), "..", "docs", "competition.svg")


def fmt(x: float, y: float) -> str:
    return f"{x:.4f},{y:.4f}"


def fmt_pts(points: list[tuple[float, float]]) -> str:
    return " ".join(f"{x:.4f},{y:.4f}" for x, y in points)


def fmt_pts_space(points: list[tuple[float, float]]) -> str:
    return " ".join(f"{x:.4f} {y:.4f}" for x, y in points)


def polygon(fill: str, points: list[tuple[float, float]]) -> str:
    return f'  <polygon fill="{fill}" points="{fmt_pts(points)}"/>'


def textri(texid: str, uvs: list[tuple[float, float]], points: list[tuple[float, float]]) -> str:
    uv_str = " ".join(f"{u:.6f} {v:.6f}" for u, v in uvs)
    pt_str = fmt_pts_space(points)
    return f'  <textri texid="{texid}" uvs="{uv_str}" points="{pt_str}"/>'


def main() -> None:
    lines = [
        '<?xml version="1.0" encoding="utf-8"?>',
        '<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">',
        '<svg version="1.1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"',
        f'     width="{W}px" height="{H}px" viewBox="0 0 {W} {H}" xml:space="preserve">',
        "",
        '  <texture filename="../svg/texmap/pexels_scene.png" texid="map"/>',
        "",
        "  <!-- Background sky gradient -->",
        polygon("#0a0e1a", [(0, 0), (W, 0), (0, H / 2)]),
        polygon("#0a0e1a", [(W, 0), (W, H / 2), (0, H / 2)]),
        polygon("#141c28", [(0, H / 2), (W, H / 2), (0, H)]),
        polygon("#141c28", [(W, H / 2), (W, H), (0, H)]),
        "",
        "  <!-- Spiral of triangles (geometric antialiasing) -->",
    ]

    spiral_colors = ["#3b82f6", "#8b5cf6", "#ec4899", "#f43f5e", "#f97316", "#eab308", "#22c55e"]
    num_arms = 7
    segments_per_arm = 24
    for arm in range(num_arms):
        color = spiral_colors[arm % len(spiral_colors)]
        for i in range(segments_per_arm):
            t0 = i / segments_per_arm
            t1 = (i + 1) / segments_per_arm
            # radius and angle: one full turn, radius from ~50 to ~280
            r0 = 50 + 230 * t0
            r1 = 50 + 230 * t1
            a0 = 2 * math.pi * t0
            a1 = 2 * math.pi * t1
            # inner point for wedge (slightly toward center)
            r_mid = (r0 + r1) / 2 * 0.85
            a_mid = (a0 + a1) / 2
            x0 = CENTER_X + r0 * math.cos(a0)
            y0 = CENTER_Y + r0 * math.sin(a0)
            x1 = CENTER_X + r1 * math.cos(a1)
            y1 = CENTER_Y + r1 * math.sin(a1)
            xm = CENTER_X + r_mid * math.cos(a_mid)
            ym = CENTER_Y + r_mid * math.sin(a_mid)
            lines.append(polygon(color, [(x0, y0), (x1, y1), (xm, ym)]))

    lines.extend([
        "",
        "  <!-- Tiled diamond pattern -->",
    ])
    half = 12.6  # half-cell size
    step = 28.0  # grid step
    start = 14.0  # first center
    diamond_colors = ["#2a314d", "#3e405a", "#524f66"]
    row_max = int((H - start) / step) + 2
    col_max = int((W - start) / step) + 2
    for row in range(row_max):
        for col in range(col_max):
            cx = start + col * step + (step / 2 if row % 2 else 0)
            cy = start + row * step
            if cx > W + half or cy > H + half:
                continue
            color = diamond_colors[(row + col) % 3]
            # 4 triangles per diamond: center (cx,cy) with points at right, down, left, up
            lines.append(polygon(color, [(cx, cy), (cx + half, cy), (cx, cy + half)]))
            lines.append(polygon(color, [(cx, cy), (cx, cy + half), (cx - half, cy)]))
            lines.append(polygon(color, [(cx, cy), (cx - half, cy), (cx, cy - half)]))
            lines.append(polygon(color, [(cx, cy), (cx, cy - half), (cx + half, cy)]))

    lines.extend([
        "",
        "  <!-- Textured panels (texture antialiasing) -->",
        textri("map", [(0.2, 0.25), (0.55, 0.25), (0.55, 0.6)], [(120, 464), (340, 464), (340, 624)]),
        textri("map", [(0.2, 0.25), (0.55, 0.6), (0.2, 0.6)], [(120, 464), (340, 624), (120, 624)]),
        textri("map", [(0.5, 0.1), (0.9, 0.1), (0.9, 0.5)], [(416, 496), (596, 496), (596, 626)]),
        textri("map", [(0.5, 0.1), (0.9, 0.5), (0.5, 0.5)], [(416, 496), (596, 626), (416, 626)]),
        textri("map", [(0.1, 0.6), (0.35, 0.6), (0.35, 0.9)], [(544, 416), (634, 416), (634, 511)]),
        textri("map", [(0.1, 0.6), (0.35, 0.9), (0.1, 0.9)], [(544, 416), (634, 511), (544, 511)]),
        "",
        "  <!-- Stylized hills (layered polygons) -->",
        polygon("#1e293b", [(0, 420), (120, 380), (280, 400), (450, 360), (600, 390), (W, 370), (W, H), (0, H)]),
        polygon("#334155", [(0, 520), (200, 460), (400, 500), (550, 450), (720, 480), (W, 440), (W, H), (0, H)]),
        polygon("#0f172a", [(0, 620), (80, 580), (240, 610), (380, 560), (520, 600), (680, 570), (W, 590), (W, H), (0, H)]),
        "",
        "  <!-- Foreground accent triangles -->",
        polygon("#4ade80", [(120, 680), (155, 600), (190, 680)]),
        polygon("#38bdf8", [(380, 690), (415, 610), (450, 690)]),
        polygon("#f97316", [(600, 685), (635, 615), (670, 685)]),
        "",
        "</svg>",
    ])

    out_dir = os.path.dirname(OUT_PATH)
    os.makedirs(out_dir, exist_ok=True)
    with open(OUT_PATH, "w") as f:
        f.write("\n".join(lines))
    print(f"Wrote {OUT_PATH}")


if __name__ == "__main__":
    main()
