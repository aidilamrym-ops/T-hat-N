# -*- coding: utf-8 -*-
"""t2n_illumina -- lightweight visualizer (F5).

Provides simple SVG renderers for T‑hat‑N artefacts: receipt label, dependency
maps, and orbit plots. No external deps; stdlib only. Writes confined to
`mcp/out/illumina/` via the write‑root allowlist.
"""
import sys
import json
import xml.etree.ElementTree as ET
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from core.skeleton import serve_generic

# ---------------------------------------------------------------------
# Helper: generic SVG canvas
def _svg_canvas(width: int, height: int) -> ET.Element:
    return ET.Element("svg", attrib={"xmlns":"http://www.w3.org/2000/svg",
                                   "width":str(width),
                                   "height":str(height)})

# ---------------------------------------------------------------------
# Receipt label (unchanged)
def _receipt_svg(receipt: dict) -> str:
    rid = receipt.get("id", "unknown")
    svg = _svg_canvas(200, 100)
    ET.SubElement(svg, "rect", attrib={"x":"10", "y":"10", "width":"180",
                                         "height":"80", "fill":"#f0f0f0",
                                         "stroke":"#333", "stroke-width":"2"})
    txt = ET.SubElement(svg, "text", attrib={"x":"100", "y":"55",
                                             "font-family":"sans-serif",
                                             "font-size":"14",
                                             "text-anchor":"middle",
                                             "fill":"#000"})
    txt.text = f"Receipt: {rid}"
    return ET.tostring(svg, encoding="unicode")

def render_receipt_svg(params: dict) -> dict:
    receipt = params.get("receipt")
    if isinstance(receipt, str):
        p = Path(receipt)
        if not p.is_file():
            raise FileNotFoundError(str(receipt))
        receipt = json.loads(p.read_text(encoding="utf-8"))
    if not isinstance(receipt, dict):
        raise ValueError("receipt: object or JSON path required")
    return {"schema": "t2n_illumina.svg.v1",
            "receipt_id": receipt.get("id"),
            "svg": _receipt_svg(receipt)}

# ---------------------------------------------------------------------
# Dependency map – simple linear layout of nodes and arrows
def render_dependency_svg(params: dict) -> dict:
    graph = params.get("graph") or {}
    nodes = graph.get("nodes", [])
    edges = graph.get("edges", [])
    if not isinstance(nodes, list) or not isinstance(edges, list):
        raise ValueError("graph: nodes list and edges list required")
    spacing = 120
    radius = 20
    width = max(200, spacing * len(nodes))
    height = 150
    svg = _svg_canvas(width, height)
    # draw nodes
    for i, nid in enumerate(nodes):
        cx = 60 + i * spacing
        cy = 75
        ET.SubElement(svg, "circle", attrib={"cx":str(cx), "cy":str(cy),
                                             "r":str(radius), "fill":"#e0e0ff",
                                             "stroke":"#000", "stroke-width":"1"})
        txt = ET.SubElement(svg, "text", attrib={"x":str(cx), "y":str(cy+5),
                                                 "font-family":"sans-serif",
                                                 "font-size":"12",
                                                 "text-anchor":"middle",
                                                 "fill":"#000"})
        txt.text = str(nid)
    # draw edges as simple lines
    for src, dst in edges:
        if src not in nodes or dst not in nodes:
            continue
        i_src = nodes.index(src)
        i_dst = nodes.index(dst)
        x1 = 60 + i_src * spacing + radius
        x2 = 60 + i_dst * spacing - radius
        y = 75
        ET.SubElement(svg, "line", attrib={"x1":str(x1), "y1":str(y),
                                            "x2":str(x2), "y2":str(y),
                                            "stroke":"#555", "stroke-width":"2",
                                            "marker-end":"url(#arrow)"})
    # define arrow marker
    defs = ET.SubElement(svg, "defs")
    marker = ET.SubElement(defs, "marker", attrib={"id":"arrow", "markerWidth":"10", "markerHeight":"7",
                                                    "refX":"0", "refY":"3", "orient":"auto"})
    ET.SubElement(marker, "polygon", attrib={"points":"0 0, 10 3, 0 6", "fill":"#555"})
    return {"schema": "t2n_illumina.deps.v1",
            "svg": ET.tostring(svg, encoding="unicode")}

# ---------------------------------------------------------------------
# Orbit plot – points on circle
def render_orbit_svg(params: dict) -> dict:
    radius = int(params.get("radius", 60))
    points = int(params.get("points", 8))
    if points <= 0:
        raise ValueError("points must be positive")
    size = radius * 2 + 40
    svg = _svg_canvas(size, size)
    cx = cy = size // 2
    ET.SubElement(svg, "circle", attrib={"cx":str(cx), "cy":str(cy), "r":str(radius),
                                          "fill":"none", "stroke":"#333", "stroke-width":"2"})
    import math
    for i in range(points):
        angle = 2 * math.pi * i / points
        x = cx + radius * math.cos(angle)
        y = cy + radius * math.sin(angle)
        ET.SubElement(svg, "circle", attrib={"cx":f"{x:.2f}", "cy":f"{y:.2f}", "r":"4",
                                             "fill":"#ff6666"})
    return {"schema": "t2n_illumina.orbit.v1",
            "svg": ET.tostring(svg, encoding="unicode")}

# ---------------------------------------------------------------------
TOOL_DEFS = [
    {"name": "render_receipt_svg",
     "description": "Render tiny SVG box labeling receipt.id.",
     "inputSchema": {"type": "object",
                       "properties": {"receipt": {"type": ["object", "string"]}},
                       "required": [], "additionalProperties": False}},
    {"name": "render_dependency_svg",
     "description": "Render simple dependency map SVG from nodes list and edges list.",
     "inputSchema": {"type": "object",
                       "properties": {"graph": {"type": "object"}},
                       "required": ["graph"], "additionalProperties": False}},
    {"name": "render_orbit_svg",
     "description": "Render orbit plot SVG: points equally spaced on a circle.",
     "inputSchema": {"type": "object",
                       "properties": {"radius": {"type": "integer"},
                                      "points": {"type": "integer"}},
                       "required": [], "additionalProperties": False}},
]

HANDLERS = {
    "render_receipt_svg": render_receipt_svg,
    "render_dependency_svg": render_dependency_svg,
    "render_orbit_svg": render_orbit_svg,
}

DESCRIPTION = ("T‑hat‑N illumina (F5): SVG renderers – receipt label, simple dependency map, and orbit plot. "
               "Stateless, stdlib only, writes to write‑root allowlist.")

if __name__ == "__main__":
    serve_generic("t2n_illumina", DESCRIPTION, TOOL_DEFS, HANDLERS)

