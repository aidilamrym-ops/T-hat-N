# -*- coding: utf-8 -*-
"""H1 floor-refinement runner -- executes the FROZEN amendment
(reports/AMENDMENT_FLOOR_SPEC.md, sha256 in reports/HANDOFF.md section 1)
against the canonical sealed instrument.

This runner does NOT modify the instrument. It imports the sealed
gw_montgomery.py module from the OMEGA instrument folder, overrides its
module-level SEED (the spec freezes the five-seed array S5; the instrument
has no --seed flag, so the declared seed is injected here before main()),
and calls main() with stdout captured to a log file.

EXACT COUNTS. The frozen spec section 3 retires the 4-decimal p printout
("0.0000") and requires exact integer counts k/20000. The instrument
computes its p values as np.mean(boolean array) and prints only %.4f, so
this runner observes (does not alter) that single computation: during
main() every np.mean of a boolean array is recorded as (n, k) and the
exact counts are appended to the log footer. The spy returns the original
value unchanged -- verdicts and printed numbers are bit-identical to an
unspied run. np.mean appears in the instrument ONLY at its two p-value
lines (upper and lower tail), so exactly 36 captures are expected:
6 cells x 3 kinds x 2 tails.

Every produced log carries a provenance header: instrument path + sha256 +
git revision, spectrum sha256, seed, samples, tool versions, wall time --
the run manifest required by the frozen spec section 3.

Usage:
    python msaf/gw_h1_floor_refine.py --spectrum <path> --samples 20000 \
        --seed 20260927 --log reports/mont_run_20000_100_100.txt --tag A_dim201

The instrument folder is overridable via GW_INSTRUMENT_DIR.
"""

import argparse
import datetime
import hashlib
import json
import os
import subprocess
import sys
import time

import numpy as np

INSTRUMENT_DIR = os.environ.get(
    "GW_INSTRUMENT_DIR",
    r"D:\THE ASYMMETRIC WAGER\guinand-weil-rigorous-numerics-main")
INSTRUMENT = "gw_montgomery.py"


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def instrument_git_revision(path):
    try:
        out = subprocess.run(
            ["git", "-C", path, "log", "-1", "--format=%H %ci", "--",
             INSTRUMENT],
            capture_output=True, text=True, timeout=60)
        return out.stdout.strip() or "UNKNOWN"
    except Exception as exc:                      # pragma: no cover
        return "UNKNOWN (%r)" % (exc,)


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--spectrum", required=True)
    ap.add_argument("--samples", type=int, required=True)
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--log", required=True)
    ap.add_argument("--tag", required=True)
    args = ap.parse_args(argv[1:])

    spec = os.path.abspath(args.spectrum)
    log = os.path.abspath(args.log)
    inst_path = os.path.join(INSTRUMENT_DIR, INSTRUMENT)
    if not os.path.exists(spec):
        raise SystemExit("spectrum not found: %s" % spec)
    if not os.path.exists(inst_path):
        raise SystemExit("instrument not found: %s" % inst_path)

    sys.path.insert(0, INSTRUMENT_DIR)
    import gw_montgomery as g

    t0 = time.time()
    rc = 2
    el = 0.0
    captured = []
    orig_mean = np.mean

    def spy_mean(a, *a_args, **a_kwargs):
        result = orig_mean(a, *a_args, **a_kwargs)
        try:
            arr = np.asarray(a)
            if arr.dtype == bool:
                captured.append((int(arr.size), int(np.count_nonzero(arr))))
        except Exception:
            pass
        return result

    with open(log, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("=" * 96 + "\n")
        fh.write("# H1 FLOOR-REFINEMENT RUN (FROZEN SPEC: "
                 "reports/AMENDMENT_FLOOR_SPEC.md)\n")
        fh.write("# tag = %s\n" % args.tag)
        fh.write("# spectrum = %s\n" % spec)
        fh.write("# spectrum sha256 = %s\n" % sha256_file(spec))
        fh.write("# instrument = %s\n" % inst_path)
        fh.write("# instrument sha256 = %s\n" % sha256_file(inst_path))
        fh.write("# instrument git revision = %s\n"
                 % instrument_git_revision(INSTRUMENT_DIR))
        fh.write("# samples = %d   seed = %d (declared; injected as module "
                 "SEED)\n" % (args.samples, args.seed))
        fh.write("# exact-count spy: np.mean of boolean arrays observed "
                 "during main(); values returned unchanged\n")
        fh.write("# python = %s\n" % sys.version.replace("\n", " "))
        fh.write("# threading env = OPENBLAS_NUM_THREADS:%s OMP_NUM_THREADS:%s"
                 " (recorded for the manifest)\n"
                 % (os.environ.get("OPENBLAS_NUM_THREADS", "unset"),
                    os.environ.get("OMP_NUM_THREADS", "unset")))
        fh.write("# start = %s\n"
                 % datetime.datetime.now().isoformat(timespec="seconds"))
        fh.write("=" * 96 + "\n")
        fh.flush()

        g.SEED = args.seed
        np.mean = spy_mean
        old_stdout = sys.stdout
        sys.stdout = fh
        try:
            rc = g.main([INSTRUMENT, spec, "--samples", str(args.samples)])
        except BaseException as exc:
            fh.write("# EXCEPTION: %r\n" % (exc,))
            raise
        finally:
            np.mean = orig_mean
            sys.stdout = old_stdout
            el = time.time() - t0
            fh.write("=" * 96 + "\n")
            fh.write("# end = %s   elapsed = %.1f s   exit = %s\n"
                     % (datetime.datetime.now().isoformat(timespec="seconds"),
                        el, rc))
            fh.write("# EXACT COUNTS -- spy on np.mean of boolean arrays\n")
            fh.write("# order: per cell [T0.3, T0.5, T1.0, L0.3, L0.5, L1.0],"
                     " per kind [gue, goe, poisson], [upper, lower]\n")
            fh.write("# expected captures: 36 (6 cells x 3 kinds x 2 tails)\n")
            fh.write("# exact_counts = %s\n" % json.dumps(captured))
            fh.write("=" * 96 + "\n")

    print("DONE tag=%s elapsed=%.1f s exit=%s captures=%d log=%s"
          % (args.tag, el, rc, len(captured), log))
    return rc


if __name__ == "__main__":
    sys.exit(main(sys.argv))
