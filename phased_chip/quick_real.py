"""quick_real.py - quick check of the fully realized 2TX/4RX chip (supply current, LO, TX on/off, divider, LO at mixers).
Also writes flo.txt (the actual LO frequency), used by angle_test_real.py.  Usage: python3 quick_real.py"""
import run_phased_core as R, numpy as np, sys
def quick(params):
    d,it=R.simulate(params,netlist='phased_real_tb.spice',outfile='phased_tran.txt',tstop='14n')
    m=d[:,0]>10e-9; t=d[m,0]; flo=R.freq(t,d[m,1])
    tx1=10*np.log10(R.tone(t,d[m,11],flo)[0]**2/100/1e-3); tx2=10*np.log10(R.tone(t,d[m,13],flo)[0]**2/100/1e-3)
    fp=R.freq(t,d[m,15]); pll=10*np.log10(R.tone(t,d[m,15],fp)[0]**2/100/1e-3)
    lo1=R.tone(t,d[m,17],flo)[0]/2; lo4=R.tone(t,d[m,19],flo)[0]/2
    return dict(I_mA=it, fLO=flo/1e9, TX1=tx1, TX2=tx2, div_ratio=flo/fp, PLL=pll, LO1=lo1, LO4=lo4)
if __name__=="__main__":
    r = quick({}); print({k:round(float(v),3) for k,v in r.items()}); open("flo.txt", "w").write(str(r["fLO"]*1e9))
