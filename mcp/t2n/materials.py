# -*- coding: utf-8 -*-
"""t2n_materials -- Materials Project API client (F7).

Stdlib-only wrapper for Materials Project REST API (api.materialsproject.org).
No external deps; writes confined to `mcp/out/materials/` via write-root allowlist.
"""
import sys
import os
import json
import urllib.parse
import urllib.request
import urllib.error
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from core import guard
from core.skeleton import serve_generic

REPO_ROOT = Path(os.environ.get("T2N_REPO_ROOT")
                 or Path(__file__).resolve().parents[2]).resolve()

MP_API_ENDPOINT = "https://api.materialsproject.org"
MP_API_KEY = os.environ.get("MP_API_KEY") or os.environ.get("PMG_MAPI_KEY")

# ---------------------------------------------------------------------
# Helper: safe name for file paths
def _safe_name(text: str) -> str:
    import re
    return re.sub(r"[^A-Za-z0-9_\-]", "_", str(text))[:64]

# ---------------------------------------------------------------------
# Core HTTP client (stdlib only)
class MPClient:
    """Minimal Materials Project API client using urllib (stdlib)."""

    def __init__(self, api_key: str | None = None, endpoint: str = MP_API_ENDPOINT):
        self.api_key = api_key
        self.endpoint = endpoint.rstrip("/")
        if not self.api_key:
            raise ValueError("MP_API_KEY or PMG_MAPI_KEY environment variable required")

    def _request(self, path: str, params: dict | None = None) -> dict:
        """Make GET request to MP API."""
        if not path.endswith("/"):
            path = path + "/"
        url = f"{self.endpoint}{path}"
        if params:
            query_params = {}
            for k, v in params.items():
                if k == "fields":
                    query_params["_fields"] = v
                elif k in ("page", "per_page"):
                    # Ignore old-style pagination
                    pass
                else:
                    query_params[k] = v
            if query_params:
                query = urllib.parse.urlencode(query_params, doseq=True)
                url = f"{url}?{query}"

        req = urllib.request.Request(url)
        req.add_header("X-API-KEY", self.api_key)
        req.add_header("Accept", "application/json")
        req.add_header("User-Agent", "Mozilla/5.0 (compatible; t2n_materials/1.0)")

        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = resp.read()
                return json.loads(data.decode("utf-8"))
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"MP API HTTP {e.code}: {body}") from e
        except urllib.error.URLError as e:
            raise RuntimeError(f"MP API network error: {e}") from e

    # ---- Summary endpoint (most common) ----
    def search_summary(self,
                       material_ids: list[str] | None = None,
                       formula: str | None = None,
                       elements: list[str] | None = None,
                       chemsys: str | None = None,
                       band_gap: tuple[float, float] | None = None,
                       e_above_hull: tuple[float, float] | None = None,
                       fields: list[str] | None = None,
                       num_chunks: int | None = None,
                       chunk_size: int = 1000) -> list[dict]:
        """Query /materials/summary endpoint."""
        params = {}
        if material_ids:
            params["material_ids"] = ",".join(material_ids)
        if formula:
            params["formula"] = formula
        if elements:
            params["elements"] = ",".join(elements)
        if chemsys:
            params["chemsys"] = chemsys
        if band_gap:
            params["band_gap_min"] = str(band_gap[0])
            params["band_gap_max"] = str(band_gap[1])
        if e_above_hull:
            params["energy_above_hull_min"] = str(e_above_hull[0])
            params["energy_above_hull_max"] = str(e_above_hull[1])
        if fields:
            params["fields"] = ",".join(fields)  # Will be converted to _fields in _request

        all_results = []
        page = 1
        while True:
            page_params = dict(params)
            page_params["_page"] = str(page)
            page_params["_per_page"] = str(chunk_size)
            resp = self._request("/materials/summary", page_params)
            data = resp.get("data", [])
            all_results.extend(data)
            if not data or (num_chunks and page >= num_chunks):
                break
            if len(data) < chunk_size:
                break
            page += 1
        return all_results

    # ---- Phase Diagram / Thermo ----
    def search_phase_diagram(self, chemsys: str, fields: list[str] | None = None) -> list[dict]:
        """Fetch thermo entries for a chemical system.
        Uses /materials/thermo endpoint (no dedicated phase diagram API)."""
        params = {"chemsys": chemsys}
        if fields:
            params["fields"] = ",".join(fields)
        resp = self._request("/materials/thermo", params)
        return resp.get("data", [])

    # ---- Electronic structure (bandstructure + DOS) ----
    def get_electronic_structure(self,
                                 material_ids: list[str],
                                 include_bandstructure: bool = True,
                                 include_dos: bool = True) -> list[dict]:
        """Query /materials/electronic_structure endpoint for bandstructure and/or DOS."""
        fields = []
        if include_bandstructure:
            fields.append("bandstructure")
        if include_dos:
            fields.append("dos")
        # Always include basic fields
        fields.extend(["material_id", "band_gap", "efermi", "is_gap_direct", "is_metal", "magnetic_ordering"])

        params = {
            "material_ids": ",".join(material_ids),
            "fields": ",".join(fields)
        }
        resp = self._request("/materials/electronic_structure", params)
        return resp.get("data", [])

    # ---- Phonon ----
    def search_phonon(self,
                      formula: str | None = None,
                      chemsys: str | None = None,
                      elements: list[str] | None = None,
                      fields: list[str] | None = None) -> list[dict]:
        """Query /materials/phonon endpoint.
        
        Note: This endpoint does NOT support material_ids parameter.
        Use formula, chemsys, or elements to filter instead.
        """
        params = {}
        if formula:
            params["formula"] = formula
        if chemsys:
            params["chemsys"] = chemsys
        if elements:
            params["elements"] = ",".join(elements)
        if fields:
            params["fields"] = ",".join(fields)
        resp = self._request("/materials/phonon", params)
        return resp.get("data", [])

    # ---- Elasticity ----
    def search_elasticity(self,
                          material_ids: list[str] | None = None,
                          fields: list[str] | None = None) -> list[dict]:
        params = {}
        if material_ids:
            params["material_ids"] = ",".join(material_ids)
        if fields:
            params["fields"] = ",".join(fields)
        resp = self._request("/materials/elasticity", params)
        return resp.get("data", [])

    # ---- Magnetism ----
    def search_magnetism(self,
                         material_ids: list[str] | None = None,
                         fields: list[str] | None = None) -> list[dict]:
        params = {}
        if material_ids:
            params["material_ids"] = ",".join(material_ids)
        if fields:
            params["fields"] = ",".join(fields)
        resp = self._request("/materials/magnetism", params)
        return resp.get("data", [])

    # ---- Synthesis ----
    def search_synthesis(self, material_ids: list[str] | None = None) -> list[dict]:
        params = {}
        if material_ids:
            params["material_ids"] = ",".join(material_ids)
        resp = self._request("/materials/synthesis", params)
        return resp.get("data", [])

    # ---- Structure from summary (no separate CIF endpoint) ----
    def get_structure(self, material_ids: list[str]) -> list[dict]:
        """Get structure data from summary endpoint."""
        return self.search_summary(material_ids=material_ids, fields=["material_id", "structure", "formula_pretty"])


# ---------------------------------------------------------------------
# Tool implementations
def mp_query(params: dict) -> dict:
    """Query Materials Project API.

    Parameters:
    - endpoint: "summary" | "thermo" | "electronic_structure" | "phonon" | "elasticity" | "magnetism" | "synthesis" | "structure"
    - filters: dict of query filters (material_ids, formula, elements, chemsys, band_gap, e_above_hull, fields, include_bandstructure, include_dos)
    - save_json: bool, whether to save response to mcp/out/materials/
    """
    endpoint = params.get("endpoint", "summary")
    filters = params.get("filters", {})
    save_json = params.get("save_json", False)

    if not MP_API_KEY:
        raise RuntimeError("MP_API_KEY not configured. Set environment variable MP_API_KEY or PMG_MAPI_KEY.")

    client = MPClient(MP_API_KEY)

    # Dispatch to appropriate method
    if endpoint == "summary":
        results = client.search_summary(**filters)
    elif endpoint == "thermo":
        results = client.search_thermo(**filters)
    elif endpoint == "electronic_structure":
        mat_ids = filters.get("material_ids", [])
        if not mat_ids:
            raise ValueError("material_ids required for electronic_structure endpoint")
        include_bs = filters.get("include_bandstructure", True)
        include_dos = filters.get("include_dos", True)
        results = client.get_electronic_structure(mat_ids, include_bs, include_dos)
    elif endpoint == "phonon":
        results = client.search_phonon(
            formula=filters.get("formula"),
            chemsys=filters.get("chemsys"),
            elements=filters.get("elements"),
            fields=filters.get("fields")
        )
    elif endpoint == "elasticity":
        results = client.search_elasticity(filters.get("material_ids"), filters.get("fields"))
    elif endpoint == "magnetism":
        results = client.search_magnetism(filters.get("material_ids"), filters.get("fields"))
    elif endpoint == "synthesis":
        results = client.search_synthesis(filters.get("material_ids"))
    elif endpoint == "phase_diagram":
        results = client.search_phase_diagram(filters.get("chemsys"), filters.get("fields"))

    # Optionally save to file
    saved_path = None
    if save_json:
        out_dir = Path(guard.write_roots()[0]) / "materials"
        fname = f"mp_{endpoint}_{_safe_name(json.dumps(filters, sort_keys=True)[:50])}.json"
        out_path = out_dir / fname
        guard.make_dirs_writable(out_path)
        out_path.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
        saved_path = str(out_path.relative_to(REPO_ROOT))

    return {
        "schema": "t2n_materials.mp_query.v1",
        "endpoint": endpoint,
        "count": len(results) if isinstance(results, list) else 1,
        "saved_path": saved_path,
        "data": results if not save_json else None  # Don't return large data inline if saved
    }


# ---------------------------------------------------------------------
TOOL_DEFS = [
    {
        "name": "mp_query",
        "description": "Query Materials Project REST API (stdlib only). Endpoints: summary, thermo, electronic_structure (bandstructure+DOS), phonon, elasticity, magnetism, synthesis, structure, phase_diagram.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "endpoint": {"type": "string", "enum": ["summary", "thermo", "electronic_structure", "phonon", "elasticity", "magnetism", "synthesis", "structure"]},
                "filters": {"type": "object"},
                "save_json": {"type": "boolean"}
            },
            "required": ["endpoint"],
            "additionalProperties": False
        }
    }
]

HANDLERS = {
    "mp_query": mp_query,
}

DESCRIPTION = ("T-hat-N materials (F7): Materials Project API client (stdlib-only). "
               "Queries summary, thermo, electronic structure (bandstructure+DOS), phonon, elasticity, magnetism, synthesis, structure. "
               "Writes to write-root allowlist.")

if __name__ == "__main__":
    serve_generic("t2n_materials", DESCRIPTION, TOOL_DEFS, HANDLERS)