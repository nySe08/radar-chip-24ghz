"""run_tx_final.py - reproduce the final TX-channel results at the three PVT corners.

TX driver (txdrv_real, load 1.6 um) -> PA (pa_final) -> TX pad + EM-fitted ESD coil -> 50 ohm.
The LO core's TX output is a sine at the amplitude extracted from the LO core layout at each corner.
Expected (ngspice 4x, IHP SG13G2 models):  slow +4.99 / typical +6.78 / fast +5.50 dBm,
2nd harmonic <= -18.6 dBm, 18.1 mA typical.   Usage:  python3 run_tx_final.py
"""
import sys, txrun

CORNERS = {  # name: (model corners, temperature, VCC, LO-core TX amplitude at that corner)
    "slow":    (("hbt_wcs", "mos_ss", "cap_wcs", "res_wcs"), 85, 2.375, 0.194),
    "typical": (None, 27, 2.5, 0.255),
    "fast":    (("hbt_bcs", "mos_ff", "cap_bcs", "res_bcs"), -40, 2.625, 0.312),
}
EXPECTED = {"slow": 4.99, "typical": 6.78, "fast": 5.50}

worst, ok = 99.0, True
print(f"{'corner':8s} {'Pout [dBm]':>11s} {'H2 [dBm]':>9s} {'I [mA]':>7s}   expected")
for name, (cor, temp, vcc, atx) in CORNERS.items():
    p, i, h2 = txrun.run(corner=cor, temp=temp, vcc=vcc, atx=atx)
    worst = min(worst, p); ok &= abs(p - EXPECTED[name]) < 0.3
    print(f"{name:8s} {p:11.2f} {h2:9.1f} {i:7.1f}   {EXPECTED[name]:+.2f}")
print(f"worst-case output {worst:+.2f} dBm (target >= +4.5 dBm): {'PASS' if worst >= 4.5 else 'FAIL'}")
sys.exit(0 if ok and worst >= 4.5 else 1)
