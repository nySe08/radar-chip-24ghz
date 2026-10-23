"""run_tx_final.py - SCHEMATIC-level check of the final (v2) TX channel at the three PVT corners.

TX driver (txdrv_real) -> PA (pa_final) -> TX pad + EM-fitted ESD coil -> 50 ohm, WITHOUT layout parasitics.
The design was re-tuned against the extracted layout, so its specification is the post-layout result
(post_layout/tx_postlayout.py). This script only confirms the schematic netlists simulate as expected; note the
fast-corner 2nd harmonic is -12.8 dBm here because the trap MIM is sized for the layout's parasitics (-19.5 dBm or
better after layout). Expected (ngspice 42): slow +6.22 / typical +7.29 / fast +4.92 dBm.   Usage: python3 run_tx_final.py
"""
import sys, txrun

CORNERS = {  # name: (model corners, temperature, VCC, LO-core TX amplitude at that corner)
    "slow":    (("hbt_wcs", "mos_ss", "cap_wcs", "res_wcs"), 85, 2.375, 0.194),
    "typical": (None, 27, 2.5, 0.255),
    "fast":    (("hbt_bcs", "mos_ff", "cap_bcs", "res_bcs"), -40, 2.625, 0.312),
}
EXPECTED = {"slow": 6.22, "typical": 7.29, "fast": 4.92}   # schematic level, ngspice 42

worst, ok = 99.0, True
print(f"{'corner':8s} {'Pout [dBm]':>11s} {'H2 [dBm]':>9s} {'I [mA]':>7s}   expected")
for name, (cor, temp, vcc, atx) in CORNERS.items():
    p, i, h2 = txrun.run(corner=cor, temp=temp, vcc=vcc, atx=atx)
    worst = min(worst, p); ok &= abs(p - EXPECTED[name]) < 0.4     # ngspice 47 differs by up to ~0.2 dB
    print(f"{name:8s} {p:11.2f} {h2:9.1f} {i:7.1f}   {EXPECTED[name]:+.2f}")
print("schematic netlists reproduce the expected values" if ok else "MISMATCH against the expected schematic values")
sys.exit(0 if ok else 1)
