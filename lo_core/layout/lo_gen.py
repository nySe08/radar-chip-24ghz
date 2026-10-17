"""lo_gen.py - LO core layout generator (IHP SG13G2). Stage 1: VCO + emitter followers wired."""
"""(placement) - LO core placement: VCO (centre-top), emitter followers, RX pre-driver (H-tree root at the bottom),
TX pre-driver (right, output up to the PAs), divider driver + /4 divider (left, output to the PLL pads)."""
from layoutlib import Builder
B = Builder("lo_core"); place = B.place
MIM = lambda w: dict(w=f"{w}u", l=f"{w}u")
def R(key, kind, x, y, w, l, rot=0): place(key, kind, x, y, rot=rot, w=f"{w}u", l=f"{l}u")
X0 = 440.0                                              # symmetry axis of the VCO / emitter followers / RX pre-driver
# ---------------- VCO ----------------
# VCO coil: CORRECT single-turn centre-tapped coil (coil1t.py). IHP's inductor3 nr_r=1 PCell is wrong: ring closed at the
# bottom where both leads attach (via-patched = ~60 pH short, EM-confirmed). Same markers/pins/footprint as the PCell.
import coil1t, ihp
pya = ihp.pya
_c1t, _ = coil1t.build(B.ly, 150.0, 10.0, ihp=ihp, name="inductor3_1t_w10_d150")
B.DEV["Lvco"] = B.top.insert(pya.DCellInstArray(_c1t.cell_index(), pya.DCplxTrans(1, 0, False, X0, 400)))
place("Qvco_6", "npn13G2", X0 - 26, 378, Nx=4); place("Qvco_7", "npn13G2", X0 + 14, 378, Nx=4)
place("Cvco_b6", "rfcmim", X0 - 18.9, 364.35, rot=180, **MIM(9)); place("Cvco_b7", "rfcmim", X0 + 18.9, 355.35, **MIM(9))   # compact: beside the verticals, inputs inward
place("Cvar", "SVaricap", X0 - 5.4, 329.0, rot=270, w="9.74u", l="0.3u", Nx=7)                # G1 left, G2 right, W up
place("Cvco_cv1", "rfcmim", 405.6, 331, rot=270, **MIM(16)); place("Cvco_cv2", "rfcmim", 458.4, 331, rot=270, **MIM(16))   # 16 um, mirrored, clear of the verticals  # compact: PLUS up, MINUS down
R("Rvco_g1", "rhigh", X0 - 22, 300, 1, 7.0); R("Rvco_g2", "rhigh", X0 + 21, 300, 1, 7.0)
R("Rvco_b6", "rppd", X0 - 60, 370, 1, 7.47); R("Rvco_b7", "rppd", X0 + 59, 370, 1, 7.47)
R("Rvco_tail", "rppd", X0 - 1, 360, 2, 1.03)
place("Cvco_gb", "rfcmim", X0 - 134, 330, **MIM(33)); R("Rvco_gb1", "rhigh", X0 - 93, 330, 1, 13.30); R("Rvco_gb2", "rhigh", X0 - 89, 330, 1, 13.30)
place("Cvco_bb", "rfcmim", X0 + 92, 330, **MIM(33)); R("Rvco_bb1", "rppd", X0 + 140, 330, 1, 15.21); R("Rvco_bb2", "rppd", X0 + 145, 330, 1, 22.95)
# ---------------- band select (below the emitter followers): 2 x 2.5 um caps, 4-finger LV NMOS on the centre line ----------------
place("Cbs_1", "rfcmim", 426.3, 283.5, rot=180, w="4.5u", l="4.5u")       # input plate right (vcop), output plate left
place("Cbs_2", "rfcmim", 453.23, 279.0, w="4.5u", l="4.5u")               # input plate left (vcon), output plate right
place("Mbs", "nmos", 436.8, 278.0, w="24u", l="0.13u", ng=12)
place("Rbs_1", "rhigh", 433.6, 262.0, w="1u", l="14.0u"); place("Rbs_2", "rhigh", 445.3, 262.0, w="1u", l="14.0u")
place("Rbs_g", "rhigh", 410.0, 275.0, w="1u", l="14.0u")
# ---------------- emitter followers ----------------
place("Qef_1", "npn13G2", X0 - 14, 296, Nx=2); place("Qef_2", "npn13G2", X0 + 8, 296, Nx=2)          # moved up: shorter tank taps
R("Ref_1", "rppd", X0 - 26, 265.1, 2, 5.15); R("Ref_2", "rppd", X0 + 23, 265.1, 2, 5.15)   # tops stay at y=270.5 (above the efn bus)
# ---------------- drivers (generic: inputs from the emitter followers, outputs via 12 um coupling caps) ----------------
def driver(tag, x, y, rtl, rdl, coil=None, coil_xy=None, coil_rot=0, rtw=2):
    up = tag.upper()
    place(f"C{up}_i1", "rfcmim", x - 50, y + 50, **MIM(12)); place(f"C{up}_i2", "rfcmim", x + 34.03, y + 55.03, rot=180, **MIM(12))   # 12 um, mirrored
    place(f"Q{up}_a", "npn13G2", x - 14, y + 20, Nx=2); place(f"Q{up}_b", "npn13G2", x + 8, y + 20, Nx=2)
    R(f"R{up}_b1", "rppd", x - 24, y - 8, 1, 19.08); R(f"R{up}_b2", "rppd", x + 23, y - 8, 1, 19.08)
    R(f"R{up}_t", "rppd", x - 1, y - 4, rtw, rtl)
    R(f"R{up}_d1", "rppd", x - 30, y + 18, 2, rdl); R(f"R{up}_d2", "rppd", x + 27, y + 18, 2, rdl)
    place(f"C{up}_c1", "rfcmim", x - 32, y - 28, rot=180, **MIM(12)); place(f"C{up}_c2", "rfcmim", x + 26, y - 40, **MIM(12))   # mirrored
    place(f"C{up}_vb", "rfcmim", x - 105, y - 44, **MIM(33)); R(f"R{up}_v1", "rppd", x - 64, y - 30, 1, 17.53); R(f"R{up}_v2", "rppd", x - 59, y - 30, 1, 20.63)
    if coil: place(f"L{up}", "inductor3", *coil_xy, rot=coil_rot, w=f"{coil[0]}u", s="2.1u", d=f"{coil[1]}u", nr_r=2, subE=False)
driver("prx", X0, 160, 0.53, 2.83, coil=(4, 65.36), coil_xy=(X0 + 64, 192), coil_rot=270)       # RX pre-driver, coil to the right
place("Rbl_r1", "rhigh", X0 - 8, 80, w="1u", l="14.0u"); place("Rbl_r2", "rhigh", X0 + 7, 80, w="1u", l="14.0u")
driver("ptx", X0 + 330, 300, 1.15, 2.83, coil=(4, 83.47), coil_xy=(X0 + 330, 420), coil_rot=0)  # TX pre-driver, coil above
place("Rbl_t1", "rhigh", X0 + 291, 225, w="1u", l="14.0u"); place("Rbl_t2", "rhigh", X0 + 361, 225, w="1u", l="14.0u")
driver("ddv", X0 - 200, 230, 1.0, 0.89, rtw=4)                                                           # divider driver (resistive)
# ---------------- /4 divider (left): 4 row-latches stacked; bias at the bottom; coupling caps + output stage on top ----------------
PL = 11.0                                        # transistor pitch inside a latch row
def latch(tag, X, Y, nt, rll, re, rlw=2, rew=4):
    """row latch: c1 | d1 d2 | h1 h2 | c2 at pitch PL; tail Qt + Re below the row; loads RLn/RLp above"""
    up = tag.upper()
    for i, n in enumerate(("c1", "d1", "d2", "h1", "h2", "c2")): place(f"Q{up}_{n}", "npn13G2", X + i * PL, Y, Nx=1)
    place(f"Q{up}_t", "npn13G2", X + 2.5 * PL - 2.0, Y - 16, Nx=nt); R(f"R{up}_e", "rppd", X + 2.5 * PL + 12, Y - 24, rew, re)
    dx_ = (rlw - 2) / 2.0                                            # wider loads grow symmetrically about the same centre
    R(f"R{up}_ln", "rppd", X + PL + 5 - dx_, Y + 14, rlw, rll); R(f"R{up}_lp", "rppd", X + 2 * PL + 5 - dx_, Y + 14, rlw, rll)
# two latch pairs side by side: stage 2 (left, X=30) and stage 1 (right, X=140); master at Y=50, slave at Y=98
LAT = {"dm2": (30.0, 50.0, 6, 0.76, 1.28, 2, 8), "ds2": (30.0, 98.0, 6, 0.76, 1.28, 2, 8), "dm1": (140.0, 50.0, 9, 1.11, 0.75, 4, 8), "ds1": (140.0, 98.0, 9, 1.11, 0.75, 4, 8)}
for tag, (X_, Y_, nt, rll, re, rlw, rew) in LAT.items(): latch(tag, X_, Y_, nt, rll, re, rlw, rew)
# bias reference, clock-input bias, their decaps: bottom middle
R("Rdiv_ck1", "rppd", 216, 24, 1, 7.47); R("Rdiv_ck2", "rppd", 220, 24, 1, 7.47)
place("Cdiv_k", "rfcmim", 236, 20, **MIM(33)); R("Rdiv_k1", "rppd", 284, 20, 1, 15.21); R("Rdiv_k2", "rppd", 289, 20, 1, 22.95)
place("Cdiv_bt", "rfcmim", 287, 95, rot=180, **MIM(25))                       # top plate faces the bias generator
R("Rdiv_ref", "rppd", 302, 30, 1, 9.5); place("Qdiv_br", "npn13G2", 312, 36, Nx=1); R("Rdiv_ebr", "rppd", 318, 26, 2, 2.05)
# inter-stage coupling (stage 1 -> stage 2) above the pairs, with the stage-2 clock bias resistors
place("Cdiv_c1", "rfcmim", 118.2, 154.2, rot=180, **MIM(8)); place("Cdiv_c2", "rfcmim", 152.2, 154.2, rot=180, **MIM(8))   # inputs right, outputs left
R("Rdiv_b1", "rppd", 166, 134, 1, 19.08); R("Rdiv_b2", "rppd", 171, 134, 1, 19.08)
# output stage (top of the left column, toward the PLL pads)
place("Qdiv_to1", "npn13G2", 34, 290, Nx=10); place("Qdiv_to2", "npn13G2", 68, 290, Nx=10)
R("Rdiv_eo1", "rppd", 40, 278, 16, 0.68); R("Rdiv_eo2", "rppd", 74, 278, 16, 0.68)
place("Qdiv_o1", "npn13G2", 40, 306, Nx=4); place("Qdiv_o2", "npn13G2", 74, 306, Nx=4)
R("Rdiv_t1", "rppd", 38, 318, 10, 1.66); R("Rdiv_t2", "rppd", 72, 318, 10, 1.66)
place("Cdiv_o1", "rfcmim", 122.2, 286.2, rot=180, **MIM(18.2)); place("Cdiv_o2", "rfcmim", 122.2, 322.2, rot=180, **MIM(18.2))   # outputs face the transistors
place("Cdiv_bo", "rfcmim", 14, 336, **MIM(33)); R("Rdiv_o1", "rppd", 62, 336, 1, 9.5); R("Rdiv_o2", "rhigh", 68, 336, 1, 5.53)
R("Rdiv_bo1", "rppd", 88, 336, 1, 19.08); R("Rdiv_bo2", "rppd", 94, 336, 1, 19.08)
pin, ends, pins_of, rect, wire, via, gnd_via = B.pin, B.ends, B.pins_of, B.rect, B.wire, B.via, B.gnd_via
# ---- IHP inductor3 with nr_r=1 is OPEN (no TopVia2 where its TM1 leads meet the TM2 ring): add the missing via arrays
def fix_open_coil(key):
    import klayout.db as kdb
    inst = B.DEV[key]; c = B.ly.cell(inst.cell_index)
    tm1 = kdb.Region(c.begin_shapes_rec(B.ly.find_layer(126, 0))); tm2 = kdb.Region(c.begin_shapes_rec(B.ly.find_layer(134, 0)))
    tv2 = kdb.Region(c.begin_shapes_rec(B.ly.find_layer(133, 0))); cb = c.dbbox(); n = 0
    for p in (tm1 & tm2).each():
        b = p.bbox()
        if not tv2.interacting(kdb.Region(b)).is_empty(): continue                 # the top crossover already has cuts
        bb = b.to_dtype(B.ly.dbu)
        if bb.top > cb.bottom + 100.0: continue                                      # only the lead overlaps near the bottom
        enc, cut, pitch = 0.63, 0.9, 1.96
        nx = int((bb.width() - 2 * enc - cut) / pitch + 1e-6) + 1; ny = int((bb.height() - 2 * enc - cut) / pitch + 1e-6) + 1
        for i in range(nx):
            for j in range(ny):
                x, y = bb.left + enc + i * pitch, bb.bottom + enc + j * pitch
                B.top.shapes(B.ly.layer(133, 0)).insert(kdb.DBox(x, y, x + cut, y + cut).transformed(inst.dcplx_trans)); n += 1
    return n
NCUT = 0                                               # the corrected coil carries its own lead vias
# ======================= stage 1: VCO + emitter followers =======================
la, lc, lb = pin("Lvco", "LA"), pin("Lvco", "LC"), pin("Lvco", "LB")
q6b, q6c, q6e = pin("Qvco_6", "B"), pin("Qvco_6", "C"), pin("Qvco_6", "E")
q7b, q7c, q7e = pin("Qvco_7", "B"), pin("Qvco_7", "C"), pin("Qvco_7", "E")
cb6p, cb6m, cb7p, cb7m = pin("Cvco_b6", "PLUS"), pin("Cvco_b6", "MINUS"), pin("Cvco_b7", "PLUS"), pin("Cvco_b7", "MINUS")
g1b, g2b, wv = pin("Cvar", "G1"), pin("Cvar", "G2"), pin("Cvar", "W")
cv1p, cv1m, cv2p, cv2m = pin("Cvco_cv1", "PLUS"), pin("Cvco_cv1", "MINUS"), pin("Cvco_cv2", "PLUS"), pin("Cvco_cv2", "MINUS")
cgbp, cgbm, cbbp, cbbm = pin("Cvco_gb", "PLUS"), pin("Cvco_gb", "MINUS"), pin("Cvco_bb", "PLUS"), pin("Cvco_bb", "MINUS")
ef1b, ef1c, ef1e = pin("Qef_1", "B"), pin("Qef_1", "C"), pin("Qef_1", "E")
ef2b, ef2c, ef2e = pin("Qef_2", "B"), pin("Qef_2", "C"), pin("Qef_2", "E")
rg1, rg2, rb6, rb7, rtl = ends("Rvco_g1"), ends("Rvco_g2"), ends("Rvco_b6"), ends("Rvco_b7"), ends("Rvco_tail")
rgb1, rgb2, rbb1, rbb2, ref1, ref2 = ends("Rvco_gb1"), ends("Rvco_gb2"), ends("Rvco_bb1"), ends("Rvco_bb2"), ends("Ref_1"), ends("Ref_2")
XP, XN = 431.9, 448.1                                      # vcop / vcon vertical tracks (fixed; the single-turn coil leads sit outside them)
YVB1, YVB2 = 393.0, 305.0                                  # VCC buses (TM2); lower bus above the raised EFs
wire("TopMetal2", [(300, YVB1), (600, YVB1)], 5); wire("TopMetal2", [(300, YVB2), (600, YVB2)], 5)
wire("TopMetal2", [(300, YVB2), (300, YVB1)], 5); wire("TopMetal2", [(600, YVB2), (600, YVB1)], 5)
rect("TopMetal2", lc.left, YVB1 - 2.5, lc.right, lc.bottom)            # centre tap -> VCC
# tank: leads -> TM1 stubs -> collectors (M1 pads); then TM1 verticals down to the emitter followers
TV = 2.0                                                          # tank verticals: 2 um TM1 (was 3) - less capacitance on the tank
for (ld, qc, xv) in ((la, q6c, XP), (lb, q7c, XN)):
    rect("TopMetal1", ld.left, 383.4, ld.right, ld.bottom)             # lead stub (10 um) straight down to the jog
    # collector: via stack on the collector bar; TM1 jog from the tank vertical, across the collector, to the lead stub
    xq = qc.center().x
    rect("Metal1", qc.left, qc.bottom, qc.right, 383.0); via(xq, 382.0, "Metal1", "TopMetal1")
    wire("TopMetal1", [(xv, 384.5), (ld.center().x, 384.5)], 2.2)
    wire("TopMetal1", [(xq, 384.5), (xq, 382.0)], 2.2)                  # >= the via's TM1 landing
    wire("TopMetal1", [(xv, 384.5), (xv, 290.0)], TV)
# cross-coupling (compact): vcop -> TM2 (y=366) -> Cb7 inner plate ; vcon -> TM2 (y=354) -> Cb6 inner plate
for (xv, yc, cp) in ((XP, 366.0, cb7p), (XN, 354.0, cb6p)):
    via(xv, yc, "TopMetal1", "TopMetal2"); via(cp.center().x, cp.center().y, "TopMetal1", "TopMetal2")   # via lands on the pin itself
    wire("TopMetal2", [(xv, yc), (cp.center().x, yc), (cp.center().x, cp.center().y)], 4)
# bases: inner cap plate -> via -> M1 -> base bar (pulled down); bias resistor joins at y=373
for (cm, qb, xv, rb) in ((cb6m, q6b, cb6m.left - 1.9, rb6), (cb7m, q7b, cb7m.right + 1.9, rb7)):   # outer plates -> around the caps -> bases
    rect("Metal1", qb.left, 372.5, qb.right, qb.top)
    via(xv, cm.center().y, "Metal1", "Metal5"); wire("Metal5", [(cm.center().x, cm.center().y), (xv, cm.center().y)], 2)
    xb = (qb.left + 0.5) if xv < qb.left else (qb.right - 0.5)
    wire("Metal1", [(xv, cm.center().y), (xv, 373.0), (xb, 373.0)], 1.0)
    wire("Metal1", [(rb[1].center().x, rb[1].center().y), (rb[1].center().x, 373.0), (xv, 373.0)], 1.0)
# tail: emitters joined (M2) -> Rtail -> ground
rect("Metal2", q6e.left, q6e.bottom, q7e.right, q6e.top)
rect("Metal1", rtl[1].left, rtl[1].bottom, rtl[1].right, 367.0); via(rtl[1].center().x, 366.2, "Metal1", "Metal2")
wire("Metal2", [(rtl[1].center().x, 366.2), (rtl[1].center().x, q6e.center().y)], 1.2)
wire("Metal1", [(rtl[0].center().x, rtl[0].center().y), (rtl[0].center().x, 355.5)], 1.0); gnd_via(rtl[0].center().x, 355.5, "Metal1")
# vbb (M3 at y=366): Rb6/Rb7 bottoms, Cbb top plate, Rbb1 bottom, Rbb2 top
YB = 365.0
for r in (rb6[0], rb7[0], rbb1[1], rbb2[1]):                # (each divider resistor: the vbb end is the one nearer the bus)
    via(r.center().x, r.center().y, "Metal1", "Metal3"); wire("Metal3", [(r.center().x, r.center().y), (r.center().x, YB)], 1.0)
wire("Metal3", [(rb6[0].center().x, YB), (rbb2[1].center().x, YB)], 1.0)
v = (cbbp.center().x, YB); via(*v, "Metal3", "TopMetal1"); wire("TopMetal1", [v, (cbbp.center().x, cbbp.center().y)], 2)
for r in (rbb1[0], rgb1[1]):                                # VCC ends of the two bias dividers
    up = r is rgb1[1]
    rect("Metal1", r.left, r.bottom - (0 if up else 1.6), r.right, r.top + (1.6 if up else 0))
    yv = r.center().y + (1.0 if up else -1.0); via(r.center().x, yv, "Metal1", "TopMetal2")
    wire("TopMetal2", [(r.center().x, yv), (r.center().x, YVB1)], 4)
for r in (rbb2[0],):
    wire("Metal1", [(r.center().x, r.center().y), (r.center().x, r.center().y - 3.5)], 1.0); gnd_via(r.center().x, r.center().y - 3.5, "Metal1")
# varactor gates: bars -> M1 pads -> M2 -> Ccv output plates + Rg tops (mirrored)
for (gb, cm, rg, sgn) in ((g1b, cv1m, rg1, -1), (g2b, cv2m, rg2, +1)):
    xo = gb.left - 6.0 if sgn < 0 else gb.right + 6.0
    rect("Metal1", min(xo, gb.left), gb.bottom, max(xo, gb.right), gb.top)
    xv = xo + 1.2 * (-sgn); via(xv, gb.bottom + 1.0, "Metal1", "Metal2")
    yg = cm.bottom - 2.5                                         # below the (compact) Ccv: via M2-M5 under its output plate
    via(cm.center().x, yg, "Metal2", "Metal5"); wire("Metal5", [(cm.center().x, cm.center().y), (cm.center().x, yg)], 2)
    wire("Metal2", [(xv, gb.bottom + 1.0), (xv, yg), (cm.center().x, yg)], 1.0)
    via(rg[1].center().x, rg[1].center().y, "Metal1", "Metal2"); wire("Metal2", [(rg[1].center().x, rg[1].center().y), (rg[1].center().x, yg)], 1.0)
# varactor input plates: vcop -> Ccv1 top (TM1 branch at y=331); vcon -> Ccv2
for (xv, cp) in ((XP, cv1p), (XN, cv2p)):
    wire("TopMetal1", [(xv, 334.0), (cp.center().x, 334.0), (cp.center().x, cp.center().y)], cp.width())   # as wide as the pin
# vgb (M3 at y=296): Rg bottoms -> Cgb top plate, Rgb1 bottom, Rgb2 top
YG = 296.0
for r in (rg1[0], rg2[0]):
    via(r.center().x, r.center().y, "Metal1", "Metal3"); wire("Metal3", [(r.center().x, r.center().y), (r.center().x, YG)], 1.0)
XG = cgbp.left - 3.0
wire("Metal3", [(rg2[0].center().x, YG), (XG, YG), (XG, cgbp.center().y)], 1.0)
v = (XG, cgbp.center().y); via(*v, "Metal3", "TopMetal1"); wire("TopMetal1", [v, (cgbp.center().x, cgbp.center().y)], 2)
for r in (rgb1[0], rgb2[0]):                                 # vgb ends (bottoms), M3 down to the bus
    via(r.center().x, r.center().y, "Metal1", "Metal3"); wire("Metal3", [(r.center().x, r.center().y), (r.center().x, YG)], 1.0)
wire("Metal1", [(rgb2[1].center().x, rgb2[1].center().y), (rgb2[1].center().x, rgb2[1].center().y + 3.5)], 1.0)
gnd_via(rgb2[1].center().x, rgb2[1].center().y + 3.5, "Metal1")
# decap bottom plates -> ground
for cm in (cgbm, cbbm):                                      # ground via straight below the bottom-plate pin (clear of the VCC vias)
    g = (cm.center().x, cm.center().y - 13.0); gnd_via(*g, "Metal5"); wire("Metal5", [(cm.center().x, cm.center().y), g], 2)
# VTUNE: varactor well (W, top) -> M2 -> left edge of the LO core (port)
rect("Metal1", wv.left, wv.bottom, wv.right, 332.6); via(wv.center().x, 331.8, "Metal1", "Metal2")
wire("Metal2", [(wv.center().x, 331.8), (396.0, 331.8), (396.0, 383.0), (6.0, 383.0)], 1.0)
B.text("VTUNE", 7.0, 383.0, gds=(10, 25))
# emitter followers: bases from the tank verticals; collectors to VCC (bus at y=290); emitters -> Ref (efp/efn)
for (xv, eb, ec, ee, rf, sgn) in ((XP, ef1b, ef1c, ef1e, ref1, -1), (XN, ef2b, ef2c, ef2e, ref2, +1)):
    via(xv, 293.6, "Metal1", "TopMetal1")                          # EF base: via landing + thin bar (was an 8 x 5 um M1 pad)
    rect("Metal1", xv - 0.865, 292.7, xv + 0.865, eb.top); rect("Metal1", min(eb.left, xv), eb.bottom, max(eb.right, xv), eb.top)
    xvc = ec.left - 3.5 if sgn < 0 else ec.right + 3.5                       # collector VCC via, away from the tank track
    rect("Metal1", min(xvc - 1.1, ec.left), ec.bottom, max(xvc + 1.1, ec.right), YVB2 + 1.2); via(xvc, YVB2, "Metal1", "TopMetal2")
    xe = ee.left - 6.0 if sgn < 0 else ee.right + 6.0
    rect("Metal2", min(xe, ee.left), ee.bottom, max(xe, ee.right), ee.top)
    via(rf[1].center().x, rf[1].center().y, "Metal1", "Metal2")
    wire("Metal2", [(xe, ee.center().y), (rf[1].center().x, ee.center().y), (rf[1].center().x, rf[1].center().y)], 1.2)
    wire("Metal1", [(rf[0].center().x, rf[0].center().y), (rf[0].center().x, 257.0)], 1.0); gnd_via(rf[0].center().x, 257.0, "Metal1")
# MIM substrate rings of the VCO -> ground (signal MIMs strap out of their cut-outs)
VCO_SIG = ("Cvco_b6", "Cvco_b7", "Cvco_cv1", "Cvco_cv2")
for k in ("Cvco_gb", "Cvco_bb") + VCO_SIG:
    B.ring_ground(k, cutout_keys=VCO_SIG, coil_keys=("Lvco",))

# ======================= band select wiring =======================
B.LY["GatPoly"] = B.ly.layer(5, 0); B.LY["Cont"] = B.ly.layer(6, 0)
OX, OY = 436.8, 278.0                                             # NMOS PCell origin (12 fingers x 2 um)
# stripe and gate-finger positions read from the PCell itself (any finger count)
_c = B.ly.cell(B.DEV["Mbs"].cell_index)
_st = sorted({round((sh.dbbox().left + sh.dbbox().right) / 2, 3) for sh in _c.shapes(B.ly.find_layer(8, 0)).each()})
_gt = sorted({round(sh.dbbox().left, 3) for sh in _c.shapes(B.ly.find_layer(5, 0)).each()})
SX, DX, GX = _st[0::2], _st[1::2], _gt                           # source = even stripes, drain = odd stripes
XG = OX + (_st[0] + _st[-1]) / 2                                  # switch centre (gate via goes straight above it)
# gate: fingers extended up, joined by a poly bar above the active area; a contact above each drain stripe; M1 bar; via above
for gx in GX: rect("GatPoly", OX + gx, OY + 2.18, OX + gx + 0.13, OY + 2.86)
rect("GatPoly", OX + GX[0], OY + 2.50, OX + GX[-1] + 0.13, OY + 2.86)
for cx in DX: rect("Cont", OX + cx - 0.08, OY + 2.60, OX + cx + 0.08, OY + 2.76)
rect("Metal1", OX + DX[0] - 0.16, OY + 2.55, OX + DX[-1] + 0.16, OY + 2.81)
rect("Metal1", XG - 0.15, OY + 2.55, XG + 0.15, OY + 4.2); via(XG, OY + 4.0, "Metal1", "TopMetal2", n=1)
# source side -> M1 bar below the active area -> bs_s1 (left)
XS1, XS2 = OX + SX[0] - 1.05, OX + SX[-1] + 0.6                   # bs_s1 drop (left of the switch), bs_s2 drop (right)
for sx in SX: rect("Metal1", OX + sx - 0.08, OY - 0.90, OX + sx + 0.08, OY)
rect("Metal1", XS1 - 0.3, OY - 0.90, OX + SX[-1] + 0.08, OY - 0.60)
# drain side -> M1 pads + Via1 -> M2 bar above the active area -> bs_s2 (right)
for dx in DX:
    rect("Metal1", OX + dx - 0.145, OY + 2.0, OX + dx + 0.145, OY + 2.29); rect("Via1", OX + dx - 0.095, OY + 2.05, OX + dx + 0.095, OY + 2.24)
rect("Metal2", OX + DX[0] - 0.145, OY + 2.0, XS2 + 0.3, OY + 2.29)
# caps: inputs on the (extended) tank verticals; outputs around underneath on M5 to the switch
cbs1p, cbs1m, cbs2p, cbs2m = pin("Cbs_1", "PLUS"), pin("Cbs_1", "MINUS"), pin("Cbs_2", "PLUS"), pin("Cbs_2", "MINUS")
for xv in (XP, XN): wire("TopMetal1", [(xv, 290.0), (xv, cbs1p.center().y - 1.0)], TV)
YR = 272.8                                                         # cap outputs return just below the caps
wire("Metal5", [(cbs1m.center().x, cbs1m.center().y), (cbs1m.center().x, YR), (XS1, YR)], 2); via(XS1, YR, "Metal1", "Metal5")
wire("Metal1", [(XS1, YR), (XS1, OY - 0.75)], 0.6)
wire("Metal5", [(cbs2m.center().x, cbs2m.center().y), (cbs2m.center().x, YR), (XS2, YR)], 2); via(XS2, YR, "Metal2", "Metal5")
wire("Metal2", [(XS2, YR), (XS2, OY + 2.145)], 0.6)
# bias resistors: switch nodes -> ground (tops on the nodes, bottoms to ground vias)
rb1_, rb2_, rbg_ = ends("Rbs_1"), ends("Rbs_2"), ends("Rbs_g")
wire("Metal1", [(rb1_[1].center().x, rb1_[1].center().y), (XS1, rb1_[1].center().y)], 0.6)
via(rb2_[1].center().x, rb2_[1].center().y, "Metal1", "Metal2", n=1); wire("Metal2", [(rb2_[1].center().x, rb2_[1].center().y), (XS2, rb2_[1].center().y)], 0.6)
for r in (rb1_[0], rb2_[0]):
    wire("Metal1", [(r.center().x, r.center().y), (r.center().x, r.center().y - 3.7)], 0.6); gnd_via(r.center().x, r.center().y - 3.7, "Metal1")
# gate resistor: top -> M2 -> gate via; bottom -> M3 -> BSEL port on the left edge (y=278)
via(rbg_[1].center().x, rbg_[1].center().y, "Metal1", "TopMetal2", n=1)
wire("TopMetal2", [(rbg_[1].center().x, rbg_[1].center().y), (rbg_[1].center().x, 284.0), (XG, 284.0), (XG, OY + 4.0)], 4)
via(rbg_[0].center().x, rbg_[0].center().y, "Metal1", "Metal3")
YBS = 283.0                                                        # BSEL line height (clear of the driver input-cap vias)
wire("Metal3", [(rbg_[0].center().x, rbg_[0].center().y), (rbg_[0].center().x, YBS), (1.0, YBS)], 1.0, end_ext=0)
B.text("BSEL", 2.0, YBS, gds=(30, 25))
BS_SIG = ("Cbs_1", "Cbs_2")
for k in BS_SIG: B.ring_ground(k, cutout_keys=VCO_SIG + BS_SIG, coil_keys=("Lvco",))

# ======================= stage 2: driver template (x3) + emitter-follower outputs + LO outputs =======================
def drv_pins(tag):
    up = tag.upper(); P_ = {}
    for k, labs in ((f"C{up}_i1", ("PLUS", "MINUS")), (f"C{up}_i2", ("PLUS", "MINUS")), (f"Q{up}_a", ("B", "C", "E")), (f"Q{up}_b", ("B", "C", "E")),
                    (f"C{up}_c1", ("PLUS", "MINUS")), (f"C{up}_c2", ("PLUS", "MINUS")), (f"C{up}_vb", ("PLUS", "MINUS"))):
        for l in labs: P_[(k.split("_")[1], l)] = pin(k, l)
    for r in ("b1", "b2", "t", "d1", "d2", "v1", "v2"): P_[r] = ends(f"R{up}_{r}")
    return P_
def wire_driver(tag, vcc_bus_y, vcc_to, extra_x=(), base_drop=21.0):
    """generic driver wiring; returns the collector pads for the per-instance coil hookup"""
    p = drv_pins(tag)
    qab, qac, qae = p[("a", "B")], p[("a", "C")], p[("a", "E")]
    qbb, qbc, qbe = p[("b", "B")], p[("b", "C")], p[("b", "E")]
    # bases: input-cap output plate (M5) -> down past the cap's ring -> via -> M1 -> base bar; bias resistor joins
    for (cm, qb, rb, qcol) in ((p[("i1", "MINUS")], qab, p["b1"], qac), (p[("i2", "MINUS")], qbb, p["b2"], qbc)):
        xv = cm.center().x; yb = qb.bottom - 6.2
        rect("Metal1", qb.left, yb - 0.5, qb.right, qb.top)
        yd = cm.bottom - base_drop                       # layer change below the cap's ring (and clear of the input buses)
        yct = qcol.top + 6.0                             # this transistor's collector M2 track: keep the via >= 2.5 um away
        if abs(yd - yct) < 2.5: yd = yct + 3.0
        xv = (qb.left - 5.4) if cm.center().x < qb.center().x else (qb.right + 6.6)   # drop beside the transistor, clear of the load's VCC via
        wire("Metal5", [(cm.center().x, cm.center().y), (xv, cm.center().y), (xv, yd)], 2); via(xv, yd, "Metal1", "Metal5")
        wire("Metal1", [(xv, yd), (xv, yb), ((qb.left + 0.5) if xv < qb.left else (qb.right - 0.5), yb)], 1.0)
        wire("Metal1", [(rb[1].center().x, rb[1].center().y), (rb[1].center().x, yb), (xv, yb)], 1.0)
    # collectors: M1 pads -> via -> M2 -> output-cap input plate (via M2-TM1 on the pin); load resistor joins on M2
    pads = []
    for (qc, cp, rd, sgn) in ((qac, p[("c1", "PLUS")], p["d1"], -1), (qbc, p[("c2", "PLUS")], p["d2"], +1)):
        rect("Metal1", qc.left, qc.bottom, qc.right, qc.top + 7.6); yc = qc.top + 6.0
        via(qc.center().x, yc, "Metal1", "Metal2")
        wire("Metal2", [(qc.center().x, yc), (cp.center().x, yc), (cp.center().x, cp.center().y)], 1.0)
        via(cp.center().x, cp.center().y, "Metal2", "TopMetal1")
        via(rd[1].center().x, rd[1].center().y, "Metal1", "Metal2"); wire("Metal2", [(rd[1].center().x, rd[1].center().y), (cp.center().x, rd[1].center().y)], 1.0)
        xv = rd[0].center().x + 5.5 * sgn                                    # load resistor's VCC end -> via -> TM2 bus
        wire("Metal1", [(rd[0].center().x, rd[0].center().y), (xv, rd[0].center().y)], 1.0); via(xv, rd[0].center().y, "Metal1", "TopMetal2")
        wire("TopMetal2", [(xv, rd[0].center().y), (xv, vcc_bus_y)], 4)
        pads.append((qc, qc.top + 2.6))
    # tail: emitters joined on M2 -> Rt -> ground
    rect("Metal2", qae.left, qae.bottom, qbe.right, qae.top)
    rt = p["t"]; rect("Metal1", rt[1].left, rt[1].bottom, rt[1].right, qae.bottom - 3.0)
    via(rt[1].center().x, qae.bottom - 3.6, "Metal1", "Metal2"); wire("Metal2", [(rt[1].center().x, qae.bottom - 3.6), (rt[1].center().x, qae.center().y)], 1.2)
    wire("Metal1", [(rt[0].center().x, rt[0].center().y), (rt[0].center().x, rt[0].center().y - 3.7)], 1.0); gnd_via(rt[0].center().x, rt[0].center().y - 3.7, "Metal1")
    # vbd (M3 bus): Rb1/Rb2 bottoms, Rv1/Rv2 tops, Cvb top plate; Rv1 bottom -> VCC; Rv2 bottom -> ground; Cvb bottom plate -> ground
    yv = p["b1"][0].center().y + 2.3
    for r in (p["b1"][0], p["b2"][0], p["v1"][1], p["v2"][1]):
        via(r.center().x, r.center().y, "Metal1", "Metal3"); wire("Metal3", [(r.center().x, r.center().y), (r.center().x, yv)], 1.0)
    cvp, cvm = p[("vb", "PLUS")], p[("vb", "MINUS")]
    xg = cvp.left - 3.5; via(xg, cvp.center().y, "Metal3", "TopMetal1"); wire("TopMetal1", [(xg, cvp.center().y), (cvp.center().x, cvp.center().y)], 2)
    wire("Metal3", [(xg, cvp.center().y), (xg, yv), (p["b2"][0].center().x, yv)], 1.0)
    rv1b = p["v1"][0]; yr = rv1b.center().y - 3.5                          # VCC via kept clear of the input buses
    via(rv1b.center().x, yr, "Metal1", "TopMetal2"); rect("Metal1", rv1b.left, yr - 0.6, rv1b.right, rv1b.top)
    wire("TopMetal2", [(rv1b.center().x, yr), (rv1b.center().x, vcc_bus_y)], 4)
    rv2b = p["v2"][0]; wire("Metal1", [(rv2b.center().x, rv2b.center().y), (rv2b.center().x, rv2b.center().y - 3.7)], 1.0); gnd_via(rv2b.center().x, rv2b.center().y - 3.7, "Metal1")
    g_ = (cvm.center().x, cvm.center().y - 13.0); gnd_via(*g_, "Metal5"); wire("Metal5", [(cvm.center().x, cvm.center().y), g_], 2)
    # driver VCC bus (TM2) and its tie into the VCC ring
    xs = [rv1b.center().x, p["d1"][0].center().x - 5.5, p["d2"][0].center().x + 5.5] + [x for x, _ in vcc_to[:1]] + list(extra_x)
    wire("TopMetal2", [(min(xs), vcc_bus_y), (max(xs), vcc_bus_y)], 4)
    wire("TopMetal2", [(vcc_to[0][0], vcc_bus_y)] + vcc_to, 4)
    return p, pads
# --- RX pre-driver (coil to the right, leads stacked: LA top = dp, LC = VCC, LB bottom = dn)
p_rx, pads = wire_driver("prx", 166.0, [(376.5, 166.0), (376.5, YVB2)], extra_x=(498.0,))
lra, lrc, lrb = pin("LPRX", "LA"), pin("LPRX", "LC"), pin("LPRX", "LB")
(qa_c, ya), (qb_c, yb_) = pads
via(qa_c.center().x, 192.0, "Metal1", "TopMetal1"); rect("Metal1", qa_c.left, qa_c.bottom, qa_c.right, 193.2)
wire("TopMetal1", [(qa_c.center().x, 192.0), (qa_c.center().x, lra.center().y), (lra.left, lra.center().y)], 3, end_ext=0)
via(qb_c.center().x, 184.4, "Metal1", "TopMetal1")
wire("TopMetal1", [(qb_c.center().x, 184.4), (qb_c.center().x, lrb.center().y), (lrb.left, lrb.center().y)], 3, end_ext=0)
wire("TopMetal2", [(lrc.left, lrc.center().y), (498.0, lrc.center().y), (498.0, 166.0)], 4, start_ext=0)
# --- TX pre-driver (coil above, leads side by side: LA = dp, LC = VCC, LB = dn)
p_tx, pads = wire_driver("ptx", 306.0, [(707.0, 306.0), (600.0, 306.0)])
lta, ltc, ltb = pin("LPTX", "LA"), pin("LPTX", "LC"), pin("LPTX", "LB")
(qa_c, ya), (qb_c, yb_) = pads
for (qc, ld) in ((qa_c, lta), (qb_c, ltb)):
    rect("Metal1", qc.left, qc.bottom, qc.right, qc.top + 9.6); yv_ = qc.top + 8.4; via(qc.center().x, yv_, "Metal1", "TopMetal1")
    wire("TopMetal1", [(qc.center().x, yv_), (qc.center().x, 410.0), (ld.center().x, 410.0), (ld.center().x, ld.bottom)], 3, end_ext=0)
wire("TopMetal2", [(ltc.center().x, ltc.bottom), (ltc.center().x, 306.0)], 4, start_ext=0)
# --- divider driver (no coil; outputs to the divider in stage 3)
p_dv, pads = wire_driver("ddv", 236.0, [(273.0, 236.0), (300.0, 236.0), (300.0, YVB2)], base_drop=31.0)
# --- emitter-follower outputs -> driver inputs: efp on Metal3 (y=260), efn on Metal2 (y=252)
YP, YN = 270.0, 267.0                                    # just below the emitter followers, clear of the RX coil (top 264.8)
via(ref1[1].center().x, ref1[1].center().y, "Metal1", "Metal3"); wire("Metal3", [(ref1[1].center().x, ref1[1].center().y), (ref1[1].center().x, YP)], 1.2)
wire("Metal2", [(ref2[1].center().x, ref2[1].center().y), (ref2[1].center().x, YN)], 1.2)
ins = {t: (p[("i1", "PLUS")], p[("i2", "PLUS")]) for t, p in (("rx", p_rx), ("tx", p_tx), ("dv", p_dv))}
wire("Metal3", [(ins["dv"][0].center().x, YP), (ins["tx"][0].center().x, YP)], 1.2)
XD = 699.0                                                   # efn leaves its bus here and goes AROUND the TX output caps
wire("Metal2", [(ins["dv"][1].center().x, YN), (XD, YN), (XD, 236.0), (832.0, 236.0), (832.0, ins["tx"][1].center().y), (ins["tx"][1].center().x, ins["tx"][1].center().y)], 1.2)
for t in ("rx", "tx", "dv"):
    c1p, c2p = ins[t]
    # efp drop: upward drops leave the M3 bus on M2; downward drops stay on M3 until past the efn bus (M2), then M2
    if c1p.center().y > YP:
        via(c1p.center().x, YP, "Metal2", "Metal3"); wire("Metal2", [(c1p.center().x, YP), (c1p.center().x, c1p.center().y)], 1.2)
    else:
        yx = YN - 6.0; wire("Metal3", [(c1p.center().x, YP), (c1p.center().x, yx)], 1.2); via(c1p.center().x, yx, "Metal2", "Metal3")
        wire("Metal2", [(c1p.center().x, yx), (c1p.center().x, c1p.center().y)], 1.2)
    via(c1p.center().x, c1p.center().y, "Metal2", "TopMetal1")
    # efn drop: M2 to the pin (the TX one arrives by the detour above)
    if t != "tx": wire("Metal2", [(c2p.center().x, YN), (c2p.center().x, c2p.center().y)], 1.2)
    via(c2p.center().x, c2p.center().y, "Metal2", "TopMetal1")
# --- RX LO outputs (H-tree root): output caps -> M5 down -> via -> TM2 pair to the bottom edge; bleeds to ground
for (cm, xo, rbl, name) in ((p_rx[("c1", "MINUS")], 432.5, ends("Rbl_r1"), "RXLOP"), (p_rx[("c2", "MINUS")], 447.5, ends("Rbl_r2"), "RXLON")):
    wire("Metal5", [(cm.center().x, cm.center().y), (cm.center().x, 108.0)], 2); via(cm.center().x, 108.0, "Metal5", "TopMetal2")
    wire("TopMetal2", [(cm.center().x, 108.0), (xo, 108.0), (xo, 10.0)], 4, end_ext=0)
    rect("Metal1", rbl[1].left, rbl[1].bottom, rbl[1].right, rbl[1].top + 1.8); via(xo, rbl[1].center().y + 1.2, "Metal1", "TopMetal2")
    wire("Metal1", [(rbl[0].center().x, rbl[0].center().y), (rbl[0].center().x, rbl[0].center().y - 3.7)], 1.0); gnd_via(rbl[0].center().x, rbl[0].center().y - 3.7, "Metal1")
    B.text(name, xo, 11.0)
# --- TX LO outputs: output caps -> via -> TM2 out the right edge; bleeds to ground
for (cm, yo, rbl, name, dx) in ((p_tx[("c1", "MINUS")], 240.0, ends("Rbl_t1"), "TXLOP", -4.0), (p_tx[("c2", "MINUS")], 248.0, ends("Rbl_t2"), "TXLON", +4.0)):
    xv = cm.center().x + dx; via(xv, cm.center().y, "Metal5", "TopMetal2"); wire("Metal5", [(cm.center().x, cm.center().y), (xv, cm.center().y)], 2)
    wire("TopMetal2", [(xv, cm.center().y), (xv, yo), (860.0, yo)], 4, end_ext=0)
    wire("TopMetal2", [(min(xv, rbl[1].center().x), yo), (max(xv, rbl[1].center().x), yo)], 4)        # bleed joins the output line
    rect("Metal1", rbl[1].left, rbl[1].bottom, rbl[1].right, yo + 1.1); via(rbl[1].center().x, yo, "Metal1", "TopMetal2")
    wire("Metal1", [(rbl[0].center().x, rbl[0].center().y), (rbl[0].center().x, rbl[0].center().y - 3.7)], 1.0); gnd_via(rbl[0].center().x, rbl[0].center().y - 3.7, "Metal1")
    B.text(name, 858.0, yo)
# --- driver MIM rings -> ground (library helper: signal MIMs strap out of their cut-outs onto real plane)
DRV_SIG = [f"C{t}_{c}" for t in ("PRX", "PTX", "DDV") for c in ("i1", "i2", "c1", "c2")]
for k in DRV_SIG + [f"C{t}_vb" for t in ("PRX", "PTX", "DDV")]:
    B.ring_ground(k, cutout_keys=tuple(DRV_SIG) + VCO_SIG, coil_keys=("Lvco", "LPRX", "LPTX"))
B.text("VCC", 300.0, YVB1)
B.text("GND", 3.0, 587.0, gds=(50, 25))                       # GND port: on the Metal4 plane (Metal4 text layer), as in the RX tile


# ======================= stage 3a: divider latches (template x4) + pair routing (template x2) =======================
def wire_latch(tag, X, Y):
    up = tag.upper(); Q = {n: {l: pin(f"Q{up}_{n}", l) for l in ("B", "C", "E")} for n in ("c1", "d1", "d2", "h1", "h2", "c2", "t")}
    x0 = {n: Q[n]["E"].center().x for n in ("c1", "d1", "d2", "h1", "h2", "c2")}
    rln, rlp, re_ = ends(f"R{up}_ln"), ends(f"R{up}_lp"), ends(f"R{up}_e")
    # ed / eh: M2 tracks at Y+5; emitter risers; clock-transistor collectors up and in
    for (cn, a, b) in (("c1", "d1", "d2"), ("c2", "h1", "h2")):
        rect("Metal1", Q[cn]["C"].left, Q[cn]["C"].bottom, Q[cn]["C"].right, Y + 5.6); via(x0[cn], Y + 5.0, "Metal1", "Metal2")
        for n in (a, b): rect("Metal2", Q[n]["E"].left, Q[n]["E"].bottom, Q[n]["E"].right, Y + 5.5)
        wire("Metal2", [(x0[cn], Y + 5.0), (x0[b] if cn == "c1" else x0[a], Y + 5.0)], 1.0)
    # q (M3, Y+9): d2 C, h2 C, RLp bottom; down to h1 B through the d2|h1 gap
    for n in ("d2", "h2"): rect("Metal1", Q[n]["C"].left, Q[n]["C"].bottom, Q[n]["C"].right, Y + 9.7); via(x0[n], Y + 9.0, "Metal1", "Metal3")
    xq = (x0["d2"] + x0["h1"]) / 2; via(xq, Y + 9.0, "Metal1", "Metal3")
    rect("Metal1", Q["h1"]["B"].left, Y - 3.5, Q["h1"]["B"].right, Q["h1"]["B"].top)
    wire("Metal1", [(xq, Y + 9.0), (xq, Y - 3.0), (Q["h1"]["B"].left + 0.5, Y - 3.0)], 1.0)
    via(rlp[0].center().x, rlp[0].center().y, "Metal1", "Metal3"); wire("Metal3", [(rlp[0].center().x, rlp[0].center().y), (rlp[0].center().x, Y + 9.0)], 1.0)
    wire("Metal3", [(x0["d2"], Y + 9.0), (x0["h2"], Y + 9.0)], 1.0)                     # the q track itself
    # qb (M2, Y+12): d1 C, h1 C, RLn bottom; down to h2 B through the h2|c2 gap
    for n in ("d1", "h1"): rect("Metal1", Q[n]["C"].left, Q[n]["C"].bottom, Q[n]["C"].right, Y + 12.7); via(x0[n], Y + 12.0, "Metal1", "Metal2")
    xqb = (x0["h2"] + x0["c2"]) / 2; via(xqb, Y + 12.0, "Metal1", "Metal2")
    rect("Metal1", Q["h2"]["B"].left, Y - 3.5, Q["h2"]["B"].right, Q["h2"]["B"].top)
    wire("Metal1", [(xqb, Y + 12.0), (xqb, Y - 3.0), (Q["h2"]["B"].right - 0.5, Y - 3.0)], 1.0)
    via(rln[0].center().x, rln[0].center().y, "Metal1", "Metal2"); wire("Metal2", [(rln[0].center().x, rln[0].center().y), (rln[0].center().x, Y + 12.0)], 1.0)
    wire("Metal2", [(x0["d1"], Y + 12.0), (xqb, Y + 12.0)], 1.0)                        # the qb track itself
    # loads' VCC ends: M1 at Y+19.5 -> via to TM2 at the left end
    yv = max(rln[1].top, rlp[1].top) + 1.6
    for r in (rln[1], rlp[1]): rect("Metal1", r.left, r.bottom, r.right, yv + 0.5)
    wire("Metal1", [(X - 4.0, yv), (rlp[1].center().x, yv)], 1.0); via(X - 4.0, yv, "Metal1", "TopMetal2")
    # tail: c1 E, c2 E -> M2 track at Y-8 -> Qt C (up); Qt E -> Re top (M2); Re bottom -> ground (right, clear of the clock buses)
    for n in ("c1", "c2"): rect("Metal2", Q[n]["E"].left, Y - 8.5, Q[n]["E"].right, Q[n]["E"].top)
    wire("Metal2", [(x0["c1"], Y - 8.0), (x0["c2"], Y - 8.0)], 1.0)
    qtc, qte, qtb = Q["t"]["C"], Q["t"]["E"], Q["t"]["B"]
    rect("Metal1", qtc.left, qtc.bottom, qtc.right, Y - 7.4); via(qtc.center().x, Y - 8.0, "Metal1", "Metal2")
    yre = re_[1].top + 2.0                                             # short resistor: via 2 um above its top pin, never on it
    cx_ = re_[1].center().x; rect("Metal1", cx_ - 0.4, re_[1].bottom, cx_ + 0.4, yre + 0.9); via(cx_, yre, "Metal1", "Metal2")   # narrow: clear of vbt
    wire("Metal2", [(qte.right - 0.5, qte.center().y), (re_[1].center().x, qte.center().y), (re_[1].center().x, yre)], 1.2)
    wire("Metal1", [(re_[0].center().x, re_[0].center().y), (X + 47.0, re_[0].center().y)], 1.0); gnd_via(X + 47.0, re_[0].center().y, "Metal1")
    # tail bias: Qt B down -> M1 left at Y-20.3 (to the vbt riser outside the pair)
    rect("Metal1", qtb.left, Y - 20.8, qtb.right, qtb.top); wire("Metal1", [(qtb.right, Y - 20.3), (X - 26.0, Y - 20.3)], 1.0)
    # ports: data / clock exits on M3 at their own heights
    rect("Metal1", Q["d1"]["B"].left, Y - 5.6, Q["d1"]["B"].right, Q["d1"]["B"].top); via(x0["d1"], Y - 5.0, "Metal1", "Metal3")
    rect("Metal1", Q["d2"]["B"].left, Y - 11.6, Q["d2"]["B"].right, Q["d2"]["B"].top); via(x0["d2"], Y - 11.0, "Metal1", "Metal3")
    cb1, cb2 = Q["c1"]["B"], Q["c2"]["B"]                                            # clock-input extensions: exactly as tall as the base bar
    rect("Metal1", X - 4.5, cb1.bottom, cb1.right, cb1.top); via(X - 4.5, Y - 1.1, "Metal1", "Metal3")
    rect("Metal1", cb2.left, cb2.bottom, X + 59.5, cb2.top); via(X + 59.5, Y - 1.1, "Metal1", "Metal3")
    return {"q": (x0["d2"], Y + 9.0), "qb": (x0["d1"], Y + 12.0), "d": (x0["d1"], Y - 5.0), "db": (x0["d2"], Y - 11.0), "ck": (X - 4.5, Y - 1.1), "ckb": (X + 59.5, Y - 1.1)}
def wire_pair(m, s, X, Ym):
    """master/slave data lanes (left, M2) and clock buses (below): P bus M2 at Ym-28, N bus M3 at Ym-31"""
    lane = lambda name, xl, a_y, a_layer, b_y, b_layer, a_x, b_x: None
    def hop(px, py, xl, layer):                      # horizontal exit from a latch port to lane x on 'layer', with via to M2 if needed
        wire(layer, [(px, py), (xl, py)], 1.0)
        if layer != "Metal2": via(xl, py, "Metal2", "Metal3")
    L = {"B": X - 7.0, "A": X - 10.0, "C": X - 13.0, "D": X - 16.0}
    # m.qb -> s.db (lane B) ; m.q -> s.d (lane A) ; s.q -> m.db (lane C) ; s.qb -> m.d (lane D)
    for (src, srcl, dst, dstl, ln) in ((m["qb"], "Metal2", s["db"], "Metal3", "B"), (m["q"], "Metal3", s["d"], "Metal3", "A"),
                                       (s["q"], "Metal3", m["db"], "Metal3", "C"), (s["qb"], "Metal2", m["d"], "Metal3", "D")):
        xl = L[ln]; hop(src[0], src[1], xl, srcl); hop(dst[0], dst[1], xl, dstl)
        wire("Metal2", [(xl, src[1]), (xl, dst[1])], 1.0)
    # clocks: master ck = P (lane E, M2), slave ck = N (lane F, M3); master ckb = N (lane G, M3), slave ckb = P (lane H, M2)
    yP, yN = Ym - 28.0, Ym - 31.0
    wire("Metal3", [m["ck"], (X - 19.0, m["ck"][1])], 1.0); via(X - 19.0, m["ck"][1], "Metal2", "Metal3"); wire("Metal2", [(X - 19.0, m["ck"][1]), (X - 19.0, yP)], 1.0)
    wire("Metal3", [s["ck"], (X - 22.0, s["ck"][1]), (X - 22.0, yN)], 1.0)
    wire("Metal3", [m["ckb"], (X + 69.0, m["ckb"][1]), (X + 69.0, yN)], 1.0)
    wire("Metal3", [s["ckb"], (X + 66.0, s["ckb"][1])], 1.0); via(X + 66.0, s["ckb"][1], "Metal2", "Metal3"); wire("Metal2", [(X + 66.0, s["ckb"][1]), (X + 66.0, yP)], 1.0)
    wire("Metal2", [(X - 19.0, yP), (X + 66.0, yP)], 1.0); wire("Metal3", [(X - 22.0, yN), (X + 69.0, yN)], 1.0)
    return {"P": (X + 66.0, yP), "N": (X + 69.0, yN), "Pl": (X - 19.0, yP), "Nl": (X - 22.0, yN)}
LP = {t: wire_latch(t, LAT[t][0], LAT[t][1]) for t in ("dm1", "ds1", "dm2", "ds2")}
CK1 = wire_pair(LP["dm1"], LP["ds1"], 140.0, 50.0)          # stage 1: P = ckp, N = ckn
CK2 = wire_pair(LP["dm2"], LP["ds2"], 30.0, 50.0)           # stage 2: P = c2p, N = c2n


# ======================= stage 3b-1: clocks in, stage 1 -> stage 2 coupling, clock bias, tail bias, divider VCC =======================
pc = lambda k, l: pin(k, l).center()
# --- clocks in: divider-driver output caps -> TM1 drops right of stage 1 -> stage-1 clock buses (P = ckp on M2, N = ckn on M3)
for (cm, xd, yb, lay, xb) in ((pc("CDDV_c1", "MINUS"), 212.0, 22.0, "Metal2", CK1["P"][0]), (pc("CDDV_c2", "MINUS"), 224.0, 19.0, "Metal3", CK1["N"][0])):
    wire("Metal5", [(cm.x, cm.y), (cm.x, 180.0)], 2); via(cm.x, 180.0, "Metal5", "TopMetal1")
    wire("TopMetal1", [(cm.x, 180.0), (xd, 180.0), (xd, yb)], 3); via(xd, yb, lay, "TopMetal1")
    wire(lay, [(xd, yb), (xb, yb)], 1.0)
rck1, rck2 = ends("Rdiv_ck1"), ends("Rdiv_ck2")
wire("Metal1", [(rck1[0].center().x, rck1[0].center().y), (rck1[0].center().x, 22.0), (214.6, 22.0)], 1.0); via(214.6, 22.0, "Metal1", "Metal2")
wire("Metal2", [(212.0, 22.0), (214.6, 22.0)], 1.0)                                          # Rck1 joins ckp
wire("Metal1", [(rck2[0].center().x, rck2[0].center().y), (rck2[0].center().x, 19.0)], 1.0); via(rck2[0].center().x, 19.0, "Metal1", "Metal3")
# --- vck (1.5 V clock bias): Rk1/Rk2 divider + Cdiv_k -> Rck tops (stage 1) and Rdiv_b tops (stage 2)
YK = 33.5
rect("Metal1", rck1[1].left, rck1[1].bottom, rck2[1].right, YK + 0.5); via(218.5, YK, "Metal1", "Metal3")
ckp_ = pc("Cdiv_k", "PLUS"); via(ckp_.x, ckp_.y, "Metal3", "TopMetal1"); wire("Metal3", [(ckp_.x, YK), (ckp_.x, ckp_.y)], 1.0)   # via on the pin
rk1, rk2 = ends("Rdiv_k1"), ends("Rdiv_k2")
wire("Metal3", [(218.5, YK), (rk2[1].center().x, YK)], 1.0)
for r in (rk1[0], rk2[1]): via(r.center().x, r.center().y, "Metal1", "Metal3"); wire("Metal3", [(r.center().x, r.center().y), (r.center().x, YK)], 1.0)
wire("Metal1", [(rk2[0].center().x, rk2[0].center().y), (rk2[0].center().x, 16.0)], 1.0); gnd_via(rk2[0].center().x, 16.0, "Metal1")
rb1, rb2 = ends("Rdiv_b1"), ends("Rdiv_b2")
wire("Metal3", [(228.0, YK), (228.0, 157.0), (rb1[1].center().x, 157.0)], 1.0)
for r in (rb1[1], rb2[1]): via(r.center().x, r.center().y, "Metal1", "Metal3"); wire("Metal3", [(r.center().x, r.center().y), (r.center().x, 157.0)], 1.0)
# --- stage 1 -> coupling caps: s1q (q track, M3) and s1qb (qb track, M2) up on TM1, no crossing
s1q, s1qb = (pin("QDS1_h2", "E").center().x, LAT["ds1"][1] + 9.0), ((pin("QDS1_h2", "E").center().x + pin("QDS1_c2", "E").center().x) / 2, LAT["ds1"][1] + 12.0)
c1p_, c2p_ = pc("Cdiv_c1", "PLUS"), pc("Cdiv_c2", "PLUS")
via(*s1q, "Metal3", "TopMetal1"); wire("TopMetal1", [s1q, (s1q[0], 125.0), (c1p_.x, 125.0), (c1p_.x, c1p_.y)], 2)
via(*s1qb, "Metal2", "TopMetal1"); wire("TopMetal1", [s1qb, (s1qb[0], 165.0), (c2p_.x, 165.0), (c2p_.x, c2p_.y)], 2)
# --- coupling caps -> stage-2 clock buses (TM1 drops in the corridor between the pairs); Rdiv_b bottoms join
for (cm, yl, xd, yb, lay, xb, rb, yr) in ((pc("Cdiv_c1", "MINUS"), 127.0, 104.0, 22.0, "Metal2", CK2["P"][0], rb1[0], 131.0),
                                         (pc("Cdiv_c2", "MINUS"), 126.0, 110.0, 19.0, "Metal3", CK2["N"][0], rb2[0], 128.5)):
    wire("Metal5", [(cm.x, cm.y), (cm.x, yl), (xd, yl)], 2); via(xd, yl, "Metal5", "TopMetal1")
    wire("TopMetal1", [(xd, max(yl, yr)), (xd, yb)], 3); via(xd, yb, lay, "TopMetal1"); wire(lay, [(xd, yb), (xb, yb)], 1.0)
    via(rb.center().x, rb.center().y, "Metal1", "Metal3"); wire("Metal3", [(rb.center().x, rb.center().y), (rb.center().x, yr), (xd, yr)], 1.0)
    via(xd, yr, "Metal3", "TopMetal1")
# --- vbt (tail bias): reference (Rref -> diode Qbr -> Rebr) + Cdiv_bt -> M1 bus along the bottom -> risers to the latch tail lines
YT = 12.0
for xr in (4.0, 114.0): wire("Metal1", [(xr, LAT["ds2"][1] - 20.3), (xr, YT)], 1.0)
qbr = {l: pin("Qdiv_br", l) for l in ("B", "C", "E")}
wire("Metal1", [(4.0, YT), (309.0, YT), (309.0, qbr["B"].center().y)], 1.0)
rect("Metal1", 309.0, qbr["B"].bottom, qbr["B"].right, qbr["B"].top)
rect("Metal1", qbr["B"].right, qbr["B"].bottom, 314.4, qbr["B"].top); rect("Metal1", qbr["C"].right, qbr["C"].bottom, 314.4, qbr["C"].top)
rect("Metal1", 313.4, qbr["B"].bottom, 314.4, qbr["C"].top)                                   # diode connection (C = B), clear of the emitter
rref, rebr = ends("Rdiv_ref"), ends("Rdiv_ebr")
wire("Metal1", [(rref[0].center().x, rref[0].center().y), (309.0, rref[0].center().y)], 1.0)
via(rebr[1].center().x, rebr[1].center().y, "Metal1", "Metal2")
wire("Metal2", [(qbr["E"].right - 0.5, qbr["E"].center().y), (rebr[1].center().x, qbr["E"].center().y), (rebr[1].center().x, rebr[1].center().y)], 1.2)
wire("Metal1", [(rebr[0].center().x, rebr[0].center().y), (rebr[0].center().x, 22.0)], 1.0); gnd_via(rebr[0].center().x, 22.0, "Metal1")
cbt = pc("Cdiv_bt", "PLUS"); via(cbt.x, cbt.y, "Metal3", "TopMetal1")                       # via on the pin
wire("Metal3", [(cbt.x, cbt.y), (cbt.x, YT)], 1.0); via(cbt.x, YT, "Metal1", "Metal3")
# --- divider VCC (TM2): bias tops -> bus at y=50 -> the RX driver's VCC riser; latch loads -> risers -> link -> left edge -> divider-driver bus
for r in (rk1[1], rref[1]):
    rect("Metal1", r.left, r.bottom, r.right, r.top + 2.0); via(r.center().x, r.center().y + 1.4, "Metal1", "TopMetal2")
    wire("TopMetal2", [(r.center().x, r.center().y + 1.4), (r.center().x, 50.0)], 4)
wire("TopMetal2", [(rk1[1].center().x, 50.0), (376.5, 50.0), (376.5, 128.0)], 4)
for (xl, a_, b_) in ((26.0, "dm2", "ds2"), (136.0, "dm1", "ds1")):
    wire("TopMetal2", [(xl, LAT[a_][1] + 17.0), (xl, 125.0)], 4)
wire("TopMetal2", [(2.0, 125.0), (136.0, 125.0)], 4); wire("TopMetal2", [(2.0, 125.0), (2.0, 236.0), (180.0, 236.0)], 4)
# --- grounds: divider decaps (bottom plates, rings); coupling caps strap out of their cut-outs
for k in ("Cdiv_k", "Cdiv_bt"):
    cm = pc(k, "MINUS"); gy = cm.y - 13.0; gnd_via(cm.x, gy, "Metal5"); wire("Metal5", [(cm.x, cm.y), (cm.x, gy)], 2)
DIV_SIG = ("Cdiv_c1", "Cdiv_c2")
for k in ("Cdiv_k", "Cdiv_bt") + DIV_SIG:
    B.ring_ground(k, cutout_keys=tuple(DRV_SIG) + VCO_SIG + DIV_SIG, coil_keys=("Lvco", "LPRX", "LPTX"))


# ======================= stage 3b-2: divider output stage -> PLLP / PLLN ports =======================
QO = {k: {l: pin(k, l) for l in ("B", "C", "E")} for k in ("Qdiv_o1", "Qdiv_o2", "Qdiv_to1", "Qdiv_to2")}
co1p, co1m, co2p, co2m = pc("Cdiv_o1", "PLUS"), pc("Cdiv_o1", "MINUS"), pc("Cdiv_o2", "PLUS"), pc("Cdiv_o2", "MINUS")
# s2q (q track, M3) -> TM1 -> Cdiv_o1 input ; s2qb (qb track, M2) -> M5 (never crosses s2q) -> Cdiv_o2 input
s2q = (pin("QDS2_h2", "E").center().x, LAT["ds2"][1] + 9.0)
s2qb = ((pin("QDS2_h2", "E").center().x + pin("QDS2_c2", "E").center().x) / 2, LAT["ds2"][1] + 12.0)
via(*s2q, "Metal3", "TopMetal1"); wire("TopMetal1", [s2q, (s2q[0], 240.0), (131.0, 240.0), (131.0, co1p.y), (co1p.x, co1p.y)], 2)
via(*s2qb, "Metal2", "Metal5"); wire("Metal5", [s2qb, (s2qb[0], 232.0), (134.0, 232.0), (134.0, co2p.y)], 2)
via(134.0, co2p.y, "Metal5", "TopMetal1"); wire("TopMetal1", [(134.0, co2p.y), (co2p.x, co2p.y)], 2)
# bases: cap outputs (M5) -> M1 at y=300 -> base bars (pulled down); Rbo bottoms join on M5
rbo1, rbo2 = ends("Rdiv_bo1"), ends("Rdiv_bo2")
for (cm, xm, qb, rb, ym) in ((co1m, 58.0, QO["Qdiv_o1"]["B"], rbo1, co1m.y), (co2m, 90.0, QO["Qdiv_o2"]["B"], rbo2, co2m.y)):
    wire("Metal5", [(cm.x, cm.y), (xm, ym), (xm, 300.0)], 2) if False else wire("Metal5", [(cm.x, cm.y), (xm, cm.y), (xm, 300.0)], 2)
    via(xm, 300.0, "Metal1", "Metal5"); rect("Metal1", qb.left, 299.5, qb.right, qb.top)
    wire("Metal1", [(xm, 300.0), ((qb.right - 0.5) if xm > qb.right else (qb.left + 0.5), 300.0)], 1.0)
    via(rb[0].center().x, rb[0].center().y - 2.7, "Metal1", "Metal5"); rect("Metal1", rb[0].left, rb[0].center().y - 3.3, rb[0].right, rb[0].top)
wire("Metal5", [(rbo1[0].center().x, rbo1[0].center().y - 2.7), (58.0, rbo1[0].center().y - 2.7), (58.0, 300.0)], 2)
wire("Metal5", [(rbo2[0].center().x, rbo2[0].center().y - 2.7), (rbo2[0].center().x, co2m.y)], 2)
# vbo (1.6 V): Rdiv_o1 (VCC at the bottom, vbo at the top), Rdiv_o2 (vbo at the top, ground at the bottom), Cdiv_bo, Rbo tops -> M3 at y=358
ro1, ro2 = ends("Rdiv_o1"), ends("Rdiv_o2"); YO = 358.0; cbop = pc("Cdiv_bo", "PLUS")
for r in (rbo1[1], rbo2[1], ro1[0], ro2[1]): via(r.center().x, r.center().y, "Metal1", "Metal3"); wire("Metal3", [(r.center().x, r.center().y), (r.center().x, YO)], 1.0)   # Rdiv_o1: vbo at the bottom
wire("Metal3", [(cbop.x, YO), (rbo2[1].center().x, YO)], 1.0); wire("Metal3", [(cbop.x, YO), (cbop.x, cbop.y)], 1.0); via(cbop.x, cbop.y, "Metal3", "TopMetal1")
wire("Metal1", [(ro2[0].center().x, ro2[0].center().y), (ro2[0].center().x, ro2[0].center().y - 3.5)], 1.0); gnd_via(ro2[0].center().x, ro2[0].center().y - 3.5, "Metal1")
# eo: output-pair emitters joined (M2) and down to both tail collectors
e1, e2 = QO["Qdiv_o1"]["E"], QO["Qdiv_o2"]["E"]; rect("Metal2", e1.left, e1.bottom, e2.right, e1.top)
for k in ("Qdiv_to1", "Qdiv_to2"):
    c = QO[k]["C"]; xv = c.center().x; rect("Metal1", c.left, c.bottom, c.right, 298.0); via(xv, 297.2, "Metal1", "Metal2")
    wire("Metal2", [(xv, 297.2), (xv, e1.center().y)], 1.2)
# tails: emitters -> Reo tops (M2); Reo bottoms -> ground; bases -> vbt (M1 at y=286, riser up the left edge)
for (k, r) in (("Qdiv_to1", ends("Rdiv_eo1")), ("Qdiv_to2", ends("Rdiv_eo2"))):
    e = QO[k]["E"]; yv_ = r[1].top + 2.0                   # tiny resistor: via 2 um above its top pin, never on it
    rect("Metal1", r[1].left, r[1].bottom, r[1].right, yv_ + 0.9); via(r[1].center().x, yv_, "Metal1", "Metal2")
    wire("Metal2", [(e.right - 0.6, e.center().y), (e.right - 0.6, yv_), (r[1].center().x, yv_)], 1.2)
    wire("Metal1", [(r[0].center().x, r[0].center().y), (r[0].center().x, r[0].center().y - 3.6)], 1.0); gnd_via(r[0].center().x, r[0].center().y - 3.6, "Metal1")
    b_ = QO[k]["B"]; rect("Metal1", b_.left, 285.5, b_.right, b_.top)
wire("Metal1", [(4.0, LAT["ds2"][1] - 20.3), (4.0, 286.0), (QO["Qdiv_to2"]["B"].right, 286.0)], 1.0)
# collectors: PLLN (left pair half) / PLLP (right) -> Rt loads (VCC on top) and TM1 out the left edge
rt1, rt2 = ends("Rdiv_t1"), ends("Rdiv_t2")
for (k, rt, yp, name) in (("Qdiv_o1", rt1, 311.0, "PLLN"), ("Qdiv_o2", rt2, 316.0, "PLLP")):
    c = QO[k]["C"]; rect("Metal1", c.left, c.bottom, c.right, rt[0].top)
    xv = c.center().x; via(xv, yp if name == "PLLN" else 311.5, "Metal1", "TopMetal1")
    wire("TopMetal1", ([(xv, 311.5), (xv, yp)] if name == "PLLP" else [(xv, yp)]) + [(0.0, yp)], 2, end_ext=0)
    B.text(name, 1.0, yp, gds=(126, 25))
    rect("Metal1", rt[1].left, rt[1].bottom, rt[1].right, rt[1].top + 2.0); via(rt[1].center().x, rt[1].center().y + 1.5, "Metal1", "TopMetal2")
    wire("TopMetal2", [(rt[1].center().x, rt[1].center().y + 1.5), (rt[1].center().x, 326.0)], 4)
# VCC for the output stage: left-edge riser up to y=326, across to the Rt tops and Rdiv_o1's VCC end
xo_ = ro1[1].center().x - 4.5                                      # Rdiv_o1: VCC at the top; via OFF the resistor's own vbo track
wire("Metal1", [(ro1[1].center().x, ro1[1].center().y), (xo_, ro1[1].center().y)], 1.0); via(xo_, ro1[1].center().y, "Metal1", "TopMetal2")
wire("TopMetal2", [(2.0, 236.0), (2.0, 326.0), (rt2[1].center().x, 326.0)], 4)
wire("TopMetal2", [(xo_, ro1[1].center().y), (xo_, 326.0)], 4)
# grounds
cbom = pc("Cdiv_bo", "MINUS"); gnd_via(cbom.x, cbom.y - 13.0, "Metal5"); wire("Metal5", [(cbom.x, cbom.y), (cbom.x, cbom.y - 13.0)], 2)
DIV_SIG = DIV_SIG + ("Cdiv_o1", "Cdiv_o2")
for k in ("Cdiv_bo", "Cdiv_o1", "Cdiv_o2"):
    B.ring_ground(k, cutout_keys=tuple(DRV_SIG) + VCO_SIG + DIV_SIG, coil_keys=("Lvco", "LPRX", "LPTX"))

# ======================= ground plane + checks =======================
TANK_CUT = [(xv - 4.0, 281.0, xv + 4.0, 387.0) for xv in (XP, XN)] + [(434.5, 276.5, 445.0, 281.5)]
TANK_CUT += [(208.0, 26.0, 216.0, 176.0), (220.0, 23.0, 228.0, 176.0), (100.0, 26.0, 114.0, 125.0), (70.0, 111.0, 78.0, 236.0)]   # divider: long TM1 drops   # no plane under the tank verticals (~40% less line C); + the sliver between them
B.ground_plane((0, 0, 860, 640), hole_keys=("Lvco", "LPRX", "LPTX"), signal_mim_keys=VCO_SIG + tuple(DRV_SIG) + DIV_SIG + BS_SIG, extra_holes=TANK_CUT)
P = {"vcop lead": ("TopMetal1", (la.center().x, 395.0)), "Q6 C": ("Metal1", q6c.center()), "Cb7 +": ("TopMetal1", cb7p.center()), "Ccv1 +": ("TopMetal1", cv1p.center()),
     "EF1 B": ("Metal1", ef1b.center()), "vcon lead": ("TopMetal1", (lb.center().x, 395.0)), "Q7 C": ("Metal1", q7c.center()), "Cb6 +": ("TopMetal1", cb6p.center()),
     "Ccv2 +": ("TopMetal1", cv2p.center()), "EF2 B": ("Metal1", ef2b.center()), "VCC tap": ("TopMetal2", (lc.center().x, 395.0)), "EF1 C": ("Metal1", ef1c.center()),
     "EF2 C": ("Metal1", ef2c.center()), "Rgb1 top": ("Metal1", rgb1[1].center()), "Rbb1 top": ("Metal1", rbb1[0].center()),
     "Q6 B": ("Metal1", q6b.center()), "Cb6 -": ("Metal5", cb6m.center()), "Rb6 top": ("Metal1", rb6[1].center()),
     "Q7 B": ("Metal1", q7b.center()), "Cb7 -": ("Metal5", cb7m.center()), "Rb7 top": ("Metal1", rb7[1].center()),
     "Q6 E": ("Metal2", q6e.center()), "Q7 E": ("Metal2", q7e.center()), "Rtail top": ("Metal1", rtl[1].center()),
     "Rb6 bot": ("Metal1", rb6[0].center()), "Rb7 bot": ("Metal1", rb7[0].center()), "Cbb +": ("TopMetal1", cbbp.center()),
     "Rbb1 bot": ("Metal1", rbb1[1].center()), "Rbb2 top": ("Metal1", rbb2[1].center()),
     "G1": ("Metal1", g1b.center()), "Ccv1 -": ("Metal5", cv1m.center()), "Rg1 top": ("Metal1", rg1[1].center()),
     "G2": ("Metal1", g2b.center()), "Ccv2 -": ("Metal5", cv2m.center()), "Rg2 top": ("Metal1", rg2[1].center()),
     "Rg1 bot": ("Metal1", rg1[0].center()), "Rg2 bot": ("Metal1", rg2[0].center()), "Cgb +": ("TopMetal1", cgbp.center()),
     "Rgb1 bot": ("Metal1", rgb1[0].center()), "Rgb2 top": ("Metal1", rgb2[0].center()), "W": ("Metal1", wv.center()), "VTUNE": ("Metal2", (7, 383)),
     "EF1 E": ("Metal2", ef1e.center()), "Ref1 top": ("Metal1", ref1[1].center()), "EF2 E": ("Metal2", ef2e.center()), "Ref2 top": ("Metal1", ref2[1].center()),
     "GND": ("Metal4", (3, 587)), "Rtail bot": ("Metal1", rtl[0].center()), "Rbb2 bot": ("Metal1", rbb2[0].center()), "Rgb2 bot": ("Metal1", rgb2[1].center()),
     "Ref1 bot": ("Metal1", ref1[0].center()), "Ref2 bot": ("Metal1", ref2[0].center()), "Cgb -": ("Metal5", cgbm.center()), "Cbb -": ("Metal5", cbbm.center()),
     **{f"{k} TIE": ("Metal1", pin(k, "TIE").center()) for k in ("Cvco_gb", "Cvco_bb") + VCO_SIG + tuple(DRV_SIG) + tuple(f"C{t}_vb" for t in ("PRX", "PTX", "DDV"))}}
for t, p in (("rx", p_rx), ("tx", p_tx), ("dv", p_dv)):
    P.update({f"{t} Ci1+": ("TopMetal1", p[("i1", "PLUS")].center()), f"{t} Ci2+": ("TopMetal1", p[("i2", "PLUS")].center()),
              f"{t} QaB": ("Metal1", p[("a", "B")].center()), f"{t} Ci1-": ("Metal5", p[("i1", "MINUS")].center()), f"{t} Rb1top": ("Metal1", p["b1"][1].center()),
              f"{t} QbB": ("Metal1", p[("b", "B")].center()), f"{t} Ci2-": ("Metal5", p[("i2", "MINUS")].center()), f"{t} Rb2top": ("Metal1", p["b2"][1].center()),
              f"{t} QaC": ("Metal1", p[("a", "C")].center()), f"{t} Cc1+": ("TopMetal1", p[("c1", "PLUS")].center()), f"{t} Rd1top": ("Metal1", p["d1"][1].center()),
              f"{t} QbC": ("Metal1", p[("b", "C")].center()), f"{t} Cc2+": ("TopMetal1", p[("c2", "PLUS")].center()), f"{t} Rd2top": ("Metal1", p["d2"][1].center()),
              f"{t} QaE": ("Metal2", p[("a", "E")].center()), f"{t} QbE": ("Metal2", p[("b", "E")].center()), f"{t} Rttop": ("Metal1", p["t"][1].center()),
              f"{t} Rb1bot": ("Metal1", p["b1"][0].center()), f"{t} Rb2bot": ("Metal1", p["b2"][0].center()), f"{t} Rv1top": ("Metal1", p["v1"][1].center()),
              f"{t} Rv2top": ("Metal1", p["v2"][1].center()), f"{t} Cvb+": ("TopMetal1", p[("vb", "PLUS")].center()),
              f"{t} Rd1bot": ("Metal1", p["d1"][0].center()), f"{t} Rd2bot": ("Metal1", p["d2"][0].center()), f"{t} Rv1bot": ("Metal1", p["v1"][0].center()),
              f"{t} Rtbot": ("Metal1", p["t"][0].center()), f"{t} Rv2bot": ("Metal1", p["v2"][0].center()), f"{t} Cvb-": ("Metal5", p[("vb", "MINUS")].center())})
P.update({"rx Cc1-": ("Metal5", p_rx[("c1", "MINUS")].center()), "RXLOP": ("TopMetal2", (432.5, 11)), "Rblr1 top": ("Metal1", ends("Rbl_r1")[1].center()),
          "rx Cc2-": ("Metal5", p_rx[("c2", "MINUS")].center()), "RXLON": ("TopMetal2", (447.5, 11)), "Rblr2 top": ("Metal1", ends("Rbl_r2")[1].center()),
          "tx Cc1-": ("Metal5", p_tx[("c1", "MINUS")].center()), "TXLOP": ("TopMetal2", (858, 240)), "Rblt1 top": ("Metal1", ends("Rbl_t1")[1].center()),
          "tx Cc2-": ("Metal5", p_tx[("c2", "MINUS")].center()), "TXLON": ("TopMetal2", (858, 248)), "Rblt2 top": ("Metal1", ends("Rbl_t2")[1].center()),
          "Rbl bots": ("Metal1", ends("Rbl_r1")[0].center()), "Rbl bots2": ("Metal1", ends("Rbl_t2")[0].center()),
          "rx coil dp": ("TopMetal1", (lra.left - 3, lra.center().y)), "rx coil dn": ("TopMetal1", (lrb.left - 3, lrb.center().y)),
          "rx coil VCC": ("TopMetal2", (lrc.left - 3, lrc.center().y)), "tx coil dp": ("TopMetal1", (lta.center().x, lta.bottom - 3)),
          "tx coil dn": ("TopMetal1", (ltb.center().x, ltb.bottom - 3)), "tx coil VCC": ("TopMetal2", (ltc.center().x, ltc.bottom - 3))})
G_ = [["vcop lead", "Q6 C", "Cb7 +", "Ccv1 +", "EF1 B"], ["vcon lead", "Q7 C", "Cb6 +", "Ccv2 +", "EF2 B"],
      ["VCC tap", "EF1 C", "EF2 C", "Rgb1 top", "Rbb1 top"] + [f"{t} {n}" for t in ("rx", "tx", "dv") for n in ("Rd1bot", "Rd2bot", "Rv1bot")] + ["rx coil VCC", "tx coil VCC"], ["Q6 B", "Cb6 -", "Rb6 top"], ["Q7 B", "Cb7 -", "Rb7 top"],
      ["Q6 E", "Q7 E", "Rtail top"], ["Rb6 bot", "Rb7 bot", "Cbb +", "Rbb1 bot", "Rbb2 top"], ["G1", "Ccv1 -", "Rg1 top"], ["G2", "Ccv2 -", "Rg2 top"],
      ["Rg1 bot", "Rg2 bot", "Cgb +", "Rgb1 bot", "Rgb2 top"], ["W", "VTUNE"], ["EF1 E", "Ref1 top", "rx Ci1+", "tx Ci1+", "dv Ci1+"], ["EF2 E", "Ref2 top", "rx Ci2+", "tx Ci2+", "dv Ci2+"],
      *[[f"{t} QaB", f"{t} Ci1-", f"{t} Rb1top"] for t in ("rx", "tx", "dv")], *[[f"{t} QbB", f"{t} Ci2-", f"{t} Rb2top"] for t in ("rx", "tx", "dv")],
      ["rx QaC", "rx Cc1+", "rx Rd1top", "rx coil dp"], ["rx QbC", "rx Cc2+", "rx Rd2top", "rx coil dn"], ["tx QaC", "tx Cc1+", "tx Rd1top", "tx coil dp"],
      ["tx QbC", "tx Cc2+", "tx Rd2top", "tx coil dn"], ["dv QaC", "dv Cc1+", "dv Rd1top"], ["dv QbC", "dv Cc2+", "dv Rd2top"],
      *[[f"{t} QaE", f"{t} QbE", f"{t} Rttop"] for t in ("rx", "tx", "dv")], *[[f"{t} Rb1bot", f"{t} Rb2bot", f"{t} Rv1top", f"{t} Rv2top", f"{t} Cvb+"] for t in ("rx", "tx", "dv")],
      ["rx Cc1-", "RXLOP", "Rblr1 top"], ["rx Cc2-", "RXLON", "Rblr2 top"], ["tx Cc1-", "TXLOP", "Rblt1 top"], ["tx Cc2-", "TXLON", "Rblt2 top"],
      ["GND", "Rbl bots", "Rbl bots2"] + [f"{t} {n}" for t in ("rx", "tx", "dv") for n in ("Rtbot", "Rv2bot", "Cvb-")] + [f"{k} TIE" for k in tuple(DRV_SIG) + tuple(f"C{t}_vb" for t in ("PRX", "PTX", "DDV"))] + ["Rtail bot", "Rbb2 bot", "Rgb2 bot", "Ref1 bot", "Ref2 bot", "Cgb -", "Cbb -"] + [f"{k} TIE" for k in ("Cvco_gb", "Cvco_bb") + VCO_SIG]]
def latch_probes(tag):
    up = tag.upper(); q = lambda n, l: ("Metal1", pin(f"Q{up}_{n}", l).center()); e = lambda n: ("Metal2", pin(f"Q{up}_{n}", "E").center())
    return {f"{tag} ed": [q("c1", "C"), e("d1"), e("d2")], f"{tag} eh": [q("c2", "C"), e("h1"), e("h2")], f"{tag} et": [e("c1"), e("c2"), q("t", "C")],
            f"{tag} q": [q("d2", "C"), q("h2", "C"), q("h1", "B"), ("Metal1", ends(f"R{up}_lp")[0].center())],
            f"{tag} qb": [q("d1", "C"), q("h1", "C"), q("h2", "B"), ("Metal1", ends(f"R{up}_ln")[0].center())],
            f"{tag} te": [e("t"), ("Metal1", ends(f"R{up}_e")[1].center())]}
LPR = {t: latch_probes(t) for t in ("dm1", "ds1", "dm2", "ds2")}
def pb(tag, n, l): return ("Metal1", pin(f"Q{tag.upper()}_{n}", l).center())
DIVG = []
for t in LPR:
    for net, pts in LPR[t].items():
        names = [f"{net} #{i}" for i in range(len(pts))]; P.update(dict(zip(names, pts))); DIVG.append(names)
# cross-latch nets of each pair (data) and clocks
for (m, s) in (("dm1", "ds1"), ("dm2", "ds2")):
    # each latch output also drives the other latch's data input: same net, so extend that latch's q/qb group
    for (src, net, dst, n) in ((m, "q", s, "d1"), (m, "qb", s, "d2"), (s, "q", m, "d2"), (s, "qb", m, "d1")):
        grp = next(g_ for g_ in DIVG if g_[0] == f"{src} {net} #0"); nm = f"{src} {net} -> {dst} {n}B"; P[nm] = pb(dst, n, "B"); grp.append(nm)
    for (net, pts) in ((f"{m}/{s} P", [pb(m, "c1", "B"), pb(s, "c2", "B")]), (f"{m}/{s} N", [pb(m, "c2", "B"), pb(s, "c1", "B")])):
        names = [f"{net} #{i}" for i in range(len(pts))]; P.update(dict(zip(names, pts))); DIVG.append(names)
def PB(name, layer, pt): P[name] = (layer, pt); return name
G3 = [[PB("ckp: ddv Cc1-", "Metal5", pc("CDDV_c1", "MINUS")), PB("ckp: dm1 c1B", "Metal1", pc("QDM1_c1", "B")), PB("ckp: ds1 c2B", "Metal1", pc("QDS1_c2", "B")), PB("ckp: Rck1 bot", "Metal1", rck1[0].center())],
      [PB("ckn: ddv Cc2-", "Metal5", pc("CDDV_c2", "MINUS")), PB("ckn: dm1 c2B", "Metal1", pc("QDM1_c2", "B")), PB("ckn: ds1 c1B", "Metal1", pc("QDS1_c1", "B")), PB("ckn: Rck2 bot", "Metal1", rck2[0].center())],
      [PB("vck: Rck1 top", "Metal1", rck1[1].center()), PB("vck: Rck2 top", "Metal1", rck2[1].center()), PB("vck: Cdiv_k+", "TopMetal1", ckp_),
       PB("vck: Rk1 bot", "Metal1", rk1[0].center()), PB("vck: Rk2 top", "Metal1", rk2[1].center()), PB("vck: Rb1 top", "Metal1", rb1[1].center()), PB("vck: Rb2 top", "Metal1", rb2[1].center())],
      [PB("s1q: ds1 d2C", "Metal1", pc("QDS1_d2", "C")), PB("s1q: Cdiv_c1+", "TopMetal1", c1p_)], [PB("s1qb: ds1 d1C", "Metal1", pc("QDS1_d1", "C")), PB("s1qb: Cdiv_c2+", "TopMetal1", c2p_)],
      [PB("c2p: Cdiv_c1-", "Metal5", pc("Cdiv_c1", "MINUS")), PB("c2p: dm2 c1B", "Metal1", pc("QDM2_c1", "B")), PB("c2p: ds2 c2B", "Metal1", pc("QDS2_c2", "B")), PB("c2p: Rb1 bot", "Metal1", rb1[0].center())],
      [PB("c2n: Cdiv_c2-", "Metal5", pc("Cdiv_c2", "MINUS")), PB("c2n: dm2 c2B", "Metal1", pc("QDM2_c2", "B")), PB("c2n: ds2 c1B", "Metal1", pc("QDS2_c1", "B")), PB("c2n: Rb2 bot", "Metal1", rb2[0].center())],
      [PB("vbt: Qto1 B", "Metal1", pc("Qdiv_to1", "B")), PB("vbt: Qto2 B", "Metal1", pc("Qdiv_to2", "B")), PB("vbt: Qbr B", "Metal1", pc("Qdiv_br", "B")), PB("vbt: Qbr C", "Metal1", pc("Qdiv_br", "C")), PB("vbt: Rref bot", "Metal1", rref[0].center()), PB("vbt: Cdiv_bt+", "TopMetal1", cbt)]
       + [PB(f"vbt: {t} QtB", "Metal1", pc(f"Q{t.upper()}_t", "B")) for t in ("dm1", "ds1", "dm2", "ds2")],
      [PB("ebr: Qbr E", "Metal2", pc("Qdiv_br", "E")), PB("ebr: Rebr top", "Metal1", rebr[1].center())]]
G3 += [[PB("s2q: ds2 d2C", "Metal1", pc("QDS2_d2", "C")), PB("s2q: Co1+", "TopMetal1", co1p)], [PB("s2qb: ds2 d1C", "Metal1", pc("QDS2_d1", "C")), PB("s2qb: Co2+", "TopMetal1", co2p)],
       [PB("o1: Co1-", "Metal5", co1m), PB("o1: Qo1 B", "Metal1", pc("Qdiv_o1", "B")), PB("o1: Rbo1 bot", "Metal1", rbo1[0].center())],
       [PB("o2: Co2-", "Metal5", co2m), PB("o2: Qo2 B", "Metal1", pc("Qdiv_o2", "B")), PB("o2: Rbo2 bot", "Metal1", rbo2[0].center())],
       [PB("vbo: Cbo+", "TopMetal1", pc("Cdiv_bo", "PLUS")), PB("vbo: Rbo1 top", "Metal1", rbo1[1].center()), PB("vbo: Rbo2 top", "Metal1", rbo2[1].center()),
        PB("vbo: Ro1 bot", "Metal1", ro1[0].center()), PB("vbo: Ro2 top", "Metal1", ro2[1].center())],
       [PB("eo: Qo1 E", "Metal2", pc("Qdiv_o1", "E")), PB("eo: Qo2 E", "Metal2", pc("Qdiv_o2", "E")), PB("eo: Qto1 C", "Metal1", pc("Qdiv_to1", "C")), PB("eo: Qto2 C", "Metal1", pc("Qdiv_to2", "C"))],
       [PB("eto1: E", "Metal2", pc("Qdiv_to1", "E")), PB("eto1: Reo1 top", "Metal1", ends("Rdiv_eo1")[1].center())],
       [PB("eto2: E", "Metal2", pc("Qdiv_to2", "E")), PB("eto2: Reo2 top", "Metal1", ends("Rdiv_eo2")[1].center())],
       [PB("PLLN: Qo1 C", "Metal1", pc("Qdiv_o1", "C")), PB("PLLN: Rt1 bot", "Metal1", rt1[0].center()), PB("PLLN port", "TopMetal1", (1.0, 311.0))],
       [PB("PLLP: Qo2 C", "Metal1", pc("Qdiv_o2", "C")), PB("PLLP: Rt2 bot", "Metal1", rt2[0].center()), PB("PLLP port", "TopMetal1", (1.0, 316.0))]]
G3 += [[PB("bs_s1: Cbs1-", "Metal5", cbs1m.center()), PB("bs_s1: S stripe", "Metal1", (OX + SX[0], OY + 1.0)), PB("bs_s1: S stripe last", "Metal1", (OX + SX[-1], OY + 1.0)), PB("bs_s1: Rbs1 top", "Metal1", rb1_[1].center())],
       [PB("bs_s2: Cbs2-", "Metal5", cbs2m.center()), PB("bs_s2: D stripe", "Metal1", (OX + DX[0], OY + 1.0)), PB("bs_s2: D stripe last", "Metal1", (OX + DX[-1], OY + 1.0)), PB("bs_s2: Rbs2 top", "Metal1", rb2_[1].center())],
       [PB("bs_g: gate M1 bar", "Metal1", (XG, OY + 2.68)), PB("bs_g: Rbsg top", "Metal1", rbg_[1].center())],
       [PB("BSEL: Rbsg bot", "Metal1", rbg_[0].center()), PB("BSEL port", "Metal3", (2.0, YBS))]]
G_ = G_ + DIVG + G3
def same(a_, b_):                                   # declare two probe groups one net (intended joins across stages)
    ia = next(i for i, g_ in enumerate(G_) if a_ in g_); ib = next(i for i, g_ in enumerate(G_) if b_ in g_)
    if ia != ib: G_[ia] += G_[ib]; del G_[ib]
for a_, b_ in (("ds1 q #0", "s1q: ds1 d2C"), ("ds1 qb #0", "s1qb: ds1 d1C"), ("dm1/ds1 P #0", "ckp: ddv Cc1-"),
               ("dm1/ds1 N #0", "ckn: ddv Cc2-"), ("dm2/ds2 P #0", "c2p: Cdiv_c1-"), ("dm2/ds2 N #0", "c2n: Cdiv_c2-"), ("ds2 q #0", "s2q: ds2 d2C"), ("ds2 qb #0", "s2qb: ds2 d1C")): same(a_, b_)
G_[[i for i, g_ in enumerate(G_) if "VCC tap" in g_][0]] += [PB("VCC: Rt1 top", "Metal1", rt1[1].center()), PB("VCC: Rt2 top", "Metal1", rt2[1].center()), PB("VCC: Ro1 top", "Metal1", ro1[1].center())]
G_[[i for i, g_ in enumerate(G_) if "vcop lead" in g_][0]] += [PB("vcop: Cbs1+", "TopMetal1", cbs1p.center())]
G_[[i for i, g_ in enumerate(G_) if "vcon lead" in g_][0]] += [PB("vcon: Cbs2+", "TopMetal1", cbs2p.center())]
G_[[i for i, g_ in enumerate(G_) if "GND" in g_][0]] += [PB("GND: Rbs1 bot", "Metal1", rb1_[0].center()), PB("GND: Rbs2 bot", "Metal1", rb2_[0].center())] + [PB(f"GND: {k} TIE", "Metal1", pc(k, "TIE")) for k in BS_SIG]
G_[[i for i, g_ in enumerate(G_) if "GND" in g_][0]] += [PB("GND: Ro2 bot", "Metal1", ro2[0].center()), PB("GND: Cbo-", "Metal5", pc("Cdiv_bo", "MINUS"))] + \
    [PB(f"GND: {k} TIE", "Metal1", pc(k, "TIE")) for k in ("Cdiv_bo", "Cdiv_o1", "Cdiv_o2")] + [PB(f"GND: {r} bot", "Metal1", ends(r)[0].center()) for r in ("Rdiv_eo1", "Rdiv_eo2")]
G_[[i for i, g_ in enumerate(G_) if "VCC tap" in g_][0]] += [PB("VCC: Rk1 top", "Metal1", rk1[1].center()), PB("VCC: Rref top", "Metal1", rref[1].center())] + \
    [PB(f"VCC: {t} {r}", "Metal1", ends(f"R{t.upper()}_{r}")[1].center()) for t in ("dm1", "ds1", "dm2", "ds2") for r in ("ln", "lp")]
G_[[i for i, g_ in enumerate(G_) if "GND" in g_][0]] += [PB("GND: Rk2 bot", "Metal1", rk2[0].center()), PB("GND: Rebr bot", "Metal1", rebr[0].center()),
    PB("GND: Cdiv_k-", "Metal5", pc("Cdiv_k", "MINUS")), PB("GND: Cdiv_bt-", "Metal5", pc("Cdiv_bt", "MINUS"))] + [PB(f"GND: {k} TIE", "Metal1", pc(k, "TIE")) for k in ("Cdiv_k", "Cdiv_bt") + DIV_SIG] + \
    [PB(f"GND: {t} Re bot", "Metal1", ends(f"R{t.upper()}_e")[0].center()) for t in ("dm1", "ds1", "dm2", "ds2")]
if __name__ == "__main__":
    import cheese
    print("Metal4 cheesing (IHP density, RF-aware):", cheese.cheese(B.ly, B.top))
    B.connectivity(P, G_); B.mini_drc(); B.min_area(); B.foreign_in_inductors(); B.floating_metal(); B.coil_topology({"Lvco": 400.0, "LPRX": 200.0, "LPTX": 200.0})
    B.write("lo_core.gds")
