"""Characterize the VCO: start-up waveform, tuning curve, K_VCO, amplitude.
Run:  python3 run_vco.py        (about 1 minute)
Out:  vco.png + printed summary
"""
import subprocess, re, os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

NGSPICE = os.environ.get("NGSPICE", "ngspice")
BASE = open("vco.spice").read()

def simulate(vtune):
    s = re.sub(r"(\.param .*?\bVTUNE=)\S+", rf"\g<1>{vtune}", BASE, count=1)
    open("_vco_tmp.spice", "w").write(s)
    subprocess.run([NGSPICE, "-b", "_vco_tmp.spice"], capture_output=True)
    return np.loadtxt("vco_tran.txt", skiprows=1)      # columns: time, vdiff, ..., v(outp)

def freq_amp(d, tmin=4e-9):
    t, v = d[:, 0], d[:, 1]
    m = t > tmin; t, v = t[m], v[m]
    amp = (v.max() - v.min()) / 2
    zc = np.where((v[:-1] < 0) & (v[1:] >= 0))[0]
    tz = t[zc] - v[zc] * (t[zc+1] - t[zc]) / (v[zc+1] - v[zc])   # interpolated zero crossings
    return (len(tz) - 1) / (tz[-1] - tz[0]) / 1e9, amp

vts = np.arange(0, 2.51, 0.25)
f, a = [], []
for vt in vts:
    d = simulate(vt)
    if abs(vt - 1.25) < 1e-6:
        wave = d
    fi, ai = freq_amp(d); f.append(fi); a.append(ai)
    print(f"Vtune = {vt:4.2f} V  ->  f = {fi:7.3f} GHz   swing = {ai:.3f} V peak (diff)", flush=True)
os.remove("_vco_tmp.spice")
f, a = np.array(f), np.array(a)
kvco = np.gradient(f, vts)

fig, ax = plt.subplots(1, 3, figsize=(17, 4.5))
t = wave[:, 0] * 1e9
ax[0].plot(t, wave[:, 1], lw=0.6)
ax[0].set_xlabel("Time [ns]"); ax[0].set_ylabel("V(outp) - V(outn) [V]")
ax[0].set_title("Start-up at Vtune = 1.25 V"); ax[0].grid(alpha=0.3)
ax[1].plot(vts, f, "o-")
ax[1].axhspan(24.0, 24.25, color="green", alpha=0.2, label="Radar band")
ax[1].axvspan(0.5, 2.0, color="gray", alpha=0.1, label="PLL tuning range")
ax[1].set_xlabel("Vtune [V]"); ax[1].set_ylabel("Frequency [GHz]")
ax[1].set_title("Tuning curve"); ax[1].grid(alpha=0.3); ax[1].legend(fontsize=8)
ax[2].plot(vts, kvco, "o-")
ax[2].set_xlabel("Vtune [V]"); ax[2].set_ylabel("K_VCO [GHz/V]")
ax[2].set_title("Tuning gain"); ax[2].grid(alpha=0.3)
plt.tight_layout(); plt.savefig("vco.png", dpi=150)

in_rng = (vts >= 0.5) & (vts <= 2.0)
print(f"\nRange for Vtune 0.5-2.0 V : {f[in_rng].min():.2f} - {f[in_rng].max():.2f} GHz "
      f"(covers 24.00-24.25: {'YES' if f[in_rng].min() < 24.0 and f[in_rng].max() > 24.25 else 'NO'})")
print(f"K_VCO in that range       : {kvco[in_rng].min():.2f} - {kvco[in_rng].max():.2f} GHz/V")
print(f"Swing                     : {a.min():.2f} - {a.max():.2f} V peak differential "
      f"({a.min()/2:.2f} - {a.max()/2:.2f} V per side)")
print("Saved vco.png")
