"""Shape algebra: flattening, integer circulant operators, and a DFT guard.

The Lean ``Shape`` type has no payload. Its Python mirror keeps only the
constructor tree, and ``flatten`` counts leaves exactly as the locked
pre-registration defines. ``H_hat`` and ``T_hat`` are built as exact integer
matrices; the DFT certificate uses Arb only to check that the construction
really is diagonalised by the Fourier matrix.

Everything here is a construction guard. A circulant commutes with a
circulant by construction, so the commutation result is tautological and is
labelled as such by the caller.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence

from flint import acb, acb_mat, arb, ctx

__all__ = [
    "Matrix",
    "Shape",
    "point",
    "line",
    "plane",
    "space",
    "flatten",
    "leaf_count",
    "shape_to_obj",
    "identity",
    "ones",
    "add",
    "mul",
    "transpose",
    "circulant",
    "shift",
    "shape_operators",
    "is_circulant",
    "DftCertificate",
    "dft_certificate",
]

Matrix = tuple[tuple[int, ...], ...]

_ARITY = {"point": 0, "line": 2, "plane": 3}


@dataclass(frozen=True)
class Shape:
    """Mirror of the Lean inductive ``Shape``.

    ``space`` accepts any number of children (including zero); the operator
    builders reject the empty case because no 0x0 matrix is claimed.
    """

    tag: str
    children: tuple["Shape", ...] = ()

    def __post_init__(self) -> None:
        if self.tag not in (*_ARITY, "space"):
            raise ValueError(f"unknown Shape constructor: {self.tag!r}")
        if self.tag != "space" and len(self.children) != _ARITY[self.tag]:
            raise ValueError(
                f"Shape.{self.tag} expects {_ARITY[self.tag]} children, "
                f"got {len(self.children)}"
            )
        if not all(isinstance(child, Shape) for child in self.children):
            raise TypeError("Shape children must themselves be Shape values")


def point() -> Shape:
    return Shape("point")


def line(left: Shape, right: Shape) -> Shape:
    return Shape("line", (left, right))


def plane(a: Shape, b: Shape, c: Shape) -> Shape:
    return Shape("plane", (a, b, c))


def space(*children: Shape) -> Shape:
    return Shape("space", tuple(children))


def flatten(shape: Shape) -> tuple[int, ...]:
    """Return the leaf weights in left-to-right order.

    ``point`` contributes one ``1``; every other constructor concatenates its
    children. The traversal is iterative so a long ``advance`` chain cannot
    overflow the Python recursion limit.
    """
    out: list[int] = []
    stack: list[Shape] = [shape]
    while stack:
        node = stack.pop()
        if node.tag == "point":
            out.append(1)
        else:
            stack.extend(reversed(node.children))
    return tuple(out)


def leaf_count(shape: Shape) -> int:
    return len(flatten(shape))


def shape_to_obj(shape: Shape) -> object:
    """Deterministic JSON-friendly tree, used for state hashing."""
    root: list[object] = []
    stack: list[tuple[Shape, list[object]]] = [(shape, root)]
    while stack:
        node, target = stack.pop()
        target.append(node.tag)
        if node.tag != "point":
            children: list[object] = []
            target.append(children)
            for child in reversed(node.children):
                stack.append((child, children))
    return root[0]


def _empty(n: int) -> list[list[int]]:
    if n < 1:
        raise ValueError(f"matrix dimension must be positive, got {n}")
    return [[0] * n for _ in range(n)]


def identity(n: int) -> Matrix:
    rows = _empty(n)
    for i in range(n):
        rows[i][i] = 1
    return tuple(tuple(row) for row in rows)


def ones(n: int) -> Matrix:
    return tuple(tuple(1 for _ in range(n)) for _ in range(n))


def add(left: Matrix, right: Matrix) -> Matrix:
    if len(left) != len(right) or len(left[0]) != len(right[0]):
        raise ValueError("matrix shapes differ")
    return tuple(
        tuple(a + b for a, b in zip(row_l, row_r))
        for row_l, row_r in zip(left, right)
    )


def mul(left: Matrix, right: Matrix) -> Matrix:
    n, m = len(left), len(right[0])
    if len(left[0]) != len(right):
        raise ValueError("matrix shapes are not composable")
    out = _empty(n)
    for i in range(n):
        for k in range(len(right)):
            aik = left[i][k]
            if aik == 0:
                continue
            for j in range(m):
                out[i][j] += aik * right[k][j]
    return tuple(tuple(row) for row in out)


def transpose(matrix: Matrix) -> Matrix:
    return tuple(tuple(matrix[j][i] for j in range(len(matrix))) for i in range(len(matrix[0])))


def circulant(first_row: Sequence[int]) -> Matrix:
    """Circulant with ``row[i][j] = first_row[(j - i) mod n]``."""
    n = len(first_row)
    if n < 1:
        raise ValueError("circulant needs at least one entry")
    return tuple(
        tuple(int(first_row[(j - i) % n]) for j in range(n))
        for i in range(n)
    )


def shift(n: int) -> Matrix:
    """Cyclic shift with ``T[i][(i + 1) mod n] = 1``."""
    if n < 1:
        raise ValueError(f"shift dimension must be positive, got {n}")
    first = [0] * n
    if n > 1:
        first[1] = 1
    return circulant(first)


def is_circulant(matrix: Matrix) -> bool:
    n = len(matrix)
    if n == 0 or any(len(row) != n for row in matrix):
        return False
    first = matrix[0]
    return all(
        matrix[i][j] == first[(j - i) % n]
        for i in range(n)
        for j in range(n)
    )


def shape_operators(shape: Shape) -> tuple[Matrix, Matrix]:
    """Return ``(H_hat, T_hat)`` for the shape.

    ``H_hat = I + J`` is the canonical symmetric circulant on the unlabelled
    leaf set; ``T_hat`` is the cyclic shift. Both are exact integer matrices.
    """
    n = leaf_count(shape)
    if n == 0:
        raise ValueError("empty Shape has no operator: 0x0 is not defined")
    return add(identity(n), ones(n)), shift(n)


def _require_precision(min_bits: int = 200) -> None:
    if ctx.prec < min_bits:
        raise RuntimeError(
            f"Arb precision {ctx.prec} is below the required {min_bits} bits; "
            "call msaf.precision.set_precision() before using the DFT guard"
        )


@dataclass(frozen=True)
class DftCertificate:
    """Enclosure data for ``F A F*``.

    ``off_diagonal_sum_upper`` bounds every off-diagonal entry (the sum of
    their absolute values is an upper bound on the maximum). The diagonal is
    returned as Acb balls so the caller can compare it against the expected
    eigenvalues of the specific operator.
    """

    dim: int
    off_diagonal_sum_upper: arb
    diagonal: tuple[acb, ...]


def dft_certificate(matrix: Matrix) -> DftCertificate:
    """Compute ``F A F*`` with Arb and bound the off-diagonal mass.

    ``F[j, k] = exp(-2*pi*i*j*k/n) / sqrt(n)``. The root is stepped by
    multiplication inside each row, so only ``n`` exponentials are evaluated;
    every remaining operation is a ball multiplication.
    """
    _require_precision()
    n = len(matrix)
    if n == 0 or any(len(row) != n for row in matrix):
        raise ValueError("matrix must be square and non-empty")

    norm = acb(arb(n).sqrt())
    base = acb_mat(n, n)
    pi = arb.pi()
    for j in range(n):
        step = acb(0, -2 * pi * j / n).exp()
        value = acb(1) / norm
        for k in range(n):
            base[j, k] = value
            value = value * step

    exact = acb_mat(n, n)
    for i in range(n):
        for j in range(n):
            exact[i, j] = acb(matrix[i][j])

    transformed = base * exact * base.conjugate()

    off_diagonal = arb(0)
    for i in range(n):
        for j in range(n):
            if i != j:
                off_diagonal += abs(transformed[i, j])

    return DftCertificate(
        dim=n,
        off_diagonal_sum_upper=off_diagonal,
        diagonal=tuple(transformed[i, i] for i in range(n)),
    )
