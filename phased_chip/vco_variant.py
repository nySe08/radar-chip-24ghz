"""vco_variant.py - run the chip check with extra elements added inside the post-layout LO core (experiments only)."""
import re, importlib, sys
def run(extra, params=None, tag="v", corner=None, temp=None):
    s = open("blocks/vco_locore_post.sp").read()
    s = s.replace(".ends lo_core", "* ---- experiment ----\n" + extra + "\n.ends lo_core")
    open(f"blocks/vco_locore_{tag}.sp", "w").write(s)
    t = open("lo_core_post_tb.spice").read().replace("blocks/vco_locore_post.sp", f"blocks/vco_locore_{tag}.sp")
    open(f"lo_core_{tag}_tb.spice", "w").write(t)
    if corner is None:
        q = open("quick_lopost.py").read().replace("lo_core_post_tb.spice", f"lo_core_{tag}_tb.spice")
        open(f"quick_{tag}.py", "w").write(q); m = importlib.import_module(f"quick_{tag}"); importlib.reload(m)
        return m.quick(params or {})
    import run_phased_core as R
    d, it = R.simulate(params or {}, corner=corner, temp=temp, netlist=f"lo_core_{tag}_tb.spice", outfile="phased_tran.txt", tstop="14n")
    mk = d[:, 0] > 10e-9; return {"fLO": R.freq(d[mk, 0], d[mk, 1]) / 1e9, "I_mA": it}
