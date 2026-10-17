"""tile_meas.py - RX tile: pre- vs post-layout S11, LNA gain, NF (AC/noise) and channel conversion gain (transient).
Usage: python3 tile_post.py && python3 tile_meas.py   (set NG below to your ngspice)"""
import subprocess, re, numpy as np, os, sys
NG = os.environ.get('NGSPICE', 'ngspice')
def ac(netlist, corner=None, temp=None):
    s = open('tile_ac_tb.spice').read().replace('NETLIST', netlist)
    if corner: s = s.replace('hbt_typ', corner[0]).replace('cap_typ', corner[1]).replace('res_typ', corner[2])
    if temp is not None: s = s.replace('.param temp=27', f'.param temp=27\n.options temp={temp}')
    open('_ac.spice', 'w').write(s)
    o = subprocess.run([NG, '-b', '_ac.spice'], capture_output=True, text=True).stdout
    s11 = float(re.search(r"s11 = ([-\d.e+]+)", o).group(1)); g = float(re.search(r"^g = ([-\d.e+]+)", o, re.M).group(1))
    vn = float(re.search(r"inoise_spectrum = ([-\d.e+]+)", o).group(1))
    T = 273.15 + (27 if temp is None else temp); nf = 10*np.log10(vn**2/(4*1.380649e-23*T*50))
    return s11, g, nf
def tran(netlist, corner=None, temp=None):
    s = open('tile_tb.spice').read().replace('.include rx_tile_sim.sp', f'.include {netlist}').replace('tile_tran.txt', '_tr.txt')
    if corner: s = s.replace('hbt_typ', corner[0]).replace('cap_typ', corner[1]).replace('res_typ', corner[2])
    if temp is not None: s = s.replace('.param temp=27', f'.param temp=27\n.options temp={temp}')
    open('_tr.spice', 'w').write(s); subprocess.run([NG, '-b', '_tr.spice'], capture_output=True)
    d = np.loadtxt('_tr.txt', skiprows=1); m = d[:, 0] > 10e-9; t = d[m, 0]
    def tone(v, f):
        A = np.column_stack([np.cos(2*np.pi*f*t), np.sin(2*np.pi*f*t), np.ones_like(t)]); c, *_ = np.linalg.lstsq(A, v, rcond=None); return np.hypot(c[0], c[1])
    return 20*np.log10(tone(d[m, 1], 100e6)/np.sqrt(100e-3*1e-4)), tone(d[m, 3], 24e9)/2
if __name__ == "__main__":
    for name, nl in (("pre-layout (LVS netlist)", "rx_tile_sim.sp"), ("post-layout", "rx_tile_post.sp")):
        s11, g, nf = ac(nl); cg, lo = tran(nl)
        print(f"{name:26s}: S11 {s11:6.1f} dB | LNA gain into mixer input {g:5.1f} dB | NF {nf:4.2f} dB | channel conv. gain {cg:5.2f} dB | LO {lo:.3f} V", flush=True)
