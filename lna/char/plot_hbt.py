"""Plot npn13G2 characterization results from hbt_char.txt
Run:  python3 plot_hbt.py            (reads hbt_char.txt)
      python3 plot_hbt.py other.txt  (reads another results file)
"""
import sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

fname = sys.argv[1] if len(sys.argv) > 1 else "hbt_char.txt"
import warnings; warnings.filterwarnings("ignore")
d = np.genfromtxt(fname, names=True, invalid_raise=False)
d = d[~np.isnan(d["ft_GHz"])]          # drop rows that failed to converge

fig, ax = plt.subplots(1, 2, figsize=(12, 4.5))

# left: speed and noise vs current
ax[0].plot(d["ic_mA"], d["ft_GHz"], "o-", c="tab:blue")
ax[0].set_xlabel("Collector current Ic [mA]")
ax[0].set_ylabel("fT [GHz]", color="tab:blue")
ax[0].grid(alpha=0.3)
a2 = ax[0].twinx()
a2.plot(d["ic_mA"], d["nfmin_dB"], "s-", c="tab:red")
a2.set_ylabel("NFmin @ 24.125 GHz [dB]", color="tab:red")
ax[0].set_title("Speed vs noise")

# right: optimum source impedance vs current
ax[1].plot(d["ic_mA"], d["ropt_ohm"], "o-", label="Ropt")
ax[1].plot(d["ic_mA"], d["xopt_ohm"], "s-", label="Xopt")
ax[1].axhline(50, ls="--", c="k", label="50 ohm target")
ax[1].set_xlabel("Collector current Ic [mA]")
ax[1].set_ylabel("Optimum source impedance [ohm]")
ax[1].set_title("Noise-matching impedance")
ax[1].grid(alpha=0.3); ax[1].legend()

plt.tight_layout()
out = fname.rsplit(".", 1)[0] + ".png"
plt.savefig(out, dpi=150)
print(f"Saved {out}")
i_pk = np.argmax(d["ft_GHz"])
print(f"Peak fT = {d['ft_GHz'][i_pk]:.0f} GHz at Ic = {d['ic_mA'][i_pk]:.2f} mA")
