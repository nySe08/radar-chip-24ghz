"""lo_cdl2spice.py - LO-core LVS netlist -> ngspice subcircuit (EM-fitted coil models, PDK varactor)."""
import sys
IND3 = {("6u", "70.88u"): ("275p", "3.08", "9.24f"),          # VCO coil (old): per side L0/2 + loss, self-cap across
        ("6u", "68.0u"): ("260p", "2.31", "9.5f"),            # VCO coil d 68.0 (EM 586.4 pH / Q 15.1 at 24.1 GHz)
        ("10u", "150.0u"): ("169p", "1.11", "3.1f"),          # VCO coil 1-turn w 10 d 150: EM 365 pH, Q 24.8 @24.1 GHz; 20 pH port closure removed
        ("4u", "65.36u"): ("257.5p", "3.63", "8.2f"),         # RX pre-driver coil
        ("4u", "83.47u"): ("345p", "5.13", "11.6f")}          # TX pre-driver coil
def convert(cdl, out):
    o = [".subckt varwrap g1 vtune g2 NX=10\nXV1 g1 vtune g2 0 sg13_hv_svaricap l=0.3u w=9.74u Nx={NX}\n.ends varwrap"]
    for ln in open(cdl).read().splitlines():
        t = ln.split()
        if not t or ln.startswith("*"): continue
        if t[0] == ".SUBCKT": o.append(".subckt " + " ".join(t[1:])); continue
        if t[0] == ".ENDS":
            o.append("* TESTBENCH STIMULUS, simulation copy only (not in the LVS netlist / design): start-up kick for the VCO")
            o.append("Ikick_tb vcop 0 pulse(0 1m 0 5p 5p 10p 1)"); o.append(".ends " + t[1]); continue
        p = dict(x.split("=") for x in t if "=" in x); n = t[0]
        if "inductor3" in t:
            la, lc, lb = t[1:4]; Ls, Rs, Cp = IND3[(p["w"], p["d"])]
            o += [f"L{n}a {lc} {n}_ma {Ls}", f"R{n}a {n}_ma {la} {Rs}", f"L{n}b {lc} {n}_mb {Ls}", f"R{n}b {n}_mb {lb} {Rs}", f"C{n}p {la} {lb} {Cp}"]
        elif "sg13_hv_svaricap" in t: o.append(f"X{n} {t[1]} {t[2]} {t[3]} varwrap NX={p['Nx']}")
        elif "rfcmim" in t: o.append(f"X{n} {t[1]} {t[2]} {t[3]} cap_rfcmim w={p['w']} l={p['l']}")
        elif t[0][0] == "R": o.append(f"X{n} {t[1]} {t[2]} {t[3]} {[m for m in ('rppd','rhigh','rsil') if m in t][0]} w={p['w']} l={p['l']}")
        elif t[0][0] == "Q": o.append(f"X{n} {' '.join(t[1:5])} npn13G2 Nx={p['Nx']}")
        elif t[0][0] == "M": o.append(f"X{n} {' '.join(t[1:5])} {t[5]} w={p['w']} l={p['l']} ng={p['ng']}")
        else: raise ValueError(ln)
    open(out, "w").write("\n".join(o) + "\n")
if __name__ == "__main__": convert(sys.argv[1], sys.argv[2])
