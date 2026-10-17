# -*- coding: utf-8 -*-
"""Resolution-series runner -- executes the canonical sealed instrument
gw_montgomery.py under the resolution-series protocol used for the series
points dims 201 / 301 / 401 (measured 2026-10-16, seed 20260927, 2000
matched-N surrogates per ensemble).

This runner does NOT modify the instrument. It imports the sealed
gw_montgomery.py module from the OMEGA instrument folder, sets its
module-level SEED to the declared value (the instrument has no --seed
flag; for the series seed 20260927 this equals the instrument default,
so the measurement is bit-equivalent to the direct invocation used for
the earlier series points), and calls main() with stdout captured to a
log file.

PROVENANCE HEADER (additive). The earlier series logs carried only the
instrument's own banner; this wrapper adds spectrum sha256, instrument
sha256 + git revision, runner sha256, python version, threading
environment, declared seed/samples and wall-clock start/end -- without
touching instrument text or numbers.

EXACT COUNTS. The instrument prints its p values as %.4f; at 2000
samples that printout is exact at 5e-4 granularity, and this runner also
observes (does not alter) every np.mean of a boolean array so exact
integer counts k/2000 are appended to the log footer. The spy returns
the original value unchanged -- verdicts and printed numbers are
bit-identical to an unspied run. np.mean appears in the instrument ONLY
at its two p-value lines (upper and lower tail), so exactly 36 captures
are expected: 6 cells x 3 kinds x 2 tails.

Usage (fourth series point, dim 501):
    python msaf/gw_series_run.py --spectrum reports/gw_spectrum_100_250.json \
        --samples 2000 --seed 20260927 --log reports/mont_run_100_250.txt \
        --tag RES4_dim501

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
        fh.write("# RESOLUTION-SERIES RUN (canonical gw_montgomery.py; "
                 "protocol of dims 201/301/401, 2026-10-16)\n")
        fh.write("# pre-registration (this point) = "
                 "reports/RESOLUTION4_DIM501_PREREG_2026-10-17.md\n")
        fh.write("# tag = %s\n" % args.tag)
        fh.write("# runner = %s\n" % os.path.abspath(__file__))
        fh.write("# runner sha256 = %s\n"
                 % sha256_file(os.path.abspath(__file__)))
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
