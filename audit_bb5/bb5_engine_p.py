#!/usr/bin/env python3
"""BB(5) witness engine P (direct interpreter; frozen for audit A-2026-0002).

Pre-registered in reports/AUDIT_BB5_PREREG_2026-10-18.md. Stdlib only.

Semantics (frozen):
  - bbch standard format: underscore-separated state groups A..; each
    group is two 3-char clauses (read-0 then read-1): [01][LR][A-Z];
    target `Z` = halt; `---` = undefined (machine halts on that read,
    no write/move, not counted as a step).
  - start: all-zero tape, head at position 0, state A.
  - every executed clause counts as one step, including a clause whose
    target is Z (write and move are performed, then the machine halts).
  - S = executed clauses; Sigma = number of 1s on the tape at halt.

Usage:
  python3 bb5_engine_p.py --out FILE        run battery, write JSON
  python3 bb5_engine_p.py --machine STR     simulate one machine
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
    n = len(groups)
    trans = []
    for gi, g in enumerate(groups):
        if len(g) != 6:
            raise ValueError("group %d has length %d, expected 6" % (gi, len(g)))
        row = []
        for si in (0, 1):
            cl = g[3 * si:3 * si + 3]
            if cl == "---":
                row.append(None)
                continue
            w, d, st = cl[0], cl[1], cl[2]
            if w not in "01":
                raise ValueError("bad write symbol %r in %r" % (cl, g))
            if d not in "LR":
                raise ValueError("bad direction %r in %r" % (cl, g))
            if st == "Z":
                nxt = -1
            elif "A" <= st <= "Y":
                nxt = ord(st) - 65
                if nxt >= n:
                    raise ValueError("target state %s beyond machine in %r" % (st, g))
            else:
                raise ValueError("bad target state %r in %r" % (st, g))
            row.append((int(w), 1 if d == "R" else -1, nxt))
        trans.append(row)
    return trans


def simulate(machine, max_steps=10 ** 9):
    trans = parse_machine(machine)
    chunk = 1 << 12
    tape = [0] * chunk
    pos = chunk // 2
    state = 0
    steps = 0
    while True:
        t = trans[state][tape[pos]]
        if t is None:
            return steps, sum(tape), "undefined"
        w, d, nxt = t
        tape[pos] = w
        steps += 1
        if steps > max_steps:
            raise RuntimeError("max steps exceeded: machine did not halt")
        if nxt < 0:
            return steps, sum(tape), "z"
        state = nxt
        if d == 1:
            pos += 1
            if pos == len(tape):
                tape.extend([0] * chunk)
        else:
            pos -= 1
            if pos < 0:
                tape = [0] * chunk + tape
                pos = chunk - 1


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
        print("[P] %-14s steps=%-9d ones=%-6d halt=%s expected=(%d,%d) %s %.2fs"
              % (label, steps, ones, kind, exp_steps, exp_ones,
                 "MATCH" if match else "MISMATCH", dt))
    return {
        "engine": "P",
        "format": "bbch standard; Z counted; --- uncounted halt",
        "results": results,
        "all_match": all(r["match"] for r in results),
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description="BB(5) witness engine P")
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
    print("[P] all_match=%s" % out["all_match"])
    return 0 if out["all_match"] else 2


if __name__ == "__main__":
    sys.exit(main())
