"""
run_lotree.py - RX LO distribution tree: amplitude and phase matching of the 4 mixer LO signals.

  python3 run_lotree.py nominal   # amplitude and phase at the 4 mixers (~5 s)
  python3 run_lotree.py mc 60     # Monte Carlo transistor mismatch over 60 virtual chips (~2 min)
  python3 run_lotree.py routing   # effect of a longer line to channel 4 (~10 s)
"""
import sys, subprocess, re, os, tempfile
import numpy as np
NGSPICE = os.environ.get("NGSPICE", "ngspice"); F0 = 24.125e9

def run(p, seed=None):
    s = open("lotree.spice").read()
    for k, v in p.items():
        s, n = re.subn(rf"(\.param .*?\b{k}=)\S+", rf"\g<1>{v}", s, count=1)
        if not n: sys.exit("parameter not found: " + k)
    if seed is not None: s = s.replace(".param temp=27", f".param temp=27\n.options seed={seed}")
    tag = os.path.basename(tempfile.mktemp(prefix="lt_", dir=".")); s = s.replace("lotree.txt", tag + ".txt")
    open(tag + ".spice", "w").write(s)
    subprocess.run([NGSPICE, "-b", tag + ".spice"], capture_output=True)
    d = np.loadtxt(tag + ".txt", skiprows=1); os.remove(tag + ".spice"); os.remove(tag + ".txt")
    t = d[:, 0]; m = t > 1.5e-9; t = t[m]
    A = np.column_stack([np.cos(2*np.pi*F0*t), np.sin(2*np.pi*F0*t), np.ones_like(t)])
    amp, ph = [], []
    for col in (1, 3, 5, 7):                      # differential LO at mixers 1..4
        c, *_ = np.linalg.lstsq(A, d[m, col], rcond=None)
        amp.append(np.hypot(c[0], c[1])/2); ph.append(np.degrees(np.arctan2(-c[1], c[0])))
    ph = (np.array(ph) - ph[0] + 180) % 360 - 180
    return np.array(amp), ph

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "nominal"
    if mode == "nominal":
        a, p = run({})
        for i in range(4): print(f"mixer {i+1}: LO {a[i]:.3f} V per side, phase {p[i]:+.2f} deg vs mixer 1")
        print("Specs: >= 0.25 V per side; phase matching within +-10 deg (FPGA calibrates the rest)")
    elif mode == "mc":
        n = int(sys.argv[2]) if len(sys.argv) > 2 else 60
        ph, am = [], []
        for seed in range(1, n+1):
            a, p = run({"MM": 1}, seed); ph.append(p[1:]); am.append(a)
            print(f"chip {seed:3d}: phases {np.round(p[1:], 2)} deg", flush=True)
        ph = np.array(ph).ravel(); am = np.array(am)
        print(f"\nTransistor mismatch over {n} chips: phase std {ph.std():.2f} deg, worst {abs(ph).max():.2f} deg; "
              f"LO {am.min():.3f}-{am.max():.3f} V per side")
    elif mode == "routing":
        for l4 in ("300u", "400u", "600u", "1000u"):
            a, p = run({"LEN4": l4}); print(f"channel-4 line {l4:6s}: phase {p[3]:+.2f} deg, LO {a[3]:.3f} V per side")
