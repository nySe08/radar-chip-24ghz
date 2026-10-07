"""Sweep input power through p1db.spice and find the 1 dB compression point.
Run:  python3 run_p1db.py     (takes about a minute)
Out:  p1db.png + printed input/output P1dB
"""
import subprocess, re, os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

NGSPICE = os.environ.get("NGSPICE", "ngspice")
F0 = 24.125e9
base = open("p1db.spice").read()

pins, pouts = [], []
for pin in np.arange(-40, 1, 1.0):                      # available input power [dBm]
    vpk = np.sqrt(8 * 50 * 1e-3 * 10 ** (pin / 10))      # Pavs = Vpk^2 / (8*Rs)
    s = re.sub(r"^\.param VPK=\S+", f".param VPK={vpk:g}", base, flags=re.M)
    open("_p1db_tmp.spice", "w").write(s)
    out = subprocess.run([NGSPICE, "-b", "_p1db_tmp.spice"], capture_output=True, text=True).stdout
    m = re.search(r"Fourier analysis for v\(p2\).*?\n 1\s+\S+\s+(\S+)", out, re.S)
    if not m:
        print(f"Pin = {pin:.0f} dBm: simulation failed, skipping"); continue
    vout = float(m.group(1))
    pins.append(pin); pouts.append(10 * np.log10(vout**2 / (2 * 50) / 1e-3))
    print(f"Pin = {pin:6.1f} dBm   Pout = {pouts[-1]:6.2f} dBm   Gain = {pouts[-1]-pin:5.2f} dB", flush=True)
os.remove("_p1db_tmp.spice")

pins, pouts = np.array(pins), np.array(pouts)
gain = pouts - pins
g0 = gain[0]
i = np.where(gain <= g0 - 1)[0][0]
ip1 = pins[i-1] + (g0 - 1 - gain[i-1]) / (gain[i] - gain[i-1]) * (pins[i] - pins[i-1])
op1 = ip1 + g0 - 1

fig, ax = plt.subplots(1, 2, figsize=(12, 4.5))
ax[0].plot(pins, pouts, "o-", ms=3, label="Simulated Pout")
ax[0].plot(pins, pins + g0, "--", label="Ideal linear")
ax[0].axvline(ip1, c="r", ls=":", label=f"Input P1dB = {ip1:.1f} dBm")
ax[0].set_xlabel("Input power [dBm]"); ax[0].set_ylabel("Output power [dBm]")
ax[0].set_title("Output vs input power"); ax[0].grid(alpha=0.3); ax[0].legend()
ax[1].plot(pins, gain, "o-", ms=3)
ax[1].axhline(g0 - 1, c="r", ls=":", label="1 dB compression")
ax[1].axvline(-20, c="k", ls="--", label="Spec: IP1dB >= -20 dBm")
ax[1].axvline(-30, c="g", ls="--", label="Expected TX leakage")
ax[1].set_xlabel("Input power [dBm]"); ax[1].set_ylabel("Gain [dB]")
ax[1].set_title("Gain compression"); ax[1].grid(alpha=0.3); ax[1].legend(fontsize=8)
plt.tight_layout(); plt.savefig("p1db.png", dpi=150)

print(f"\nSmall-signal gain = {g0:.2f} dB")
print(f"Input  P1dB = {ip1:.1f} dBm   (spec >= -20 dBm: {'PASS' if ip1 >= -20 else 'FAIL'})")
print(f"Output P1dB = {op1:.1f} dBm")
print("Saved p1db.png")
