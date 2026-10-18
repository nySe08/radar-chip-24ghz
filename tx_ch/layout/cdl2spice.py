"""cdl2spice.py - turn the LVS reference netlist (IHP deck conventions) into a simulatable ngspice subcircuit.
Every device keeps its LVS parameters; only the model names change. Inductors -> EM-calibrated pi-models (by geometry).
Le (a metal strip, invisible to LVS) is re-inserted between Q1's emitter and ground, because it is part of the circuit."""
import re, sys
IND = {("7u", "68.66u"): "ind_lb", ("5u", "55.83u"): "ind_lc"}
def convert(cdl, out):
    lines, o = open(cdl).read().splitlines(), []
    for ln in lines:
        t = ln.split()
        if not t or ln.startswith("*"): o.append(ln); continue
        if t[0].upper() == ".SUBCKT": o.append(".subckt " + " ".join(t[1:])); continue
        if t[0].upper() == ".ENDS": o.append("Xle e1_le GND ind_le\n.ends " + " ".join(t[1:])); continue
        name, kind = t[0], t[0][0].upper()
        p = dict(x.split("=") for x in t if "=" in x)
        if kind == "C":
            n1, n2 = t[1], t[2]
            model = "cap_rfcmim" if "rfcmim" in t else "cap_cmim"
            m = int(p.get("m", 1))
            for i in range(m):
                o.append(f"X{name}_{i} {n1} {n2}" + (f" {t[3]}" if model == "cap_rfcmim" else "") + f" {model} w={p['w']} l={p['l']}")
        elif kind == "R":
            if "ptap1" in t: o.append(f"* {name}: substrate tap (no circuit function)"); continue
            model = [x for x in ("rppd", "rhigh", "rsil") if x in t][0]
            o.append(f"X{name} {t[1]} {t[2]} {t[3]} {model} w={p['w']} l={p['l']}")
        elif kind == "Q":
            c, b, e, sub = t[1:5]
            if name == "Q1": e = "e1_le"                      # Le re-inserted (metal strip)
            o.append(f"X{name} {c} {b} {e} {sub} npn13G2 Nx={p['Nx']}")
        elif kind == "L":
            o.append(f"X{name} {t[1]} {t[2]} {IND[(p['w'], p['d'])]}")
        else:
            raise ValueError("unknown device: " + ln)
    open(out, "w").write("\n".join(o) + "\n")
if __name__ == "__main__":
    convert(sys.argv[1], sys.argv[2])
