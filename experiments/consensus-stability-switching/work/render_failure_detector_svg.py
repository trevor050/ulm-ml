#!/usr/bin/env python3
"""Render detector-bound curves for MATH/Llama and MATH/Gemma."""

from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"


def read_curve(path: Path, target: str):
    rows = []
    with path.open(newline="") as f:
        for row in csv.DictReader(f):
            if row["target"] == target:
                rows.append(
                    {
                        "invoke": float(row["invoke_rate"]),
                        "acc": float(row["perfect_visible_oracle_acc"]),
                        "precision": float(row["precision"]),
                        "recall": float(row["recall"]),
                    }
                )
    return rows


def read_baseline(path: Path):
    rows = read_curve(path, "visible_miss")
    # perfect_visible_oracle_acc includes cluster_sum + captured visible misses.
    # At zero invoke, the baseline is the first curve point minus its captured
    # visible-miss contribution. Easier and exact enough: parse matching report
    # is overkill; use known CSV relation from diagnostics.
    first = rows[0]
    return first["acc"] - first["invoke"] * first["precision"]


def poly(points):
    return " ".join(f"{x:.1f},{y:.1f}" for x, y in points)


def main():
    configs = [
        ("MATH/Llama", OUT / "failure_detector_math_llama_n128.csv", "#246bfe"),
        ("MATH/Gemma-2B", OUT / "failure_detector_math_gemma2b_n128.csv", "#d04f30"),
    ]
    width, height = 900, 500
    ml, mr, mt, mb = 80, 34, 58, 70
    plot_w, plot_h = width - ml - mr, height - mt - mb

    def x_pos(v):
        return ml + v * plot_w

    def y_pos(v):
        ymin, ymax = 0.20, 0.62
        return mt + (ymax - v) / (ymax - ymin) * plot_h

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#fbfaf7"/>',
        '<text x="80" y="32" font-family="Inter, Arial, sans-serif" font-size="22" font-weight="700" fill="#151515">Failure detector bound for a perfect top-5 verifier</text>',
        '<text x="80" y="53" font-family="Inter, Arial, sans-serif" font-size="13" fill="#555">Cheap detector ranks risky candidate sets, but even optimistic invoked-verifier accuracy remains far below full oracle coverage.</text>',
    ]
    for i in range(6):
        v = 0.20 + i * (0.42 / 5)
        y = y_pos(v)
        parts.append(f'<line x1="{ml}" y1="{y:.1f}" x2="{width-mr}" y2="{y:.1f}" stroke="#dedbd2"/>')
        parts.append(f'<text x="{ml-10}" y="{y+4:.1f}" text-anchor="end" font-family="Inter, Arial, sans-serif" font-size="12" fill="#666">{v:.2f}</text>')
    for v in [0.0, 0.1, 0.2, 0.3, 0.5]:
        x = x_pos(v)
        parts.append(f'<line x1="{x:.1f}" y1="{height-mb}" x2="{x:.1f}" y2="{height-mb+5}" stroke="#333"/>')
        parts.append(f'<text x="{x:.1f}" y="{height-mb+23}" text-anchor="middle" font-family="Inter, Arial, sans-serif" font-size="12" fill="#333">{v:.1f}</text>')
    parts.append(f'<line x1="{ml}" y1="{mt}" x2="{ml}" y2="{height-mb}" stroke="#333" stroke-width="1.2"/>')
    parts.append(f'<line x1="{ml}" y1="{height-mb}" x2="{width-mr}" y2="{height-mb}" stroke="#333" stroke-width="1.2"/>')
    parts.append(f'<text x="{ml + plot_w/2:.1f}" y="{height-22}" text-anchor="middle" font-family="Inter, Arial, sans-serif" font-size="13" fill="#333">detector invocation rate</text>')
    parts.append(f'<text x="24" y="{mt + plot_h/2:.1f}" transform="rotate(-90 24 {mt + plot_h/2:.1f})" text-anchor="middle" font-family="Inter, Arial, sans-serif" font-size="13" fill="#333">deployed accuracy upper bound</text>')

    legend_y = 90
    for label, path, color in configs:
        curve = read_curve(path, "visible_miss")
        baseline = read_baseline(path)
        pts = [(x_pos(0.0), y_pos(baseline))] + [(x_pos(r["invoke"]), y_pos(r["acc"])) for r in curve]
        parts.append(f'<polyline points="{poly(pts)}" fill="none" stroke="{color}" stroke-width="3"/>')
        for x, y in pts:
            parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3.4" fill="{color}"/>')
        parts.append(f'<text x="{width-250}" y="{legend_y}" font-family="Inter, Arial, sans-serif" font-size="13" font-weight="700" fill="{color}">{label}</text>')
        legend_y += 22
    parts += [
        f'<text x="{width-250}" y="{legend_y+14}" font-family="Inter, Arial, sans-serif" font-size="12" fill="#333">Assumes invoked verifier is perfect</text>',
        f'<text x="{width-250}" y="{legend_y+32}" font-family="Inter, Arial, sans-serif" font-size="12" fill="#333">over visible top-5 clusters.</text>',
        "</svg>",
    ]
    path = OUT / "failure_detector_bound_plot.svg"
    path.write_text("\n".join(parts))
    print(path)


if __name__ == "__main__":
    main()
