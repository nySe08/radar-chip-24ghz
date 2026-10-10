import numpy as np, subprocess, sys, os
NG=os.environ.get('NGSPICE','ngspice')
F0=24.125e9
def run(hbt,mos,temp):
    s=open('pa_en.spice').read().replace('hbt_typ',hbt).replace('mos_tt',mos).replace('.param temp=27',f'.param temp=27\n.options temp={temp}').replace('pa_en.txt','_pe.txt')
    open('_pe.spice','w').write(s); subprocess.run([NG,'-b','_pe.spice'],capture_output=True)
    d=np.loadtxt('_pe.txt',skiprows=1); t=d[:,0]; v=d[:,1]
    def tone(a,b):
        m=(t>a)&(t<b); tt=t[m]; A=np.column_stack([np.cos(2*np.pi*F0*tt),np.sin(2*np.pi*F0*tt),np.ones_like(tt)])
        c,*_=np.linalg.lstsq(A,v[m],rcond=None); return 10*np.log10(np.hypot(c[0],c[1])**2/100/1e-3)
    on,off=tone(60e-9,115e-9),tone(170e-9,200e-9)
    # turn-on: 1 dB settling, using 1-ns windows after the enable edge
    ts=None
    for k in range(0,40):
        if tone(20e-9+k*1e-9,21e-9+k*1e-9)>on-1: ts=k; break
    return on,off,ts
"""run_pa_en.py - PA enable (TDM-MIMO) check at three corners (~3 min).
Usage: python3 run_pa_en.py      Needs pa_en.spice in the same folder."""
for name,h,mo,tp in [("typical, 27 C","hbt_typ","mos_tt",27),("fast, -40 C","hbt_bcs","mos_ff",-40),("slow, 85 C","hbt_wcs","mos_ss",85)]:
    on,off,ts=run(h,mo,tp); print(f"{name:14s}: ON {on:.2f} dBm, OFF {off:.1f} dBm, isolation {on-off:.0f} dB, turn-on within 1 dB in ~{ts} ns", flush=True)
print('Specs: isolation >= 30 dB; switching << 128 us chirp time')
