#!/usr/bin/env python3
"""Auxiliary checks for audit A-2026-0002 (see AUDIT_BB5_PREREG_2026-10-18.md).

Subcommands:
  sha256lf PATH...     print LF-normalized sha256 (registry convention)
  weld-tar TGZ CLONE   compare a source tarball against a git clone tree
  bb3-max CSV          replay all halt rows of the BB3 enumeration CSV
                       (uses engine P or Q via --engine)
"""
import argparse
import csv
import hashlib
import json
import os
import sys
import tarfile


def sha256lf_bytes(data):
    return hashlib.sha256(data.replace(b"\r\n", b"\n")).hexdigest()


def cmd_sha256lf(args):
    for path in args.paths:
        with open(path, "rb") as fh:
            digest = sha256lf_bytes(fh.read())
        print("sha256LF %s %s" % (digest, path.replace(os.sep, "/")))
    return 0


def _file_sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def cmd_weld_tar(args):
    tar_tree = {}
    with tarfile.open(args.tarball, "r:gz") as tf:
        for member in tf.getmembers():
            if not member.isfile():
                continue
            parts = member.name.split("/")
            name = "/".join(parts[1:]) if len(parts) > 1 else parts[0]
            fobj = tf.extractfile(member)
            tar_tree[name] = hashlib.sha256(fobj.read()).hexdigest()
    clone_tree = {}
    for dirpath, dirnames, filenames in os.walk(args.clone):
        dirnames[:] = [d for d in dirnames if d != ".git"]
        for filename in filenames:
            full = os.path.join(dirpath, filename)
            rel = os.path.relpath(full, args.clone).replace(os.sep, "/")
            clone_tree[rel] = _file_sha256(full)
    only_tar = sorted(set(tar_tree) - set(clone_tree))
    only_clone = sorted(set(clone_tree) - set(tar_tree))
    changed = sorted(k for k in set(tar_tree) & set(clone_tree)
                     if tar_tree[k] != clone_tree[k])
    out = {
        "tarball": args.tarball,
        "clone": args.clone,
        "file_counts": {"tarball": len(tar_tree), "clone": len(clone_tree)},
        "only_in_tarball": only_tar,
        "only_in_clone": only_clone,
        "changed": changed,
        "identical": len(tar_tree) - len(only_tar) - len(changed),
    }
    text = json.dumps(out, indent=2, sort_keys=True)
    if args.out:
        with open(args.out, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(text + "\n")
    print(text)
    return 0

CANDIDATES = [
    "1RB---_1LB0RC_1LC1LA",
    "1RB---_0RC1RB_1LC1LA",
    "1RB1RZ_1LB0RC_1LC1LA",
    "1RB1RZ_0RC1RB_1LC1LA",
]


def cmd_bb3_max(args):
    here = os.path.dirname(os.path.abspath(__file__))
    if here not in sys.path:
        sys.path.insert(0, here)
    if args.engine == "p":
        import bb5_engine_p as engine
    else:
        import bb5_engine_q as engine

    rows = []
    with open(args.csv, newline="", encoding="utf-8") as fh:
        reader = csv.reader(fh)
        try:
            header = next(reader)
        except StopIteration:
            raise SystemExit("empty csv")
        for row in reader:
            if len(row) >= 2:
                machine = row[0].strip()
                status = row[1].strip()
                decider = row[2].strip() if len(row) > 2 else ""
                rows.append((machine, status, decider))

    status_counts = {}
    machines = set()
    duplicates = set()
    parse_issues = []
    for machine, status, _decider in rows:
        status_counts[status] = status_counts.get(status, 0) + 1
        if machine in machines:
            duplicates.add(machine)
        machines.add(machine)
        groups = machine.split("_")
        if len(groups) != 3 or any(len(g) != 6 for g in groups):
            parse_issues.append(machine)

    best_steps = -1
    best_steps_machines = []
    best_ones = -1
    best_ones_machines = []
    anomalies = []
    replayed = 0
    for machine, status, _decider in rows:
        if status != "halt":
            continue
        replayed += 1
        try:
            steps, ones, _kind = engine.simulate(machine, args.max_steps)
        except Exception as exc:  # recorded, not raised
            anomalies.append({"machine": machine, "error": str(exc)})
            continue
        if steps > best_steps:
            best_steps, best_steps_machines = steps, [machine]
        elif steps == best_steps:
            best_steps_machines.append(machine)
        if ones > best_ones:
            best_ones, best_ones_machines = ones, [machine]
        elif ones == best_ones:
            best_ones_machines.append(machine)

    out = {
        "csv": args.csv,
        "engine": "P" if args.engine == "p" else "Q",
        "header": header,
        "data_rows": len(rows),
        "unique_machines": len(machines),
        "duplicate_rows": sorted(duplicates),
        "status_counts": status_counts,
        "halt_rows_replayed": replayed,
        "max_steps": best_steps,
        "max_steps_machines": sorted(best_steps_machines),
        "max_ones": best_ones,
        "max_ones_machines": sorted(best_ones_machines),
        "anomalies": anomalies,
        "parse_issues": parse_issues,
        "candidate_presence": {c: (c in machines) for c in CANDIDATES},
    }
    text = json.dumps(out, indent=2, sort_keys=True)
    if args.out:
        with open(args.out, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(text + "\n")
    print(text)
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)

    p1 = sub.add_parser("sha256lf")
    p1.add_argument("paths", nargs="+")
    p1.set_defaults(func=cmd_sha256lf)

    p2 = sub.add_parser("weld-tar")
    p2.add_argument("tarball")
    p2.add_argument("clone")
    p2.add_argument("--out")
    p2.set_defaults(func=cmd_weld_tar)

    p3 = sub.add_parser("bb3-max")
    p3.add_argument("csv")
    p3.add_argument("--engine", choices=("p", "q"), default="p")
    p3.add_argument("--max-steps", type=int, default=10 ** 6)
    p3.add_argument("--out")
    p3.set_defaults(func=cmd_bb3_max)

    args = ap.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())


