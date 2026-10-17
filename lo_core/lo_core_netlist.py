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
def ind3(n, la, lc, lb, w, d, nr=2, s=2.1): dev(f"{n} {la} {lc} {lb} GND inductor3 w={w}u s={s}u d={d}u nr_r={nr}")

def vco():
    p = "vco_"
# VCO coil: hand-drawn single-turn centre-tapped coil (layout coil1t.py), octagonal TopMetal2, w=10u, inner 150u,
    # open at the bottom between the TopMetal1 leads, centre tap from the top midpoint down the symmetry axis.
    # (IHP's inductor3 nr_r=1 PCell is wrong: its ring is closed where both leads attach.) Parameters below are what
    # IHP's LVS deck measures on this geometry (its calc_ind_params, reproduced exactly on the PCell; s = ring end to tap).
    ind3("Lvco", "vcop", "VCC", "vcon", 10, 150.0, nr=1, s=16.11)                       # tank coil, centre tap to VCC (EM pending)
    mim("Cvco_cv1", "vcop", p+"g1", 16); mim("Cvco_cv2", "vcon", p+"g2", 16)   # re-centred against the post-layout model with band select (11.3 -> 8.55 -> 7.55)
    rhigh("Rvco_g1", p+"vgb", p+"g1", 1, 7.0); rhigh("Rvco_g2", p+"vgb", p+"g2", 1, 7.0)
    rhigh("Rvco_gb1", "VCC", p+"vgb", 1, 13.30); rhigh("Rvco_gb2", p+"vgb", "GND", 1, 13.30); mim("Cvco_gb", p+"vgb", "GND", 33)
    dev(f"Cvco_var {p}g1 VTUNE {p}g2 GND sg13_hv_svaricap l=0.3u w=9.74u Nx=7")      # 7 fingers + 16 um coupling caps (range vs extracted parasitics)
    # band select: switched caps (2 x 3.5 um rfcmim) + LV NMOS (16 um, 8 fingers) between them; BSEL = 1.2 V -> lower sub-band (~0.7 GHz down)
    mim("Cbs_1", "vcop", "bs_s1", 4.5); mim("Cbs_2", "vcon", "bs_s2", 4.5)       # band-select unit sized against the extracted parasitics
    dev("Mbs bs_s1 bs_g bs_s2 GND sg13_lv_nmos w=24u l=0.13u ng=12 m=1")
    rhigh("Rbs_1", "bs_s1", "GND", 1, 14.0); rhigh("Rbs_2", "bs_s2", "GND", 1, 14.0); rhigh("Rbs_g", "BSEL", "bs_g", 1, 14.0)
    npn("Qvco_6", "vcop", p+"b6", p+"tail", 4); npn("Qvco_7", "vcon", p+"b7", p+"tail", 4)
    mim("Cvco_b6", "vcon", p+"b6", 9); mim("Cvco_b7", "vcop", p+"b7", 9)
    rppd("Rvco_b6", p+"vbb", p+"b6", 1, 7.47); rppd("Rvco_b7", p+"vbb", p+"b7", 1, 7.47)
    rppd("Rvco_bb1", "VCC", p+"vbb", 1, 15.21); rppd("Rvco_bb2", p+"vbb", "GND", 1, 22.95); mim("Cvco_bb", p+"vbb", "GND", 33)
    rppd("Rvco_tail", p+"tail", "GND", 2, 1.03)                          # ~168 ohm: +30% tail current (LO drive)
def emitter_followers():
    npn("Qef_1", "VCC", "vcop", "efp", 2); npn("Qef_2", "VCC", "vcon", "efn", 2)
    rppd("Ref_1", "efp", "GND", 2, 5.15); rppd("Ref_2", "efn", "GND", 2, 5.15)   # ~700 ohm: stronger emitter followers
def driver(tag, inp, inn, outp, outn, rtl, rdl, coil=None, swap_coil_leads=False, rtw=2):
    """realized limiting driver (lodrv_g); coil=(w, d) -> inductor3 load with centre tap to VCC, else resistive only"""
    p = tag + "_"; up = tag.upper()
    mim(f"C{up}_i1", inp, p+"b1", 12); mim(f"C{up}_i2", inn, p+"b2", 12)   # 12 um: less bottom-plate load on the buses
    rppd(f"R{up}_v1", "VCC", p+"vbd", 1, 17.53); rppd(f"R{up}_v2", p+"vbd", "GND", 1, 20.63); mim(f"C{up}_vb", p+"vbd", "GND", 33)
    rppd(f"R{up}_b1", p+"vbd", p+"b1", 1, 19.08); rppd(f"R{up}_b2", p+"vbd", p+"b2", 1, 19.08)
    npn(f"Q{up}_a", p+"dp", p+"b1", p+"t", 2); npn(f"Q{up}_b", p+"dn", p+"b2", p+"t", 2)
    rppd(f"R{up}_t", p+"t", "GND", rtw, rtl)
    if coil:
        # The layout rotates the RX pre-driver's coil by 270 deg (leads facing the driver). The LVS deck assigns inductor3
        # terminals by lead POSITION, so for that coil its first terminal is the lead wired to dn. inductor3 is a symmetric
        # centre-tapped coil (outer leads interchangeable, identical halves in the EM model), so the netlist records the
        # leads in the order the extractor reads them: electrically identical, and LVS can match the driver uncrossed.
        a_, b_ = (p+"dn", p+"dp") if swap_coil_leads else (p+"dp", p+"dn")
        ind3(f"L{up}", a_, "VCC", b_, *coil)
    rppd(f"R{up}_d1", "VCC", p+"dp", 2, rdl); rppd(f"R{up}_d2", "VCC", p+"dn", 2, rdl)
    mim(f"C{up}_c1", p+"dp", outp, 12); mim(f"C{up}_c2", p+"dn", outn, 12)
def latch(tag, d, db, ck, ckb, q, qb, nt, rll, re, rlw=2, rew=4):
    p = tag + "_"; up = tag.upper()
    rppd(f"R{up}_lp", "VCC", q, rlw, rll); rppd(f"R{up}_ln", "VCC", qb, rlw, rll)
    npn(f"Q{up}_d1", qb, d, p+"ed", 1); npn(f"Q{up}_d2", q, db, p+"ed", 1)
    npn(f"Q{up}_h1", qb, q, p+"eh", 1); npn(f"Q{up}_h2", q, qb, p+"eh", 1)
    npn(f"Q{up}_c1", p+"ed", ck, p+"et", 1); npn(f"Q{up}_c2", p+"eh", ckb, p+"et", 1)
    npn(f"Q{up}_t", p+"et", "div_vbt", p+"etr", nt); rppd(f"R{up}_e", p+"etr", "GND", rew, re)
def divider(ckp, ckn):
    rppd("Rdiv_ref", "VCC", "div_vbt", 1, 9.5); npn("Qdiv_br", "div_vbt", "div_vbt", "div_ebr", 1)
    rppd("Rdiv_ebr", "div_ebr", "GND", 2, 2.05); mim("Cdiv_bt", "div_vbt", "GND", 25)
    rppd("Rdiv_k1", "VCC", "div_vck", 1, 15.21); rppd("Rdiv_k2", "div_vck", "GND", 1, 22.95); mim("Cdiv_k", "div_vck", "GND", 33)
    rppd("Rdiv_ck1", "div_vck", ckp, 1, 7.47); rppd("Rdiv_ck2", "div_vck", ckn, 1, 7.47)
    latch("dm1", "s1qb", "s1q", ckp, ckn, "m1q", "m1qb", 9, 1.11, 0.75, rlw=4, rew=8)   # 4.5 mA / 89 ohm
    latch("ds1", "m1q", "m1qb", ckn, ckp, "s1q", "s1qb", 9, 1.11, 0.75, rlw=4, rew=8)
    mim("Cdiv_c1", "s1q", "c2p", 8); mim("Cdiv_c2", "s1qb", "c2n", 8)   # 8 um: less load on the 12 GHz nodes
    rppd("Rdiv_b1", "div_vck", "c2p", 1, 19.08); rppd("Rdiv_b2", "div_vck", "c2n", 1, 19.08)
    latch("dm2", "s2qb", "s2q", "c2p", "c2n", "m2q", "m2qb", 6, 0.76, 1.28, rew=8)   # 3 mA / 134 ohm
    latch("ds2", "m2q", "m2qb", "c2n", "c2p", "s2q", "s2qb", 6, 0.76, 1.28, rew=8)
    mim("Cdiv_o1", "s2q", "div_o1", 18.2); mim("Cdiv_o2", "s2qb", "div_o2", 18.2)
    rppd("Rdiv_o1", "VCC", "div_vbo", 1, 9.5); rhigh("Rdiv_o2", "div_vbo", "GND", 1, 5.53); mim("Cdiv_bo", "div_vbo", "GND", 33)   # vbo +~0.4 V: tail out of saturation at the slow corner
    rppd("Rdiv_bo1", "div_vbo", "div_o1", 1, 19.08); rppd("Rdiv_bo2", "div_vbo", "div_o2", 1, 19.08)
    npn("Qdiv_o1", "PLLN", "div_o1", "div_eo", 4); npn("Qdiv_o2", "PLLP", "div_o2", "div_eo", 4)
    npn("Qdiv_to1", "div_eo", "div_vbt", "div_eto1", 10); npn("Qdiv_to2", "div_eo", "div_vbt", "div_eto2", 10)
    rppd("Rdiv_eo1", "div_eto1", "GND", 16, 0.68); rppd("Rdiv_eo2", "div_eto2", "GND", 16, 0.68)   # ~14 ohm: ~15 mA at the slow corner (~21 mA typ)
    rppd("Rdiv_t1", "VCC", "PLLP", 10, 1.66); rppd("Rdiv_t2", "VCC", "PLLN", 10, 1.66)
def build():
    vco(); emitter_followers()
    driver("prx", "efp", "efn", "RXLOP", "RXLON", 0.53, 2.83, coil=(4, 65.36), swap_coil_leads=True)   # RX pre-driver, 3.5 mA, EM coil (rotated in layout)
    rhigh("Rbl_r1", "RXLOP", "GND", 1, 14.0); rhigh("Rbl_r2", "RXLON", "GND", 1, 14.0)
    driver("ptx", "efp", "efn", "TXLOP", "TXLON", 1.15, 2.83, coil=(4, 83.47))      # TX pre-driver, 2 mA, EM coil
    rhigh("Rbl_t1", "TXLOP", "GND", 1, 14.0); rhigh("Rbl_t2", "TXLON", "GND", 1, 14.0)
    driver("ddv", "efp", "efn", "div_ckp", "div_ckn", 1.0, 0.89, rtw=4)   # faster divider driver: ~150 ohm loads, ~2x current                  # divider driver, resistive
    divider("div_ckp", "div_ckn")
    names = [l.split()[0] for l in L]
    dn = [n for n, c in collections.Counter(x.lower() for x in names).items() if c > 1]
    nets = collections.defaultdict(set)
    for l in L:
        t = l.split(); k = {"Q": 4, "R": 3, "C": 3, "L": 4, "M": 4}[t[0][0]]
        if "svaricap" in l: k = 4
        for x in t[1:1+k]: nets[x.lower()].add(x)
    nc = [v for v in nets.values() if len(v) > 1]
    assert not dn and not nc, (dn, nc)
    ports = "BSEL GND PLLN PLLP RXLON RXLOP TXLON TXLOP VCC VTUNE"
    out = ["* LO core - LVS reference netlist (generated by lo_core_netlist.py)", f".SUBCKT lo_core {ports}"] + L + [".ENDS lo_core"]
    open("lo_core_lvs.cdl", "w").write("\n".join(out) + "\n")
    # KLayout-PEX runs IHP's LVS with device combining OFF: multi-finger MOS must be written as their individual fingers
    Lk = []
    for l in L:
        t = l.split()
        if t[0].startswith("M") and "sg13_lv_nmos" in t:
            p = dict(x.split("=") for x in t if "=" in x); ng = int(p["ng"]); wf = float(p["w"].rstrip("u")) / ng
            Lk += [f"{t[0]}_f{i} {t[1]} {t[2]} {t[3]} {t[4]} sg13_lv_nmos w={wf:g}u l={p['l']} ng=1 m=1" for i in range(ng)]
        else: Lk.append(l)
    open("lo_core_lvs_kpex.cdl", "w").write("\n".join(["* LO core - reference netlist for KLayout-PEX (multi-finger MOS split into fingers)", f".SUBCKT lo_core {ports}"] + Lk + [".ENDS lo_core"]) + "\n")
    print(f"lo_core_lvs.cdl: {len(L)} devices, {len(nets)} nets, no name or case collisions")
if __name__ == "__main__":
    build()
