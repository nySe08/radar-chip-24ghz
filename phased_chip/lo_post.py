"""lo_post.py - LO-core post-layout model: the LVS-verified netlist (blocks/vco_locore.sp) + the interconnect of every
significant route, measured from the LO-core layout (lo_gen.py). One pi-section per segment (Hammerstad microstrip):
top metals over the Metal4 plane; Metal2/Metal3 under it (gap to the plane as height, 0.49 um / 0.1 ohm-per-square metal)."""
from build_post import line
TM1 = dict(h_um=1.88, t=2e-6); TM2 = dict(h_um=6.68, t=3e-6)
BS2_LEN = 29.0                                   # tank-vertical extension from the bit-0 to the bit-1 band-select unit (um)
M3 = dict(h_um=0.60, t=0.49e-6, sigma=2.04e7); M2 = dict(h_um=1.70, t=0.49e-6, sigma=2.04e7)
def build(src="blocks/vco_locore.sp", out="blocks/vco_locore_post.sp", bus_w=1.2, tank=True, tank_scale=1.0, compact=True):
    L = open(src).read().splitlines(); idx = {l.split()[0]: i for i, l in enumerate(L) if l and l[0] not in "*."}
    def move(inst, k, node):                      # reroute terminal k (1-based) of an instance onto a new node
        t = L[idx[inst]].split(); t[k] = node; L[idx[inst]] = " ".join(t)
    add = []
    def seg(name, a, b, length, w, kind, n=1):     # one route, split into n pi-sections
        nodes = [a] + [f"{name}_{i}" for i in range(1, n)] + [b]
        for i in range(n):
            txt, _ = line(f"{name}{i}", nodes[i], nodes[i+1], length / n, w, **kind); add.append(txt)
    # ---- VCO tank: lead stub (TM1 w6) -> collector; TM1 w3 vertical with taps: cross-coupling (TM2), varactor branch, EF base
    # tank-route lengths per side (um): lead stub, collector->cross tap, cross (TM2), cross tap->varactor tap, varactor branch, ->EF base
    TANK = {"p": (13, 22, 28.6, 32, 17.0, 43), "n": (13, 34, 28.2, 20, 17.9, 43)} if compact else \
           {"p": (13, 36, 55, 18, 64, 60), "n": (13, 36, 61, 18, 64, 60)}
    for (s, cpl, cv, ef, coil, xlen) in ([] if not tank else (("p", "XCvco_b7", "XCvco_cv1", "XQef_1", "RLvcoa", 55), ("n", "XCvco_b6", "XCvco_cv2", "XQef_2", "RLvcob", 61))):
        v = "vcop" if s == "p" else "vcon"
        l0, l1, lx, l2, lcv, l3 = (x * tank_scale for x in TANK[s])
        move(coil, 2, f"{v}_L"); seg(f"tk{s}stub", f"{v}_L", v, l0, 6, TM1)
        seg(f"tk{s}1", v, f"{v}_x", l1, 3, TM1); seg(f"tk{s}x", f"{v}_x", f"{v}_cb", lx, 4, TM2); move(cpl, 1, f"{v}_cb")
        seg(f"tk{s}2", f"{v}_x", f"{v}_v", l2, 3, TM1); seg(f"tk{s}cv", f"{v}_v", f"{v}_cv", lcv, 3, TM1); move(cv, 1, f"{v}_cv")
        seg(f"tk{s}3", f"{v}_v", f"{v}_e", l3, 3, TM1); move(ef, 2, f"{v}_e")
        # band-select cap: at the bottom of the tank vertical (below the EF), short TM1 stub to its top plate
        move("XCbs_1" if s == "p" else "XCbs_2", 1, f"{v}_bs"); seg(f"tk{s}bs", f"{v}_e", f"{v}_bs", 9 * tank_scale, 3, TM1)
    # ---- emitter-follower buses: efp on Metal3, efn on Metal2 (with the detour around the TX output caps)
    move("XCDDV_i1", 1, "efp_dv"); move("XCPRX_i1", 1, "efp_rx"); move("XCPTX_i1", 1, "efp_tx")
    seg("bp_dv", "efp", "efp_dvd", 230, bus_w, M3, 2); seg("bp_dvd", "efp_dvd", "efp_dv", 22, bus_w, M2)
    seg("bp_rx", "efp", "efp_rxd", 39, bus_w, M3); seg("bp_rxd", "efp_rxd", "efp_rx", 33, bus_w, M2)
    seg("bp_tx", "efp", "efp_txd", 300, bus_w, M3, 3); seg("bp_txd", "efp_txd", "efp_tx", 92, bus_w, M2)
    move("XCDDV_i2", 1, "efn_dv"); move("XCPRX_i2", 1, "efn_rx"); move("XCPTX_i2", 1, "efn_tx")
    seg("bn_dv", "efn", "efn_dv", 197, bus_w, M2, 2); seg("bn_rx", "efn", "efn_rx", 73, bus_w, M2)
    seg("bn_tx", "efn", "efn_tx", 545, bus_w, M2, 4)
    # ---- pre-drivers: collector -> coil lead (TM1, in series with each coil half) and collector -> output cap (M2)
    for (coil_p, coil_n, lp, ln) in (("RLPRXb", "RLPRXa", 82, 56), ("RLPTXa", "RLPTXb", 96, 92)):
        t = "prx" if "PRX" in coil_p else "ptx"
        move(coil_p, 2, f"{t}_dpL"); seg(f"{t}cp", f"{t}_dp", f"{t}_dpL", lp, 3, TM1)
        move(coil_n, 2, f"{t}_dnL"); seg(f"{t}cn", f"{t}_dn", f"{t}_dnL", ln, 3, TM1)
    for t in ("PRX", "PTX", "DDV"):
        lo = t.lower()
        move(f"XC{t}_c1", 1, f"{lo}_dpC"); seg(f"{lo}op", f"{lo}_dp", f"{lo}_dpC", 75, 1.0, M2)
        move(f"XC{t}_c2", 1, f"{lo}_dnC"); seg(f"{lo}on", f"{lo}_dn", f"{lo}_dnC", 74, 1.0, M2)
    # ---- LO outputs: RX pair (TM2) to the H-tree root, TX pair (TM2) out the right edge
    for (cap, k, port, ln) in (("XCPRX_c1", 2, "RXLOP", 139), ("XCPRX_c2", 2, "RXLON", 133), ("XCPTX_c1", 2, "TXLOP", 169), ("XCPTX_c2", 2, "TXLON", 62)):
        move(cap, k, f"{port}_c"); seg(f"o{port}", f"{port}_c", port, ln, 4, TM2)
    # ---- divider clock lines: driver output caps -> TM1 drops -> M2 (ckp) / M3 (ckn) buses to the latches
    move("XCDDV_c1", 2, "ckp_c"); seg("ckp1", "ckp_c", "ckp_b", 180, 3, TM1); seg("ckp2", "ckp_b", "div_ckp", 150, 1.0, M2, 2)
    move("XCDDV_c2", 2, "ckn_c"); seg("ckn1", "ckn_c", "ckn_b", 220, 3, TM1); seg("ckn2", "ckn_b", "div_ckn", 160, 1.0, M3, 2)
    s = "\n".join(L)
    s = s.replace(".ends lo_core", "* ======== layout interconnect (post-layout) ========\n" + "".join(add) + ".ends lo_core")
    open(out, "w").write(s); return len(add)
if __name__ == "__main__":
    import sys
    n = build(bus_w=float(sys.argv[1]) if len(sys.argv) > 1 else 1.2); print(f"post-layout LO core: {n} route sections added")
