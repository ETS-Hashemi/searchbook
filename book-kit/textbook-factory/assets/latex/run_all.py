#!/usr/bin/env python3
"""Run the self-test of every chapter's reference implementation.

Usage: python3 code/run_all.py        (from the Overleaf/ directory)
Each chNN_*.py file runs its own self-test when executed; this script runs them all,
reports pass/fail and the time taken, and exits non-zero if any test fails.
"""
import glob, os, subprocess, sys, time

here = os.path.dirname(os.path.abspath(__file__))
files = sorted(f for f in glob.glob(os.path.join(here, "ch*_*.py")))
failed = []
for f in files:
    t0 = time.time()
    r = subprocess.run([sys.executable, f], capture_output=True, text=True, timeout=600, cwd=os.path.dirname(here))
    dt = time.time() - t0
    ok = r.returncode == 0
    optional = (not ok) and ("ModuleNotFoundError: No module named 'torch'" in r.stderr)
    tag = 'PASS' if ok else ('SKIP' if optional else 'FAIL')
    print(f"{tag}  {os.path.basename(f):32s} {dt:6.1f} s" + ("  (optional: needs PyTorch)" if optional else ""))
    if not ok and not optional:
        failed.append(f)
        print((r.stdout + r.stderr)[-800:])
print(f"\n{len(files) - len(failed)}/{len(files)} self-tests passed")
sys.exit(1 if failed else 0)
