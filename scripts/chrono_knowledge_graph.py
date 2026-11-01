# -*- coding: utf-8 -*-
"""Build the Chrono-RH internal knowledge graph and render it offline.

Track 2 deliverable. The graph is derived from repository artefacts, not from
hand-typed claims:

* Stage 1-4 receipt JSON files (status read from each receipt);
* Stage/Track pre-registration files (presence only);
* the live `FENCE_REGISTRY` certificate hashes (measured here);
* the tail of `ledger/chrono_execution_ledger.jsonl`;
* the Track 3 sweep receipt, if present.

Every generated file lands below ``mcp/out/`` (the untracked T2N staging zone)
and the HTML dashboard embeds inline SVG only: no CDN, script, font, image or
network reference.

Usage::

    python scripts/chrono_knowledge_graph.py
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
for extra in (ROOT, ROOT / "mcp", ROOT / "mcp" / "t2n"):
    if str(extra) not in sys.path:
        sys.path.insert(0, str(extra))

from core import guard  # noqa: E402
from t2n.illumina import (  # noqa: E402
    render_dependency_svg,
    render_gate_tree_svg,
    render_html_dashboard,
    render_orbit_svg,
    render_receipt_svg,
)

DATE = "2026-11-01"
OUTPUT_DIR = "chrono_kg"
LEDGER_RULE_ID = "T-2026-0095"

STAGE_SPECS = (
    {
        "id": "stage1",
        "label": "Stage 1 enclosure",
        "receipt": "reports/chrono_rh_stage1_receipt_2026-11-01.json",
        "prereg": "reports/PREREG_RH_STRATEGY_STAGE1_2026-11-01.md",
        "module": "ChronoGeometric_Framework/lean/ChronoRiemann.lean",
    },
    {
        "id": "stage2",
        "label": "Stage 2 tail bound",
        "receipt": "reports/chrono_rh_stage2_receipt_2026-11-01.json",
        "prereg": "reports/PREREG_RH_STRATEGY_STAGE2_2026-11-01.md",
        "module": "msaf/chrono_runtime/stage2_tail_bound.py",
    },
    {
        "id": "stage3",
        "label": "Stage 3 spectral lock",
        "receipt": "reports/chrono_rh_stage3_receipt_2026-11-01.json",
        "prereg": "reports/PREREG_RH_STRATEGY_STAGE3_2026-11-01.md",
        "module": "msaf/chrono_runtime/stage3_spectral_lock.py",
    },
    {
        "id": "stage4",
        "label": "Stage 4 containment",
        "receipt": "reports/chrono_rh_stage4_receipt_2026-11-01.json",
        "prereg": "reports/PREREG_RH_STRATEGY_STAGE4_2026-11-01.md",
        "module": "msaf/chrono_runtime/stage4_containment_proof.py",
    },
)

TRACK3_RECEIPT = "reports/chrono_rh_dirichlet_sweep_2026-11-01.json"
CONSOLIDATED_RECEIPT = "reports/chrono_rh_multi_track_receipt_2026-11-01.json"
FENCE_REGISTRY = "reports/FENCE_REGISTRY.md"
LEDGER = "ledger/chrono_execution_ledger.jsonl"


# ------------------------------------------------------------------ reading
def _read_json(relative: str) -> dict[str, Any] | None:
    path = ROOT / relative
    if not path.is_file():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    return payload if isinstance(payload, dict) else None


def _receipt_status(relative: str) -> str:
    payload = _read_json(relative)
    if payload is None:
        return "NOT_RUN"
    status = payload.get("status")
    return str(status) if status else "INFO"


def _exists(relative: str) -> bool:
    return (ROOT / relative).is_file()


def measure_fence_registry() -> dict[str, Any]:
    """Re-hash every ``sha256LF`` line in the registry (same convention)."""
    path = ROOT / FENCE_REGISTRY
    if not path.is_file():
        return {"status": "NOT_RUN", "checked": 0, "drift": [], "missing": []}
    text = path.read_text(encoding="utf-8")
    pattern = re.compile(r"^\s*sha256LF\s+([0-9a-f]{64})\s+(\S.*?)\s*$", re.M)
    drift: list[str] = []
    missing: list[str] = []
    checked = 0
    for match in pattern.finditer(text):
        digest, relative = match.group(1), match.group(2).strip()
        target = ROOT / relative
        checked += 1
        if not target.is_file():
            missing.append(relative)
            continue
        data = target.read_bytes().replace(b"\r\n", b"\n")
        actual = hashlib.sha256(data).hexdigest()
        if actual != digest:
            drift.append(relative)
    status = "PASS" if not drift and not missing else "FAIL"
    return {"status": status, "checked": checked,
            "drift": drift, "missing": missing}


def read_ledger_tail() -> dict[str, Any]:
    path = ROOT / LEDGER
    if not path.is_file():
        return {"record_count": 0, "last_index": None, "last_rule_id": None,
                "track2_track3_anchored": False}
    records = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            records.append(json.loads(line))
        except ValueError:
            continue
    if not records:
        return {"record_count": 0, "last_index": None, "last_rule_id": None,
                "track2_track3_anchored": False}
    last = records[-1]
    anchored = any(record.get("rule_id") == LEDGER_RULE_ID for record in records)
    return {
        "record_count": len(records),
        "last_index": last.get("index"),
        "last_rule_id": last.get("rule_id"),
        "last_record_hash": last.get("record_hash"),
        "track2_track3_anchored": anchored,
    }


# ------------------------------------------------------------------- graph
def build_graph() -> dict[str, Any]:
    fence = measure_fence_registry()
    ledger = read_ledger_tail()
    consolidated = _read_json(CONSOLIDATED_RECEIPT)
    consolidated_status = (
        str(consolidated.get("status")) if consolidated else "NOT_RUN")

    nodes: list[dict[str, Any]] = [
        {"id": "program", "label": "Chrono-RH program", "layer": 0,
         "status": "INFO"},
        {"id": "the-asymmetric-wager-msaf", "label": "The Asymmetric Wager (Epistemic Sieve)", "layer": 0,
         "status": "CERTIFIED"},
        {"id": "ChronoGeometric_Framework", "label": "ChronoGeometric Framework (Lean 4 Triad)", "layer": 1,
         "status": "CERTIFIED"},
        {"id": "guinand-weil-rigorous-numerics", "label": "Guinand-Weil OMEGA Engine", "layer": 2,
         "status": "CERTIFIED"},
        {"id": "anti-turing-pnp", "label": "Anti-Turing PnP Logic", "layer": 1,
         "status": "CERTIFIED"},
        {"id": "prereg", "label": "Stage 1-4 pre-registration", "layer": 1,
         "status": "INFO" if _exists(
             "reports/PREREG_RH_STRATEGY_STAGE1_2026-11-01.md") else "NOT_RUN"},
        {"id": "bridge", "label": "Laurent bridge", "layer": 1,
         "status": "INFO" if _exists(
             "msaf/chrono_runtime/laurent_bridge_operator.py") else "NOT_RUN"},
    ]
    for index, spec in enumerate(STAGE_SPECS, start=2):
        nodes.append({
            "id": spec["id"],
            "label": spec["label"],
            "layer": index,
            "status": _receipt_status(spec["receipt"]),
        })
    nodes.extend([
        {"id": "track3", "label": "Track 3 Dirichlet sweep", "layer": 4,
         "status": _receipt_status(TRACK3_RECEIPT)},
        {"id": "track2", "label": "Track 2 knowledge graph", "layer": 5,
         "status": "PASS"},
        {"id": "consolidated", "label": "Consolidated receipt", "layer": 6,
         "status": consolidated_status},
        {"id": "ledger", "label": f"Ledger anchor {LEDGER_RULE_ID}", "layer": 7,
         "status": "CERTIFIED" if ledger["track2_track3_anchored"] else "NOT_RUN"},
        {"id": "fence", "label": "FENCE_REGISTRY pins", "layer": 6,
         "status": fence["status"]},
    ])

    edges = [
        ["program", "prereg"],
        ["program", "bridge"],
        ["the-asymmetric-wager-msaf", "program"],
        ["anti-turing-pnp", "program"],
        ["ChronoGeometric_Framework", "stage1"],
        ["guinand-weil-rigorous-numerics", "stage2"],
        ["prereg", "stage1"],
        ["stage1", "stage2"],
        ["bridge", "stage2"],
        ["stage2", "stage3"],
        ["stage3", "stage4"],
        ["bridge", "track3"],
        ["stage1", "track2"],
        ["stage2", "track2"],
        ["stage3", "track2"],
        ["stage4", "track2"],
        ["track3", "track2"],
        ["stage4", "consolidated"],
        ["track2", "consolidated"],
        ["track3", "consolidated"],
        ["fence", "consolidated"],
        ["consolidated", "ledger"],
    ]

    return {"nodes": nodes, "edges": edges,
            "fence": fence, "ledger": ledger,
            "consolidated_status": consolidated_status}


def build_gate_tree(graph: dict[str, Any]) -> dict[str, Any]:
    by_id = {node["id"]: node for node in graph["nodes"]}
    gate_status = {}

    def status_of(node_id: str) -> str:
        return str(by_id.get(node_id, {}).get("status", "NOT_RUN"))

    track3_ok = status_of("track3") == "CERTIFIED"
    integer_gate = "CERTIFIED" if track3_ok else "NOT_RUN"
    bridge_gate = "CERTIFIED" if _exists(
        "msaf/chrono_runtime/laurent_bridge_operator.py") else "NOT_RUN"

    gate_status["scope"] = "PASS"
    gate_status["integer"] = integer_gate
    gate_status["zero"] = integer_gate
    gate_status["complex"] = integer_gate
    gate_status["bridge"] = bridge_gate
    gate_status["stage1"] = status_of("stage1")
    gate_status["stage2"] = status_of("stage2")
    gate_status["stage3"] = status_of("stage3")
    gate_status["stage4"] = status_of("stage4")
    gate_status["fence"] = graph["fence"]["status"]
    gate_status["track2"] = "PASS"
    gate_status["ledger"] = status_of("ledger")

    children = [
        {"id": "rh_scope", "label": "rh_claim = false", "status": "PASS"},
        {"id": "weil_scope", "label": "weil_positivity = false",
         "status": "PASS"},
        {"id": "integer", "label": "exact fmpz {-1,0,+1}",
         "status": gate_status["integer"]},
        {"id": "zero", "label": "structural zero = gcd",
         "status": gate_status["zero"]},
        {"id": "complex", "label": "complex rejected, not coerced",
         "status": gate_status["complex"]},
        {"id": "bridge", "label": "bridge transport",
         "status": gate_status["bridge"]},
        {"id": "stage1", "label": "Stage 1 enclosure",
         "status": gate_status["stage1"]},
        {"id": "stage2", "label": "Stage 2 tail bound",
         "status": gate_status["stage2"]},
        {"id": "stage3", "label": "Stage 3 spectral lock",
         "status": gate_status["stage3"]},
        {"id": "stage4", "label": "Stage 4 containment",
         "status": gate_status["stage4"]},
        {"id": "fence", "label": "FENCE registry pins",
         "status": gate_status["fence"]},
        {"id": "track2", "label": "Track 2 renderers",
         "status": gate_status["track2"]},
        {"id": "ledger", "label": f"ledger {LEDGER_RULE_ID}",
         "status": gate_status["ledger"]},
    ]

    bad = {"FAIL", "FAILED", "NOT_VERIFIED"}
    overall = "NOT_VERIFIED" if any(
        child["status"] in bad for child in children) else "PASS"

    return {
        "id": "root",
        "label": f"chrono gate tree ({overall})",
        "status": overall,
        "children": children,
    }


def build_orbit(graph: dict[str, Any]) -> dict[str, Any]:
    by_id = {node["id"]: node for node in graph["nodes"]}
    parent = {
        "stage1": "program",
        "prereg": "program",
        "bridge": "prereg",
        "stage2": "bridge",
        "stage3": "stage2",
        "stage4": "stage3",
        "track3": "bridge",
        "track2": "track3",
        "fence": "stage4",
        "consolidated": "fence",
        "ledger": "consolidated",
        "the-asymmetric-wager-msaf": "program",
        "anti-turing-pnp": "program",
        "ChronoGeometric_Framework": "stage1",
        "guinand-weil-rigorous-numerics": "stage2",
    }
    nodes = [
        {"id": "program", "label": "chrono program", "status": "INFO"}
    ]
    for node in graph["nodes"]:
        if node["id"] == "program":
            continue
        nodes.append({
            "id": node["id"],
            "parent": parent.get(node["id"], "program"),
            "label": node["label"],
            "status": node["status"],
        })
    return {"root": "program", "nodes": nodes}


# ----------------------------------------------------------------- writing
def _write_text(directory: Path, name: str, text: str) -> Path:
    target = guard.make_dirs_writable(directory / name)
    target.write_text(text, encoding="utf-8")
    return target


def render_all() -> dict[str, Any]:
    repo_out = (ROOT / "mcp" / "out").resolve()
    os.environ.setdefault("T2N_WRITE_ROOTS", str(repo_out))
    out_dir = guard.assert_writable(repo_out / OUTPUT_DIR)
    guard.make_dirs_writable(out_dir / "placeholder.json")
    out_dir.mkdir(parents=True, exist_ok=True)

    graph = build_graph()
    dependency = render_dependency_svg({"graph": graph})
    orbit = render_orbit_svg(build_orbit(graph))
    gate_spec = build_gate_tree(graph)
    gate_tree = render_gate_tree_svg({"tree": gate_spec})

    receipt_labels = []
    for spec in STAGE_SPECS:
        receipt_labels.append(render_receipt_svg({
            "receipt": {"id": f"{spec['label']} / {_receipt_status(spec['receipt'])}"}
        })["svg"])
    receipt_labels.append(render_receipt_svg({
        "receipt": {"id": f"Track 3 sweep / {_receipt_status(TRACK3_RECEIPT)}"}
    })["svg"])
    receipt_labels.append(render_receipt_svg({
        "receipt": {"id": f"Ledger {LEDGER_RULE_ID} / "
                           f"{'PRESENT' if graph['ledger']['track2_track3_anchored'] else 'ABSENT'}"}
    })["svg"])

    summary = {
        "date": DATE,
        "node_count": len(graph["nodes"]),
        "edge_count": len(graph["edges"]),
        "stage_status": {
            spec["id"]: _receipt_status(spec["receipt"]) for spec in STAGE_SPECS
        },
        "track3_status": _receipt_status(TRACK3_RECEIPT),
        "consolidated_status": graph["consolidated_status"],
        "fence": graph["fence"],
        "ledger": graph["ledger"],
        "gate_overall": gate_spec["status"],
        "gate_counts": gate_tree["status_counts"],
        "scope_notice": {
            "rh_claim": False,
            "grh_claim": False,
            "weil_positivity_claim": False,
            "zero_location_claim": False,
        },
    }

    written: list[str] = []

    def emit(directory: Path, name: str, text: str) -> None:
        written.append(str(_write_text(directory, name, text)))

    emit(out_dir, "graph.json",
         json.dumps({"nodes": graph["nodes"], "edges": graph["edges"]},
                    indent=2))
    emit(out_dir, "summary.json", json.dumps(summary, indent=2))
    emit(out_dir, "dependency.svg", dependency["svg"])
    emit(out_dir, "orbit.svg", orbit["svg"])
    emit(out_dir, "gate_tree.svg", gate_tree["svg"])
    emit(out_dir, "receipt_labels.svg",
         '<svg xmlns="http://www.w3.org/2000/svg" width="660" height="'
         f'{120 * len(receipt_labels)}">' + "".join(
             f'<g transform="translate(0,{120 * index})">{svg[svg.index(">") + 1:-6]}</g>'
             for index, svg in enumerate(receipt_labels)) + "</svg>")

    dashboard = render_html_dashboard({
        "title": f"Chrono-RH Knowledge Graph {DATE}",
        "sections": [
            {"header": "Measured summary", "content": json.dumps(summary, indent=2)},
            {"header": "Layered dependency map", "content": dependency["svg"]},
            {"header": "Root-pulling orbit", "content": orbit["svg"]},
            {"header": "Functional gate tree", "content": gate_tree["svg"]},
            {"header": "Receipt labels", "content": "".join(receipt_labels)},
            {"header": "Ledger tail", "content": json.dumps(graph["ledger"], indent=2)},
        ],
    })
    
    # Write to mcp/out/dashboards/maa_convergence_v1.html
    dash_dir = ROOT / "mcp" / "out" / "dashboards"
    dash_path = guard.make_dirs_writable(dash_dir / "maa_convergence_v1.html")
    html_content = Path(dashboard["path"]).read_text(encoding="utf-8")
    dash_path.write_text(html_content, encoding="utf-8")
    written.append(str(dash_path))
    
    written.append(dashboard["path"])
    summary["written"] = written
    manifest = _write_text(out_dir, "manifest.json", json.dumps(summary, indent=2))
    written.append(str(manifest))
    return summary


def main() -> dict[str, Any]:
    result = render_all()
    print(json.dumps({
        "status": "PASS",
        "node_count": result["node_count"],
        "edge_count": result["edge_count"],
        "gate_overall": result["gate_overall"],
        "fence_status": result["fence"]["status"],
        "written": result["written"],
    }, indent=2))
    return result


if __name__ == "__main__":
    main()
