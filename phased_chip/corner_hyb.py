"""corner_hyb.py - hybrid-model chip check at a process/temperature corner: LO frequency, LO swing at the mixers, TX power."""
import run_phased_core as R, numpy as np
def corner(params, corner, temp):
    d, it = R.simulate(params, corner=corner, temp=temp, netlist='lo_core_hyb_tb.spice', outfile='phased_tran.txt', tstop='14n')
    m = d[:, 0] > 10e-9; t = d[m, 0]; flo = R.freq(t, d[m, 1])
    return dict(fLO=flo / 1e9, LO1=R.tone(t, d[m, 17], flo)[0] / 2, TX1=10 * np.log10(R.tone(t, d[m, 11], flo)[0] ** 2 / 100 / 1e-3), I_mA=it)
