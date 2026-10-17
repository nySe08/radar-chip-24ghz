"""lo_core_netlist.py - generates the LVS reference netlist of the LO core (single source of truth).
VCO (realized, EM coil) + emitter followers + RX/TX pre-drivers (EM coils) + bleeds + divider driver + realized /4 divider.
Device lines follow IHP's LVS deck conventions; names are made unique per block, and case collisions are checked."""
import collections
L = []          # netlist lines
def dev(line): L.append(line)
def rppd(n, a, b, w, l): dev(f"{n} {a} {b} GND rppd w={w}u l={l}u ps=0u b=0 m=1")
def rhigh(n, a, b, w, l): dev(f"{n} {a} {b} GND rhigh w={w}u l={l}u ps=0u b=0 m=1")
def mim(n, a, b, w): dev(f"{n} {a} {b} GND rfcmim w={w}u l={w}u m=1 wfeed=3u")
def npn(n, c, b, e, nx): dev(f"{n} {c} {b} {e} GND npn13G2 we=70n le=900n Nx={nx} m=1")
def ind3(n, la, lc, lb, w, d): dev(f"{n} {la} {lc} {lb} GND inductor3 w={w}u s=2.1u d={d}u nr_r=2")

def vco():
    p = "vco_"
    ind3("Lvco", "vcop", "VCC", "vcon", 6, 70.88)                      # EM-verified tank coil, centre tap to VCC
    mim("Cvco_cv1", "vcop", p+"g1", 11.3); mim("Cvco_cv2", "vcon", p+"g2", 11.3)
    rhigh("Rvco_g1", p+"vgb", p+"g1", 1, 7.0); rhigh("Rvco_g2", p+"vgb", p+"g2", 1, 7.0)
    rhigh("Rvco_gb1", "VCC", p+"vgb", 1, 13.30); rhigh("Rvco_gb2", p+"vgb", "GND", 1, 13.30); mim("Cvco_gb", p+"vgb", "GND", 33)
    dev(f"Cvco_var {p}g1 VTUNE {p}g2 GND sg13_hv_svaricap l=0.3u w=9.74u Nx=10")
    npn("Qvco_6", "vcop", p+"b6", p+"tail", 4); npn("Qvco_7", "vcon", p+"b7", p+"tail", 4)
    mim("Cvco_b6", "vcon", p+"b6", 11.5); mim("Cvco_b7", "vcop", p+"b7", 11.5)
    rppd("Rvco_b6", p+"vbb", p+"b6", 1, 7.47); rppd("Rvco_b7", p+"vbb", p+"b7", 1, 7.47)
    rppd("Rvco_bb1", "VCC", p+"vbb", 1, 15.21); rppd("Rvco_bb2", p+"vbb", "GND", 1, 22.95); mim("Cvco_bb", p+"vbb", "GND", 33)
    rppd("Rvco_tail", p+"tail", "GND", 2, 1.41)
def emitter_followers():
    npn("Qef_1", "VCC", "vcop", "efp", 2); npn("Qef_2", "VCC", "vcon", "efn", 2)
    rppd("Ref_1", "efp", "GND", 2, 8.24); rppd("Ref_2", "efn", "GND", 2, 8.24)
def driver(tag, inp, inn, outp, outn, rtl, rdl, coil=None, swap_coil_leads=False):
    """realized limiting driver (lodrv_g); coil=(w, d) -> inductor3 load with centre tap to VCC, else resistive only"""
    p = tag + "_"; up = tag.upper()
    mim(f"C{up}_i1", inp, p+"b1", 25); mim(f"C{up}_i2", inn, p+"b2", 25)
    rppd(f"R{up}_v1", "VCC", p+"vbd", 1, 17.53); rppd(f"R{up}_v2", p+"vbd", "GND", 1, 20.63); mim(f"C{up}_vb", p+"vbd", "GND", 33)
    rppd(f"R{up}_b1", p+"vbd", p+"b1", 1, 19.08); rppd(f"R{up}_b2", p+"vbd", p+"b2", 1, 19.08)
    npn(f"Q{up}_a", p+"dp", p+"b1", p+"t", 2); npn(f"Q{up}_b", p+"dn", p+"b2", p+"t", 2)
    rppd(f"R{up}_t", p+"t", "GND", 2, rtl)
    if coil:
        # The layout rotates the RX pre-driver's coil by 270 deg (leads facing the driver). The LVS deck assigns inductor3
        # terminals by lead POSITION, so for that coil its first terminal is the lead wired to dn. inductor3 is a symmetric
        # centre-tapped coil (outer leads interchangeable, identical halves in the EM model), so the netlist records the
        # leads in the order the extractor reads them: electrically identical, and LVS can match the driver uncrossed.
        a_, b_ = (p+"dn", p+"dp") if swap_coil_leads else (p+"dp", p+"dn")
        ind3(f"L{up}", a_, "VCC", b_, *coil)
    rppd(f"R{up}_d1", "VCC", p+"dp", 2, rdl); rppd(f"R{up}_d2", "VCC", p+"dn", 2, rdl)
    mim(f"C{up}_c1", p+"dp", outp, 12); mim(f"C{up}_c2", p+"dn", outn, 12)
def latch(tag, d, db, ck, ckb, q, qb, nt, rll, re):
    p = tag + "_"; up = tag.upper()
    rppd(f"R{up}_lp", "VCC", q, 2, rll); rppd(f"R{up}_ln", "VCC", qb, 2, rll)
    npn(f"Q{up}_d1", qb, d, p+"ed", 1); npn(f"Q{up}_d2", q, db, p+"ed", 1)
    npn(f"Q{up}_h1", qb, q, p+"eh", 1); npn(f"Q{up}_h2", q, qb, p+"eh", 1)
    npn(f"Q{up}_c1", p+"ed", ck, p+"et", 1); npn(f"Q{up}_c2", p+"eh", ckb, p+"et", 1)
    npn(f"Q{up}_t", p+"et", "div_vbt", p+"etr", nt); rppd(f"R{up}_e", p+"etr", "GND", 4, re)
def divider(ckp, ckn):
    rppd("Rdiv_ref", "VCC", "div_vbt", 1, 11.34); npn("Qdiv_br", "div_vbt", "div_vbt", "div_ebr", 1)
    rppd("Rdiv_ebr", "div_ebr", "GND", 2, 2.05); mim("Cdiv_bt", "div_vbt", "GND", 25)
    rppd("Rdiv_k1", "VCC", "div_vck", 1, 15.21); rppd("Rdiv_k2", "div_vck", "GND", 1, 22.95); mim("Cdiv_k", "div_vck", "GND", 33)
    rppd("Rdiv_ck1", "div_vck", ckp, 1, 7.47); rppd("Rdiv_ck2", "div_vck", ckn, 1, 7.47)
    latch("dm1", "s1qb", "s1q", ckp, ckn, "m1q", "m1qb", 3, 1.79, 1.28)
    latch("ds1", "m1q", "m1qb", ckn, ckp, "s1q", "s1qb", 3, 1.79, 1.28)
    mim("Cdiv_c1", "s1q", "c2p", 18.2); mim("Cdiv_c2", "s1qb", "c2n", 18.2)
    rppd("Rdiv_b1", "div_vck", "c2p", 1, 19.08); rppd("Rdiv_b2", "div_vck", "c2n", 1, 19.08)
    latch("dm2", "s2qb", "s2q", "c2p", "c2n", "m2q", "m2qb", 2, 2.83, 2.05)
    latch("ds2", "m2q", "m2qb", "c2n", "c2p", "s2q", "s2qb", 2, 2.83, 2.05)
    mim("Cdiv_o1", "s2q", "div_o1", 18.2); mim("Cdiv_o2", "s2qb", "div_o2", 18.2)
    rppd("Rdiv_o1", "VCC", "div_vbo", 1, 17.14); rhigh("Rdiv_o2", "div_vbo", "GND", 1, 5.53); mim("Cdiv_bo", "div_vbo", "GND", 33)
    rppd("Rdiv_bo1", "div_vbo", "div_o1", 1, 19.08); rppd("Rdiv_bo2", "div_vbo", "div_o2", 1, 19.08)
    npn("Qdiv_o1", "PLLN", "div_o1", "div_eo", 4); npn("Qdiv_o2", "PLLP", "div_o2", "div_eo", 4)
    npn("Qdiv_to1", "div_eo", "div_vbt", "div_eto1", 10); npn("Qdiv_to2", "div_eo", "div_vbt", "div_eto2", 10)
    rppd("Rdiv_eo1", "div_eto1", "GND", 8, 0.66); rppd("Rdiv_eo2", "div_eto2", "GND", 8, 0.66)
    rppd("Rdiv_t1", "VCC", "PLLP", 10, 1.66); rppd("Rdiv_t2", "VCC", "PLLN", 10, 1.66)
def build():
    vco(); emitter_followers()
    driver("prx", "efp", "efn", "RXLOP", "RXLON", 0.94, 2.83, coil=(4, 65.36), swap_coil_leads=True)   # RX pre-driver, 3.5 mA, EM coil (rotated in layout)
    rhigh("Rbl_r1", "RXLOP", "GND", 1, 14.0); rhigh("Rbl_r2", "RXLON", "GND", 1, 14.0)
    driver("ptx", "efp", "efn", "TXLOP", "TXLON", 1.86, 2.83, coil=(4, 83.47))      # TX pre-driver, 2 mA, EM coil
    rhigh("Rbl_t1", "TXLOP", "GND", 1, 14.0); rhigh("Rbl_t2", "TXLON", "GND", 1, 14.0)
    driver("ddv", "efp", "efn", "div_ckp", "div_ckn", 1.86, 2.05)                  # divider driver, resistive
    divider("div_ckp", "div_ckn")
    names = [l.split()[0] for l in L]
    dn = [n for n, c in collections.Counter(x.lower() for x in names).items() if c > 1]
    nets = collections.defaultdict(set)
    for l in L:
        t = l.split(); k = {"Q": 4, "R": 3, "C": 3, "L": 4}[t[0][0]]
        if "svaricap" in l: k = 4
        for x in t[1:1+k]: nets[x.lower()].add(x)
    nc = [v for v in nets.values() if len(v) > 1]
    assert not dn and not nc, (dn, nc)
    ports = "GND PLLN PLLP RXLON RXLOP TXLON TXLOP VCC VTUNE"
    out = ["* LO core - LVS reference netlist (generated by lo_core_netlist.py)", f".SUBCKT lo_core {ports}"] + L + [".ENDS lo_core"]
    open("lo_core_lvs.cdl", "w").write("\n".join(out) + "\n")
    print(f"lo_core_lvs.cdl: {len(L)} devices, {len(nets)} nets, no name or case collisions")
if __name__ == "__main__":
    build()
