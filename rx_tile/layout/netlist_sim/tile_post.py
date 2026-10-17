"""tile_post.py - post-layout model of the RX tile: LVS netlist (simulated) + interconnect from the tile geometry + RF pad."""
import re, sys
from build_post import microstrip, line, H_TM2, H_TM1
def via(name, a, b, L): return f"Lv_{name} {a} {b} {L}\n"
def build(src="rx_tile_sim.sp", out="rx_tile_post.sp", lb_scale=1.0, lc=None, rp=None):
    s = open(src).read()
    add = []
    # RF pad (TopMetal-only, 42 fF via lossy substrate) + pad-to-Cin line (~105 um TM2 w10)
    add.append("Cpad RFIN spad 4.2e-14\nRspad spad GND 20\n")
    t, _ = line("rfin", "RFIN", "rfin_c", 105, 10, H_TM2); add.append(t)
    s = s.replace("XCin_0 in RFIN GND", "XCin_0 in rfin_c GND")
    # in: Cin PLUS -> 231 um TM2 (w5) + 2 vias -> Lb
    add.append(via("in1", "in", "in_a", "3p")); t, _ = line("in", "in_a", "in_b", 231, 5, H_TM2); add.append(t)
    add.append(via("in2", "in_b", "in_l", "3p"))
    s = s.replace("XLb in b1 ind_lb", "XLb in_l b1_l ind_lb")
    # b1: Lb lead -> TM1 stub 8 um + via -> Q1 base bar
    t, _ = line("b1", "b1_l", "b1_v", 8, 7, H_TM1); add.append(t); add.append(via("b1", "b1_v", "b1", "4p"))
    # Le: via M2-TM2, 47 um strip (ind_le), via to the plane
    s = s.replace("Xle e1_le GND ind_le", "L_le1 e1_le e1a 4p\nXle e1a e1b ind_le\nL_le2 e1b GND 3p")
    # c1 (Metal2 ~30 um)
    add.append("C_c1 c1 GND 3f\n")
    # b2: Q2 base -> 130 um Metal3 bus under the plane -> Ccas / R1 / R2
    s = s.replace("XQ2 out b2 c1 GND npn13G2", "XQ2 out_q b2q c1 GND npn13G2")
    add.append("L_b2 b2q b2 41p\nC_b2a b2q GND 9.5f\nC_b2b b2 GND 9.5f\n")
    # out: Q2 collector -> via -> 25 um TM1 (w4) -> Lc lead; Cout branch 30 um TM1 (w3) + via to M5
    add.append(via("o1", "out_q", "out_v", "4p")); t, _ = line("out", "out_v", "out", 25, 4, H_TM1); add.append(t)
    t, _ = line("cob", "out", "out_c", 30, 3, H_TM1); add.append(t); add.append(via("co", "out_c", "out_m", "3p"))
    s = s.replace("XCout_0 b3 out GND", "XCout_0 b3_c out_m GND")
    # VCC: Lc lead -> TM1 stub + via -> 86 um TM2 -> 70 um TM2 -> Cdec -> 100 um TM2 -> rail
    s = s.replace("XLc VCC out ind_lc", "XLc vcc_l out ind_lc")
    s = re.sub(r"XRP out VCC GND rppd", "XRP out vcc_l GND rppd", s)
    t, _ = line("v1", "vcc_l", "vcc_a", 15, 5, H_TM1); add.append(t); add.append(via("v1", "vcc_a", "vcc_b", "2p"))
    t, _ = line("v2", "vcc_b", "vcc_c", 86, 5, H_TM2); add.append(t)
    t, _ = line("v3", "vcc_c", "vdec", 70, 5, H_TM2); add.append(t)
    t, _ = line("v4", "vdec", "VCC", 100, 5, H_TM2); add.append(t)
    s = s.replace("XCdec_0 VCC GND GND", "XCdec_0 vdec GND GND").replace("XCdec_1 VCC GND GND", "XCdec_1 vdec GND GND")
    # LNA -> mixer link: Cout PLUS -> via -> 180 um TM2 (w5) -> via -> 63 um TM1 (w3) -> via -> b3
    add.append(via("l1", "b3_c", "lk_a", "3p")); t, _ = line("link", "lk_a", "lk_b", 180, 5, H_TM2); add.append(t)
    add.append(via("l2", "lk_b", "lk_c", "3p")); t, _ = line("link2", "lk_c", "lk_d", 63, 3, H_TM1); add.append(t)
    add.append(via("l3", "lk_d", "b3", "4p"))
    # LO jogs: coupling caps -> 45 um Metal5 over the plane -> Q4/Q5 bases
    for n in ("mlop", "mlon"):
        s = re.sub(rf"(XCc[12]_0 d[pn]) {n} ", rf"\1 {n}_c ", s)
        add.append(f"L_{n} {n}_c {n} 15p\nC_{n}a {n}_c GND 3f\nC_{n}b {n} GND 3f\n")
    # optional re-tune knobs
    if lb_scale != 1.0: s = s.replace("XLb in_l b1_l ind_lb", f"XLb in_l b1_l ind_lb_s")
    s = s.replace(".ends rx_tile", "* ======== layout interconnect (post-layout) ========\n" + "".join(add) + ".ends rx_tile")
    if rp: s = re.sub(r"(XRP out vcc_l GND rppd w=2u) l=\S+", rf"\1 l={rp}", s)
    open(out, "w").write(s)
if __name__ == "__main__":
    build()
