"""
run_top.py - simulate the complete 24 GHz radar transceiver (all six blocks).

  python3 run_top.py quick      # chip alive? supply current, LO frequency, TX power, PLL output   (~30 s)
  python3 run_top.py full       # TX + RX at once: echo at f_LO+100 MHz, with and without TX leakage (~2 min)
  python3 run_top.py corners    # the full test at typical, fast -40 C, slow 85 C, slow 85 C + VCC-5% (~4 min)

Files: chip_tb.spice (top level) + blocks/*.sp (one subcircuit per block).
Robust start: DC is solved without the varactor (it is AC-coupled, carries no DC),
then the transient starts from that point (.ic + uic).
"""
import subprocess, re, os, sys, tempfile
import numpy as np

NGSPICE = os.environ.get("NGSPICE", "ngspice")
FB = 100e6                                   # beat (IF) frequency used for the echo test

def simulate(params=None, corner=None, temp=None, tstop="30n", netlist="phased_tb.spice", outfile="phased_tran.txt"):
    s = open(netlist).read()
    for k, v in (params or {}).items():
        s, n = re.subn(rf"(\.param .*?\b{k}=)\S+", rf"\g<1>{v}", s, count=1)
        if not n: sys.exit("parameter not found: " + k)
    if corner: s = s.replace("hbt_typ", corner[0]).replace("mos_tt", corner[1])
    if temp is not None: s = s.replace(".param temp=27", f".param temp=27\n.options temp={temp}")
    tag = os.path.basename(tempfile.mktemp(prefix="top_", dir="."))
    # 1) DC without the varactor
    open(tag + "_vco.sp", "w").write(open("blocks/vco.sp").read().replace("XV1 g1 vtune g2", "*XV1 g1 vtune g2"))
    sop = s.replace(".include blocks/vco.sp", ".include " + tag + "_vco.sp")
    sop = sop[:sop.index(".control")] + '.control\nop\nprint all\nlet itot=-i(vcc)*1e3\necho "ITOT $&itot"\n.endc\n.end\n'
    open(tag + "_op.spice", "w").write(sop)
    out = subprocess.run([NGSPICE, "-b", tag + "_op.spice"], capture_output=True, text=True).stdout
    for f in (tag + "_op.spice", tag + "_vco.sp"): os.remove(f)
    m = re.search(r"ITOT (\S+)", out)
    if not m: sys.exit("DC operating point failed")
    itot = float(m.group(1))
    ic = [f"v({x.group(1)})={x.group(2)}" for x in re.finditer(r"^([\w\.]+) = (\S+)$", out, re.M)
          if "nan" not in x.group(2)]
    # 2) transient from that point
    s2 = s.replace(".control", ".ic " + " ".join(ic) + "\n.control", 1)
    s2 = re.sub(r"tran 0.5p \S+ 0 0.5p", f"tran 0.5p {tstop} 0 0.5p uic", s2).replace(outfile, tag + ".txt")
    open(tag + ".spice", "w").write(s2)
    subprocess.run([NGSPICE, "-b", tag + ".spice"], capture_output=True)
    d = np.loadtxt(tag + ".txt", skiprows=1)
    for f in (tag + ".spice", tag + ".txt"): os.remove(f)
    return d, itot
# columns of chip_tran.txt: 1 VCO diff, 3 IF diff, 5 TX antenna, 7 PLL pin, 9 mixer RF in, 11 mixer LO+, 13 PA in

def freq(t, v):
    v = v - v.mean(); zc = np.where((v[:-1] < 0) & (v[1:] >= 0))[0]
    tz = t[zc] - v[zc] * (t[zc+1] - t[zc]) / (v[zc+1] - v[zc]); return (len(tz) - 1) / (tz[-1] - tz[0])

def tone(t, v, f):
    A = np.column_stack([np.sin(2*np.pi*f*t), np.cos(2*np.pi*f*t), np.ones_like(t)])
    c, *_ = np.linalg.lstsq(A, v, rcond=None); return np.hypot(c[0], c[1]), c[2]

def dbm(a): return 10*np.log10(a**2 / 100 / 1e-3)

def quick(corner=None, temp=None, vcc="2.5"):
    d, itot = simulate({"LEAK": 0, "PECHO": -120, "VCC": vcc}, corner, temp, tstop="12n")
    m = d[:, 0] > 8e-9; t = d[m, 0]; flo = freq(t, d[m, 1]); fp = freq(t, d[m, 7])
    return dict(itot=itot, flo=flo, ptx=dbm(tone(t, d[m, 5], flo)[0]), fpll=fp, ppll=dbm(tone(t, d[m, 7], fp)[0]),
                lo=(d[m, 11].max() - d[m, 11].min()) / 2)

def full(leak, corner=None, temp=None, vcc="2.5", pecho=-40):
    q = quick(corner, temp, vcc)
    d, itot = simulate({"LEAK": leak, "FECHO": f"{q['flo']+FB:.6e}", "PECHO": pecho, "VCC": vcc}, corner, temp, tstop="32n")
    m = d[:, 0] > 12e-9; t = d[m, 0]
    a_if, dc_if = tone(t, d[m, 3], FB)
    vin = np.sqrt(100e-3 * 10**(pecho/10))
    q.update(rx_gain=20*np.log10(a_if/vin), if_dc=dc_if*1e3)
    return q

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "quick"
    if mode == "quick":
        r = quick()
        print(f"Supply current : {r['itot']:.1f} mA  ({r['itot']*2.5:.0f} mW)")
        print(f"LO frequency   : {r['flo']/1e9:.4f} GHz (Vtune = 1.25 V)")
        print(f"TX power       : {r['ptx']:+.2f} dBm into the antenna")
        print(f"To PLL         : {r['fpll']/1e9:.4f} GHz (= LO / {r['flo']/r['fpll']:.3f}), {r['ppll']:.1f} dBm per pin")
        print(f"LO at mixer    : {r['lo']:.3f} V per side")
    elif mode == "full":
        for leak in (0, 1):
            r = full(leak)
            print(f"{'with' if leak else 'without'} TX leakage: RX gain (antenna -> IF) {r['rx_gain']:.2f} dB, "
                  f"IF DC offset {r['if_dc']:+.1f} mV, TX {r['ptx']:+.2f} dBm", flush=True)
    elif mode == "corners":
        print("corner                 LO [GHz]  Itot [mA]  RX gain  TX power   PLL out    LO at mixer  IF DC (leak)")
        for name, c, t, v in [("typical, 27 C", None, None, "2.5"), ("fast, -40 C", ("hbt_bcs", "mos_ff"), -40, "2.5"),
                              ("slow, 85 C", ("hbt_wcs", "mos_ss"), 85, "2.5"), ("slow, 85 C, VCC-5%", ("hbt_wcs", "mos_ss"), 85, "2.375")]:
            r = full(1, c, t, v)
            print(f"{name:22s} {r['flo']/1e9:7.3f}   {r['itot']:6.1f}    {r['rx_gain']:5.1f} dB  {r['ptx']:+5.2f} dBm  "
                  f"{r['ppll']:6.1f} dBm  {r['lo']:.3f} V      {r['if_dc']:+6.1f} mV", flush=True)
        print("Specs: TX >= +4.5 dBm, PLL -10..0 dBm, LO >= 0.25 V/side; IF must be AC-coupled (DC offset from leakage)")
