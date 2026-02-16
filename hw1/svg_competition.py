#!/usr/bin/env python3
"""
Procedural generator for docs/competition.svg (art competition extra credit).

HOW IT WORKS
------------
This script writes an 800x800 SVG that uses only elements the rasterizer supports:
Polygon (triangles), texture + textri (textured triangles), and no Path/curves.

1. what it pops out
   - Standard SVG header with viewBox "0 0 800 800".
   - <texture filename="..." texid="map"/> declares the image (path relative to
     docs/ when the SVG is loaded from docs/competition.svg).
   - <polygon fill="#hex" points="x1,y1 x2,y2 x3,y3"/> for solid triangles.
   - <textri texid="map" uvs="u1 v1 u2 v2 u3 v3" points="x1 y1 x2 y2 x3 y3"/>
     for textured triangles (uvs are normalized 0-1; each quad is two textris).

2. how to generate the svg:
   - Background: four large triangles forming a two-tone gradient.
   - Spiral: 7 arms × 24 wedge triangles per arm, with radius and angle
     parameterized by t in [0,1]; colors cycle across arms. Highlights
     geometric (edge) antialiasing.
   - Diamond tiling: grid of small diamonds (each 4 triangles from center),
     offset every other row; color shade varies by (row,col). More thin edges.
   - Textured panels: three quads (each emitted as two textri elements) with
     different uv regions into the same texture. Highlights texture
     (bilinear/trilinear) antialiasing.
   - Hills: three layered polygons (many vertices); the parser triangulates
     them. Foreground accent triangles complete the scene.

3. running it
   From repo root:  python3 src/generate_competition_svg.py
   Writes: docs/competition.svg

   Then load docs/competition.svg in the rasterizer, resize to 800x800, and
   press 'S' to save the 800x800 PNG screenshot for the write-up.
"""
import math
import sys
from pathlib import Path

W, H = 800, 800
# When this script lives in src/, parent.parent is repo root
OUT_PATH = Path(__file__).resolve().parent.parent / "docs" / "competition.svg"
# Texture path relative to docs/ when SVG is loaded from docs/competition.svg
TEX_PATH = "../svg/texmap/pexels_scene.png"


def emit_header(f):
    f.write('<?xml version="1.0" encoding="utf-8"?>\n')
    f.write('<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">\n')
    f.write(
        f'<svg version="1.1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"\n'
    )
    f.write(f'     width="{W}px" height="{H}px" viewBox="0 0 {W} {H}" xml:space="preserve">\n\n')


def emit_triangle(f, p0, p1, p2, fill):
    pts = f"{p0[0]:.4f},{p0[1]:.4f} {p1[0]:.4f},{p1[1]:.4f} {p2[0]:.4f},{p2[1]:.4f}"
    f.write(f'  <polygon fill="{fill}" points="{pts}"/>\n')


def emit_textured_quad(f, texid, corners, uvs):
    """corners = [(x0,y0), (x1,y1), (x2,y2), (x3,y3)]; uvs = [(u0,v0), ...]"""
    for tri_inds in [(0, 1, 2), (0, 2, 3)]:
        i, j, k = tri_inds
        pts = f"{corners[i][0]:.4f} {corners[i][1]:.4f} {corners[j][0]:.4f} {corners[j][1]:.4f} {corners[k][0]:.4f} {corners[k][1]:.4f}"
        uv = f"{uvs[i][0]:.6f} {uvs[i][1]:.6f} {uvs[j][0]:.6f} {uvs[j][1]:.6f} {uvs[k][0]:.6f} {uvs[k][1]:.6f}"
        f.write(f'  <textri texid="{texid}" uvs="{uv}" points="{pts}"/>\n')


def main():
    with open(OUT_PATH, "w") as f:
        emit_header(f)

        f.write(f'  <texture filename="{TEX_PATH}" texid="map"/>\n\n')

        f.write("  <!-- Background sky gradient -->\n")
        emit_triangle(f, (0, 0), (W, 0), (0, H * 0.5), "#0a0e1a")
        emit_triangle(f, (W, 0), (W, H * 0.5), (0, H * 0.5), "#0a0e1a")
        emit_triangle(f, (0, H * 0.5), (W, H * 0.5), (0, H), "#141c28")
        emit_triangle(f, (W, H * 0.5), (W, H), (0, H), "#141c28")
        f.write("\n")

        f.write("  <!-- Spiral of triangles (geometric antialiasing) -->\n")
        cx, cy = W * 0.5, H * 0.45
        n_arms = 7
        triangles_per_arm = 24
        spiral_colors = ["#3b82f6", "#8b5cf6", "#ec4899", "#f43f5e", "#f97316", "#eab308", "#22c55e"]
        for arm in range(n_arms):
            base_angle = 2 * math.pi * arm / n_arms
            color = spiral_colors[arm % len(spiral_colors)]
            for i in range(triangles_per_arm):
                t0 = i / triangles_per_arm
                t1 = (i + 1) / triangles_per_arm
                r0 = 40 + t0 * 220
                r1 = 40 + t1 * 220
                a0 = base_angle + t0 * 4 * math.pi
                a1 = base_angle + t1 * 4 * math.pi
                x0 = cx + r0 * math.cos(a0)
                y0 = cy + r0 * math.sin(a0)
                x1 = cx + r1 * math.cos(a1)
                y1 = cy + r1 * math.sin(a1)
                r2 = r0 + (r1 - r0) * 0.5
                a2 = (a0 + a1) / 2
                x2 = cx + (r2 - 15) * math.cos(a2)
                y2 = cy + (r2 - 15) * math.sin(a2)
                emit_triangle(f, (x0, y0), (x1, y1), (x2, y2), color)
        f.write("\n")

        f.write("  <!-- Tiled diamond pattern -->\n")
        tile_sz = 28
        for row in range(0, H // tile_sz + 2):
            for col in range(0, W // tile_sz + 2):
                ox = col * tile_sz + (row % 2) * (tile_sz // 2)
                oy = row * tile_sz
                if oy > H * 0.7:
                    continue
                cx_t = ox + tile_sz / 2
                cy_t = oy + tile_sz / 2
                for k in range(4):
                    a1 = k * math.pi / 2
                    a2 = (k + 1) * math.pi / 2
                    p0 = (cx_t, cy_t)
                    p1 = (cx_t + tile_sz * 0.45 * math.cos(a1), cy_t + tile_sz * 0.45 * math.sin(a1))
                    p2 = (cx_t + tile_sz * 0.45 * math.cos(a2), cy_t + tile_sz * 0.45 * math.sin(a2))
                    shade = 0.15 + 0.25 * ((row + col) % 3)
                    r = int(30 + shade * 80)
                    g = int(40 + shade * 60)
                    b = int(70 + shade * 50)
                    emit_triangle(f, p0, p1, p2, f"#{r:02x}{g:02x}{b:02x}")
        f.write("\n")

        f.write("  <!-- Textured panel (texture antialiasing) -->\n")
        panel_x0, panel_y0 = W * 0.15, H * 0.58
        panel_w, panel_h = 220, 160
        corners = [
            (panel_x0, panel_y0),
            (panel_x0 + panel_w, panel_y0),
            (panel_x0 + panel_w, panel_y0 + panel_h),
            (panel_x0, panel_y0 + panel_h),
        ]
        uvs = [(0.2, 0.25), (0.55, 0.25), (0.55, 0.6), (0.2, 0.6)]
        emit_textured_quad(f, "map", corners, uvs)

        panel_x1, panel_y1 = W * 0.52, H * 0.62
        pw2, ph2 = 180, 130
        corners2 = [
            (panel_x1, panel_y1),
            (panel_x1 + pw2, panel_y1),
            (panel_x1 + pw2, panel_y1 + ph2),
            (panel_x1, panel_y1 + ph2),
        ]
        uvs2 = [(0.5, 0.1), (0.9, 0.1), (0.9, 0.5), (0.5, 0.5)]
        emit_textured_quad(f, "map", corners2, uvs2)

        panel_x2, panel_y2 = W * 0.68, H * 0.52
        pw3, ph3 = 90, 95
        corners3 = [
            (panel_x2, panel_y2),
            (panel_x2 + pw3, panel_y2),
            (panel_x2 + pw3, panel_y2 + ph3),
            (panel_x2, panel_y2 + ph3),
        ]
        uvs3 = [(0.1, 0.6), (0.35, 0.6), (0.35, 0.9), (0.1, 0.9)]
        emit_textured_quad(f, "map", corners3, uvs3)
        f.write("\n")

        f.write("  <!-- Stylized hills (layered polygons) -->\n")
        hills = [
            ("#1e293b", [0, 420, 120, 380, 280, 400, 450, 360, 600, 390, W, 370, W, H, 0, H]),
            ("#334155", [0, 520, 200, 460, 400, 500, 550, 450, 720, 480, W, 440, W, H, 0, H]),
            ("#0f172a", [0, 620, 80, 580, 240, 610, 380, 560, 520, 600, 680, 570, W, 590, W, H, 0, H]),
        ]
        for color, pts in hills:
            pt_list = " ".join(f"{pts[i]:.0f},{pts[i+1]:.0f}" for i in range(0, len(pts), 2))
            f.write(f'  <polygon fill="{color}" points="{pt_list}"/>\n')
        f.write("\n")

        f.write("  <!-- Foreground accent triangles -->\n")
        accents = [
            ((120, 680), (155, 600), (190, 680), "#4ade80"),
            ((380, 690), (415, 610), (450, 690), "#38bdf8"),
            ((600, 685), (635, 615), (670, 685), "#f97316"),
        ]
        for p0, p1, p2, fill in accents:
            emit_triangle(f, p0, p1, p2, fill)
        f.write("\n")

        f.write("</svg>\n")

    print(f"Wrote {OUT_PATH}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
