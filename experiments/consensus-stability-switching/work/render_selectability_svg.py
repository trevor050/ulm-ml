#!/usr/bin/env python3
"""Render a compact SVG for cluster selectability gaps."""

from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"


def read_by_n(path: Path):
    rows = []
    with path.open(newline="") as f:
        for row in csv.DictReader(f):
            rows.append(
                {
                    "N": int(row["N"]),
                    "any": float(row["any_correct"]),
                    "sc": float(row["self_consistency"]),
                    "sum": float(row["cluster_sum"]),
                }
            )
    return rows


def poly(points):
    return " ".join(f"{x:.1f},{y:.1f}" for x, y in points)


def main():
    configs = [
        ("MATH/Llama-3-8B", OUT / "monkey_selectability_math_llama_by_n.csv", "#246bfe"),
        ("MATH/Gemma-2B", OUT / "monkey_selectability_math_gemma2b_by_n.csv", "#d04f30"),
    ]
    width, height = 920, 520
    ml, mr, mt, mb = 82, 32, 54, 74
    plot_w, plot_h = width - ml - mr, height - mt - mb
    ns = [4, 8, 16, 32, 64, 128]

    def x_pos(n):
        return ml + (ns.index(n) / (len(ns) - 1)) * plot_w

    def y_pos(v):
        return mt + (1.0 - v) * plot_h

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#fbfaf7"/>',
        '<text x="82" y="31" font-family="Inter, Arial, sans-serif" font-size="22" font-weight="700" fill="#161616">Cluster selectability gap on Monkey Business MATH traces</text>',
        '<text x="82" y="52" font-family="Inter, Arial, sans-serif" font-size="13" fill="#555">Any-correct coverage rises with N, but deployed cluster selectors lag far behind.</text>',
    ]

    for i in range(6):
        v = i / 5
        y = y_pos(v)
        parts.append(f'<line x1="{ml}" y1="{y:.1f}" x2="{width-mr}" y2="{y:.1f}" stroke="#dedbd2" stroke-width="1"/>')
        parts.append(f'<text x="{ml-12}" y="{y+4:.1f}" text-anchor="end" font-family="Inter, Arial, sans-serif" font-size="12" fill="#666">{v:.1f}</text>')
    parts.append(f'<line x1="{ml}" y1="{mt}" x2="{ml}" y2="{height-mb}" stroke="#333" stroke-width="1.2"/>')
    parts.append(f'<line x1="{ml}" y1="{height-mb}" x2="{width-mr}" y2="{height-mb}" stroke="#333" stroke-width="1.2"/>')

    for n in ns:
        x = x_pos(n)
        parts.append(f'<line x1="{x:.1f}" y1="{height-mb}" x2="{x:.1f}" y2="{height-mb+5}" stroke="#333" stroke-width="1"/>')
        parts.append(f'<text x="{x:.1f}" y="{height-mb+23}" text-anchor="middle" font-family="Inter, Arial, sans-serif" font-size="12" fill="#333">{n}</text>')
    parts.append(f'<text x="{ml + plot_w/2:.1f}" y="{height-22}" text-anchor="middle" font-family="Inter, Arial, sans-serif" font-size="13" fill="#333">sample budget N</text>')
    parts.append(f'<text x="24" y="{mt + plot_h/2:.1f}" transform="rotate(-90 24 {mt + plot_h/2:.1f})" text-anchor="middle" font-family="Inter, Arial, sans-serif" font-size="13" fill="#333">accuracy / coverage</text>')

    legend_y = 82
    for label, path, color in configs:
        rows = read_by_n(path)
        any_pts = [(x_pos(r["N"]), y_pos(r["any"])) for r in rows]
        sum_pts = [(x_pos(r["N"]), y_pos(r["sum"])) for r in rows]
        sc_pts = [(x_pos(r["N"]), y_pos(r["sc"])) for r in rows]
        parts.append(f'<polyline points="{poly(any_pts)}" fill="none" stroke="{color}" stroke-width="3.2"/>')
        parts.append(f'<polyline points="{poly(sum_pts)}" fill="none" stroke="{color}" stroke-width="2.2" stroke-dasharray="7 5"/>')
        parts.append(f'<polyline points="{poly(sc_pts)}" fill="none" stroke="{color}" stroke-width="1.7" stroke-dasharray="2 5" opacity="0.7"/>')
        for x, y in any_pts + sum_pts:
            parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3.2" fill="{color}"/>')
        parts.append(f'<text x="{width-300}" y="{legend_y}" font-family="Inter, Arial, sans-serif" font-size="13" fill="{color}" font-weight="700">{label}</text>')
        legend_y += 21

    parts += [
        f'<line x1="{width-300}" y1="{legend_y+7}" x2="{width-265}" y2="{legend_y+7}" stroke="#333" stroke-width="3.2"/>',
        f'<text x="{width-258}" y="{legend_y+11}" font-family="Inter, Arial, sans-serif" font-size="12" fill="#333">any-correct oracle coverage</text>',
        f'<line x1="{width-300}" y1="{legend_y+28}" x2="{width-265}" y2="{legend_y+28}" stroke="#333" stroke-width="2.2" stroke-dasharray="7 5"/>',
        f'<text x="{width-258}" y="{legend_y+32}" font-family="Inter, Arial, sans-serif" font-size="12" fill="#333">cluster_sum selected accuracy</text>',
        f'<line x1="{width-300}" y1="{legend_y+49}" x2="{width-265}" y2="{legend_y+49}" stroke="#333" stroke-width="1.7" stroke-dasharray="2 5" opacity="0.7"/>',
        f'<text x="{width-258}" y="{legend_y+53}" font-family="Inter, Arial, sans-serif" font-size="12" fill="#333">self-consistency</text>',
        "</svg>",
    ]
    path = OUT / "cluster_selectability_gap_plot.svg"
    path.write_text("\n".join(parts))
    print(path)


if __name__ == "__main__":
    main()
