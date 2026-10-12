import subprocess, re, os, tempfile, numpy as np, sys
NG=os.environ.get('NGSPICE','ngspice'); FB=100e6; FLO=24.0e9
def run(real, corner=None, temp=None, rtl="1.86u", vcc="2.5", drv=""):
    s=open('channel_tb.spice').read().replace('.param RTL=1.86u', f'.param RTL={rtl}').replace('.param VCC=2.5', f'.param VCC={vcc}')
    if real:
        s=s.replace('XDRV','Xdrv lp ln mlp mln vcc ' + ('lodrv_res' if real == 2 else 'lodrv_real '+drv)).replace('XMIX','Xmix a mlp mln ifp ifn vcc mixer_real')
    else:
        s=s.replace('XDRV','Xdrv lp ln mlp mln vcc lodrv').replace('XMIX','Xmix a mlp mln ifp ifn vcc mixer')
    if corner: s=s.replace('hbt_typ',corner[0]).replace('cap_typ',corner[1]).replace('res_typ',corner[2])
    if temp is not None: s=s.replace('.param temp=27',f'.param temp=27\n.options temp={temp}')
    tag=os.path.basename(tempfile.mktemp(dir='.')); s=s.replace('ch.txt',tag+'.txt'); open(tag+'.spice','w').write(s)
    out=subprocess.run([NG,'-b',tag+'.spice'],capture_output=True,text=True)
    try: d=np.loadtxt(tag+'.txt',skiprows=1)
    except Exception: print(out.stdout[-1500:]); raise
    for f in (tag+'.spice',tag+'.txt'): os.remove(f)
    m=d[:,0]>10e-9; t=d[m,0]
    def tone(v,f):
        A=np.column_stack([np.cos(2*np.pi*f*t),np.sin(2*np.pi*f*t),np.ones_like(t)]); c,*_=np.linalg.lstsq(A,v,rcond=None); return np.hypot(c[0],c[1])
    vin=np.sqrt(100e-3*10**(-40/10))
    return dict(gain_db=20*np.log10(tone(d[m,1],FB)/vin), lo_side=tone(d[m,3],FLO)/2)
if __name__=="__main__":
    print("ideal channel:", {k:round(float(v),3) for k,v in run(0).items()}, flush=True)
    print("real  channel (inductive driver, ideal 1.8 nH):", {k:round(float(v),3) for k,v in run(1).items()}, flush=True)
    for name,c,t,v in [("typical",None,None,"2.5"),("slow 85C, VCC-5%",('hbt_wcs','cap_wcs','res_wcs'),85,"2.375"),("fast -40C",('hbt_bcs','cap_bcs','res_bcs'),-40,"2.5")]:
        r=run(2,c,t,vcc=v); print(f"FINAL (resistive driver) {name:17s}: gain {r['gain_db']:.1f} dB, LO {r['lo_side']:.3f} V per side", flush=True)
