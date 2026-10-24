# -*- coding: utf-8 -*-
"""Simple crystal structure SVG renderer (F7b) and phase‑diagram SVG renderer (F7c).

Uses only stdlib. Crystal renderer expects pymatgen JSON structure.
Phase‑diagram renderer expects thermo entries with ``composition`` and ``energy_above_hull``.
Both output dark‑theme SVG strings.
"""
import math
import xml.etree.ElementTree as ET
from typing import Dict, List, Tuple


def _vec_mul(mat: List[List[float]], frac: Tuple[float, float, float]) -> Tuple[float, float, float]:
    """Convert fractional coords to Cartesian using lattice matrix."""
    x = mat[0][0] * frac[0] + mat[0][1] * frac[1] + mat[0][2] * frac[2]
    y = mat[1][0] * frac[0] + mat[1][1] * frac[1] + mat[1][2] * frac[2]
    z = mat[2][0] * frac[0] + mat[2][1] * frac[1] + mat[2][2] * frac[2]
    return (x, y, z)


def render_crystal_svg(structure: Dict) -> str:
    """Render crystal structure as minimal SVG.

    Parameters
    ----------
    structure: dict
        Pymatgen JSON dict with keys ``lattice`` (matrix) and ``sites``.
        ``lattice`` must contain ``matrix``: 3×3 list of floats.
        ``sites`` list of dicts with ``abc`` fractional coords and ``species``.
    Returns
    -------
    str
        SVG XML string.
    """
    try:
        mat = structure["lattice"]["matrix"]
    except Exception as e:
        raise ValueError("Invalid structure format: missing lattice matrix") from e

    a_vec = (mat[0][0], mat[1][0], mat[2][0])
    b_vec = (mat[0][1], mat[1][1], mat[2][1])
    def proj(v):
        return (v[0], v[1])
    origin = (0.0, 0.0)
    a_xy = proj(a_vec)
    b_xy = proj(b_vec)
    ab_xy = (a_xy[0] + b_xy[0], a_xy[1] + b_xy[1])

    xs = [origin[0], a_xy[0], b_xy[0], ab_xy[0]]
    ys = [origin[1], a_xy[1], b_xy[1], ab_xy[1]]
    for site in structure.get("sites", []):
        frac = tuple(site.get("abc", (0, 0, 0)))
        cart = _vec_mul(mat, frac)
        xs.append(cart[0])
        ys.append(cart[1])
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)
    pad = 10
    width = max_x - min_x
    height = max_y - min_y
    view_min_x = min_x - pad
    view_min_y = min_y - pad
    view_w = width + 2 * pad
    view_h = height + 2 * pad

    svg = ET.Element("svg", xmlns="http://www.w3.org/2000/svg",
                     width=str(view_w), height=str(view_h),
                     viewBox=f"{view_min_x} {view_min_y} {view_w} {view_h}")
    style = ET.SubElement(svg, "style")
    style.text = "path{stroke:#fff;stroke-width:0.5;fill:none} circle{stroke:#fff;stroke-width:0.2;fill:#ff0}"
    def line(p1, p2):
        ET.SubElement(svg, "path", d=f"M {p1[0]},{p1[1]} L {p2[0]},{p2[1]}")
    line(origin, a_xy)
    line(origin, b_xy)
    line(a_xy, ab_xy)
    line(b_xy, ab_xy)
    atom_radius = max(width, height) * 0.02 or 0.5
    for site in structure.get("sites", []):
        frac = tuple(site.get("abc", (0, 0, 0)))
        cart = _vec_mul(mat, frac)
        cx, cy = cart[0], cart[1]
        ET.SubElement(svg, "circle", cx=str(cx), cy=str(cy), r=str(atom_radius))
    return ET.tostring(svg, encoding="unicode")

# Phase‑diagram SVG renderer (F7c)
def render_phase_diagram_svg(chemsys: str, entries: list[dict]) -> str:
    """Render simple 2‑D phase diagram SVG for binary/ternary systems.

    Parameters
    ----------
    chemsys: str
        Elements dash‑separated, e.g. "Li-Fe-O".
    entries: list[dict]
        Thermo entries from ``search_phase_diagram``; each must contain
        ``composition`` mapping element → amount and ``energy_above_hull``.

    Returns
    -------
    str
        SVG XML (dark theme). Points coloured by hull energy (0 eV → yellow,
        higher → dark gray).
    """
    elements = chemsys.split('-')
    if len(elements) not in (2, 3):
        raise ValueError('Phase diagram limited to binary or ternary systems')
    def bary_coords(comp: dict) -> tuple[float, float]:
        total = sum(comp.get(e, 0) for e in elements)
        if total == 0:
            return (0.0, 0.0)
        fracs = [comp.get(e, 0) / total for e in elements]
        if len(elements) == 2:
            return (fracs[0], 0.0)
        a, b, _ = fracs
        x = a + 0.5 * b
        y = (math.sqrt(3) / 2) * b
        return (x, y)
    points = []
    min_e, max_e = float('inf'), -float('inf')
    for entry in entries:
        comp = entry.get('composition')
        if not comp:
            continue
        x, y = bary_coords(comp)
        e = entry.get('energy_above_hull', 0)
        min_e = min(min_e, e)
        max_e = max(max_e, e)
        label = entry.get('material_id', '')
        points.append((x, y, e, label))
    if not points:
        raise ValueError('No valid entries for phase diagram')
    def energy_to_color(e: float) -> str:
        if max_e == min_e:
            ratio = 0.0
        else:
            ratio = (e - min_e) / (max_e - min_e)
        v = int(64 + (191 * (1 - ratio)))
        return f"#{v:02x}{v:02x}00"
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    pad = 0.1
    min_x, max_x = min(xs) - pad, max(xs) + pad
    min_y, max_y = min(ys) - pad, max(ys) + pad
    width, height = max_x - min_x, max_y - min_y
    svg = ET.Element('svg', xmlns='http://www.w3.org/2000/svg',
                     width=str(width * 200), height=str(height * 200),
                     viewBox=f"{min_x} {min_y} {width} {height}")
    ET.SubElement(svg, 'rect', x=str(min_x), y=str(min_y), width=str(width), height=str(height), fill='#202020')
    style = ET.SubElement(svg, 'style')
    style.text = "text{font-family:Arial,Helvetica,sans-serif;font-size:0.03px;fill:#fff}"
    for x, y, e, label in points:
        col = energy_to_color(e)
        ET.SubElement(svg, 'circle', cx=str(x), cy=str(y), r='0.02', fill=col, stroke='#fff', stroke_width='0.005')
        if label:
            ET.SubElement(svg, 'text', x=str(x + 0.02), y=str(y + 0.02)).text = label
    return ET.tostring(svg, encoding='unicode')

# ponytail: upgrade to interactive D3 plot, legend, axis labels.
