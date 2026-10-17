#!/usr/bin/env python3
"""
zscan.py - internal-node stability scan (negative-resistance / Kurokawa check) with ngspice AC analysis.

Two-port K/mu cannot see loops that close inside a block (emitter followers, bias lines, a VCO's common mode,
cascode bases, supply/ground return). This script linearises the circuit at its DC operating point, injects
an AC test current at internal nodes and computes the small-signal impedance seen there:
    --node A          single-ended Z(A to ground)
    --diff P N        differential Z (current +1 into P, -1 into N) AND common-mode Z (+0.5 into each)
It reports every band where Re(Z) < 0 and the frequencies inside it where Im(Z) crosses zero: an oscillation
can start there if the rest of the loop is lossless enough (Kurokawa). For a VCO, the differential tank SHOULD
show a negative-R band containing the oscillation frequency; any OTHER negative band (common mode, buffers,
followers, far out of band) is a spurious-oscillation risk to fix (series base R, damping, emitter degeneration).

Node names inside subcircuits use ngspice's flattened form, e.g. xlo.vcop for node vcop of instance Xlo.
The testbench's own transient/control section is removed; its supplies and biases are kept.

usage: python3 zscan.py lo_core_hyb_tb.spice --diff xlo.vcop xlo.vcon --diff xlo.efp xlo.efn --fstop 100e9
"""
import argparse, os, re, subprocess, sys, tempfile
import numpy as np

NGSPICE = os.environ.get("NGSPICE", "ngspice")

def run_scan(text, wd, src_lines, exprs, fstart, fstop, pts, nodeset=()):
    t = re.sub(r"(?is)^\s*\.control.*?^\s*\.endc\s*$", "", text, flags=re.M)
    t = re.sub(r"(?im)^\s*\.(sp|ac|tran|noise|op|pss)\b.*$", "", t)
    t = re.sub(r"(?im)^\s*\.end\s*$", "", t)
    # transient-only stimuli (kick pulses etc.) must not move the DC point: keep their DC value only
    if nodeset:   # cross-coupled pairs: the symmetric DC point is an unstable equilibrium; hint the solver to it
        t += "\n.nodeset " + " ".join(f"v({k})={v}" for k, v in (x.split("=") for x in nodeset))
    t += "\n" + "\n".join(src_lines) + "\n.control\nset noaskquit\noption rshunt=1e12\n"
    t += f"ac dec {pts} {fstart:g} {fstop:g}\n"
    names = []
    for k, e in enumerate(exprs):
        t += f"let zr{k} = real({e})\nlet zi{k} = imag({e})\n"; names += [f"zr{k}", f"zi{k}"]
    with tempfile.NamedTemporaryFile("w", suffix=".spice", dir=wd, delete=False) as tf:
        out = tf.name.replace(".spice", ".txt")
        tf.write(t + f"wrdata {os.path.basename(out)} {' '.join(names)}\nquit\n.endc\n.end\n")
    r = subprocess.run([NGSPICE, "-b", os.path.basename(tf.name)], cwd=wd, capture_output=True, text=True)
    try:
        a = np.loadtxt(out)
    except Exception:
        print(r.stdout[-2000:], r.stderr[-2000:]); sys.exit("ngspice AC run failed (check node names, e.g. xlo.vcop)")
    finally:
        for p in (tf.name, out):
            try: os.remove(p)
            except OSError: pass
    f = a[:, 0]; cols = a[:, 1::2]                       # wrdata repeats the scale before every vector
    return f, [cols[:, 2 * k] + 1j * cols[:, 2 * k + 1] for k in range(len(exprs))]

def report(label, f, Z, band):
    neg = Z.real < 0
    print(f"\n  {label}: |Z| at {band/1e9:g} GHz = {abs(np.interp(band, f, Z.real) + 1j*np.interp(band, f, Z.imag)):.1f} ohm")
    if not neg.any():
        print("    Re(Z) > 0 over the whole sweep -> no negative-resistance band (passive-looking, stable)")
        return []
    edges = np.flatnonzero(np.diff(neg.astype(int))); starts = [0] if neg[0] else []
    segs, cur = [], None
    for i in range(len(f)):
        if neg[i] and cur is None: cur = i
        if (not neg[i] or i == len(f) - 1) and cur is not None:
            segs.append((cur, i if neg[i] else i - 1)); cur = None
    found = []
    for s, e in segs:
        x = Z.imag[s:e + 1]; cross = [f[s + j] for j in range(len(x) - 1) if np.sign(x[j]) != np.sign(x[j + 1])]
        rmin = Z.real[s:e + 1].min()
        print(f"    Re(Z) < 0 from {f[s]/1e9:7.2f} to {f[e]/1e9:7.2f} GHz (most negative {rmin:8.1f} ohm)"
              + (f"; Im(Z)=0 at {', '.join(f'{c/1e9:.2f}' for c in cross)} GHz  <-- possible oscillation" if cross else ""))
        found.append((f[s], f[e], cross))
    return found

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("netlist"); ap.add_argument("--node", action="append", default=[])
    ap.add_argument("--diff", nargs=2, action="append", default=[])
    ap.add_argument("--fstart", type=float, default=0.5e9); ap.add_argument("--fstop", type=float, default=100e9)
    ap.add_argument("--nodeset", nargs="*", default=[], help="DC hints, e.g. xlo.vcop=2.5 xlo.vcon=2.5")
    ap.add_argument("--pts", type=int, default=80); ap.add_argument("--fosc", type=float, default=24.1e9,
                    help="intended oscillation frequency: a negative-R band containing it on a --diff tank is expected")
    a = ap.parse_args()
    text = open(a.netlist).read(); wd = os.path.dirname(os.path.abspath(a.netlist)); bad = 0
    print(f"=== impedance scan of {os.path.basename(a.netlist)}, {a.fstart/1e9:g}-{a.fstop/1e9:g} GHz (DC operating point) ===")
    for n in a.node:
        f, (Z,) = run_scan(text, wd, [f"Izs_{0} 0 {n} dc 0 ac 1"], [f"v({n})"], a.fstart, a.fstop, a.pts, a.nodeset)
        bad += sum(1 for s_, e_, c in report(f"node {n} (single-ended)", f, Z, a.fosc) if c)   # only bands with Im(Z)=0 can start
    for p, n in a.diff:
        src = [f"Izd_p 0 {p} dc 0 ac 1", f"Izd_n {n} 0 dc 0 ac 1"]          # +1 A into p, -1 A into n
        f, (Zd,) = run_scan(text, wd, src, [f"v({p})-v({n})"], a.fstart, a.fstop, a.pts, a.nodeset)
        segs = report(f"{p} / {n} differential", f, Zd, a.fosc)
        bad += sum(1 for s, e, c in segs if c and not (s <= a.fosc <= e))    # the intended tank band is not a defect
        src = [f"Izc_p 0 {p} dc 0 ac 0.5", f"Izc_n 0 {n} dc 0 ac 0.5"]
        f, (Zc,) = run_scan(text, wd, src, [f"(v({p})+v({n}))/2"], a.fstart, a.fstop, a.pts, a.nodeset)
        bad += sum(1 for s_, e_, c in report(f"{p} / {n} common mode", f, Zc, a.fosc) if c)
    print(f"\nverdict: {'no possible spurious oscillation (any negative-R band listed above has no reactance zero: watch, not fail)' if bad == 0 else f'{bad} band(s) with Re(Z)<0 AND Im(Z)=0 - possible spurious oscillation, check above'}")
    sys.exit(1 if bad else 0)

if __name__ == "__main__":
    main()
