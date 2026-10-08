"""Plot varactor C-V and Q from var_char.txt.  Run: python3 plot_var.py"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

d = np.sort(np.genfromtxt("var_char.txt", names=True), order="vgw")
fig, ax = plt.subplots(figsize=(8, 4.5))
ax.plot(d["vgw"], d["cdiff_fF"], "o-", c="tab:blue")
ax.set_xlabel("Gate-to-well voltage VGW [V]")
ax.set_ylabel("Differential capacitance [fF]", color="tab:blue")
ax.axvspan(-0.75, 0.75, color="green", alpha=0.12, label="Useful tuning region")
ax.grid(alpha=0.3); ax.legend(loc="upper left")
a2 = ax.twinx()
a2.plot(d["vgw"], d["q"], "s--", c="tab:red")
a2.set_ylabel("Q at 24.125 GHz", color="tab:red")
ax.set_title("sg13_hv_svaricap: capacitance and Q vs bias")
plt.tight_layout(); plt.savefig("var_char.png", dpi=150)

i0, i1 = np.argmin(abs(d["vgw"] - 0.75)), np.argmin(abs(d["vgw"] + 0.75))
print(f"Cmax = {d['cdiff_fF'].max():.1f} fF   Cmin = {d['cdiff_fF'].min():.1f} fF")
print(f"Usable swing (VGW +0.75 -> -0.75 V): {d['cdiff_fF'][i0]:.1f} -> {d['cdiff_fF'][i1]:.1f} fF "
      f"(dC = {d['cdiff_fF'][i0]-d['cdiff_fF'][i1]:.1f} fF)")
print(f"Q range: {d['q'].min():.1f} - {d['q'].max():.1f}")
print("Saved var_char.png")
