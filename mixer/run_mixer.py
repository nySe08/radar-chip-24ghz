"""Characterize the mixer: conversion gain, LO drive, P1dB, leakage desensitization.
Run:  python3 run_mixer.py      (about 2-3 minutes; ~40 transient simulations)
Out:  mixer.png + printed summary
"""
import subprocess, re, os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

NGSPICE = os.environ.get("NGSPICE", "ngspice")
BASE = open("mixer.spice").read()

def dbm_to_vpk(p):            # matched 50 ohm node: P = Vpk^2 / (2*50)
    return np.sqrt(100e-3 * 10 ** (p / 10))

def conv_gain(params, extra=None):
    """Voltage conversion gain [dB] = differential IF amplitude / RF amplitude."""
    s = BASE
    for k, v in params.items():
        s = re.sub(rf"^\.param {k}=\S+", f".param {k}={v}", s, flags=re.M)
    if extra:
        s = s.replace(*extra)
    open("_mix_tmp.spice", "w").write(s)
    out = subprocess.run([NGSPICE, "-b", "_mix_tmp.spice"], capture_output=True, text=True).stdout
    m = re.search(r"Fourier analysis for vif.*?\n 1\s+\S+\s+(\S+)", out, re.S)
    vrf = float(params.get("VRF", 0.01))
    return 20 * np.log10(float(m.group(1)) / vrf)

# 1) LO drive sweep
alos = [0.05, 0.1, 0.15, 0.2, 0.3, 0.4]
cg_lo = []
for a in alos:
    cg_lo.append(conv_gain({"ALO": a}))
    print(f"LO = {a:.2f} V peak/side  ->  CG = {cg_lo[-1]:.2f} dB", flush=True)

# 2) P1dB sweep
pins = np.arange(-20, 9, 1.0)
cg_p = []
for p in pins:
    cg_p.append(conv_gain({"VRF": f"{dbm_to_vpk(p):g}"}))
    print(f"Pin = {p:5.1f} dBm  ->  CG = {cg_p[-1]:.2f} dB", flush=True)
cg_p = np.array(cg_p); g0 = cg_p[0]
i = np.where(cg_p <= g0 - 1)[0][0]
ip1 = pins[i-1] + (g0 - 1 - cg_p[i-1]) / (cg_p[i] - cg_p[i-1]) * (pins[i] - pins[i-1])

# 3) Desensitization: weak target (-40 dBm) with -7 dBm TX leakage at the LO frequency
small = {"VRF": f"{dbm_to_vpk(-40):g}"}
cg_clean = conv_gain(small)
leak = ("Vrf  src 0 dc 0 sin(0 {2*VRF} {FLO+FIF})",
        f"Vrf  src s2 dc 0 sin(0 {{2*VRF}} {{FLO+FIF}})\nVlk  s2 0 dc 0 sin(0 {2*dbm_to_vpk(-7):g} {{FLO}})")
cg_leak = conv_gain(small, leak)
os.remove("_mix_tmp.spice")

fig, ax = plt.subplots(1, 2, figsize=(12, 4.5))
ax[0].plot(alos, cg_lo, "o-"); ax[0].axvline(0.25, ls="--", c="r", label="LO spec: >= 0.25 V peak/side")
ax[0].set_xlabel("LO amplitude [V peak per side]"); ax[0].set_ylabel("Conversion gain [dB]")
ax[0].set_title("How much LO does the mixer need?"); ax[0].grid(alpha=0.3); ax[0].legend()
ax[1].plot(pins, cg_p, "o-", ms=3)
ax[1].axhline(g0 - 1, c="r", ls=":", label=f"1 dB compression: IP1dB = {ip1:.1f} dBm")
ax[1].axvline(-7, c="g", ls="--", label="Amplified TX leakage (-7 dBm)")
ax[1].set_xlabel("RF input power [dBm]"); ax[1].set_ylabel("Conversion gain [dB]")
ax[1].set_title("Mixer compression"); ax[1].grid(alpha=0.3); ax[1].legend(fontsize=8)
plt.tight_layout(); plt.savefig("mixer.png", dpi=150)

print(f"\nConversion gain        : {g0:.2f} dB")
print(f"Input P1dB             : {ip1:.1f} dBm   (target >= 0 dBm: {'PASS' if ip1 >= 0 else 'FAIL'})")
print(f"Desense from -7 dBm TX leakage: {cg_clean - cg_leak:.2f} dB")
print("Saved mixer.png")
