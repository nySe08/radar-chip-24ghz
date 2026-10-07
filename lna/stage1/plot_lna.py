"""Plot LNA stage-1 results: S-parameters, noise figure, stability.
Run after:  ngspice -b lna_stage1.spice
"""
import warnings; warnings.filterwarnings("ignore")
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

d = np.genfromtxt("lna_stage1.txt", names=True)
s = np.genfromtxt("lna_stage1_stab.txt", names=True)
f = d["frequency"] / 1e9
band = (24.0, 24.25)

fig, ax = plt.subplots(1, 3, figsize=(16, 4.5))

ax[0].plot(f, d["s21db"], label="S21 (gain)")
ax[0].plot(f, d["s11db"], label="S11 (input match)")
ax[0].plot(f, d["s22db"], label="S22 (output match)")
ax[0].axhline(18, ls=":", c="tab:blue"); ax[0].axhline(-10, ls=":", c="k")
ax[0].set_ylim(-50, 30); ax[0].set_ylabel("dB"); ax[0].set_title("S-parameters")

ax[1].plot(f, d["nfdb"], label="NF")
ax[1].plot(f, d["nfmindb"], "--", label="NFmin (device limit)")
ax[1].axhline(5, ls=":", c="r", label="Spec: 5 dB")
ax[1].set_ylim(0, 6); ax[1].set_ylabel("dB"); ax[1].set_title("Noise figure")

for a in ax[:2]:
    a.axvspan(*band, color="green", alpha=0.15, label="Radar band")
    a.set_xlabel("Frequency [GHz]"); a.grid(alpha=0.3); a.legend(fontsize=8)

fs = s["frequency"] / 1e9
ax[2].semilogy(fs, s["kfac"], label="K (must be > 1)")
ax[2].semilogy(fs, s["magdlt"], label="|Delta| (must be < 1)")
ax[2].axhline(1, c="r", ls="--")
ax[2].set_xlabel("Frequency [GHz]"); ax[2].set_title("Stability, 1-100 GHz")
ax[2].grid(alpha=0.3, which="both"); ax[2].legend(fontsize=8)

plt.tight_layout(); plt.savefig("lna_stage1.png", dpi=150)

i = np.argmin(abs(d["frequency"] - 24.125e9))
inb = (d["frequency"] >= 24e9) & (d["frequency"] <= 24.25e9)
print(f"At 24.125 GHz:  S21 = {d['s21db'][i]:.1f} dB   S11 = {d['s11db'][i]:.1f} dB   "
      f"S22 = {d['s22db'][i]:.1f} dB   NF = {d['nfdb'][i]:.2f} dB")
print(f"Worst in band:  S21 >= {d['s21db'][inb].min():.1f} dB   S11 <= {d['s11db'][inb].max():.1f} dB   "
      f"NF <= {d['nfdb'][inb].max():.2f} dB")
ok = (s["kfac"] > 1).all() and (s["magdlt"] < 1).all()
print(f"Unconditionally stable 1-100 GHz: {'YES' if ok else 'NO'}   (min K = {s['kfac'].min():.2f})")
print("Saved lna_stage1.png")
