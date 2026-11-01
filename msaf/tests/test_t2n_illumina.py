# -*- coding: utf-8 -*-
"""Unit tests for the Track 2 illumina renderers.

The MCP-level guard in ``test_mcp_servers.py`` drives real stdio subprocesses;
this module exercises the renderers directly so layout regressions fail with a
useful message instead of a JSON-RPC trace.
"""
from __future__ import annotations

import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
T2N = ROOT / "mcp" / "t2n"
sys.path.insert(0, str(T2N))

from illumina import (  # noqa: E402  (path bootstrap must run first)
    render_dependency_svg,
    render_gate_tree_svg,
    render_html_dashboard,
    render_orbit_svg,
    render_receipt_svg,
)

REMOTE_MARKERS = ("<script", "src=", "href=", "@import", "url(http")


def _assert_self_contained_svg(svg: str) -> None:
    assert svg.startswith("<svg")
    for marker in REMOTE_MARKERS:
        assert marker not in svg
    ET.fromstring(svg)


def test_legacy_dependency_nodes_still_render_one_row() -> None:
    payload = render_dependency_svg({"graph": {
        "nodes": ["alpha", "beta"],
        "edges": [["alpha", "beta"]],
    }})
    assert payload["node_count"] == 2
    assert payload["edge_count"] == 1
    assert payload["layers"] == [0]
    _assert_self_contained_svg(payload["svg"])


def test_layered_dependency_uses_columns_and_named_edges() -> None:
    payload = render_dependency_svg({"graph": {
        "nodes": [
            {"id": "s1", "label": "Stage 1", "layer": 0, "status": "CERTIFIED"},
            {"id": "s2", "label": "Stage 2", "layer": 1, "status": "PASS"},
            {"id": "s3", "label": "Stage 3", "layer": 2, "status": "NOT_RUN"},
        ],
        "edges": [
            {"source": "s1", "target": "s2"},
            {"source": "s2", "target": "s3"},
            {"source": "s1", "target": "s3"},
        ],
    }})
    assert payload["layers"] == [0, 1, 2]
    assert payload["edge_count"] == 3
    assert payload["svg"].count("<rect") == 3
    _assert_self_contained_svg(payload["svg"])


def test_dependency_rejects_duplicate_ids() -> None:
    with pytest.raises(ValueError):
        render_dependency_svg({"graph": {
            "nodes": [{"id": "a"}, {"id": "a"}],
            "edges": [],
        }})


def test_legacy_orbit_is_unchanged() -> None:
    payload = render_orbit_svg({"radius": 50, "points": 6})
    assert payload["mode"] == "ring"
    assert payload["svg"].count("<circle") == 7  # guide circle + 6 points
    _assert_self_contained_svg(payload["svg"])


def test_root_pulling_orbit_places_by_depth() -> None:
    payload = render_orbit_svg({
        "root": "root",
        "nodes": [
            {"id": "root", "label": "root", "status": "PASS"},
            {"id": "a", "parent": "root", "label": "a", "status": "CERTIFIED"},
            {"id": "b", "parent": "root", "label": "b", "status": "FAIL"},
            {"id": "c", "parent": "a", "label": "c", "status": "INFO"},
        ],
    })
    assert payload["mode"] == "root_pulling"
    assert payload["root"] == "root"
    assert payload["max_depth"] == 2
    assert payload["detached"] == []
    _assert_self_contained_svg(payload["svg"])


def test_root_pulling_orbit_marks_detached_nodes() -> None:
    payload = render_orbit_svg({
        "root": "root",
        "nodes": [
            {"id": "root"},
            {"id": "lost", "parent": None, "label": "lost"},
        ],
    })
    assert payload["detached"] == ["lost"]
    assert payload["max_depth"] == 1


def test_root_pulling_orbit_rejects_missing_parent() -> None:
    with pytest.raises(ValueError):
        render_orbit_svg({
            "root": "root",
            "nodes": [{"id": "root"}, {"id": "x", "parent": "ghost"}],
        })


def test_gate_tree_nested_and_flat_agree_on_counts() -> None:
    nested = render_gate_tree_svg({"tree": {
        "id": "G0", "label": "scope", "status": "PASS",
        "children": [
            {"id": "G1", "label": "integer", "status": "CERTIFIED",
             "children": [{"id": "G3", "label": "bridge",
                           "status": "CERTIFIED"}]},
            {"id": "G2", "label": "zero", "status": "CERTIFIED"},
        ],
    }})
    flat = render_gate_tree_svg({"gates": [
        {"id": "G0", "label": "scope", "status": "PASS"},
        {"id": "G1", "label": "integer", "status": "CERTIFIED",
         "parent": "G0"},
        {"id": "G2", "label": "zero", "status": "CERTIFIED", "parent": "G0"},
        {"id": "G3", "label": "bridge", "status": "CERTIFIED",
         "parent": "G1"},
    ]})
    assert nested["gate_count"] == flat["gate_count"] == 4
    assert nested["max_depth"] == flat["max_depth"] == 2
    assert nested["roots"] == flat["roots"] == ["G0"]
    assert nested["status_counts"] == flat["status_counts"]
    _assert_self_contained_svg(nested["svg"])


def test_gate_tree_rejects_missing_parent_and_cycles() -> None:
    with pytest.raises(ValueError):
        render_gate_tree_svg({"gates": [{"id": "a", "parent": "ghost"}]})
    with pytest.raises(ValueError):
        render_gate_tree_svg({"tree": {
            "id": "a", "children": [{"id": "b", "children": [
                {"id": "a"}]}]}})


def test_gate_tree_requires_input() -> None:
    with pytest.raises(ValueError):
        render_gate_tree_svg({})


def test_receipt_svg_still_labels_the_receipt() -> None:
    payload = render_receipt_svg({"receipt": {"id": "T-2026-0095"}})
    assert payload["receipt_id"] == "T-2026-0095"
    assert "T-2026-0095" in payload["svg"]
    _assert_self_contained_svg(payload["svg"])


def test_dashboard_is_offline_and_escapes_text(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("T2N_WRITE_ROOTS", str(tmp_path))
    gate = render_gate_tree_svg({"tree": {
        "id": "root", "label": "root", "status": "PASS",
        "children": [{"id": "leaf", "label": "leaf", "status": "CERTIFIED"}],
    }})
    payload = render_html_dashboard({
        "title": "Track 2 <dashboard>",
        "sections": [
            {"header": "Gate tree", "content": gate["svg"]},
            {"header": "<raw>", "content": "<script>alert(1)</script>"},
        ],
    })
    path = Path(payload["path"])
    assert path.is_file()
    assert tmp_path.resolve() in path.resolve().parents
    text = path.read_text(encoding="utf-8")
    assert "<h1>Track 2 &lt;dashboard&gt;</h1>" in text
    assert "<h2>&lt;raw&gt;</h2>" in text
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in text
    for forbidden in ("http://", "https://", "<script", "src=", "@import"):
        assert forbidden not in text
    assert "<svg" in text
