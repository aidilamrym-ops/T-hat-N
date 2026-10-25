# -*- coding: utf-8 -*-
"""t2n_illumina -- lightweight visualizer (F5/F6).

Provides SVG and HTML renderers for T‑hat‑N artefacts. No external deps;
stdlib only. Writes confined to `mcp/out/illumina/` via the write‑root
allowlist.
"""
import sys
import json
import os
import re
import math
import xml.etree.ElementTree as ET
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from core import guard
from core.skeleton import serve_generic

REPO_ROOT = Path(os.environ.get("T2N_REPO_ROOT")
                 or Path(__file__).resolve().parents[2]).resolve()

def _safe_name(text: str) -> str:
    return re.sub(r"[^A-Za-z0-9_\-]", "_", str(text))[:64]

# ---------------------------------------------------------------------
# Helper: generic SVG canvas
def _svg_canvas(width: int, height: int) -> ET.Element:
    return ET.Element("svg", attrib={"xmlns":"http://www.w3.org/2000/svg",
                                   "width":str(width),
                                   "height":str(height)})

# ---------------------------------------------------------------------
# Receipt label
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
# Dependency map
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
    defs = ET.SubElement(svg, "defs")
    marker = ET.SubElement(defs, "marker", attrib={"id":"arrow", "markerWidth":"10", "markerHeight":"7",
                                                    "refX":"0", "refY":"3", "orient":"auto"})
    ET.SubElement(marker, "polygon", attrib={"points":"0 0, 10 3, 0 6", "fill":"#555"})
    return {"schema": "t2n_illumina.deps.v1",
            "svg": ET.tostring(svg, encoding="unicode")}

# ---------------------------------------------------------------------
# Orbit plot
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
    for i in range(points):
        angle = 2 * math.pi * i / points
        x = cx + radius * math.cos(angle)
        y = cy + radius * math.sin(angle)
        ET.SubElement(svg, "circle", attrib={"cx":f"{x:.2f}", "cy":f"{y:.2f}", "r":"4",
                                             "fill":"#ff6666"})
    return {"schema": "t2n_illumina.orbit.v1",
            "svg": ET.tostring(svg, encoding="unicode")}

# ---------------------------------------------------------------------
# Materials dashboard – combines crystal and phase diagram SVGs
def render_materials_dashboard(params: dict) -> dict:
    """Render HTML dashboard with crystal structure and phase diagram.

    Expected params:
    - chemsys: chemical system for phase diagram (e.g. "Li-Fe-O")
    - material_id: material id for crystal SVG (e.g. "mp-149")
    - title: optional dashboard title
    """
    chemsys = params.get("chemsys")
    material_id = params.get("material_id")
    title = params.get("title", "Materials Dashboard")
    if not chemsys or not material_id:
        raise ValueError("chemsys and material_id required")
    # Query structure
    struct_res = materials.mp_query({
        "endpoint": "structure",
        "filters": {"material_ids": [material_id]},
        "save_json": False
    })
    if not struct_res.get("data"):
        raise RuntimeError("Structure fetch failed")
    struct_svg = visualize_materials.render_crystal_svg(struct_res["data"][0])
    # Query phase diagram entries
    pd_res = materials.mp_query({
        "endpoint": "phase_diagram",
        "filters": {"chemsys": chemsys, "fields": ["material_id", "composition", "energy_above_hull"]},
        "save_json": False
    })
    if not pd_res.get("data"):
        raise RuntimeError("Phase diagram fetch failed")
    pd_svg = visualize_materials.render_phase_diagram_svg(chemsys, pd_res["data"])
    sections = [
        {"header": "Crystal Structure", "content": struct_svg},
        {"header": f"Phase Diagram ({chemsys})", "content": pd_svg}
    ]
    return render_html_dashboard({"title": title, "sections": sections})

    title = params.get("title", "T2N Documentation Visual")
    sections = params.get("sections", [])
    if not isinstance(sections, list):
        raise ValueError("sections: must be a list of {header, content} objects")
    
    html_parts = [
        "<!DOCTYPE html>",
        "<html lang='id'>",
        "<head>",
        "  <meta charset='UTF-8'>",
        f"  <title>{title}</title>",
        "  <style>",
        "    body { font-family: ui-sans-serif, system-ui; background: #020617; color: #f1f5f9; margin: 0; padding: 2rem; line-height: 1.5; }",
        "    .container { max-width: 1200px; mx-auto: auto; }",
        "    header { border-bottom: 1px solid #1e293b; padding-bottom: 1rem; margin-bottom: 2rem; }",
        "    h1 { font-size: 1.875rem; font-weight: 700; color: #f8fafc; margin: 0; }",
        "    .section { background: #0f172a; border: 1px solid #1e293b; border-radius: 0.75rem; padding: 1.5rem; margin-bottom: 1.5rem; shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1); }",
        "    h2 { font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.1em; color: #94a3b8; margin-top: 0; margin-bottom: 1rem; border-bottom: 1px solid #334155; padding-bottom: 0.5rem; }",
        "    .content { font-family: ui-monospace, monospace; font-size: 0.875rem; white-space: pre-wrap; color: #cbd5e1; }",
        "    .formula { color: #818cf8; font-style: italic; }",
        "  </style>",
        "</head>",
        "<body>",
        "  <div class='container'>",
        "    <header>",
        f"      <h1>{title}</h1>",
        "    </header>",
        "    <main>"
    ]
    
    for sec in sections:
        header = str(sec.get("header", "Section"))
        content = str(sec.get("content", ""))
        is_json = False
        is_svg = False
        try:
            if content.lstrip().startswith('<svg'):
                is_svg = True
            elif content.startswith(('{', '[')):
                json_content = json.loads(content)
                content = json.dumps(json_content, indent=2)
                is_json = True
        except:
            pass
        
        html_parts.append("      <div class='section'>")
        html_parts.append(f"        <h2>{header}</h2>")
        if is_svg:
            html_parts.append(f"        <div class='content'>{content}</div>")
        else:
            html_parts.append(f"        <div class='content'>{'<pre>' if is_json else ''}{content}{'</pre>' if is_json else ''}</div>")
        html_parts.append("      </div>")
        
    html_parts.extend([
        "    </main>",
        "  </div>",
        "</body>",
        "</html>"
    ])
    
    html = "\n".join(html_parts)
    out_dir = Path(guard.write_roots()[0]) / "illumina"
    out_path = out_dir / f"{_safe_name(title)}.html"
    guard.make_dirs_writable(out_path)
    out_path.write_text(html, encoding="utf-8")
    
    return {
        "schema": "t2n_illumina.html.v1",
        "title": title,
        "path": str(out_path)
    }

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
    {"name": "render_html_dashboard",
     "description": "Render a rich HTML documentation dashboard for work results.",
     "inputSchema": {"type": "object",
                       "properties": {
                           "title": {"type": "string"},
                           "sections": {
                               "type": "array",
                               "items": {
                                   "type": "object",
                                   "properties": {
                                       "header": {"type": "string"},
                                       "content": {"type": "string"}
                                   },
                                   "required": ["header", "content"]
                               }
                           }
                       },
                       "required": ["sections"], "additionalProperties": False}},
]

HANDLERS = {
    "render_receipt_svg": render_receipt_svg,
    "render_dependency_svg": render_dependency_svg,
    "render_orbit_svg": render_orbit_svg,
    "render_html_dashboard": render_html_dashboard,
}

DESCRIPTION = ("T‑hat‑N illumina (F5/F6): SVG and HTML renderers – dashboard, receipt label, dependency map, and orbit plot. "
               "Stateless, stdlib only, writes to write‑root allowlist.")

if __name__ == "__main__":
    serve_generic("t2n_illumina", DESCRIPTION, TOOL_DEFS, HANDLERS)
