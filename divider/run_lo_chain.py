"""
run_lo_chain.py - verify the VCO + LO buffer (+ mixer).

  python3 run_lo_chain.py range    # tuning range and output swings vs Vtune   (~1 min)
  python3 run_lo_chain.py pull     # VCO frequency shift when the PA/mixer load changes (~1 min)
  python3 run_lo_chain.py mixer    # real mixer driven by the real LO: conversion gain (~1 min)

Robust start: ngspice sometimes cannot solve the DC point when the HBTs and the OSDI
varactor share a netlist. The varactor carries no DC current (it is AC-coupled), so the
DC point is solved without it, and the transient then starts from that point (.ic + uic).
"""
import subprocess, re, os, sys, tempfile
import numpy as np

NGSPICE = os.environ.get("NGSPICE", "ngspice")

def simulate(netlist, params=None, tstop="8n"):
    s = open(netlist).read()
    for k, v in (params or {}).items():
        s, n = re.subn(rf"(\.param .*?\b{k}=)\S+", rf"\g<1>{v}", s, count=1)
        if not n: sys.exit(f"parameter {k} not found")
    tag = os.path.basename(tempfile.mktemp(prefix="lo_", dir="."))
    # 1) DC without the varactor
    sop = s.replace("\nXV1", "\n*XV1")
    sop = sop[:sop.index(".control")] + ".control\nop\nprint all\n.endc\n.end\n"
    open(tag + "_op.spice", "w").write(sop)
    out = subprocess.run([NGSPICE, "-b", tag + "_op.spice"], capture_output=True, text=True).stdout
    os.remove(tag + "_op.spice")
    ic = [f"v({m.group(1)})={m.group(2)}" for m in re.finditer(r"^([\w\.]+) = (\S+)$", out, re.M)
          if "nan" not in m.group(2)]
    if not ic: sys.exit("DC operating point failed")
    # 2) transient from that point
    s2 = s.replace(".control", ".ic " + " ".join(ic) + "\n.control", 1)
    s2 = s2.replace("tran 0.5p 6n", f"tran 0.5p {tstop} uic").replace("vco_tran.txt", tag + ".txt")
    open(tag + ".spice", "w").write(s2)
    subprocess.run([NGSPICE, "-b", tag + ".spice"], capture_output=True)
    d = np.loadtxt(tag + ".txt", skiprows=1)
    for f in (tag + ".spice", tag + ".txt"): os.remove(f)
    return d

def freq(t, v):
    zc = np.where((v[:-1] < 0) & (v[1:] >= 0))[0]
    tz = t[zc] - v[zc] * (t[zc+1] - t[zc]) / (v[zc+1] - v[zc])
    return (len(tz) - 1) / (tz[-1] - tz[0])

def swing(v): return (v.max() - v.min()) / 2

def measure(d, tmin):
    m = d[:, 0] > tmin; t = d[m, 0]
    return dict(f=freq(t, d[m, 1]) / 1e9, mix=swing(d[m, 3]), pa=swing(d[m, 7]), div=swing(d[m, 11]))

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "range"

    if mode == "range":
        print("Vtune   f [GHz]   LO swing per side [V]: mixer   PA     divider")
        for vt in (0.5, 1.0, 1.25, 1.5, 2.0):
            r = measure(simulate("vco_buf.spice", {"VTUNE": vt}), 6e-9)
            print(f"{vt:4.2f}   {r['f']:7.3f}                       {r['mix']:.3f}   {r['pa']:.3f}  {r['div']:.3f}", flush=True)
        print("Specs: mixer >= 0.25 V, divider >= 0.20 V; band 24.00-24.25 GHz inside the range")

    elif mode == "pull":
        base = measure(simulate("vco_buf.spice", tstop="14n"), 10e-9)["f"]
        print(f"Reference frequency: {base:.4f} GHz")
        for name, p in [("PA load doubled", {"CPA": "80f", "RPA": "500"}),
                        ("PA load removed", {"CPA": "1f", "RPA": "1meg"}),
                        ("Mixer load doubled", {"CMIX": "50f", "RMIX": "1k"})]:
            f = measure(simulate("vco_buf.spice", p, tstop="14n"), 10e-9)["f"]
            print(f"{name:20s}: frequency shift {(f-base)*1e3:+7.2f} MHz", flush=True)

    elif mode == "mixer":
        f_if, vrf = 50e6, 0.01
        d = simulate("vco_buf_mix.spice", {"VRF": 1e-6}, tstop="12n")
        m = d[:, 0] > 10e-9; flo = freq(d[m, 0], d[m, 1])
        print(f"LO frequency (VCO in this circuit): {flo/1e9:.4f} GHz", flush=True)
        d = simulate("vco_buf_mix.spice", {"FRF": f"{flo+f_if:.6e}", "VRF": vrf}, tstop="52n")
        m = d[:, 0] > 12e-9; t, y = d[m, 0], d[m, 7]
        A = np.column_stack([np.sin(2*np.pi*f_if*t), np.cos(2*np.pi*f_if*t), np.ones_like(t)])
        c, *_ = np.linalg.lstsq(A, y, rcond=None)          # fit the 50 MHz IF tone
        amp = np.hypot(c[0], c[1])
        print(f"LO at mixer: {swing(d[m,3]):.3f} V per side")
        print(f"IF amplitude: {amp*1e3:.2f} mV for {vrf*1e3:.0f} mV RF  ->  conversion gain {20*np.log10(amp/vrf):.2f} dB")
        print("Spec: >= 6 dB (stand-alone mixer with ideal 0.3 V LO: 7.0 dB)")
