"""budget.py - LO swing budget along the chain (per-side amplitude at 24 GHz) for a corner, hybrid model."""
import run_phased_core as R
def budget(params, corner=None, temp=None):
    d, it = R.simulate(params, corner=corner, temp=temp, netlist="lo_core_hyb_bud_tb.spice", outfile="phased_tran.txt", tstop="14n")
    m = d[:, 0] > 10e-9; t = d[m, 0]; f = R.freq(t, d[m, 1])
    a = lambda c: R.tone(t, d[m, c], f)[0] / 2
    import numpy as np
    tx1 = 10 * np.log10(R.tone(t, d[m, 11], f)[0] ** 2 / 100 / 1e-3)
    return {"f_GHz": f / 1e9, "TX1_dBm": tx1, "VCO tank": a(1), "EF outputs": a(21), "RX pre-driver collectors": a(23), "H-tree root (rxp/rxn)": a(25), "mixer LO (driver out)": a(17)}
