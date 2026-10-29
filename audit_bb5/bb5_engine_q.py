#!/usr/bin/env python3
"""BB(5) witness engine Q (two-stack tape model; frozen for A-2026-0002).

Pre-registered in reports/AUDIT_BB5_PREREG_2026-10-18.md. Stdlib only.
Independent in structure from engine P: tape is two stacks (cells left
and right of the head, head cell separate); transitions are a flat
tuple-list indexed state*2+symbol.

Semantics (frozen, identical to engine P):
  - bbch standard format; `Z` target = halt after write+move, counted;
    `---` = undefined (halt on that read, uncounted).
  - start: all-zero tape, head position 0, state A.
  - S = executed clauses; Sigma = 1s on tape at halt.

Usage:
  python3 bb5_engine_q.py --out FILE        run battery, write JSON
  python3 bb5_engine_q.py --machine STR     simulate one machine
Exit codes: 0 ok; 2 battery mismatch; 3 malformed machine / limit.
"""
import argparse
import json
import sys
import time

BATTERY = [
    # (label, machine, expected_steps, expected_ones, source)
    ("classic-2state", "1RB1LB_1LA1RZ", 6, 4, "wiki BB(2) oldid 5358"),
    ("green-1964", "1LD1LB_1LZ1LA_0LB1LD_0LE0LD_1RE1RC", 79, 13, "wiki BB(5) oldid 9024 timeline"),
    ("brady-1964", "1RB1LD_0LC0RC_1LC1LA_1RZ0LA", 84, 11, "wiki BB(5) oldid 9024 timeline"),
    ("lee-1965", "1RB0RC_1LA1RA_1RZ1RD_1LD0LB", 96, 13, "wiki BB(5) oldid 9024 timeline"),
    ("brady-1966", "1RB1LB_1LA0LC_1RZ1LD_1RD0RA", 107, 13, "wiki BB(5) oldid 9024 timeline"),
    ("lynn-1972", "1RB1RA_1LC0LD_0RA1LB_1RZ0LE_1RC1RB", 435, 15, "wiki BB(5) oldid 9024 timeline"),
    ("weimann-1973", "1RB0LD_1RC0RB_1LA0RA_0LC0LE_1LC1RZ", 992, 23, "wiki BB(5) oldid 9024 timeline"),
    ("lynn-1974", "0RB1RZ_1RC0LD_1RD0RE_1LB0LD_1RE1RA", 7707, 88, "wiki BB(5) oldid 9024 timeline"),
    ("schult-1982", "1RB0LC_1RC1RD_1LA0RB_0RE1RZ_1LC1RA", 134467, 501, "wiki BB(5) oldid 9024 timeline"),
    ("uhing-1984", "1RB1LC_0LA0LD_1LA1RZ_1LB1RE_0RD0RB", 2133492, 1915, "wiki BB(5) oldid 9024 timeline"),
    ("feb-1986", "1RB1RZ_1LC1RC_0RE0LD_1LC0LB_1RD1RA", 2358064, 1471, "wiki BB(5) oldid 9024 timeline/top-halters"),
    ("mb89-sigma", "1RB1RA_1LC1LB_1RA1LD_1RA1LE_1RZ0LC", 11798826, 4098, "PRIMARY; wiki BB(5) oldid 9024 champions/top-halters; winner page oldid 4369"),
    ("mb89-runner", "1RB0LD_1LC1RD_1LA1LC_1RZ1RE_1RA0RB", 23554764, 4097, "wiki BB(5) oldid 9024 top-halters; michel/beh"),
    ("mb89-shift", "1RB1LC_1RC1RB_1RD0LE_1LA1LD_1RZ0LA", 47176870, 4098, "PRIMARY; wiki BB(5) oldid 9024 champions; winner page oldid 4369; michel/beh"),
    ("bb3-champion", "1RB1RZ_1LB0RC_1LC1LA", 21, 5, "wiki BB(3) oldid 8372"),
]


def parse_machine(s):
    groups = s.split("_")
    flat = []
    limit = len(groups)
    for g in groups:
        if len(g) != 6:
            raise ValueError("group %r has length %d, expected 6" % (g, len(g)))
        for si in (0, 1):
            cl = g[3 * si:3 * si + 3]
            if cl == "---":
                flat.append(None)
                continue
            if len(cl) != 3 or cl[0] not in "01" or cl[1] not in "LR":
                raise ValueError("bad clause %r" % cl)
            if cl[2] == "Z":
                nxt = -1
            elif "A" <= cl[2] <= "Y":
                nxt = ord(cl[2]) - 65
                if nxt >= limit:
                    raise ValueError("target %s beyond machine in %r" % (cl[2], g))
            else:
                raise ValueError("bad target %r" % cl[2])
            flat.append((int(cl[0]), 1 if cl[1] == "R" else -1, nxt))
    return flat


def simulate(machine, max_steps=10 ** 9):
    flat = parse_machine(machine)
    left = []   # cells strictly left of head; last = nearest to head
    right = []  # cells strictly right of head; last = nearest to head
    cur = 0
    state = 0
    steps = 0
    while True:
        t = flat[state * 2 + cur]
        if t is None:
            return steps, cur + sum(left) + sum(right), "undefined"
        w, d, nxt = t
        cur = w
        steps += 1
        if steps > max_steps:
            raise RuntimeError("max steps exceeded: machine did not halt")
        if nxt < 0:
            return steps, cur + sum(left) + sum(right), "z"
        state = nxt
        if d == 1:
            left.append(cur)
            cur = right.pop() if right else 0
        else:
            right.append(cur)
            cur = left.pop() if left else 0


def run_battery():
    results = []
    for label, machine, exp_steps, exp_ones, source in BATTERY:
        t0 = time.perf_counter()
        steps, ones, kind = simulate(machine)
        dt = time.perf_counter() - t0
        match = steps == exp_steps and ones == exp_ones
        results.append({
            "label": label,
            "machine": machine,
            "expected_steps": exp_steps,
            "expected_ones": exp_ones,
            "source": source,
            "steps": steps,
            "ones": ones,
            "halt_kind": kind,
            "match": match,
        })
        print("[Q] %-14s steps=%-9d ones=%-6d halt=%s expected=(%d,%d) %s %.2fs"
              % (label, steps, ones, kind, exp_steps, exp_ones,
                 "MATCH" if match else "MISMATCH", dt))
    return {
        "engine": "Q",
        "format": "bbch standard; Z counted; --- uncounted halt",
        "results": results,
        "all_match": all(r["match"] for r in results),
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description="BB(5) witness engine Q")
    ap.add_argument("--out")
    ap.add_argument("--machine")
    ap.add_argument("--max-steps", type=int, default=10 ** 9)
    a = ap.parse_args(argv)
    try:
        if a.machine:
            steps, ones, kind = simulate(a.machine, a.max_steps)
            print(json.dumps({"machine": a.machine, "steps": steps,
                              "ones": ones, "halt_kind": kind},
                             sort_keys=True))
            return 0
        out = run_battery()
    except (ValueError, RuntimeError) as exc:
        print("ERROR: %s" % exc, file=sys.stderr)
        return 3
    text = json.dumps(out, indent=2, sort_keys=True)
    if a.out:
        with open(a.out, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(text + "\n")
    else:
        print(text)
    print("[Q] all_match=%s" % out["all_match"])
    return 0 if out["all_match"] else 2


if __name__ == "__main__":
    sys.exit(main())


