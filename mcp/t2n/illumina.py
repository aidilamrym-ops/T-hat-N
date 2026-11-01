# -*- coding: utf-8 -*-
"""t2n_illumina -- lightweight visualizer (F5/F6).

Provides SVG and HTML renderers for Tâ€‘hatâ€‘N artefacts. No external deps;
stdlib only. Writes confined to `mcp/out/illumina/` via the writeâ€‘root
allowlist.
"""
import sys
import json
import os
import re
import math
import html as html_mod
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
                                   "height":str(height),
                                   "viewBox":f"0 0 {width} {height}"})


# Node geometry shared by the graph renderers.
_NODE_W = 168
_NODE_H = 44
_NODE_GAP_X = 30
_NODE_GAP_Y = 28

_STATUS_COLORS = {
    "PASS": ("#dcfce7", "#16a34a"),
    "CERTIFIED": ("#dcfce7", "#16a34a"),
    "OK": ("#dcfce7", "#16a34a"),
    "TRUE": ("#dcfce7", "#16a34a"),
    "FAIL": ("#fee2e2", "#dc2626"),
    "FAILED": ("#fee2e2", "#dc2626"),
    "ERROR": ("#fee2e2", "#dc2626"),
    "FALSE": ("#fee2e2", "#dc2626"),
    "NOT_VERIFIED": ("#fef3c7", "#d97706"),
    "NOT_RUN": ("#fef3c7", "#d97706"),
    "UNAVAILABLE": ("#fef3c7", "#d97706"),
    "UNAVAILABLE_NON_PRIMITIVE": ("#fef3c7", "#d97706"),
    "REJECTED": ("#fef3c7", "#d97706"),
    "PARTIAL_PASS": ("#fef3c7", "#d97706"),
    "PARTIAL": ("#fef3c7", "#d97706"),
    "INFO": ("#e2e8f0", "#475569"),
}


def _status_colors(status: str) -> tuple[str, str]:
    return _STATUS_COLORS.get(str(status).upper(), ("#e2e8f0", "#475569"))


def _node_id(node: object) -> str:
    if isinstance(node, dict):
        return str(node.get("id") or node.get("label") or "")
    return str(node)


def _node_label(node: object) -> str:
    if isinstance(node, dict):
        return str(node.get("label") or node.get("id") or "")
    return str(node)


def _truncate(text: str, limit: int = 26) -> str:
    text = str(text)
    return text if len(text) <= limit else text[: limit - 1] + "\u2026"


def _edge_pair(edge: object) -> tuple[str, str]:
    if isinstance(edge, dict):
        src = edge.get("source", edge.get("src", edge.get("from")))
        dst = edge.get("target", edge.get("dst", edge.get("to")))
    elif isinstance(edge, (list, tuple)) and len(edge) >= 2:
        src, dst = edge[0], edge[1]
    else:
        raise ValueError(f"edge must be a pair or object, got {edge!r}")
    if src is None or dst is None:
        raise ValueError(f"edge needs source and target, got {edge!r}")
    return str(src), str(dst)


def _add_arrow_defs(svg: ET.Element) -> None:
    defs = ET.SubElement(svg, "defs")
    marker = ET.SubElement(defs, "marker", attrib={
        "id": "arrow", "markerWidth": "9", "markerHeight": "7",
        "refX": "8", "refY": "3.5", "orient": "auto",
        "markerUnits": "strokeWidth"})
    ET.SubElement(marker, "polygon", attrib={
        "points": "0 0, 9 3.5, 0 7", "fill": "#64748b"})


def _add_box(svg: ET.Element, x: float, y: float, w: float, h: float,
             label: str, status: str = "INFO", sublabel: str = "") -> None:
    fill, stroke = _status_colors(status)
    ET.SubElement(svg, "rect", attrib={
        "x": f"{x:.1f}", "y": f"{y:.1f}", "width": f"{w:.1f}",
        "height": f"{h:.1f}", "rx": "8", "ry": "8",
        "fill": fill, "stroke": stroke, "stroke-width": "1.6"})
    text = ET.SubElement(svg, "text", attrib={
        "x": f"{x + w / 2:.1f}", "y": f"{y + (h / 2 - 3 if sublabel else h / 2 + 4):.1f}",
        "font-family": "ui-sans-serif, system-ui, sans-serif",
        "font-size": "11", "text-anchor": "middle", "fill": "#0f172a"})
    text.text = _truncate(label)
    if sublabel:
        sub = ET.SubElement(svg, "text", attrib={
            "x": f"{x + w / 2:.1f}", "y": f"{y + h / 2 + 11:.1f}",
            "font-family": "ui-monospace, monospace", "font-size": "9",
            "text-anchor": "middle", "fill": "#475569"})
        sub.text = _truncate(sublabel, 30)


def _add_edge(svg: ET.Element, a: tuple[float, float],
              b: tuple[float, float]) -> None:
    ET.SubElement(svg, "line", attrib={
        "x1": f"{a[0]:.1f}", "y1": f"{a[1]:.1f}",
        "x2": f"{b[0]:.1f}", "y2": f"{b[1]:.1f}",
        "stroke": "#64748b", "stroke-width": "1.6", "marker-end": "url(#arrow)"})

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
# Dependency map (single row or layered DAG)
def render_dependency_svg(params: dict) -> dict:
    """Render a dependency map.

    Accepts the original single-row contract (``nodes`` are strings) and the
    layered form used by the Chrono knowledge graph: ``nodes`` are objects
    with ``id``, optional ``layer``, ``label`` and ``status``. Nodes sharing a
    layer are drawn in one column; edges may be pairs or
    ``{source, target}`` objects.
    """
    graph = params.get("graph") or {}
    nodes = graph.get("nodes", [])
    edges = graph.get("edges", [])
    if not isinstance(nodes, list) or not isinstance(edges, list):
        raise ValueError("graph: nodes list and edges list required")
    if not nodes:
        raise ValueError("graph: at least one node required")

    ids = [_node_id(node) for node in nodes]
    if any(not nid for nid in ids):
        raise ValueError("graph: every node needs an id")
    if len(set(ids)) != len(ids):
        raise ValueError("graph: node ids must be unique")
    by_id = dict(zip(ids, nodes))

    layers: dict[int, list[str]] = {}
    for node, nid in zip(nodes, ids):
        raw_layer = node.get("layer", 0) if isinstance(node, dict) else 0
        try:
            layer = int(raw_layer)
        except (TypeError, ValueError) as exc:
            raise ValueError(f"graph: node {nid!r} has a non-integer layer") from exc
        layers.setdefault(layer, []).append(nid)

    ordered_layers = sorted(layers)
    max_rows = max(len(column) for column in layers.values())
    col_w = _NODE_W + _NODE_GAP_X + 46
    row_h = _NODE_H + _NODE_GAP_Y
    width = max(260, 60 + col_w * len(ordered_layers))
    height = max(160, 60 + row_h * max_rows)

    positions: dict[str, tuple[float, float]] = {}
    for column_index, layer in enumerate(ordered_layers):
        column = layers[layer]
        offset = (max_rows - len(column)) * row_h / 2
        for row_index, nid in enumerate(column):
            x = 40 + column_index * col_w
            y = 34 + offset + row_index * row_h
            positions[nid] = (x, y)

    svg = _svg_canvas(int(width), int(height))
    _add_arrow_defs(svg)

    valid_edges = []
    for edge in edges:
        src, dst = _edge_pair(edge)
        if src in positions and dst in positions:
            valid_edges.append((src, dst))

    for src, dst in valid_edges:
        sx, sy = positions[src]
        dx, dy = positions[dst]
        if abs(sx - dx) < 1:  # same column: route vertically
            a = (sx + _NODE_W / 2, sy + (_NODE_H if dy > sy else 0))
            b = (dx + _NODE_W / 2, dy + (0 if dy > sy else _NODE_H))
        elif dx > sx:  # forward column
            a = (sx + _NODE_W, sy + _NODE_H / 2)
            b = (dx, dy + _NODE_H / 2)
        else:  # backward column
            a = (sx, sy + _NODE_H / 2)
            b = (dx + _NODE_W, dy + _NODE_H / 2)
        _add_edge(svg, a, b)

    for nid in ids:
        node = by_id[nid]
        x, y = positions[nid]
        status = str(node.get("status", "INFO")) if isinstance(node, dict) else "INFO"
        layer = node.get("layer", 0) if isinstance(node, dict) else 0
        _add_box(svg, x, y, _NODE_W, _NODE_H, _node_label(node),
                 status=status, sublabel=f"layer {layer}")

    return {"schema": "t2n_illumina.deps.v2",
            "node_count": len(ids),
            "edge_count": len(valid_edges),
            "layers": ordered_layers,
            "svg": ET.tostring(svg, encoding="unicode")}


# ---------------------------------------------------------------------
# Orbit plot (legacy ring or root-pulling node graph)
def _orbit_legacy(params: dict) -> dict:
    radius = int(params.get("radius", 60))
    points = int(params.get("points", 8))
    if points <= 0:
        raise ValueError("points must be positive")
    if radius <= 0:
        raise ValueError("radius must be positive")
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
            "mode": "ring",
            "svg": ET.tostring(svg, encoding="unicode")}


def _orbit_root_pulling(params: dict) -> dict:
    nodes_raw = params["nodes"]
    if not isinstance(nodes_raw, list) or not nodes_raw:
        raise ValueError("orbit: nodes must be a non-empty list")
    if not all(isinstance(node, dict) for node in nodes_raw):
        raise ValueError("orbit: every node must be an object")

    ids = [_node_id(node) for node in nodes_raw]
    if any(not nid for nid in ids):
        raise ValueError("orbit: every node needs an id")
    if len(set(ids)) != len(ids):
        raise ValueError("orbit: node ids must be unique")
    by_id = dict(zip(ids, nodes_raw))

    root = params.get("root")
    if root is None:
        roots = [nid for nid in ids if not by_id[nid].get("parent")]
        if not roots:
            raise ValueError("orbit: root is required when no node has a null parent")
        root = roots[0]
    root = str(root)
    if root not in by_id:
        raise ValueError(f"orbit: root {root!r} is not a node")

    children: dict[str, list[str]] = {nid: [] for nid in ids}
    for nid in ids:
        if nid == root:
            continue
        parent = by_id[nid].get("parent")
        if parent is None:
            continue
        parent = str(parent)
        if parent not in children:
            raise ValueError(f"orbit: node {nid!r} points at missing parent {parent!r}")
        children[parent].append(nid)

    # Breadth-first depth from the root; anything detached is parked on an
    # extra outer ring so it is still visible and honestly marked detached.
    depth: dict[str, int] = {root: 0}
    queue = [root]
    while queue:
        current = queue.pop(0)
        for child in children[current]:
            if child in depth:
                # A second parent (DAG) or an unreachable cycle: keep the
                # first, shallowest placement instead of inventing an orbit.
                continue
            depth[child] = depth[current] + 1
            queue.append(child)
    detached = [nid for nid in ids if nid not in depth]
    max_depth = max(depth.values(), default=0)
    for nid in detached:
        depth[nid] = max_depth + 1

    base_radius = float(params.get("radius", 70))
    ring_step = float(params.get("ring_step", 96))
    if base_radius <= 0 or ring_step <= 0:
        raise ValueError("orbit: radius and ring_step must be positive")
    max_ring = max(depth.values(), default=0)
    pad = 70
    size = int(2 * (base_radius + ring_step * max_ring) + 2 * pad)
    centre = size / 2

    rings: dict[int, list[str]] = {}
    for nid in ids:
        rings.setdefault(depth[nid], []).append(nid)

    positions: dict[str, tuple[float, float]] = {root: (centre, centre)}
    for ring, members in rings.items():
        if ring == 0:
            continue
        radius = base_radius + ring_step * (ring - 1)
        # Stagger rings so parent/child edges do not overlap on the same ray.
        offset = (ring % 2) * math.pi / max(len(members), 1)
        for index, nid in enumerate(members):
            angle = 2 * math.pi * index / len(members) + offset
            positions[nid] = (centre + radius * math.cos(angle),
                              centre + radius * math.sin(angle))

    svg = _svg_canvas(size, size)
    _add_arrow_defs(svg)

    # Guide rings, drawn first.
    for ring in sorted(rings):
        if ring == 0:
            continue
        radius = base_radius + ring_step * (ring - 1)
        ET.SubElement(svg, "circle", attrib={
            "cx": f"{centre:.1f}", "cy": f"{centre:.1f}", "r": f"{radius:.1f}",
            "fill": "none", "stroke": "#334155", "stroke-width": "0.8",
            "stroke-dasharray": "4 6", "opacity": "0.55"})

    for nid in ids:
        parent = by_id[nid].get("parent")
        if parent is None or nid == root:
            continue
        parent = str(parent)
        if parent in positions and nid in positions:
            _add_edge(svg, positions[parent], positions[nid])

    for nid in ids:
        node = by_id[nid]
        cx, cy = positions[nid]
        status = str(node.get("status", "INFO"))
        fill, stroke = _status_colors(status)
        radius = 13 if nid == root else float(node.get("size", 7))
        ET.SubElement(svg, "circle", attrib={
            "cx": f"{cx:.1f}", "cy": f"{cy:.1f}", "r": f"{radius:.1f}",
            "fill": fill, "stroke": stroke, "stroke-width": "1.8"})
        label = _node_label(node)
        anchor = "middle"
        tx, ty = cx, cy - radius - 6
        if nid != root and abs(cx - centre) > 1:
            anchor = "start" if cx > centre else "end"
            tx = cx + (radius + 5) * (1 if cx > centre else -1)
            ty = cy + 3
        text = ET.SubElement(svg, "text", attrib={
            "x": f"{tx:.1f}", "y": f"{ty:.1f}",
            "font-family": "ui-sans-serif, system-ui, sans-serif",
            "font-size": "10", "text-anchor": anchor, "fill": "#0f172a"})
        text.text = _truncate(label, 28)
        if nid == root:
            caption = ET.SubElement(svg, "text", attrib={
                "x": f"{cx:.1f}", "y": f"{cy + radius + 15:.1f}",
                "font-family": "ui-monospace, monospace", "font-size": "9",
                "text-anchor": "middle", "fill": "#475569"})
            caption.text = "root"

    return {"schema": "t2n_illumina.orbit.v2",
            "mode": "root_pulling",
            "root": root,
            "node_count": len(ids),
            "max_depth": max(depth.values(), default=0),
            "detached": detached,
            "svg": ET.tostring(svg, encoding="unicode")}


def render_orbit_svg(params: dict) -> dict:
    """Render either the legacy ring or a root-pulling orbit graph.

    Legacy form: ``{radius, points}`` -> equally spaced points on one circle.
    Graph form: ``{root, nodes:[{id,parent,label,status}]}`` -> nodes pulled
    onto rings by breadth-first distance from the root.
    """
    if params.get("nodes") is None:
        return _orbit_legacy(params)
    return _orbit_root_pulling(params)


# ---------------------------------------------------------------------
# Functional gate tree
def _gate_graph(params: dict) -> tuple[dict[str, dict], list[str]]:
    tree = params.get("tree")
    gates = params.get("gates")

    if tree is not None and gates is not None:
        raise ValueError("gate tree: provide either tree or gates, not both")

    nodes: dict[str, dict] = {}
    order: list[str] = []

    if tree is not None:
        if not isinstance(tree, dict):
            raise ValueError("gate tree: tree must be an object")

        def walk(spec: dict, parent: str | None, ancestors: frozenset[str]) -> str:
            nid = str(spec.get("id") or spec.get("label") or "")
            if not nid:
                raise ValueError("gate tree: every node needs an id or label")
            if nid in nodes:
                raise ValueError(f"gate tree: duplicate gate id {nid!r}")
            if nid in ancestors:
                raise ValueError(f"gate tree: cycle at gate {nid!r}")
            nodes[nid] = {
                "id": nid,
                "label": str(spec.get("label") or nid),
                "status": str(spec.get("status") or "INFO"),
                "parent": parent,
                "children": [],
            }
            order.append(nid)
            raw_children = spec.get("children") or []
            if not isinstance(raw_children, list):
                raise ValueError(f"gate tree: children of {nid!r} must be a list")
            for child in raw_children:
                if not isinstance(child, dict):
                    raise ValueError(
                        f"gate tree: children of {nid!r} must be objects")
                child_id = walk(child, nid, ancestors | {nid})
                nodes[nid]["children"].append(child_id)
            return nid

        root = walk(tree, None, frozenset())
        return nodes, [root]

    if gates is not None:
        if not isinstance(gates, list) or not gates:
            raise ValueError("gate tree: gates must be a non-empty list")
        for spec in gates:
            if not isinstance(spec, dict):
                raise ValueError("gate tree: every gate must be an object")
            nid = str(spec.get("id") or spec.get("label") or "")
            if not nid:
                raise ValueError("gate tree: every gate needs an id or label")
            if nid in nodes:
                raise ValueError(f"gate tree: duplicate gate id {nid!r}")
            nodes[nid] = {
                "id": nid,
                "label": str(spec.get("label") or nid),
                "status": str(spec.get("status") or "INFO"),
                "parent": None if spec.get("parent") is None else str(spec["parent"]),
                "children": [],
            }
            order.append(nid)
        for nid in order:
            parent = nodes[nid]["parent"]
            if parent is None:
                continue
            if parent not in nodes:
                raise ValueError(
                    f"gate tree: gate {nid!r} points at missing parent {parent!r}")
            nodes[parent]["children"].append(nid)
        # Drop parent links that form a cycle back onto the node itself.
        for nid in order:
            if nodes[nid]["parent"] == nid:
                raise ValueError(f"gate tree: gate {nid!r} is its own parent")
        roots = [nid for nid in order if nodes[nid]["parent"] is None]
        if not roots:
            raise ValueError("gate tree: at least one gate must have no parent")
        return nodes, roots

    raise ValueError("gate tree: tree or gates required")


def render_gate_tree_svg(params: dict) -> dict:
    """Render a functional gate tree as a layered SVG.

    Accepts either a nested ``tree`` object or a flat ``gates`` list where each
    gate carries an optional ``parent`` id. Gate status drives the fill colour
    (PASS/CERTIFIED green, FAIL red, NOT_VERIFIED/NOT_RUN amber, INFO slate).
    """
    nodes, roots = _gate_graph(params)

    positions: dict[str, tuple[float, int]] = {}
    cursor = [0.0]
    max_depth = [0]
    placed: set[str] = set()

    def place(nid: str, depth: int, ancestors: frozenset[str]) -> tuple[float, int]:
        if nid in ancestors:
            raise ValueError(f"gate tree: cycle at gate {nid!r}")
        if nid in placed:
            x, y = positions[nid]
            return x, y
        max_depth[0] = max(max_depth[0], depth)
        children = [c for c in nodes[nid]["children"] if c in nodes]
        if not children:
            x = cursor[0]
            cursor[0] += _NODE_W + _NODE_GAP_X
        else:
            child_positions = [
                place(child, depth + 1, ancestors | {nid}) for child in children
            ]
            xs = [position[0] for position in child_positions]
            x = (min(xs) + max(xs)) / 2
        positions[nid] = (x, depth)
        placed.add(nid)
        return x, depth

    for root in roots:
        place(root, 0, frozenset())
        cursor[0] += _NODE_GAP_X * 2

    unplaced = [nid for nid in nodes if nid not in placed]
    if unplaced:
        raise ValueError(
            "gate tree: unplaced gates (parent cycle?): " + ", ".join(unplaced))

    row_h = _NODE_H + _NODE_GAP_Y + 10
    width = max(260, int(cursor[0] + 30))
    height = max(160, 70 + row_h * (max_depth[0] + 1))
    svg = _svg_canvas(width, height)
    _add_arrow_defs(svg)

    for nid in [n for n in nodes if n in placed]:
        parent = nodes[nid]["parent"]
        if parent is None or parent not in positions:
            continue
        px, py = positions[parent]
        cx, cy = positions[nid]
        _add_edge(svg, (px + _NODE_W / 2, py + _NODE_H),
                  (cx + _NODE_W / 2, cy))

    for nid in nodes:
        if nid not in positions:
            continue
        x, depth = positions[nid]
        node = nodes[nid]
        _add_box(svg, x, 34 + depth * row_h, _NODE_W, _NODE_H,
                 node["label"], status=node["status"], sublabel=node["status"])

    return {
        "schema": "t2n_illumina.gate_tree.v1",
        "gate_count": len(nodes),
        "roots": roots,
        "max_depth": max_depth[0],
        "status_counts": {
            status: sum(1 for n in nodes.values() if n["status"] == status)
            for status in sorted({n["status"] for n in nodes.values()})
        },
        "svg": ET.tostring(svg, encoding="unicode"),
    }


def render_materials_dashboard(params: dict) -> dict:
    """Render HTML dashboard with crystal structure and phase diagram.

    Expected params:
    - chemsys: chemical system for phase diagram (e.g. "Li-Fe-O")
    - material_id: material id for crystal SVG (e.g. "mp-149")
    - title: optional dashboard title
    """
    from t2n import materials, visualize_materials

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


def render_html_dashboard(params: dict) -> dict:
    """Render a standalone HTML dashboard into the illumina write root.

    The output is deliberately self-contained: inline CSS only, no external
    script, font, CDN, image source, or ``@import``. Inline SVG keeps its
    geometry but drops the XML namespace, which is a namespace identifier
    rather than a fetched resource.
    """
    title = str(params.get("title", "T2N Documentation Visual"))
    sections = params.get("sections", [])
    if not isinstance(sections, list):
        raise ValueError("sections: must be a list of {header, content} objects")

    html_parts = [
        "<!DOCTYPE html>",
        "<html lang='id'>",
        "<head>",
        "  <meta charset='UTF-8'>",
        f"  <title>{html_mod.escape(title)}</title>",
        "  <style>",
        "    body { font-family: ui-sans-serif, system-ui, sans-serif; background: #020617; color: #f1f5f9; margin: 0; padding: 2rem; line-height: 1.5; }",
        "    .container { max-width: 1200px; margin: 0 auto; }",
        "    header { border-bottom: 1px solid #1e293b; padding-bottom: 1rem; margin-bottom: 2rem; }",
        "    h1 { font-size: 1.875rem; font-weight: 700; color: #f8fafc; margin: 0; }",
        "    .section { background: #0f172a; border: 1px solid #1e293b; border-radius: 0.75rem; padding: 1.5rem; margin-bottom: 1.5rem; }",
        "    h2 { font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.1em; color: #94a3b8; margin-top: 0; margin-bottom: 1rem; border-bottom: 1px solid #334155; padding-bottom: 0.5rem; }",
        "    .content { font-family: ui-monospace, monospace; font-size: 0.875rem; white-space: pre-wrap; color: #cbd5e1; overflow-x: auto; }",
        "    .content svg { max-width: 100%; height: auto; background: #f8fafc; border-radius: 0.5rem; }",
        "    pre { margin: 0; }",
        "  </style>",
        "</head>",
        "<body>",
        "  <div class='container'>",
        "    <header>",
        f"      <h1>{html_mod.escape(title)}</h1>",
        "    </header>",
        "    <main>"
    ]

    for sec in sections:
        if not isinstance(sec, dict):
            raise ValueError("sections: every section must be an object")
        header = str(sec.get("header", "Section"))
        content = str(sec.get("content", ""))
        is_json = False
        is_svg = False
        stripped = content.lstrip()
        if stripped.startswith("<svg"):
            is_svg = True
            content = re.sub(
                r'\s+xmlns="http://www\.w3\.org/2000/svg"', "", content)
        elif stripped.startswith(("{", "[")):
            try:
                content = json.dumps(json.loads(content), indent=2)
                is_json = True
            except (TypeError, ValueError):
                is_json = False

        html_parts.append("      <div class='section'>")
        html_parts.append(f"        <h2>{html_mod.escape(header)}</h2>")
        if is_svg:
            html_parts.append(f"        <div class='content'>{content}</div>")
        elif is_json:
            html_parts.append(
                f"        <div class='content'><pre>{html_mod.escape(content)}</pre></div>")
        else:
            html_parts.append(
                f"        <div class='content'>{html_mod.escape(content)}</div>")
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
        "schema": "t2n_illumina.html.v2",
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
     "description": "Render a dependency map SVG from a nodes/edges graph; nodes may declare a layer for a layered column layout.",
     "inputSchema": {"type": "object",
                       "properties": {"graph": {"type": "object"}},
                       "required": ["graph"], "additionalProperties": False}},
    {"name": "render_orbit_svg",
     "description": "Render an orbit SVG: either equally spaced points on one circle, or a root-pulling graph laid out by distance from a root node.",
     "inputSchema": {"type": "object",
                       "properties": {"radius": {"type": "integer"},
                                      "points": {"type": "integer"},
                                      "ring_step": {"type": "integer"},
                                      "root": {"type": "string"},
                                      "nodes": {"type": "array",
                                                "items": {"type": "object"}}},
                       "required": [], "additionalProperties": False}},
    {"name": "render_gate_tree_svg",
     "description": "Render a functional gate tree SVG from a nested tree object or a flat gates list with parent ids.",
     "inputSchema": {"type": "object",
                       "properties": {"tree": {"type": "object"},
                                      "gates": {"type": "array",
                                                "items": {"type": "object"}}},
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
    "render_gate_tree_svg": render_gate_tree_svg,
    "render_html_dashboard": render_html_dashboard,
}

DESCRIPTION = ("T\u2011hat\u2011N illumina (F5/F6): SVG and HTML renderers \u2013 dashboard, receipt label, "
               "layered dependency map, root-pulling orbit, and functional gate tree. "
               "Stateless, stdlib only, writes to write\u2011root allowlist.")

if __name__ == "__main__":
    serve_generic("t2n_illumina", DESCRIPTION, TOOL_DEFS, HANDLERS)


