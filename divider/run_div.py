"""
run_div.py - characterize the /4 divider.

  python3 run_div.py sens      # sensitivity curve: minimum input needed vs frequency   (~2 min)
  python3 run_div.py corners   # division + output power at worst corners and VCC +-5%   (~1 min)
  python3 run_div.py chain     # divider driven by the real VCO + LO buffer               (~1 min)
"""
import subprocess, re, os, sys, tempfile
import numpy as np

NGSPICE = os.environ.get("NGSPICE", "ngspice")

def run(netlist, params, outname, corner=None, temp=None):
    s = open(netlist).read()
    for k, v in params.items():
        s, n = re.subn(rf"(\.param .*?\b{k}=)\S+", rf"\g<1>{v}", s, count=1)
        if not n: sys.exit(f"parameter {k} not found")
    if corner: s = s.replace("hbt_typ", corner)
    if temp is not None: s = s.replace(".param temp=27", f".param temp=27\n.options temp={temp}")
    tag = os.path.basename(tempfile.mktemp(prefix="div_", dir="."))
    s = s.replace(outname, tag + ".txt"); open(tag + ".spice", "w").write(s)
    subprocess.run([NGSPICE, "-b", tag + ".spice"], capture_output=True)
    try: d = np.loadtxt(tag + ".txt", skiprows=1)
    except Exception: d = None
    for f in (tag + ".spice", tag + ".txt"):
        if os.path.exists(f): os.remove(f)
    return d

def freq(t, v):
    v = v - v.mean()
    zc = np.where((v[:-1] < 0) & (v[1:] >= 0))[0]
    if len(zc) < 3: return 0.0
    tz = t[zc] - v[zc] * (t[zc+1] - t[zc]) / (v[zc+1] - v[zc])
    return (len(tz) - 1) / (tz[-1] - tz[0])

def tone_dbm(t, v, f):
    A = np.column_stack([np.sin(2*np.pi*f*t), np.cos(2*np.pi*f*t), np.ones_like(t)])
    c, *_ = np.linalg.lstsq(A, v, rcond=None)
    return 10*np.log10(np.hypot(c[0], c[1])**2 / 100 / 1e-3)     # into 50 ohm

def check(params, corner=None, temp=None):
    """Returns (division ratio, output dBm per pin) for div4.spice."""
    d = run("div4.spice", params, "div4.txt", corner, temp)
    if d is None: return 0.0, None
    m = d[:, 0] > 3e-9; t = d[m, 0]
    fo = freq(t, d[m, 1])
    if fo == 0: return 0.0, None
    return float(params["FIN"]) / fo, tone_dbm(t, d[m, 1], fo)

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "corners"

    if mode == "sens":
        freqs = [8, 12, 16, 20, 24, 28, 32, 36]
        amps = [0.02, 0.05, 0.1, 0.2, 0.3]
        result = []
        print("f_in [GHz]   minimum input [V per side]")
        for f in freqs:
            need = None
            for a in amps:
                r, _ = check({"FIN": f"{f}e9", "ACK": a})
                if abs(r - 4) < 0.01: need = a; break
            result.append(need if need else np.nan)
            print(f"{f:6.0f}       {need if need else '> 0.3'}", flush=True)
        import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
        plt.figure(figsize=(7, 4.2))
        plt.semilogy(freqs, result, "o-", label="minimum input that still divides")
        plt.axhline(0.34, c="g", ls="--", label="available from LO buffer (0.34 V)")
        plt.axvspan(22.8, 26.0, color="green", alpha=0.12, label="VCO range, all corners")
        plt.xlabel("Input frequency [GHz]"); plt.ylabel("Input amplitude [V per side]")
        plt.title("Divider sensitivity curve"); plt.grid(alpha=0.3, which="both"); plt.legend(fontsize=8)
        plt.tight_layout(); plt.savefig("div_sensitivity.png", dpi=150); print("Saved div_sensitivity.png")

    elif mode == "corners":
        print("corner        VCC     f_in    ratio   output per pin   (input 0.1 V/side)")
        for vcc in ("2.375", "2.5", "2.625"):
            for f, corner, temp in ((26e9, "hbt_wcs", 85), (22.8e9, "hbt_bcs", -40)):
                r, p = check({"FIN": f, "ACK": 0.1, "VCC": vcc}, corner, temp)
                print(f"{corner} {temp:4d}C  {vcc}  {f/1e9:5.1f}   {r:5.3f}   {p:6.1f} dBm", flush=True)
        print("Specs: ratio 4.000 everywhere; output -10 to 0 dBm (ADF4159 RF input)")

    elif mode == "chain":
        sys.path.insert(0, ".")
        import run_lo_chain as L
        L.NGSPICE = NGSPICE
        for vt in (0.5, 1.25, 2.0):
            d = L.simulate("vco_buf_div.spice", {"VTUNE": vt}, tstop="10n")
            m = d[:, 0] > 6e-9; t = d[m, 0]
            fv, fo = L.freq(t, d[m, 1]), freq(t, d[m, 15])
            print(f"Vtune {vt:4.2f}: VCO {fv/1e9:.3f} GHz -> divider {fo/1e9:.4f} GHz "
                  f"(ratio {fv/fo:.3f}), {tone_dbm(t, d[m, 15], fo):.1f} dBm per pin", flush=True)
