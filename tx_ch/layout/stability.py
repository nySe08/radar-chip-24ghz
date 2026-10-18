#!/usr/bin/env python3
"""
stability.py - broadband two-port stability sign-off with ngspice's S-parameter analysis.

Takes any netlist whose two RF ports are ngspice SP ports, e.g.
    V1 rfin_pad 0 dc 0 ac 1 portnum 1 z0 50
    V2 rfout_pad 0 dc 0 ac 0 portnum 2 z0 50
strips its .control block, runs  sp dec <pts> <fstart> <fstop>  and writes a Touchstone file,
then evaluates at every frequency:
    K, |Delta|, B1 (Rollett; unconditional stability needs K>1 AND B1>0)
    mu  (Edwards-Sinsky, load side)   mu' (source side)   -> unconditional stability iff mu>1 (equivalently mu'>1)
    worst-case |Gamma_in| over all load phases at each VSWR in --vswr, and |Gamma_out| over source phases
      (>1 means an oscillation is possible for SOME phase of that mismatch)
Corners: --corner hbt_typ hbt_wcs hbt_bcs  rewrites '.lib cornerHBT.lib <x>' per run (also --mos for MOS libs).

LIMITS (read these): a two-port test only sees loops that close through the two ports. Internal loops
(bias networks, supply lines, cascode bases, emitter followers inside the block) need the node impedance
scan in zscan.py. Run it on the POST-LAYOUT netlist including pads, bondwire/package and supply decoupling,
because out-of-band oscillations usually close through exactly those parts.

usage: python3 stability.py lna_post.spice --corner hbt_typ hbt_wcs hbt_bcs --vswr 2 3 6 --fstop 100e9
"""
import argparse, os, re, subprocess, sys, tempfile
import numpy as np

NGSPICE = os.environ.get("NGSPICE", "ngspice")

def build_netlist(text, corner, mos, pts, fstart, fstop, s2p):
    t = re.sub(r"(?is)^\s*\.control.*?^\s*\.endc\s*$", "", text, flags=re.M)        # drop any control block
    t = re.sub(r"(?im)^\s*\.(sp|ac|tran|noise|op)\b.*$", "", t)                       # and stray analyses
    t = re.sub(r"(?im)^\s*\.end\s*$", "", t)
    if corner: t = re.sub(r"(?im)^(\s*\.lib\s+\S*cornerHBT\.lib\s+)\S+", r"\g<1>" + corner, t)
    if mos:    t = re.sub(r"(?im)^(\s*\.lib\s+\S*cornerMOS(lv|hv)\.lib\s+)\S+", r"\g<1>" + mos, t)
    if not re.search(r"(?i)portnum\s+1", t) or not re.search(r"(?i)portnum\s+2", t):
        sys.exit("netlist needs two SP ports: 'Vx node 0 dc 0 ac 1 portnum 1 z0 50' and '... portnum 2 z0 50'")
    t += f"""
.csparam Rbase=50
.control
set noaskquit
sp dec {pts} {fstart:g} {fstop:g}
wrs2p {s2p}
quit
.endc
.end
"""
    return t

def read_s2p(path):
    """Touchstone v1 two-port: '# Hz S RI|MA|DB R 50' then f S11 S21 S12 S22."""
    fmt, data = "RI", []
    for line in open(path):
        line = line.split("!")[0].strip()
        if not line: continue
        if line.startswith("#"):
            u = line.upper().split()
            fmt = next((x for x in ("RI", "MA", "DB") if x in u), "RI")
            scale = {"HZ": 1, "KHZ": 1e3, "MHZ": 1e6, "GHZ": 1e9}.get(u[1], 1)
            continue
        data += [float(x) for x in line.split()]
    a = np.array(data).reshape(-1, 9)
    f = a[:, 0] * scale
    def cpx(x, y):
        if fmt == "RI": return x + 1j * y
        if fmt == "MA": return x * np.exp(1j * np.radians(y))
        return 10 ** (x / 20) * np.exp(1j * np.radians(y))
    S11, S21, S12, S22 = (cpx(a[:, 1 + 2 * k], a[:, 2 + 2 * k]) for k in range(4))
    return f, S11, S21, S12, S22

def metrics(S11, S21, S12, S22, vswrs):
    D = S11 * S22 - S12 * S21
    K = (1 - abs(S11) ** 2 - abs(S22) ** 2 + abs(D) ** 2) / (2 * abs(S12 * S21) + 1e-300)
    B1 = 1 + abs(S11) ** 2 - abs(S22) ** 2 - abs(D) ** 2
    mu = (1 - abs(S11) ** 2) / (abs(S22 - D * np.conj(S11)) + abs(S12 * S21) + 1e-300)
    mup = (1 - abs(S22) ** 2) / (abs(S11 - D * np.conj(S22)) + abs(S12 * S21) + 1e-300)
    ph = np.exp(1j * np.linspace(0, 2 * np.pi, 361))[:, None]
    worst = {}
    for v in vswrs:
        r = 1.0 if np.isinf(v) else (v - 1) / (v + 1)
        GL = r * ph
        Gin = S11 + S12 * S21 * GL / (1 - S22 * GL)
        Gout = S22 + S12 * S21 * GL / (1 - S11 * GL)
        worst[v] = (np.max(abs(Gin), axis=0), np.max(abs(Gout), axis=0))
    return K, abs(D), B1, mu, mup, worst

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("netlist"); ap.add_argument("--corner", nargs="*", default=[None])
    ap.add_argument("--mos", default=None); ap.add_argument("--vswr", nargs="*", type=float, default=[2, 3, 6])
    ap.add_argument("--fstart", type=float, default=100e6); ap.add_argument("--fstop", type=float, default=100e9)
    ap.add_argument("--pts", type=int, default=60); ap.add_argument("--band", nargs=2, type=float, default=[24.0e9, 24.25e9])
    ap.add_argument("--mu_margin", type=float, default=1.05, help="sign-off threshold for min(mu) (default 1.05)")
    a = ap.parse_args()
    text = open(a.netlist).read(); wd = os.path.dirname(os.path.abspath(a.netlist)); fail = False
    for corner in a.corner:
        with tempfile.NamedTemporaryFile("w", suffix=".spice", dir=wd, delete=False) as tf:
            s2p = tf.name.replace(".spice", ".s2p")
            tf.write(build_netlist(text, corner, a.mos, a.pts, a.fstart, a.fstop, os.path.basename(s2p)))
        r = subprocess.run([NGSPICE, "-b", os.path.basename(tf.name)], cwd=wd, capture_output=True, text=True)
        if not os.path.exists(s2p):
            print(r.stdout[-1500:], r.stderr[-1500:]); sys.exit(f"ngspice produced no Touchstone file for corner {corner}")
        f, S11, S21, S12, S22 = read_s2p(s2p)
        K, aD, B1, mu, mup, worst = metrics(S11, S21, S12, S22, a.vswr)
        inband = (f >= a.band[0]) & (f <= a.band[1])
        # a lossless port (e.g. AC-coupled output at low frequency) gives |S22| -> 1 and mu -> 1 with no loop transmission:
        # neutral, not unstable. Judge mu only where the two-port actually closes a loop (|S12*S21| > -60 dB),
        # and fail anywhere mu or the reflections cross 1 for real.
        active = abs(S12 * S21) > 1e-3
        i = int(np.argmin(np.where(active, mu, np.inf))) if active.any() else int(np.argmin(mu))
        ok = bool(np.all(mu > 1 - 1e-3) and np.all(np.where(active, mu, np.inf) > a.mu_margin))
        fail |= not ok
        print(f"\n=== {os.path.basename(a.netlist)}  corner={corner or 'as in netlist'}  {a.fstart/1e9:g}-{a.fstop/1e9:g} GHz ===")
        print(f"  min mu (where |S12 S21| > -60 dB) = {mu[i]:.3f} at {f[i]/1e9:6.2f} GHz | overall min mu = {mu.min():.4f} at {f[np.argmin(mu)]/1e9:.2f} GHz")
        print(f"  min mu' = {mup.min():.3f} at {f[np.argmin(mup)]/1e9:6.2f} GHz"
              f" | min K = {K.min():.2f} at {f[np.argmin(K)]/1e9:6.2f} GHz | min B1 = {B1.min():.3f}")
        if inband.any():
            print(f"  in band: S21 = {20*np.log10(abs(S21[inband])).mean():.1f} dB, mu >= {mu[inband].min():.2f}")
        for v, (gi, go) in worst.items():
            j = int(np.argmax(gi)); k = int(np.argmax(go))
            tag = "all passive loads" if np.isinf(v) else f"VSWR {v:g}:1"
            print(f"  {tag:>18}: worst |Gin| = {gi[j]:.3f} at {f[j]/1e9:6.2f} GHz, worst |Gout| = {go[k]:.3f} at {f[k]/1e9:6.2f} GHz"
                  f"  {'OK' if max(gi[j], go[k]) < 1 + 1e-3 else '<-- can oscillate'}")
        print(f"  verdict: {'PASS (unconditionally stable, mu > %.2f everywhere)' % a.mu_margin if ok else 'FAIL / conditionally stable - inspect the frequencies above'}")
        for p in (tf.name, s2p):
            try: os.remove(p)
            except OSError: pass
    sys.exit(1 if fail else 0)

if __name__ == "__main__":
    main()
