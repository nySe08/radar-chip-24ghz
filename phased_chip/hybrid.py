"""hybrid.py - post-layout model = my route L/R sections (no route C) + KLayout-PEX capacitances (MIM plate pairs excluded).
pad_cut: fF removed per tank node from its capacitance to ground/substrate (layout shrink not yet re-extracted)."""
import json, csv, re
def build(pad_cut=9.3, swap=None, src="blocks/vco_locore_post.sp", out="blocks/vco_locore_hyb.sp",
          pex="/home/claude/pex/pex_out/lo_core__lo_core/lo_core_k25d_pex_netlist.csv", netmap="/home/claude/pex/netmap.json",
          cdl="/home/claude/locore/lo_core_lvs.cdl"):
    x = json.load(open(netmap)); inv = {k: v.upper() for k, v in x.items()}
    swap = swap or {}                                                # nets the extractor's own LVS matched crosswise
    nm = lambda n: "GND" if n.upper() in ("VSUBS", "GND") else swap.get(inv.get(n, n.upper()), inv.get(n, n.upper()))
    mims = {frozenset((t[1].upper(), t[2].upper())) for t in (l.split() for l in open(cdl)) if len(t) > 4 and "rfcmim" in t}
    caps = {}
    for row in csv.DictReader(open(pex), delimiter=';'):
        if not row['Device'].startswith('C'): continue
        a, b = nm(row['Net1']), nm(row['Net2']); v = float(row['Capacitance [fF]'])
        if a == b or v <= 0 or frozenset((a, b)) in mims: continue
        k = tuple(sorted((a, b))); caps[k] = caps.get(k, 0) + v
    for node in ("VCOP", "VCON"):                                    # collector-pad shrink (overlap part only)
        k = tuple(sorted((node, "GND"))); caps[k] = max(0.0, caps[k] - pad_cut)
    s = open(src).read()
    s = "\n".join(l for l in s.splitlines() if not re.match(r"^C_\w+ ", l)) + "\n"     # drop my route capacitances, keep L/R
    add = "* ======== hybrid: KLayout-PEX capacitances (MIM pairs excluded) ========\n" + "".join(
        f"Chyb{i} {a} {b} {v:.4f}f\n" for i, ((a, b), v) in enumerate(caps.items()))
    open(out, "w").write(s.replace(".ends lo_core", add + ".ends lo_core"))
    return len(caps), sum(caps.values())
if __name__ == "__main__":
    n, c = build(); print(f"hybrid model: {n} PEX capacitances ({c:.0f} fF) + route L/R")
