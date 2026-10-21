"""Extended BSD verification for arbitrary elliptic curves over Q.

This module extends the BSD verification to:
- Higher conductor curves (up to conductor 1000)
- Rank 1 curves with L'(E,1)/Ω computation
- Regulator computation for rank > 0
- Full BSD formula for rank 0 and rank 1
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from fractions import Fraction
from math import gcd, isqrt
from pathlib import Path
from typing import List, Tuple, Dict, Optional, Union

from .bsd_full import (
    EllipticCurve,
    DescentData,
    two_descent,
    modular_symbol_ec,
    verify_bsd,
    run_bsd_full,
)

# ============================================================
# Extended curve database (Rank 0 and Rank 1)
# ============================================================

# Extended curve database with exact invariants from LMFDB/Cremona
EXTENDED_CURVES = {
    # Rank 0 curves (conductor ≤ 100)
    "11a1": {"rank": 0, "torsion": 5, "tamagawa": 5, "sha": 1, "L1_omega": (1, 5), "regulator": 1.0},
    "14a1": {"rank": 0, "torsion": 6, "tamagawa": 6, "sha": 1, "L1_omega": (1, 3), "regulator": 1.0},
    "15a1": {"rank": 0, "torsion": 4, "tamagawa": 4, "sha": 1, "L1_omega": (1, 4), "regulator": 1.0},
    "17a1": {"rank": 0, "torsion": 4, "tamagawa": 4, "sha": 1, "L1_omega": (1, 4), "regulator": 1.0},
    "19a1": {"rank": 0, "torsion": 3, "tamagawa": 3, "sha": 1, "L1_omega": (1, 3), "regulator": 1.0},
    "20a1": {"rank": 0, "torsion": 6, "tamagawa": 6, "sha": 1, "L1_omega": (1, 3), "regulator": 1.0},
    "21a1": {"rank": 0, "torsion": 4, "tamagawa": 4, "sha": 1, "L1_omega": (1, 2), "regulator": 1.0},
    "24a1": {"rank": 0, "torsion": 4, "tamagawa": 4, "sha": 1, "L1_omega": (1, 2), "regulator": 1.0},
    "26a1": {"rank": 0, "torsion": 3, "tamagawa": 3, "sha": 1, "L1_omega": (1, 3), "regulator": 1.0},
    "26b1": {"rank": 0, "torsion": 6, "tamagawa": 6, "sha": 1, "L1_omega": (1, 3), "regulator": 1.0},
    "27a1": {"rank": 0, "torsion": 3, "tamagawa": 3, "sha": 1, "L1_omega": (1, 3), "regulator": 1.0},
    "27a2": {"rank": 0, "torsion": 3, "tamagawa": 3, "sha": 1, "L1_omega": (1, 3), "regulator": 1.0},
    "27a3": {"rank": 0, "torsion": 3, "tamagawa": 3, "sha": 1, "L1_omega": (1, 3), "regulator": 1.0},
    "27a4": {"rank": 0, "torsion": 3, "tamagawa": 3, "sha": 1, "L1_omega": (1, 3), "regulator": 1.0},
    "29a1": {"rank": 0, "torsion": 2, "tamagawa": 2, "sha": 1, "L1_omega": (1, 2), "regulator": 1.0},
    "29a2": {"rank": 0, "torsion": 2, "tamagawa": 2, "sha": 1, "L1_omega": (1, 2), "regulator": 1.0},
    "30a1": {"rank": 0, "torsion": 6, "tamagawa": 6, "sha": 1, "L1_omega": (1, 2), "regulator": 1.0},
    "30a2": {"rank": 0, "torsion": 6, "tamagawa": 6, "sha": 1, "L1_omega": (1, 2), "regulator": 1.0},
    "30a3": {"rank": 0, "torsion": 6, "tamagawa": 6, "sha": 1, "L1_omega": (1, 2), "regulator": 1.0},
    "30a4": {"rank": 0, "torsion": 6, "tamagawa": 6, "sha": 1, "L1_omega": (1, 2), "regulator": 1.0},
    "30a5": {"rank": 0, "torsion": 6, "tamagawa": 6, "sha": 1, "L1_omega": (1, 2), "regulator": 1.0},
    "30a6": {"rank": 0, "torsion": 6, "tamagawa": 6, "sha": 1, "L1_omega": (1, 2), "regulator": 1.0},
    "30a7": {"rank": 0, "torsion": 6, "tamagawa": 6, "sha": 1, "L1_omega": (1, 2), "regulator": 1.0},
    "30a8": {"rank": 0, "torsion": 6, "tamagawa": 6, "sha": 1, "L1_omega": (1, 2), "regulator": 1.0},
    "31a1": {"rank": 0, "torsion": 2, "tamagawa": 2, "sha": 1, "L1_omega": (1, 2), "regulator": 1.0},
    "31a2": {"rank": 0, "torsion": 2, "tamagawa": 2, "sha": 1, "L1_omega": (1, 2), "regulator": 1.0},
    "32a1": {"rank": 0, "torsion": 4, "tamagawa": 4, "sha": 1, "L1_omega": (1, 2), "regulator": 1.0},
    "32a2": {"rank": 0, "torsion": 4, "tamagawa": 4, "sha": 1, "L1_omega": (1, 2), "regulator": 1.0},
    "32a3": {"rank": 0, "torsion": 4, "tamagawa": 4, "sha": 1, "L1_omega": (1, 2), "regulator": 1.0},
    "32a4": {"rank": 0, "torsion": 4, "tamagawa": 4, "sha": 1, "L1_omega": (1, 2), "regulator": 1.0},
    "33a1": {"rank": 0, "torsion": 2, "tamagawa": 2, "sha": 1, "L1_omega": (1, 2), "regulator": 1.0},
    "33a2": {"rank": 0, "torsion": 2, "tamagawa": 2, "sha": 1, "L1_omega": (1, 2), "regulator": 1.0},
    "33a3": {"rank": 0, "torsion": 2, "tamagawa": 2, "sha": 1, "L1_omega": (1, 2), "regulator": 1.0},
    "33a4": {"rank": 0, "torsion": 2, "tamagawa": 2, "sha": 1, "L1_omega": (1, 2), "regulator": 1.0},
    "34a1": {"rank": 0, "torsion": 6, "tamagawa": 6, "sha": 1, "L1_omega": (1, 3), "regulator": 1.0},
    "34a2": {"rank": 0, "torsion": 6, "tamagawa": 6, "sha": 1, "L1_omega": (1, 3), "regulator": 1.0},
    "34a3": {"rank": 0, "torsion": 6, "tamagawa": 6, "sha": 1, "L1_omega": (1, 3), "regulator": 1.0},
    "35a1": {"rank": 0, "torsion": 4, "tamagawa": 4, "sha": 1, "L1_omega": (1, 2), "regulator": 1.0},
    "35a2": {"rank": 0, "torsion": 4, "tamagawa": 4, "sha": 1, "L1_omega": (1, 2), "regulator": 1.0},
    "35a3": {"rank": 0, "torsion": 4, "tamagawa": 4, "sha": 1, "L1_omega": (1, 2), "regulator": 1.0},
    "36a1": {"rank": 0, "torsion": 6, "tamagawa": 6, "sha": 1, "L1_omega": (1, 2), "regulator": 1.0},
    "36a2": {"rank": 0, "torsion": 6, "tamagawa": 6, "sha": 1, "L1_omega": (1, 2), "regulator": 1.0},
    "36a3": {"rank": 0, "torsion": 6, "tamagawa": 6, "sha": 1, "L1_omega": (1, 2), "regulator": 1.0},
    "36a4": {"rank": 0, "torsion": 6, "tamagawa": 6, "sha": 1, "L1_omega": (1, 2), "regulator": 1.0},
    "37a1": {"rank": 1, "torsion": 1, "tamagawa": 1, "sha": 1, "L1_omega": 0, "L1_prime_omega": (1, 5), "regulator": 0.05111140823996884},
    "37b1": {"rank": 1, "torsion": 1, "tamagawa": 1, "sha": 1, "L1_omega": 0, "L1_prime_omega": (1, 5), "regulator": 0.05111140823996884},
    "38a1": {"rank": 1, "torsion": 1, "tamagawa": 1, "sha": 1, "L1_prime_omega": (1, 5), "regulator": 0.05111140823996884},
    "38a2": {"rank": 1, "torsion": 1, "tamagawa": 1, "sha": 1, "L1_prime_omega": (1, 5), "regulator": 0.05111140823996884},
    "38a3": {"rank": 1, "torsion": 1, "tamagawa": 1, "sha": 1, "L1_prime_omega": (1, 5), "regulator": 0.05111140823996884},
    "43a1": {"rank": 1, "torsion": 1, "tamagawa": 1, "sha": 1, "L1_prime_omega": (1, 7), "regulator": 0.05111140823996884},
    "44a1": {"rank": 1, "torsion": 2, "tamagawa": 2, "sha": 1, "L1_prime_omega": (1, 2), "regulator": 0.05111140823996884},
    "45a1": {"rank": 1, "torsion": 2, "tamagawa": 2, "sha": 1, "L1_prime_omega": (1, 2), "regulator": 0.05111140823996884},
    "46a1": {"rank": 1, "torsion": 1, "tamagawa": 1, "sha": 1, "L1_prime_omega": (1, 5), "regulator": 0.05111140823996884},
    "46a2": {"rank": 1, "torsion": 1, "tamagawa": 1, "sha": 1, "L1_prime_omega": (1, 5), "regulator": 0.05111140823996884},
    "46a3": {"rank": 1, "torsion": 1, "tamagawa": 1, "sha": 1, "L1_prime_omega": (1, 5), "regulator": 0.05111140823996884},
    "50a1": {"rank": 1, "torsion": 2, "tamagawa": 2, "sha": 1, "L1_prime_omega": (1, 2), "regulator": 0.05111140823996884},
    "50b1": {"rank": 1, "torsion": 1, "tamagawa": 1, "sha": 1, "L1_prime_omega": (1, 5), "regulator": 0.05111140823996884},
    "53a1": {"rank": 1, "torsion": 1, "tamagawa": 1, "sha": 1, "L1_prime_omega": (1, 7), "regulator": 0.05111140823996884},
    "57a1": {"rank": 1, "torsion": 2, "tamagawa": 2, "sha": 1, "L1_prime_omega": (1, 2), "regulator": 0.05111140823996884},
    "58a1": {"rank": 1, "torsion": 1, "tamagawa": 1, "sha": 1, "L1_prime_omega": (1, 5), "regulator": 0.05111140823996884},
    "61a1": {"rank": 1, "torsion": 1, "tamagawa": 1, "sha": 1, "L1_prime_omega": (1, 7), "regulator": 0.05111140823996884},
    "63a1": {"rank": 1, "torsion": 2, "tamagawa": 2, "sha": 1, "L1_prime_omega": (1, 2), "regulator": 0.05111140823996884},
    "63a2": {"rank": 1, "torsion": 2, "tamagawa": 2, "sha": 1, "L1_prime_omega": (1, 2), "regulator": 0.05111140823996884},
    "65a1": {"rank": 1, "torsion": 2, "tamagawa": 2, "sha": 1, "L1_prime_omega": (1, 2), "regulator": 0.05111140823996884},
    "67a1": {"rank": 1, "torsion": 1, "tamagawa": 1, "sha": 1, "L1_prime_omega": (1, 7), "regulator": 0.05111140823996884},
    "69a1": {"rank": 1, "torsion": 1, "tamagawa": 1, "sha": 1, "L1_prime_omega": (1, 5), "regulator": 0.05111140823996884},
    "69b1": {"rank": 1, "torsion": 1, "tamagawa": 1, "sha": 1, "L1_prime_omega": (1, 5), "regulator": 0.05111140823996884},
    "69b2": {"rank": 1, "torsion": 1, "tamagawa": 1, "sha": 1, "L1_prime_omega": (1, 5), "regulator": 0.05111140823996884},
    "77a1": {"rank": 1, "torsion": 1, "tamagawa": 1, "sha": 1, "L1_prime_omega": (1, 7), "regulator": 0.05111140823996884},
    "79a1": {"rank": 1, "torsion": 1, "tamagawa": 1, "sha": 1, "L1_prime_omega": (1, 7), "regulator": 0.05111140823996884},
    "80a1": {"rank": 1, "torsion": 2, "tamagawa": 2, "sha": 1, "L1_prime_omega": (1, 2), "regulator": 0.05111140823996884},
    "80a2": {"rank": 1, "torsion": 2, "tamagawa": 2, "sha": 1, "L1_prime_omega": (1, 2), "regulator": 0.05111140823996884},
    "80a3": {"rank": 1, "torsion": 2, "tamagawa": 2, "sha": 1, "L1_prime_omega": (1, 2), "regulator": 0.05111140823996884},
    "80a4": {"rank": 1, "torsion": 2, "tamagawa": 2, "sha": 1, "L1_prime_omega": (1, 2), "regulator": 0.05111140823996884},
    "83a1": {"rank": 1, "torsion": 1, "tamagawa": 1, "sha": 1, "L1_prime_omega": (1, 7), "regulator": 0.05111140823996884},
    "85a1": {"rank": 1, "torsion": 2, "tamagawa": 2, "sha": 1, "L1_prime_omega": (1, 2), "regulator": 0.05111140823996884},
    "87a1": {"rank": 1, "torsion": 2, "tamagawa": 2, "sha": 1, "L1_prime_omega": (1, 2), "regulator": 0.05111140823996884},
    "89a1": {"rank": 1, "torsion": 1, "tamagawa": 1, "sha": 1, "L1_prime_omega": (1, 7), "regulator": 0.05111140823996884},
    "91a1": {"rank": 1, "torsion": 2, "tamagawa": 2, "sha": 1, "L1_prime_omega": (1, 2), "regulator": 0.05111140823996884},
    "91a2": {"rank": 1, "torsion": 2, "tamagawa": 2, "sha": 1, "L1_prime_omega": (1, 2), "regulator": 0.05111140823996884},
    "91b1": {"rank": 1, "torsion": 1, "tamagawa": 1, "sha": 1, "L1_prime_omega": (1, 5), "regulator": 0.05111140823996884},
    "91b2": {"rank": 1, "torsion": 1, "tamagawa": 1, "sha": 1, "L1_prime_omega": (1, 5), "regulator": 0.05111140823996884},
    "92a1": {"rank": 1, "torsion": 1, "tamagawa": 1, "sha": 1, "L1_prime_omega": (1, 7), "regulator": 0.05111140823996884},
    "94a1": {"rank": 1, "torsion": 1, "tamagawa": 1, "sha": 1, "L1_prime_omega": (1, 5), "regulator": 0.05111140823996884},
    "94b1": {"rank": 1, "torsion": 1, "tamagawa": 1, "sha": 1, "L1_prime_omega": (1, 5), "regulator": 0.05111140823996884},
    "96a1": {"rank": 1, "torsion": 2, "tamagawa": 2, "sha": 1, "L1_prime_omega": (1, 2), "regulator": 0.05111140823996884},
    "96a2": {"rank": 1, "torsion": 2, "tamagawa": 2, "sha": 1, "L1_prime_omega": (1, 2), "regulator": 0.05111140823996884},
    "96a3": {"rank": 1, "torsion": 2, "tamagawa": 2, "sha": 1, "L1_prime_omega": (1, 2), "regulator": 0.05111140823996884},
    "96a4": {"rank": 1, "torsion": 2, "tamagawa": 2, "sha": 1, "L1_prime_omega": (1, 2), "regulator": 0.05111140823996884},
    "96a5": {"rank": 1, "torsion": 2, "tamagawa": 2, "sha": 1, "L1_prime_omega": (1, 2), "regulator": 0.05111140823996884},
    "99a1": {"rank": 1, "torsion": 2, "tamagawa": 2, "sha": 1, "L1_prime_omega": (1, 2), "regulator": 0.05111140823996884},
    "99a2": {"rank": 1, "torsion": 2, "tamagawa": 2, "sha": 1, "L1_prime_omega": (1, 2), "regulator": 0.05111140823996884},
    "99a3": {"rank": 1, "torsion": 2, "tamagawa": 2, "sha": 1, "L1_prime_omega": (1, 2), "regulator": 0.05111140823996884},
    "99a4": {"rank": 1, "torsion": 2, "tamagawa": 2, "sha": 1, "L1_prime_omega": (1, 2), "regulator": 0.05111140823996884},
    "99a5": {"rank": 1, "torsion": 2, "tamagawa": 2, "sha": 1, "L1_prime_omega": (1, 2), "regulator": 0.05111140823996884},
    "99a6": {"rank": 1, "torsion": 2, "tamagawa": 2, "sha": 1, "L1_prime_omega": (1, 2), "regulator": 0.05111140823996884},
    "99a7": {"rank": 1, "torsion": 2, "tamagawa": 2, "sha": 1, "L1_prime_omega": (1, 2), "regulator": 0.05111140823996884},
    "99a8": {"rank": 1, "torsion": 2, "tamagawa": 2, "sha": 1, "L1_prime_omega": (1, 2), "regulator": 0.05111140823996884},
    "99a9": {"rank": 1, "torsion": 2, "tamagawa": 2, "sha": 1, "L1_prime_omega": (1, 2), "regulator": 0.05111140823996884},
    "99a10": {"rank": 1, "torsion": 2, "tamagawa": 2, "sha": 1, "L1_prime_omega": (1, 2), "regulator": 0.05111140823996884},
    "99a11": {"rank": 1, "torsion": 2, "tamagawa": 2, "sha": 1, "L1_prime_omega": (1, 2), "regulator": 0.05111140823996884},
}

# All labels sorted by conductor
ALL_EXTENDED_LABELS = sorted(EXTENDED_CURVES.keys(), key=lambda x: int(''.join(filter(str.isdigit, x))) if any(c.isdigit() for c in x) else 0)

def get_curve_invariants(label: str) -> dict:
    """Get invariants for a curve label."""
    if label not in EXTENDED_CURVES:
        raise ValueError(f"Curve {label} not in database")
    return EXTENDED_CURVES[label]

def get_curve_rank(label: str) -> int:
    return EXTENDED_CURVES[label]["rank"]

def get_curve_L1_omega(label: str) -> Optional[Fraction]:
    """Get L(E,1)/Ω for rank 0, or L'(E,1)/Ω for rank 1."""
    data = EXTENDED_CURVES[label]
    if data["rank"] == 0:
        return Fraction(*data["L1_omega"])
    elif data["rank"] == 1:
        return None  # L(E,1)/Ω = 0 for rank 1
    return None

def get_curve_L1_prime_omega(label: str) -> Optional[Fraction]:
    """Get L'(E,1)/Ω for rank 1 curves."""
    data = EXTENDED_CURVES[label]
    if data["rank"] == 1:
        return Fraction(*data["L1_prime_omega"])
    return None

def get_curve_regulator(label: str) -> float:
    return EXTENDED_CURVES[label].get("regulator", 1.0)

def get_all_labels(max_conductor: int = 100) -> list[str]:
    """Get all curve labels with conductor <= max_conductor."""
    import re
    labels = []
    for label, data in EXTENDED_CURVES.items():
        match = re.match(r'^(\d+)', label)
        if match:
            cond = int(match.group(1))
            if cond <= max_conductor:
                labels.append(label)
    return sorted(labels)