#!/usr/bin/env python3
"""E2 - lrand48/srand48 reimplementation, pure Python, from the POSIX spec.
V1 audit (ECDSA seed origins). FROZEN at the V1 freeze commit.
Mirrors engine_e1.c (usage and semantics identical).
Usage:
  e2.py draws <t> <k>
  e2.py cand <t> <per> <shift> <width> <n>
  e2.py scan <t> <per> <shift> <width> <target_hex> <nmax>
"""
import sys

A = 0x5DEECE66D
C = 0xB
MASK = (1 << 48) - 1


def srand48(t: int) -> int:
    return ((t & 0xFFFFFFFF) << 16) | 0x330E


def step(x: int) -> int:
    return (A * x + C) & MASK


def draws(t: int, k: int):
    x = srand48(t)
    for _ in range(k):
        x = step(x)
        yield x >> 17


def cand(t: int, per: int, shift: int, width: int, n: int) -> str:
    x = srand48(t)
    keep = []
    for i in range(per * n):
        x = step(x)
        if i >= per * (n - 1):
            keep.append(x)
    return "".join(f"{s >> shift:0{width}X}" for s in keep)


def scan(t: int, per: int, shift: int, width: int, target: str, nmax: int):
    tgt = "".join(target.split()).upper()
    if len(tgt) != per * width:
        return None
    x = srand48(t)
    slots = [0] * per
    for i in range(1, per * nmax + 1):  # nmax counts candidates; one candidate = per draws
        x = step(x)
        slots[(i - 1) % per] = x
        if i % per == 0:
            if "".join(f"{s >> shift:0{width}X}" for s in slots) == tgt:
                return i // per  # candidate index n'
    return None


def main(argv):
    if len(argv) == 4 and argv[1] == "draws":
        t, k = int(argv[2]), int(argv[3])
        print("\n".join(f"{v:08X}" for v in draws(t, k)))
        return 0
    if len(argv) == 7 and argv[1] == "cand":
        print(cand(int(argv[2]), int(argv[3]), int(argv[4]), int(argv[5]), int(argv[6])))
        return 0
    if len(argv) == 8 and argv[1] == "scan":
        r = scan(int(argv[2]), int(argv[3]), int(argv[4]), int(argv[5]), argv[6], int(argv[7]))
        print("NONE" if r is None else r)
        return 0
    print(
        "usage: e2.py draws <t> <k> | e2.py cand <t> <per> <shift> <width> <n> | "
        "e2.py scan <t> <per> <shift> <width> <target> <nmax>",
        file=sys.stderr,
    )
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))


