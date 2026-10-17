"""tank_mutual.py - add the odd-mode mutual inductance between the differential tank lines (vcop/vcon sections) to the
hybrid block. Each pair of mirrored straight sections couples with k from Grover's parallel-strip formula (TopMetal1,
2 um wide, 16.2 um centre spacing). Both sections are written top-to-bottom, so with opposite (differential) currents
k > 0 is the inductance-cancelling sign (checked: +133 MHz; k < 0 moved the frequency the wrong way)."""
import math, re
def add(path="blocks/vco_locore_hyb.sp", d=16.2e-6, w=2e-6, t=2e-6):
    s = open(path).read()
    if "K_tank" in s: return 0
    L = {m.group(1): float(m.group(2)) for m in re.finditer(r"^L_(\w+)\s+\S+\s+\S+\s+([0-9.eE+-]+)", s, re.M)}
    def length(Lv):
        lo, hi = 1e-7, 1e-3
        for _ in range(80):
            l = (lo * hi) ** 0.5; v = 2e-7 * l * (math.log(2 * l / (w + t)) + 0.5); lo, hi = (l, hi) if v < Lv else (lo, l)
        return l
    ks = []
    for n, v in L.items():
        m = re.match(r"tkp(\d+)$", n)
        if m and "tkn" + m.group(1) in L:
            l = length(min(v, L["tkn" + m.group(1)]))
            Ls = 2e-7 * l * (math.log(2 * l / (w + t)) + 0.5)
            M = 2e-7 * l * (math.log(l / d + math.sqrt(1 + (l / d) ** 2)) - math.sqrt(1 + (d / l) ** 2) + d / l)
            ks.append(f"K_tank{m.group(1)} L_tkp{m.group(1)} L_tkn{m.group(1)} {max(0.0, M / Ls):.3f}")
    i = s.index("L_tkp10"); j = s.index(".ends", i)
    open(path, "w").write(s[:j] + "* odd-mode mutual inductance of the tank lines (tank_mutual.py)\n" + "\n".join(ks) + "\n" + s[j:])
    return len(ks)
