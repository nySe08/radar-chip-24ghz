"""
run_pa.py - characterize the 24 GHz PA.

  python3 run_pa.py corners   # output power, efficiency, harmonics, device voltages at all corners  (~30 s)
  python3 run_pa.py drive     # output power vs drive level + plot                                   (~30 s)
  python3 run_pa.py stab      # small-signal stability K, 1-100 GHz, three corners                   (~10 s)
"""
import subprocess, re, os, sys, tempfile
import numpy as np

NGSPICE = os.environ.get("NGSPICE", "ngspice")
F0 = 24.125e9

def run(netlist, params=None, corner=None, temp=None, out="pa.txt"):
    s = open(netlist).read()
    for k, v in (params or {}).items():
        s, n = re.subn(rf"(\.param .*?\b{k}=)\S+", rf"\g<1>{v}", s, count=1)
        if not n: sys.exit(f"parameter {k} not found")
    if corner: s = s.replace("hbt_typ", corner)
    if temp is not None: s = s.replace(".param temp=27", f".param temp=27\n.options temp={temp}")
    tag = os.path.basename(tempfile.mktemp(prefix="pa_", dir="."))
    s = s.replace(out, tag + ".txt"); open(tag + ".spice", "w").write(s)
    subprocess.run([NGSPICE, "-b", tag + ".spice"], capture_output=True)
    try: d = np.genfromtxt(tag + ".txt", names=True) if out == "pa_stab.txt" else np.loadtxt(tag + ".txt", skiprows=1)
    except Exception: d = None
    for f in (tag + ".spice", tag + ".txt"):
        if os.path.exists(f): os.remove(f)
    return d

def measure(d, vcc=2.5, tmin=2e-9):
    m = d[:, 0] > tmin; t = d[m, 0]
    def tone(v, f):
        A = np.column_stack([np.sin(2*np.pi*f*t), np.cos(2*np.pi*f*t), np.ones_like(t)])
        c, *_ = np.linalg.lstsq(A, v, rcond=None); return np.hypot(c[0], c[1])
    a1, a2 = tone(d[m, 1], F0), tone(d[m, 1], 2*F0)
    pout = a1**2 / 100                         # into the 50-ohm antenna
    idc = -d[m, 5].mean()
    vout, vc1, vcas = d[m, 3], d[m, 7], d[m, 9]
    return dict(pout=10*np.log10(pout/1e-3), h2=20*np.log10(a2/a1), idc=idc*1e3,
                eff=100*pout/(idc*vcc), vce2=(vout-vc1).max(), vcb2=(vout-vcas).max())

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "corners"

    if mode == "corners":
        cases = [("typical, 27 C", None, None, "2.5"), ("fast, -40 C", "hbt_bcs", -40, "2.5"),
                 ("slow, 85 C", "hbt_wcs", 85, "2.5"), ("fast, -40 C", "hbt_bcs", -40, "2.375"),
                 ("fast, -40 C", "hbt_bcs", -40, "2.625"), ("slow, 85 C", "hbt_wcs", 85, "2.375"),
                 ("slow, 85 C", "hbt_wcs", 85, "2.625")]
        print("corner          VCC     Pout      2nd harm.  Idc      eff.   peak VCE(Q2)  peak VCB(Q2)")
        for name, corner, temp, vcc in cases:
            r = measure(run("pa.spice", {"VCC": vcc}, corner, temp), float(vcc))
            print(f"{name:14s} {vcc:5s}  {r['pout']:5.2f} dBm  {r['h2']:6.1f} dBc  {r['idc']:5.2f} mA  "
                  f"{r['eff']:4.1f} %   {r['vce2']:.2f} V        {r['vcb2']:.2f} V", flush=True)
        print("Spec: Pout >= +5 dBm (<= +10 dBm for the EIRP limit). Q2 (npn13G2v): keep peak VCE <= ~3.0 V, VCB < 7.0 V")

    elif mode == "drive":
        amps = [0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.5]
        res = {}
        for name, corner, temp in [("typical", None, None), ("fast, -40 C", "hbt_bcs", -40), ("slow, 85 C", "hbt_wcs", 85)]:
            res[name] = [measure(run("pa.spice", {"AIN": a}, corner, temp))["pout"] for a in amps]
            print(name, " ".join(f"{p:5.2f}" for p in res[name]), flush=True)
        import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
        plt.figure(figsize=(7, 4.3))
        for name, p in res.items(): plt.plot(amps, p, "o-", label=name)
        plt.axhline(5, c="r", ls="--", label="spec +5 dBm"); plt.axvline(0.35, c="g", ls=":", label="buffer drive")
        plt.xlabel("Drive amplitude [V peak]"); plt.ylabel("Output power [dBm]")
        plt.title("PA output power vs drive"); plt.grid(alpha=0.3); plt.legend(fontsize=8)
        plt.tight_layout(); plt.savefig("pa_drive.png", dpi=150); print("Saved pa_drive.png")

    elif mode == "stab":
        for corner in ("hbt_typ", "hbt_bcs", "hbt_wcs"):
            d = run("pa_stab.spice", corner=corner if corner != "hbt_typ" else None, out="pa_stab.txt")
            i = np.argmin(abs(d["frequency"] - F0))
            print(f"{corner}: min K = {d['kfac'].min():.2f} (at {d['frequency'][d['kfac'].argmin()]/1e9:.0f} GHz), "
                  f"max |Delta| = {d['magdlt'].max():.2f}, small-signal gain {d['s21'][i]:.1f} dB")
        print("Unconditionally stable if K > 1 and |Delta| < 1 everywhere")
