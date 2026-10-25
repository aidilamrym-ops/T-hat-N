# -*- coding: utf-8 -*-
"""t2n_science -- exact & interval calculators with whitelist-only AST (F3).

Three stateless instruments for the repo's certification work:

- `iv_eval`: interval arithmetic (outward rounding, stdlib `decimal`
  with per-operation ROUND_FLOOR / ROUND_CEILING contexts). The user
  expression is parsed with `ast.parse` and evaluated against a CLOSED
  whitelist: + - * / *, unary +/-, integer exponents |n| <= 32, the
  functions sqrt/exp/ln/log10/abs, and numeric variables supplied as
  exact decimal strings. There is no `eval`; attributes, subscripts,
  comparisons, float literals, foreign names -- everything unlisted
  fails closed with an explicit reason.

- `frac_compare`: exact rational comparison via `fractions.Fraction`
  over the same whitelist (int literals + ( ) + - * / and unary sign).
  Returns the exact difference, so certificates can be compared without
  floating-point noise.

- `ast_float_scan`: quality gate for repo modules -- finds float
  literals, float(...) calls and eval/exec/compile/__import__ calls via
  AST (never regex-on-text). strict=True turns any non-waived hit into
  an overall REFUSED verdict; the only waiver is the line marker
  `T2N-FLOAT-ALLOW`.

Signature honesty note: interval endpoints are DIRECTED (outward) bounds
at the requested decimal precision -- they may be slightly wider than
the exact range, never narrower.
"""
from __future__ import annotations

import ast
import os
import re
import sys
from decimal import (Decimal, Context, DecimalException, ROUND_CEILING,
                     ROUND_FLOOR, ROUND_HALF_EVEN)
from fractions import Fraction
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from core import guard
from core.skeleton import serve_generic

REPO_ROOT = Path(os.environ.get("T2N_REPO_ROOT")
                 or Path(__file__).resolve().parents[2]).resolve()

_DIGITS_MIN, _DIGITS_MAX, _DIGITS_DEF = 20, 400, 60
_MAX_EXPR_CHARS, _MAX_NODES = 500, 64
_MAX_POW_ABS = 32
_MAX_VARS = 8
_NAME_OK = re.compile(r"^[A-Za-z_][A-Za-z0-9_]{0,15}$")
FUNCS = ("sqrt", "exp", "ln", "log10", "abs")
_IV_RE = re.compile(
    r"^\s*\[\s*([^\s,]+)\s*,\s*([^\s,]+)\s*\]\s*$")


def _repo_path(raw: str) -> Path:
    """Resolve and confine any path to the repo root (read side)."""
    p = Path(raw)
    p = p if p.is_absolute() else (REPO_ROOT / p)
    p = p.resolve(strict=False)
    if p != REPO_ROOT and REPO_ROOT not in p.parents:
        raise PermissionError("path outside T2N_REPO_ROOT: %s" % raw)
    return p


# ------------------------------------------------------------------ intervals --
class _Iv:
    __slots__ = ("lo", "hi")

    def __init__(self, lo: Decimal, hi: Decimal) -> None:
        self.lo, self.hi = lo, hi

    def __repr__(self) -> str:                       # pragma: no cover
        return "[%s, %s]" % (self.lo, self.hi)


class _Ctx:
    __slots__ = ("dn", "up", "digits")

    def __init__(self, digits: int) -> None:
        self.digits = digits
        self.dn = Context(prec=digits, rounding=ROUND_FLOOR)
        self.up = Context(prec=digits, rounding=ROUND_CEILING)


def _dec(text: str, where: str) -> Decimal:
    try:
        return Decimal(str(text))
    except DecimalException as exc:
        raise ValueError("bad decimal '%s' (%s): %s" % (text, where, exc))


def _parse_var(name: str, raw: str) -> _Iv:
    v = str(raw).strip()
    m = _IV_RE.match(v)
    endpoints = m.groups() if m else (v, v)
    lo, hi = _dec(endpoints[0], name), _dec(endpoints[1], name)
    if not (lo.is_finite() and hi.is_finite()):
        raise ValueError("var '%s': only finite decimals allowed" % name)
    if lo > hi:
        raise ValueError("var '%s': interval lower > upper" % name)
    return _Iv(lo, hi)


# ---------------------------------------------------------- interval algebra --
def _iv_add(a: _Iv, b: _Iv, c: _Ctx) -> _Iv:
    return _Iv(c.dn.add(a.lo, b.lo), c.up.add(a.hi, b.hi))


def _iv_sub(a: _Iv, b: _Iv, c: _Ctx) -> _Iv:
    return _Iv(c.dn.subtract(a.lo, b.hi), c.up.subtract(a.hi, b.lo))


def _iv_neg(a: _Iv) -> _Iv:                          # exact, no rounding
    return _Iv(-a.hi, -a.lo)


def _iv_mul(a: _Iv, b: _Iv, c: _Ctx) -> _Iv:
    lo = None
    hi = None
    for x in (a.lo, a.hi):
        for y in (b.lo, b.hi):
            d = c.dn.multiply(x, y)
            u = c.up.multiply(x, y)
            lo = d if lo is None or d < lo else lo
            hi = u if hi is None or u > hi else hi
    return _Iv(lo, hi)


def _iv_div(a: _Iv, b: _Iv, c: _Ctx) -> _Iv:
    if b.lo <= 0 <= b.hi:
        raise ValueError(
            "division refused: denominator interval touches or contains "
            "zero (singular for real interval arithmetic)")
    lo = None
    hi = None
    for x in (a.lo, a.hi):
        for y in (b.lo, b.hi):
            d = c.dn.divide(x, y)
            u = c.up.divide(x, y)
            lo = d if lo is None or d < lo else lo
            hi = u if hi is None or u > hi else hi
    return _Iv(lo, hi)


def _pow_pos(x: Decimal, n: int, ctx: Context) -> Decimal:
    """x >= 0, n >= 1: repeated OUTWARD multiply (containment preserved)."""
    out = Decimal(1)
    for _ in range(n):
        out = ctx.multiply(out, x)
    return out


def _iv_pow(a: _Iv, n: int, c: _Ctx) -> _Iv:
    if n == 0:
        return _Iv(Decimal(1), Decimal(1))
    if n < 0:
        return _iv_div(_Iv(Decimal(1), Decimal(1)),
                       _iv_pow(a, -n, c), c)
    even = (n % 2 == 0)
    if even and a.lo <= 0 <= a.hi:
        mag = max(a.lo.copy_abs(), a.hi.copy_abs())
        return _Iv(Decimal(0), _pow_pos(mag, n, c.up))
    lower: Decimal | None = None
    upper: Decimal | None = None
    for e in (a.lo, a.hi):
        if e == 0:
            v_lo = v_hi = Decimal(0)
        elif e > 0:
            v_lo = _pow_pos(e, n, c.dn)
            v_hi = _pow_pos(e, n, c.up)
        else:
            base_lo = _pow_pos(e.copy_abs(), n, c.dn)
            base_hi = _pow_pos(e.copy_abs(), n, c.up)
            if even:
                v_lo, v_hi = base_lo, base_hi
            else:
                v_lo, v_hi = -base_hi, -base_lo   # negate flips outwardness
        lower = v_lo if lower is None or v_lo < lower else lower
        upper = v_hi if upper is None or v_hi > upper else upper
    return _Iv(lower, upper)


def _iv_abs(a: _Iv) -> _Iv:
    if a.lo >= 0:
        return _Iv(a.lo, a.hi)
    if a.hi <= 0:
        return _Iv(-a.hi, -a.lo)
    return _Iv(Decimal(0), max(a.lo.copy_abs(), a.hi.copy_abs()))


# ----------------------------------------------------------------- evaluator --
def _eval_node(node: ast.AST, info: dict, c: _Ctx, env: dict[str, _Iv]) -> _Iv:
    info["nodes"] += 1
    if info["nodes"] > _MAX_NODES:
        raise ValueError("expression too complex: more than %d nodes"
                         % _MAX_NODES)
    kind = type(node).__name__
    info["kinds"].add(kind)

    if isinstance(node, ast.Expression):
        return _eval_node(node.body, info, c, env)
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
        return _iv_add(_eval_node(node.left, info, c, env),
                       _eval_node(node.right, info, c, env), c)
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Sub):
        return _iv_sub(_eval_node(node.left, info, c, env),
                       _eval_node(node.right, info, c, env), c)
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Mult):
        return _iv_mul(_eval_node(node.left, info, c, env),
                       _eval_node(node.right, info, c, env), c)
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div):
        return _iv_div(_eval_node(node.left, info, c, env),
                       _eval_node(node.right, info, c, env), c)
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Pow):
        expo = node.right
        if not (isinstance(expo, ast.Constant) and isinstance(expo.value, int)
                and not isinstance(expo.value, bool)
                and abs(expo.value) <= _MAX_POW_ABS):
            raise ValueError(
                "power exponent must be an integer constant with "
                "|n| <= %d" % _MAX_POW_ABS)
        return _iv_pow(_eval_node(node.left, info, c, env), expo.value, c)
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
        return _iv_neg(_eval_node(node.operand, info, c, env))
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.UAdd):
        return _eval_node(node.operand, info, c, env)
    if isinstance(node, ast.Constant):
        if isinstance(node.value, bool) or not isinstance(node.value, int):
            raise ValueError(
                "float/array constants are refused; pass decimals as "
                "explicit string variables (this is the honest-exact rule)")
        return _Iv(Decimal(node.value), Decimal(node.value))
    if isinstance(node, ast.Name):
        name = node.id
        if name in env:
            return env[name]
        raise ValueError(
            "unknown name '%s'; only declared variables and these "
            "functions are allowed: %s" % (name, ", ".join(FUNCS)))
    if isinstance(node, ast.Call):
        fn = node.func
        if not isinstance(fn, ast.Name) or fn.id not in FUNCS:
            raise ValueError("call refused: only %s allowed" %
                             "/".join(FUNCS))
        if len(node.args) != 1 or node.keywords:
            raise ValueError("call %s takes exactly one argument" % fn.id)
        x = _eval_node(node.args[0], info, c, env)
        info["funcs_used"].add(fn.id)
        if fn.id == "abs":
            return _iv_abs(x)
        if fn.id == "sqrt":
            if x.lo < 0:
                raise ValueError("sqrt of an interval with lower < 0 "
                                 "(domain violation)")
            return _Iv(c.dn.sqrt(x.lo), c.up.sqrt(x.hi))
        if fn.id == "exp":
            return _Iv(c.dn.exp(x.lo), c.up.exp(x.hi))
        if fn.id == "ln":
            if x.lo <= 0:
                raise ValueError("ln of an interval touching or below "
                                 "zero (domain violation)")
            return _Iv(c.dn.ln(x.lo), c.up.ln(x.hi))
        if fn.id == "log10":
            if x.lo <= 0:
                raise ValueError("log10 of an interval touching or below "
                                 "zero (domain violation)")
            return _Iv(c.dn.log10(x.lo), c.up.log10(x.hi))
    raise ValueError("AST node refused: %s (whitelist only) -- no eval, "
                     "no attribute access, no arbitrary calls" % kind)


def iv_eval(params: dict) -> dict:
    expr = params.get("expr")
    if not isinstance(expr, str) or not expr.strip():
        raise ValueError("expr: expression string required")
    if len(expr) > _MAX_EXPR_CHARS:
        raise ValueError("expr: at most %d characters" % _MAX_EXPR_CHARS)
    digits = int(params.get("digits") or _DIGITS_DEF)
    if not _DIGITS_MIN <= digits <= _DIGITS_MAX:
        raise ValueError(
            "digits: integer in [%d, %d]" % (_DIGITS_MIN, _DIGITS_MAX))
    vars_in = params.get("vars") or {}
    if not isinstance(vars_in, dict):
        raise ValueError("vars: object mapping name -> number or "
                         "'[lo, hi]' string")
    if len(vars_in) > _MAX_VARS:
        raise ValueError("vars: at most %d variables" % _MAX_VARS)
    env: dict[str, _Iv] = {}
    for name, raw in vars_in.items():
        name = str(name)
        if not _NAME_OK.fullmatch(name) or name in FUNCS:
            raise ValueError("variable name refused: %r" % name)
        env[name] = _parse_var(name, raw)

    try:
        tree = ast.parse(expr, mode="eval")
    except SyntaxError as exc:
        raise ValueError("expr not parseable: %s" % exc.msg) from exc
    info: dict = {"nodes": 0, "kinds": set(), "funcs_used": set()}
    try:
        result_iv = _eval_node(tree, info, _Ctx(digits), env)
    except DecimalException as exc:
        raise ValueError(
            "decimal arithmetic failed (precision/magnitude): %s "
            "-- reduce the expression scale or lower digits" % exc) from exc
    return {
        "schema": "t2n_science.iv.v1",
        "expr": expr,
        "vars": {k: "[%s, %s]" % (v.lo, v.hi) for k, v in env.items()},
        "digits": digits,
        "lower": str(result_iv.lo),
        "upper": str(result_iv.hi),
        "width_note": ("point-width" if result_iv.lo == result_iv.hi
                       else "outward-rounded width"),
        "computational": {"nodes": info["nodes"],
                          "kinds": sorted(info["kinds"]),
                          "functions_used": sorted(info["funcs_used"])},
        "honesty": ("outward rounding at %d digits: endpoints are "
                    "reliable BOUNDS (may be wider, never narrower)"
                    % digits),
    }


# ------------------------------------------------------------- frac compare --
def _frac_node(node: ast.AST, info: dict) -> Fraction:
    info["nodes"] += 1
    if info["nodes"] > _MAX_NODES:
        raise ValueError("expression too complex: more than %d nodes"
                         % _MAX_NODES)
    if isinstance(node, ast.Expression):
        return _frac_node(node.body, info)
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
        return (_frac_node(node.left, info)
                + _frac_node(node.right, info))
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Sub):
        return (_frac_node(node.left, info)
                - _frac_node(node.right, info))
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Mult):
        return (_frac_node(node.left, info)
                * _frac_node(node.right, info))
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div):
        den = _frac_node(node.right, info)
        if den == 0:
            raise ValueError("division by zero in rational expression")
        return _frac_node(node.left, info) / den
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
        return -_frac_node(node.operand, info)
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.UAdd):
        return _frac_node(node.operand, info)
    if isinstance(node, ast.Constant):
        if isinstance(node.value, bool) or not isinstance(node.value, int):
            raise ValueError("only INTEGER literals allowed in rational "
                             "mode; write decimals as p/q (exact)")
        return Fraction(node.value)
    raise ValueError("AST node refused: %s (rational whitelist only)"
                     % type(node).__name__)


def frac_compare(params: dict) -> dict:
    left, right = params.get("left"), params.get("right")
    for obj, label in ((left, "left"), (right, "right")):
        if not isinstance(obj, str) or not obj.strip():
            raise ValueError("%s: expression string required" % label)
        if len(obj) > _MAX_EXPR_CHARS:
            raise ValueError("%s: at most %d characters"
                             % (label, _MAX_EXPR_CHARS))
    out = {}
    info: dict = {"nodes": 0}
    try:
        l_tree = ast.parse(left, mode="eval")
        out["left_exact"] = str(_frac_node(l_tree, info))
        out["left_nodes"] = info["nodes"]
        info = {"nodes": 0}
        r_tree = ast.parse(right, mode="eval")
        out["right_exact"] = str(_frac_node(r_tree, info))
        out["right_nodes"] = info["nodes"]
    except SyntaxError as exc:
        raise ValueError("expression not parseable: %s" % exc.msg) from exc
    lf, rf = Fraction(out["left_exact"]), Fraction(out["right_exact"])
    diff = lf - rf
    symbol = "<" if diff < 0 else (">" if diff > 0 else "=")
    digits = int(params.get("digits") or _DIGITS_DEF)
    if not _DIGITS_MIN <= digits <= _DIGITS_MAX:
        raise ValueError(
            "digits: integer in [%d, %d]" % (_DIGITS_MIN, _DIGITS_MAX))
    neutral = Context(prec=digits, rounding=ROUND_HALF_EVEN)
    approx = neutral.divide(Decimal(diff.numerator),
                            Decimal(diff.denominator)) if diff else Decimal(0)
    out.update({
        "schema": "t2n_science.frac.v1",
        "left": left, "right": right,
        "symbol": symbol,
        "difference_exact": str(diff),
        "difference_decimal_approx": str(approx),
        "honesty": "EXACT rational arithmetic (fractions.Fraction); the "
                   "decimal value is an approximation of the exact "
                   "difference only",
    })
    return out


# ------------------------------------------------------------ ast float scan --
_FLOAT_MARKER = "T2N-FLOAT-ALLOW"
_DANGER_CALLS = {"eval", "exec", "compile", "__import__"}
_MAX_SCAN_PATHS, _MAX_SCAN_BYTES, _MAX_HITS = 8, 512 * 1024, 25


def ast_float_scan(params: dict) -> dict:
    paths = params.get("paths")
    if not isinstance(paths, list) or not paths:
        raise ValueError("paths: non-empty list of .py paths required")
    if len(paths) > _MAX_SCAN_PATHS:
        raise ValueError("paths: at most %d files per call"
                         % _MAX_SCAN_PATHS)
    strict = bool(params.get("strict", False))
    files, any_hits = [], False
    for raw in paths:
        p = _repo_path(str(raw))
        if p.suffix != ".py":
            raise ValueError("paths: only .py files accepted (%s)" % raw)
        if not p.is_file():
            raise FileNotFoundError(str(raw))
        if p.stat().st_size > _MAX_SCAN_BYTES:
            raise ValueError("path too large (> %d bytes): %s"
                             % (_MAX_SCAN_BYTES, raw))
        src = p.read_text(encoding="utf-8", errors="replace")
        lines = src.splitlines()
        try:
            tree = ast.parse(src, filename=str(raw))
        except SyntaxError as exc:
            files.append({"path": str(p.relative_to(REPO_ROOT)),
                          "verdict": "SYNTAX_ERROR",
                          "detail": "line %s: %s" % (exc.lineno, exc.msg)})
            any_hits = True                      # fail closed on unreadable code
            continue
        hit_rows: list[dict] = []
        counts = {"float_literal": 0, "waived_float": 0,
                  "float_call": 0, "danger_call": 0}
        for node in ast.walk(tree):
            row = None
            if isinstance(node, ast.Constant) and isinstance(node.value, float):
                line_text = (lines[node.lineno - 1]
                             if 0 < node.lineno <= len(lines) else "")
                if _FLOAT_MARKER in line_text:
                    counts["waived_float"] += 1
                else:
                    counts["float_literal"] += 1
                    row = {"kind": "float_literal", "line": node.lineno,
                           "col": node.col_offset + 1,
                           "value": repr(node.value)}
            elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                fname = node.func.id
                if fname in _DANGER_CALLS:
                    counts["danger_call"] += 1
                    row = {"kind": "danger_call", "line": node.lineno,
                           "col": node.col_offset + 1, "value": fname + "(...)"}
                elif fname == "float":
                    counts["float_call"] += 1
                    row = {"kind": "float_call", "line": node.lineno,
                           "col": node.col_offset + 1, "value": "float(...)"}
            if row is not None and len(hit_rows) < _MAX_HITS:
                hit_rows.append(row)
        blocked = (counts["float_literal"] > 0 or counts["float_call"] > 0
                   or counts["danger_call"] > 0)
        any_hits = any_hits or blocked
        files.append({"path": str(p.relative_to(REPO_ROOT)),
                      "verdict": "HITS" if blocked else "CLEAN",
                      "counts": counts,
                      "hits": hit_rows,
                      "note": ("waiver marker: a line containing "
                               "'%s' allows its own float literal"
                               % _FLOAT_MARKER)})
    refused = strict and any_hits
    return {"schema": "t2n_science.scan.v1",
            "strict": strict,
            "verdict": "REFUSED" if refused
                       else ("RISK" if any_hits else "CLEAN"),
            "files": files,
            "honesty": "AST-based scan (never text regex); strict=True "
                       "fails any non-waived float usage or danger call"}


TOOLS = [
    {"name": "iv_eval",
     "description": ("Interval arithmetic with OUTWARD rounding "
                     "(stdlib decimal; ROUND_FLOOR/ROUND_CEILING). "
                     "Expression via closed AST whitelist: + - * / , "
                     "unary signs, integer power |n|<=32, "
                     "sqrt/exp/ln/log10/abs, and variables as decimal "
                     "strings ('[lo, hi]' or one point). No eval anywhere."),
     "inputSchema": {"type": "object",
                     "properties": {"expr": {"type": "string"},
                                    "vars": {"type": "object"},
                                    "digits": {"type": "integer"}},
                     "required": ["expr"], "additionalProperties": False}},
    {"name": "frac_compare",
     "description": ("Exact rational comparison via Fraction: integer "
                     "literals with parentheses, + - * / and unary signs. "
                     "Returns exact difference and a decimal approximation."),
     "inputSchema": {"type": "object",
                     "properties": {"left": {"type": "string"},
                                    "right": {"type": "string"},
                                    "digits": {"type": "integer"}},
                     "required": ["left", "right"],
                     "additionalProperties": False}},
    {"name": "ast_float_scan",
     "description": ("AST-based float-literal / float() / eval-exec/"
                     "compile-__import__ scan of repo .py files. "
                     "strict=True returns REFUSED unless every hit is "
                     "waived by the line marker T2N-FLOAT-ALLOW."),
     "inputSchema": {"type": "object",
                     "properties": {"paths": {"type": "array",
                                              "items": {"type": "string"},
                                              "minItems": 1},
                                    "strict": {"type": "boolean"}},
                     "required": ["paths"], "additionalProperties": False}},
]

HANDLERS = {
    "iv_eval": iv_eval,
    "frac_compare": frac_compare,
    "ast_float_scan": ast_float_scan,
}

DESCRIPTION = (
    "T-hat-N science (F3): whitelist-only interval evaluator (outward "
    "rounding), exact rational comparisons, and AST float/danger-call "
    "scanning. Stateless; no eval; stdlib only (mpmath may join later).")

if __name__ == "__main__":
    serve_generic("t2n_science", DESCRIPTION, TOOLS, HANDLERS)
