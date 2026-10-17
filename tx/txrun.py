"""txrun.py - run one TX-path transient (TX driver -> PA -> pad/ESD -> 50 ohm) and return
(output power at the fundamental [dBm], supply current [mA], 2nd harmonic [dBm]).

Run inside IIC-OSIC-TOOLS with PDK_ROOT/PDK set for ihp-sg13g2. If this folder has no .spiceinit,
IHP's own (model search path + OSDI models) is copied in. NGSPICE overrides the ngspice binary.
"""
import os, shutil, subprocess, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
NG = os.environ.get("NGSPICE", "ngspice")

def _spiceinit():
    dst = os.path.join(HERE, ".spiceinit")
    if not os.path.exists(dst):
        src = os.path.join(os.environ.get("PDK_ROOT", "/foss/pdks"), os.environ.get("PDK", "ihp-sg13g2"), "libs.tech", "ngspice", ".spiceinit")
        shutil.copy(src, dst)

def run(driver_inst="txdrv_real RDL=1.6u RTL=0.79u", pa_inst="pa_final", atx=0.255, corner=None, temp=27, vcc=2.5, ftx=24.15e9,
        tb="tx_tb.spice"):
    _spiceinit()
    s = open(os.path.join(HERE, tb)).read()
    s = s.replace("DRIVER_INST", driver_inst).replace("PA_INST", pa_inst).replace("FTX=24.15e9", f"FTX={ftx}")
    s = s.replace(".param VCC=2.5 ATX=0.255", f".param VCC={vcc} ATX={atx}").replace(".param temp=27", f".param temp={temp}\n.options temp={temp}")
    if corner: s = s.replace("hbt_typ", corner[0]).replace("mos_tt", corner[1]).replace("cap_typ", corner[2]).replace("res_typ", corner[3])
    open(os.path.join(HERE, "_tx.spice"), "w").write(s)
    subprocess.run([NG, "-b", "_tx.spice"], capture_output=True, text=True, cwd=HERE)
    d = np.loadtxt(os.path.join(HERE, "tx_out.txt")); m = d[:, 0] > 2e-9; t, v, i = d[m, 0], d[m, 1], d[m, 3]
    w = 2 * np.pi * ftx
    a1 = 2 * np.abs(np.mean(v * np.exp(-1j * w * t))); a2 = 2 * np.abs(np.mean(v * np.exp(-2j * w * t)))
    return 10 * np.log10(a1**2 / 100 / 1e-3), -np.mean(i) * 1e3, 10 * np.log10(max(a2, 1e-12)**2 / 100 / 1e-3)
