"""Standalone diagnostics dashboard for Campaign V2 (K-Q5).

Constraints (frozen): one self-contained HTML page, raw SVG graphics and
inline CSS only, no scripts, no external links, no network requests. The
existing gw dashboards are untouched by design; this module writes only the
Campaign V2 diagnostic page.

``assert_self_contained`` re-checks the constraints; it runs in the selftest
and in the CI guard test.
"""

from __future__ import annotations

import html as _html
from pathlib import Path

__all__ = ["assert_self_contained", "render_report", "write_report"]

_FORBIDDEN = ("<script", "http://", "https://", "@import", "<link", "javascript:", "src=")

_CSS = """
body { font-family: Consolas, Menlo, monospace; margin: 24px; background: #f7f7f4; color: #1a1a1a; }
h1 { font-size: 18px; } h2 { font-size: 15px; margin-top: 28px; }
p.note { background: #fff3cd; border: 1px solid #d8b64a; padding: 8px 10px; max-width: 980px; }
table { border-collapse: collapse; margin-top: 8px; font-size: 12px; }
th, td { border: 1px solid #999; padding: 3px 7px; text-align: left; }
th { background: #e8e8e2; }
td.ok { color: #146c2e; } td.bad { color: #a11; }
svg { background: #ffffff; border: 1px solid #bbb; display: block; margin-top: 8px; }
footer { margin-top: 30px; font-size: 11px; color: #555; }
"""


def _esc(x) -> str:
    return _html.escape(str(x), quote=True)


def _num(x, sig: int = 17) -> str:
    try:
        return format(float(x), ".%dg" % sig)
    except (TypeError, ValueError, OverflowError):
        return _esc(x)


def _bar_svg(counts, expected: float, width: int = 640, height: int = 190) -> str:
    n = len(counts)
    maxv = max(max(counts) if counts else 1, expected * 1.6, 1.0)
    bw = (width - 40) / n
    parts = [
        '<svg width="%d" height="%d" viewBox="0 0 %d %d">' % (width, height, width, height)
    ]
    base = height - 30
    for i, c in enumerate(counts):
        h = (c / maxv) * (height - 50)
        x = 20 + i * bw
        parts.append(
            '<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="#4a6da7" stroke="#233"/>'
            % (x, base - h, bw * 0.82, max(h, 0.8))
        )
    ye = base - (expected / maxv) * (height - 50)
    parts.append(
        '<line x1="20" y1="%.1f" x2="%d" y2="%.1f" stroke="#a11" stroke-width="2" stroke-dasharray="6,4"/>'
        % (ye, width - 20, ye)
    )
    parts.append(
        '<text x="24" y="14" font-size="12" fill="#333">16 quantile cells; bars = observed counts; dashed = expected (S/16)</text>'
    )
    parts.append("</svg>")
    return "".join(parts)


def render_report(payload: dict) -> str:
    dims = payload.get("dims", [])
    v = payload.get("verdict", {})
    ent = payload.get("entropy", {})
    out = [
        "<!DOCTYPE html>",
        '<html lang="en"><head><meta charset="utf-8">',
        "<title>Quantum Entropy Kernel - Campaign V2 (SIMULATED)</title>",
        "<style>%s</style></head><body>" % _CSS,
        "<h1>Quantum Entropy Kernel - Campaign V2 (SIMULATED)</h1>",
        '<p class="note">Entropy source: SIMULATED operating-system CSPRNG stream; '
        "this is NOT a physical quantum measurement. This page is standalone: raw SVG "
        "and inline CSS only, no scripts and no network requests. "
        "global_claim_supported = false (K-Q7).</p>",
        "<p><b>Campaign status:</b> %s &nbsp; <b>exit code:</b> %s &nbsp; <b>generated:</b> %s</p>"
        % (_esc(v.get("status")), _esc(v.get("exit_code")), _esc(payload.get("created_utc"))),
        "<p>Entropy descriptor: label=%s, backend=%s, block_bits=%s</p>"
        % (_esc(ent.get("label")), _esc(ent.get("backend")), _esc(ent.get("block_bits"))),
    ]
    if v.get("reasons"):
        out.append("<p><b>Reasons:</b> %s</p>" % _esc("; ".join(v.get("reasons"))))
    for d in dims:
        out.append("<h2>dim %s - status %s</h2>" % (_esc(d.get("dim")), _esc(d.get("status"))))
        out.append(
            "<p>samples=%s; chi2=%s; kept cells=%s; dropped=%s; exceedances=%s; envelope_exceeded=%s</p>"
            % (
                _esc(d.get("samples")),
                _esc(d.get("chi2")),
                _esc(d.get("chi2_kept")),
                _esc(d.get("chi2_dropped")),
                _esc(d.get("exceedances")),
                _esc(d.get("envelope_exceeded")),
            )
        )
        counts = d.get("counts", [])
        exp = d.get("expected_float", 0.0)
        if counts:
            out.append(_bar_svg(counts, exp))
        rows = [
            "<table><tr><th>k</th><th>envelope lo</th><th>envelope hi</th><th>rel width</th><th>floor ok</th><th>cert (A/B)</th></tr>"
        ]
        for c in d.get("coords", []):
            ok = d.get("floor_rel", 0.02)
            rows.append(
                "<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td>"
                '<td class="%s">%s</td><td>%s</td></tr>'
                % (
                    _esc(c.get("k")),
                    _num(c.get("lo_float"), 12),
                    _num(c.get("hi_float"), 12),
                    _num(c.get("rel_width_float"), 6),
                    "ok" if (c.get("rel_width_float") or 1) <= ok else "bad",
                    _esc(c.get("contracted")),
                    _esc(c.get("cert")),
                )
            )
        rows.append("</table>")
        out.append("".join(rows))
        piv = d.get("pivots", {})
        newt = d.get("newton", {})
        dec = d.get("decisions", {})
        out.append(
            "<p>pivots: A=%s B=%s &nbsp;|&nbsp; newton: A=%s (final width %s) B=%s (final width %s) "
            "&nbsp;|&nbsp; decisions: steps=%s dual=%s exact=%s zero=%s disagree=%s</p>"
            % (
                _esc(piv.get("a")),
                _esc(piv.get("b")),
                _esc(newt.get("a_status")),
                _num(newt.get("a_final"), 6),
                _esc(newt.get("b_status")),
                _num(newt.get("b_final"), 6),
                _esc(dec.get("steps")),
                _esc(dec.get("dual")),
                _esc(dec.get("exact")),
                _esc(dec.get("exact_zero")),
                _esc(dec.get("disagree")),
            )
        )
    out.append(
        "<footer>Campaign V2 / reports/REPLAY_CERT_SPEC_V0.2_QUANTUM.md + "
        "reports/AUDIT_QUANTUM_PREREG_2026-10-19.md; SIMULATED entropy; "
        "statistical layer float64; certified layer Arb 6000 bits / mpmath dps 50.</footer>"
    )
    out.append("</body></html>")
    return "\n".join(out)


def assert_self_contained(page: str) -> None:
    low = page.lower()
    for pat in _FORBIDDEN:
        if pat in low:
            raise AssertionError("dashboard violates K-Q5 (found %r)" % pat)
    if "SIMULATED" not in page:
        raise AssertionError("dashboard missing SIMULATED label (D1)")


def write_report(path, payload: dict) -> dict:
    page = render_report(payload)
    assert_self_contained(page)
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(page, encoding="utf-8", newline="\n")
    return {"path": str(p), "bytes": len(page.encode("utf-8"))}


