"""tx_gen.py - TX channel layout generator (driver + 24 GHz PA + 2nd-harmonic trap), IHP SG13G2.
Stage 1: placement and the PA core's RF wiring (collector, cascode, output, trap, emitter, supply lead).
Coils face each other: output coil Lc (leads down) above, trap coil L2 (rot 180, leads up) below; the PA core sits in
the 80 um band between them so the RF nodes stay a few um long. Trap branch: OUT -> C2t -> L2 -> GND (series L-C)."""
from layoutlib import Builder, G, pya
B = Builder("tx_ch")
place, pin, pins_of, ends = B.place, B.pin, B.pins_of, B.ends
rect, wire, via, gnd_via = B.rect, B.wire, B.via, B.gnd_via
MIM = lambda w: dict(w=f"{w}u", l=f"{w}u")
W, H = 455.0, 495.0

# ======================= placement =======================
place("Lc", "inductor2", 300, 262, w="12u", s="2.1u", d="147u", nr_r=1, subE=False)            # LA (287..299) VCC, LB (301..313) collector
place("L2", "inductor2", 356, 181, rot=180, w="12u", s="2.1u", d="85u", nr_r=1, subE=False)    # rot 180: LA right (357..369) -> C2t, LB left -> GND
place("Q2",  "npn13G2V", 300, 248, Nx=8)         # cascode pair side by side, collectors (top) under Lc's LB lead
place("Q2b", "npn13G2V", 326, 248, Nx=8)
place("Q1",  "npn13G2",  316, 236, Nx=8)         # gain stage: collector (top) -> cascode emitters, base (bottom) <- driver Cc1, Rb
place("Re1", "rsil",     318.5, 226, w="4u", l="1.58u")
place("Cdec1", "rfcmim", 240, 210, **MIM(33))     # supply decoupling at the coil's VCC lead
place("Ccas",  "rfcmim", 376, 205, **MIM(37))     # cascode base bypass, right beside the bases
place("Cout",  "rfcmim", 353, 232, **MIM(7))      # collector -> OUT
place("C2t",   "rfcmim", 353, 194, **MIM(6.0))    # OUT -> trap coil (re-tuned post-layout: 6.4 -> 6.0 um)
place("Rb",    "rppd",   306.2, 225, w="1u", l="3.60u")   # base bias feed, at the base

# ======================= PA core wiring =======================
lcA, lcB = pin("Lc", "LA"), pin("Lc", "LB")
l2A, l2B = pin("L2", "LA"), pin("L2", "LB")
q1b, q1c, q1e = pin("Q1", "B"), pin("Q1", "C"), pin("Q1", "E")
qa = {k: (pin(k, "B"), pin(k, "C"), pin(k, "E")) for k in ("Q2", "Q2b")}
P_ = {k: (pin(k, "PLUS"), pin(k, "MINUS")) for k in ("Cdec1", "Ccas", "Cout", "C2t")}
re0, re1 = ends("Re1"); rb0, rb1 = ends("Rb")

# --- col: both cascode collectors (Metal1, top) -> vias -> TopMetal1 bar -> TopVia2 -> Lc's LB lead (TopMetal2)
YCB0, YCB1 = 253.4, 259.8
for k in ("Q2", "Q2b"):
    c = qa[k][1]; rect("Metal1", c.left, c.bottom, c.right, c.top + 1.6)
    for x in (c.left + 2.5, c.center().x, c.right - 2.5): via(x, c.top + 0.9, "Metal1", "TopMetal1", n=2, nt=1)
rect("TopMetal1", qa["Q2"][1].left, YCB0, P_["Cout"][1].center().x + 2, YCB1)
rect("TopMetal2", lcB.left, YCB0 + 0.5, lcB.right, lcB.bottom)                     # meet the lead at its end (no metal inside the coil)
via(lcB.center().x, YCB0 + 2.9, "TopMetal1", "TopMetal2", n=3, nt=3)
# --- col -> Cout bottom plate (MINUS, Metal5): via down from the bar's right end
com = P_["Cout"][1]; vco = (com.center().x, YCB0 + 1.0); via(*vco, "Metal5", "TopMetal1")
wire("Metal5", [vco, (com.center().x, com.center().y)], 2)
# --- c1: Q1 collector -> Metal2 riser in the gap between Q2 and Q2b -> Metal2 bar joining both cascode emitters
XG = 325.0
YC1 = 242.5                                                   # above Q1's emitter (Metal2 top at 236.8), below the cascode bases
rect("Metal1", q1c.left, q1c.bottom, q1c.right, YC1 + 0.6)
via(XG, YC1, "Metal1", "Metal2"); rect("Metal1", q1c.left, YC1 - 0.6, XG + 0.6, YC1 + 0.6)
e2, e2b = qa["Q2"][2], qa["Q2b"][2]
rect("Metal2", e2.left, e2.bottom, e2b.right, e2.top)
wire("Metal2", [(XG, YC1), (XG, e2.center().y)], 1.2)
# --- vcas: both cascode bases (Metal1) joined -> right -> Metal3 -> Ccas top plate (PLUS, TopMetal1)
b2, b2b = qa["Q2"][0], qa["Q2b"][0]
rect("Metal1", b2.left, b2.bottom, b2b.right, b2.top)
vb2 = (b2b.right + 2.0, b2.center().y); rect("Metal1", b2b.right - 1, b2.bottom, vb2[0] + 0.6, b2.top); via(*vb2, "Metal1", "Metal3")
ccp = P_["Ccas"][0]; vcc_ = (ccp.left + 3.0, ccp.top - 3.0); via(*vcc_, "Metal3", "TopMetal1")
wire("Metal3", [vb2, (vcc_[0], vb2[1]), vcc_], 1.5)
# --- Q1 emitter (Metal2) -> Re1 top end -> Re1 bottom end -> ground
via(re1.center().x, re1.center().y, "Metal1", "Metal2"); rect("Metal2", re1.left, re1.bottom, re1.right, q1e.top)
gnd_via(re0.center().x, re0.center().y - 2.0, "Metal1"); rect("Metal1", re0.left, re0.bottom - 3.0, re0.right, re0.top)
# --- b1: Q1 base bar (Metal1) pulled down into a wide base pad, extended left to the drive line's riser (x = XB1)
# (post-layout re-tune: the PA input MIM is gone; the driver's Cc1 feeds the base directly, see the drive line below)
YBP, XB1 = 229.0, 302.0                                       # base pad: pulled DOWN (an upward extension would crowd the emitters)
rect("Metal1", XB1 - 1.2, YBP, q1b.right, q1b.top)
# --- VCC lead: Lc's LA (TopMetal2) down beside Q2 -> Cdec1 top plate (PLUS, TopMetal1)
rect("TopMetal2", lcA.left, 238.0, lcA.right, lcA.bottom)
cdp = P_["Cdec1"][0]; vvd = (lcA.right - 3.0, 240.0); via(*vvd, "TopMetal1", "TopMetal2")   # 6 um from Rc1's TopVia2 (TV2.b: 1.06 um)
wire("TopMetal1", [vvd, (cdp.center().x, vvd[1]), (cdp.center().x, cdp.center().y)], 3)
# --- OUT: Cout top plate (PLUS) and C2t top plate (PLUS) joined on TopMetal1; OUT port on TopMetal2 to the right edge
cop, c2p, c2m = P_["Cout"][0], P_["C2t"][0], P_["C2t"][1]
XO = cop.right + 3.0
wire("TopMetal1", [(cop.center().x, cop.center().y), (XO, cop.center().y), (XO, c2p.center().y), (c2p.center().x, c2p.center().y)], 3)
YO = 199.0; vo = (XO, YO); via(*vo, "TopMetal1", "TopMetal2"); wire("TopMetal1", [(XO, c2p.center().y), vo], 3)
wire("TopMetal2", [vo, (W, YO)], 6, end_ext=0); B.text("OUT", W - 2, YO)
# --- trap: C2t bottom plate (MINUS, Metal5) -> TopMetal2 -> L2's LA lead; L2's LB lead -> ground
vt3 = (l2A.center().x, l2A.top + 6.0); via(*vt3, "Metal5", "TopMetal2")
rect("TopMetal2", l2A.left, l2A.top, l2A.right, vt3[1] + 2.0); wire("Metal5", [vt3, (vt3[0], c2m.center().y), (c2m.center().x, c2m.center().y)], 2)
rect("TopMetal2", l2B.left, l2B.top, l2B.right, l2B.top + 8.0); gnd_via(l2B.center().x, l2B.top + 5.0, "TopMetal2")

# ======================= stage 2: TX driver (the RX tile's signed-off channel LO driver, shifted) =======================
DX, DY = -107.0, -265.0                       # RX tile coordinates -> TX block coordinates
place("Cvb", "rfcmim", 120 + DX, 495 + DY, **MIM(33))
place("Rv1", "rppd", 172 + DX, 497 + DY, w="1u", l="17.53u"); place("Rv2", "rppd", 180 + DX, 494 + DY, w="1u", l="20.63u")
place("Rb1", "rppd", 190 + DX, 497 + DY, w="1u", l="19.08u"); place("Rb2", "rppd", 236 + DX, 497 + DY, w="1u", l="19.08u")
place("Ci1", "rfcmim", 200 + DX, 534 + DY, rot=270, **MIM(25)); place("Ci2", "rfcmim", 246 + DX, 534 + DY, rot=270, **MIM(25))
place("Qa", "npn13G2", 212 + DX, 494 + DY, rot=180, Nx=2); place("Qb", "npn13G2", 258 + DX, 494 + DY, rot=180, Nx=2)
place("Rtail", "rppd", 233 + DX, 487 + DY, w="2.2u", l="0.5u")  # re-tuned: 2/0.79 -> 2.2/0.5 um (more drive; 0.5 um is the cell minimum)
place("RD1", "rppd", 204 + DX, 487.4 + DY, w="2u", l="0.9u"); place("RD2", "rppd", 250 + DX, 487.4 + DY, w="2u", l="0.9u")   # re-tuned load 0.9 um (higher output pole)
place("Cc1", "rfcmim", 205.6 + DX, 479.9 + DY, rot=270, **MIM(16)); place("Cc2", "rfcmim", 251.6 + DX, 479.9 + DY, rot=270, **MIM(16))   # 12 -> 16 um
place("Cd", "rfcmim", 168, 175, **MIM(7)); place("Rd", "rsil", 186, 170, w="1u", l="1.30u")      # dummy load on the unused output

XR = 2.5                                                      # VCC rail (TopMetal2) along the left edge, below the input ports
wire("TopMetal2", [(XR, 20.0), (XR, 279.0)], 5, end_ext=0); B.text("VCC", XR, 30.0)
qab, qac, qae = pin("Qa", "B"), pin("Qa", "C"), pin("Qa", "E")
qbb, qbc, qbe = pin("Qb", "B"), pin("Qb", "C"), pin("Qb", "E")
cc1p, c1m, cc2p, c2m_ = pin("Cc1", "PLUS"), pin("Cc1", "MINUS"), pin("Cc2", "PLUS"), pin("Cc2", "MINUS")
ci1p, ci1m, ci2p, ci2m = pin("Ci1", "PLUS"), pin("Ci1", "MINUS"), pin("Ci2", "PLUS"), pin("Ci2", "MINUS")
rv10, rv11 = ends("Rv1"); rv20, rv21 = ends("Rv2"); rb10, rb11 = ends("Rb1"); rb20, rb21 = ends("Rb2")
rta0, rta1 = ends("Rtail"); rd10_, rd11_ = ends("RD1"); rd20_, rd21_ = ends("RD2")
# --- the RX tile's driver wiring, heights shifted by DY (geometry otherwise unchanged)
YVD = 487.0 + DY                                              # driver VCC bus (TM2) from the rail
wire("TopMetal2", [(XR, YVD), (rd20_.center().x + 2.0, YVD)], 4)        # rail on the LEFT here: the bus must reach both loads
wire("TopMetal2", [(rv10.center().x, YVD), (rv10.center().x, rv10.center().y)], 4)
via(rv10.center().x, rv10.center().y, "Metal1", "TopMetal2")
for (qc, cp, r0, r1) in ((qac, cc1p, rd10_, rd11_), (qbc, cc2p, rd20_, rd21_)):
    rect("Metal1", r1.left, r1.bottom - 0.3, qc.right, qc.top)
    vd = (cp.center().x, 490.0 + DY); via(*vd, "Metal1", "TopMetal1"); rect("TopMetal1", cp.left, cp.bottom, cp.right, vd[1] + 1.05)
    via(r0.center().x, r0.center().y - 0.2, "Metal1", "TopMetal2")
for (qb_, cim_, rbb) in ((qab, ci1m, rb10), (qbb, ci2m, rb20)):
    rect("Metal1", qb_.left, qb_.bottom, ci1m.right if qb_ is qab else ci2m.right, 501.6 + DY)
    vb_ = (cim_.center().x, 500.5 + DY); via(*vb_, "Metal1", "Metal5"); wire("Metal5", [(cim_.center().x, cim_.center().y), vb_], 2)
    wire("Metal1", [(rbb.center().x, rbb.center().y), (rbb.center().x, 497.5 + DY), (qb_.left + 0.5, 497.5 + DY)], 1.0)
rect("Metal2", qae.left, qae.bottom, qbe.right, qae.top)
rect("Metal1", rta1.left, rta1.bottom, rta1.right, qae.center().y + 0.8); via(rta1.center().x, qae.center().y, "Metal1", "Metal2")
wire("Metal1", [(rta0.center().x, rta0.center().y), (rta0.center().x, 482.5 + DY)], 1.0); gnd_via(rta0.center().x, 482.5 + DY, "Metal1")
YBD = 519.0 + DY
for r in (rv11, rv21, rb11, rb21):
    rect("Metal1", r.left, r.bottom, r.right, YBD + 0.6); via(r.center().x, YBD, "Metal1", "Metal2")
cvbp, cvbm = pin("Cvb", "PLUS"), pin("Cvb", "MINUS")
vcvb = (cvbp.left - 3.0, cvbp.center().y); via(*vcvb, "Metal2", "TopMetal1"); wire("TopMetal1", [vcvb, (cvbp.center().x, cvbp.center().y)], 2)
wire("Metal2", [vcvb, (vcvb[0], YBD), (rb21.center().x, YBD)], 1.0)
wire("Metal1", [(rv20.center().x, rv20.center().y), (rv20.center().x, 490.0 + DY)], 1.0); gnd_via(rv20.center().x, 490.0 + DY, "Metal1")
g = (cvbm.right + 3.0, cvbm.center().y); gnd_via(*g, "Metal5"); wire("Metal5", [(cvbm.center().x, cvbm.center().y), g], 2)
# --- TX-specific: input ports on the left edge (TopMetal2), above the VCC rail
for cp, name, yp in ((ci1p, "TXINP", 285.0), (ci2p, "TXINN", 296.0)):
    x = cp.center().x; rect("TopMetal1", cp.left, cp.bottom, cp.right, yp + 1.1); via(x, yp, "TopMetal1", "TopMetal2")
    wire("TopMetal2", [(x, yp), (0, yp)], 4, end_ext=0); B.text(name, 1.5, yp)
# --- b1 drive line: Cc1 bottom plate (Metal5) -> down -> 2 um TopMetal1 at y = 192, BELOW the decoupling MIM (not under it)
#     -> Metal3 riser at x = XB1 (Metal3: the vbn line crosses here on Metal2) -> the base pad
YB1L = 192.0
vpn = (c1m.center().x, YB1L); via(*vpn, "Metal5", "TopMetal1"); wire("Metal5", [(c1m.center().x, c1m.center().y), vpn], 2)
wire("TopMetal1", [vpn, (XB1, YB1L)], 2)
via(XB1, YB1L, "Metal3", "TopMetal1"); wire("Metal3", [(XB1, YB1L), (XB1, YBP + 2.0)], 1.5); via(XB1, YBP + 2.0, "Metal1", "Metal3")
# --- dummy load: Cc2 bottom plate (Metal5, crosses under the pin line) -> Cd top plate; Cd bottom plate -> Rd -> ground
cdp_, cdm_ = pin("Cd", "PLUS"), pin("Cd", "MINUS"); rd0, rd1 = ends("Rd")
vdm = (c2m_.center().x, 183.0); via(*vdm, "Metal5", "TopMetal1"); wire("Metal5", [(c2m_.center().x, c2m_.center().y), vdm], 2)
wire("TopMetal1", [vdm, (cdp_.center().x, vdm[1]), (cdp_.center().x, cdp_.center().y)], 2)
vdd = (rd1.center().x, rd1.center().y); via(*vdd, "Metal1", "Metal5")
wire("Metal5", [(cdm_.center().x, cdm_.center().y), (vdd[0], cdm_.center().y), vdd], 2)
gnd_via(rd0.center().x, rd0.center().y - 2.0, "Metal1"); rect("Metal1", rd0.left, rd0.bottom - 3.0, rd0.right, rd0.top)
# --- VCC feed to the coil's decoupling MIM: rail -> TopMetal2 below the driver -> up beside Cdec1 -> its top plate
YVF, XVF = 158.0, 246.0; cdp = P_["Cdec1"][0]               # via lands on the top plate itself
wire("TopMetal2", [(XR, YVF), (XVF, YVF), (XVF, cdp.center().y)], 5); via(XVF, cdp.center().y, "TopMetal1", "TopMetal2")

# ======================= stage 3a: PA bias mirror (the RX tile's LNA mirror, shifted; Rif replaces the IREF port) =======================
BX = -120.0                                                   # tile x -> TX x (heights unchanged: the mirror sits in the lower left)
place("Qr", "npn13G2", 180 + BX, 70, Nx=1); place("Qf", "npn13G2", 200 + BX, 70, Nx=1)
place("Rref", "rhigh", 222 + BX, 62, w="1u", l="5.53u"); place("Rief", "rhigh", 236 + BX, 62, w="1u", l="12.6u")
place("Cbn", "rfcmim", 180 + BX, 105, **MIM(37))
place("Rer", "rsil", 168 + BX, 52, w="1u", l="4.47u")         # reference emitter resistor (new in the PA)
place("Rif", "rppd", 76.0, 84.0, w="1u", l="2.0u")             # reference current from VCC (replaces the tile's IREF port)
qrb, qrc, qre = pin("Qr", "B"), pin("Qr", "C"), pin("Qr", "E")
qfb, qfc, qfe = pin("Qf", "B"), pin("Qf", "C"), pin("Qf", "E")
rref0, rref1 = ends("Rref"); rief0, rief1 = ends("Rief"); rer0, rer1 = ends("Rer"); rif0, rif1 = ends("Rif")
cbp, cbm = pin("Cbn", "PLUS"), pin("Cbn", "MINUS")
# cr: Qr collector (top) + Qf base (bottom), as in the tile; Metal3 tap -> Rif bottom (Rif top -> VCC)
rect("Metal1", qrc.left, qrc.bottom, qrc.right, 76.0)
wire("Metal1", [(qrc.center().x, 75.5), (196.0 + BX, 75.5), (196.0 + BX, 65.5), (qfb.center().x, 65.5)], 1.0)
rect("Metal1", qfb.left, 65.0, qfb.right, qfb.top)
via(190.0 + BX, 75.5, "Metal1", "Metal3")
via(rif0.center().x, rif0.center().y, "Metal1", "Metal3"); wire("Metal3", [(190.0 + BX, 75.5), (rif0.center().x, 75.5), (rif0.center().x, rif0.center().y)], 1.0)
# br: Qr base (bottom) -> Metal2 -> Rref bottom (as in the tile)
rect("Metal1", qrb.left, 62.0, qrb.right, qrb.top); via(qrb.center().x, 63.0, "Metal1", "Metal2")
via(rref0.center().x, 63.0, "Metal1", "Metal2"); rect("Metal1", rref0.left, rref0.bottom, rref0.right, 63.5)
wire("Metal2", [(qrb.center().x, 63.0), (rref0.center().x, 63.0)], 1.0)
# Qr emitter (Metal2) -> left -> Rer top; Rer bottom -> ground
rect("Metal2", qre.left - 6.5, qre.bottom, qre.right, qre.top); via(rer1.center().x, rer1.center().y, "Metal1", "Metal2")
wire("Metal2", [(qre.left - 6.0, qre.center().y), (rer1.center().x, qre.center().y), (rer1.center().x, rer1.center().y)], 1.0)
gnd_via(rer0.center().x, rer0.center().y - 2.0, "Metal1"); rect("Metal1", rer0.left, rer0.bottom - 3.0, rer0.right, rer0.top)
# vbn: Metal2 bus at y = 95 (as in the tile): Qf emitter, Rref top, Rief top, Cbn top plate
YV = 95.0
rect("Metal2", qfe.left, qfe.bottom, qfe.right + 6.0, qfe.top)
wire("Metal2", [(qfe.right + 5.0, qfe.center().y), (qfe.right + 5.0, YV)], 1.2)
via(rref1.center().x, rref1.center().y, "Metal1", "Metal2"); wire("Metal2", [(rref1.center().x, rref1.center().y), (rref1.center().x, YV)], 1.0)
via(rief1.center().x, rief1.center().y, "Metal1", "Metal2"); wire("Metal2", [(rief1.center().x, rief1.center().y), (rief1.center().x, YV)], 1.0)
vcb = (cbp.left - 3.5, cbp.center().y); via(*vcb, "Metal2", "TopMetal1")
wire("TopMetal1", [(cbp.center().x, cbp.center().y), vcb], 2)
wire("Metal2", [vcb, (vcb[0], YV), (rief1.center().x + 4.0, YV)], 1.0)
# Rief bottom, Cbn bottom plate -> ground (as in the tile)
wire("Metal1", [(rief0.center().x, rief0.center().y), (rief0.center().x, 57.0)], 1.0); gnd_via(rief0.center().x, 57.0, "Metal1")
g = (cbm.right + 3.0, cbm.center().y); gnd_via(*g, "Metal5"); wire("Metal5", [(cbm.center().x, cbm.center().y), g], 2)
# Qf collector and Rif top -> VCC rail (TopMetal2, left edge)
rect("Metal1", qfc.left, qfc.bottom, qfc.right, 81.0); via(qfc.center().x, 80.0, "Metal1", "TopMetal2")
wire("TopMetal2", [(qfc.center().x, 80.0), (XR, 80.0)], 4)
via(rif1.center().x, rif1.center().y + 0.5, "Metal1", "TopMetal2"); rect("Metal1", rif1.left, rif1.bottom, rif1.right, rif1.top + 1.0)
wire("TopMetal2", [(rif1.center().x, rif1.center().y + 0.5), (rif1.center().x, 80.0)], 4)
# vbn -> the PA's base resistor Rb: Metal2 east along y = 95, north beside Cdec1 (x = 231.9), east to Rb
XCH = 231.9; YRB = 221.0
wire("Metal2", [(rief1.center().x + 4.0, YV), (XCH, YV), (XCH, YRB), (rb0.center().x, YRB)], 1.0)
via(rb0.center().x, YRB, "Metal1", "Metal2"); rect("Metal1", rb0.left, YRB - 0.6, rb0.right, rb0.top)

# ======================= stage 3b: enable switches, cascode divider, substrate taps =======================
B.LY["GatPoly"] = B.ly.layer(5, 0); B.LY["Cont"] = B.ly.layer(6, 0); B.LY["Via1"] = B.ly.layer(19, 0)
place("M1", "nmos", 66.0, 80.0, w="10u", l="0.13u", ng=1)     # cr switch (pulls the mirror reference down when ENB is high)
place("M2", "nmos", 93.0, 75.0, w="8u", l="0.13u", ng=1)      # vbn switch
def nmos_gate(key, wch):
    """Single-finger gate contact, the LO core's proven dimensions: poly pad 0.32 um above the active edge, contact, M1 pad."""
    o = B.DEV[key].dbbox(); ox, oy = o.left, o.bottom + 0.18            # PCell origin = active bottom-left
    rect("GatPoly", ox + 0.34, oy + wch + 0.18, ox + 0.47, oy + wch + 0.86)
    rect("GatPoly", ox + 0.19, oy + wch + 0.50, ox + 0.62, oy + wch + 0.86)
    rect("Cont", ox + 0.325, oy + wch + 0.60, ox + 0.485, oy + wch + 0.76)
    rect("Metal1", ox + 0.275, oy + wch + 0.55, ox + 0.535, oy + wch + 0.81)
    return ox, oy
ENBY = 92.5
for key, wch in (("M1", 10.0), ("M2", 8.0)):
    ox, oy = nmos_gate(key, wch); xg = ox + 0.405
    rect("Metal1", xg - 0.15, oy + wch + 0.55, xg + 0.15, ENBY + 0.6); via(xg, ENBY, "Metal1", "Metal3", n=1)
wire("Metal3", [(0, ENBY), (B.DEV["M2"].dbbox().left + 0.405, ENBY)], 1.0, start_ext=0); B.text("ENB", 1.0, ENBY, gds=(30, 25))
# M1: drain (right stripe) -> Metal3 -> cr (joins the cr Metal3 at x = 70, y = 75.5); source (left stripe) -> ground
o1 = B.DEV["M1"].dbbox(); ox1, oy1 = o1.left, o1.bottom + 0.18
rect("Metal1", ox1 + 0.58, oy1 - 1.4, ox1 + 0.74, oy1); rect("Metal1", ox1 + 0.58, oy1 - 1.4, ox1 + 1.9, oy1 - 1.0)
via(ox1 + 1.6, oy1 - 1.2, "Metal1", "Metal3", n=1); wire("Metal3", [(ox1 + 1.6, oy1 - 1.2), (70.0, oy1 - 1.2), (70.0, 75.5)], 1.0)
# source -> LEFT, above the cr wire (y = 75.5): a 4x4 ground via below the switch would land on that wire (cr-GND short)
rect("Metal1", ox1 + 0.07, oy1 - 0.6, ox1 + 0.23, oy1); rect("Metal1", ox1 - 3.0, oy1 - 0.6, ox1 + 0.23, oy1 - 0.2)
vgs = (ox1 - 2.6, oy1 - 0.4); via(*vgs, "Metal1", "Metal4", n=1); B.GPATCH.append(tuple(G(v) for v in (vgs[0] - 3, vgs[1] - 3, vgs[0] + 3, vgs[1] + 3)))
# M2: drain (right stripe) -> Metal2 west to the vbn riser (x = qfe.right + 5); source (left stripe) -> ground
o2 = B.DEV["M2"].dbbox(); ox2, oy2 = o2.left, o2.bottom + 0.18
XVB = qfe.right + 5.0
rect("Metal1", ox2 + 0.58, oy2 - 1.5, ox2 + 0.74, oy2); rect("Metal1", ox2 + 0.58, oy2 - 1.5, ox2 + 1.6, oy2 - 1.1)
via(ox2 + 1.3, oy2 - 1.3, "Metal1", "Metal2", n=1); wire("Metal2", [(ox2 + 1.3, oy2 - 1.3), (ox2 + 1.3, oy2 - 2.0), (XVB, oy2 - 2.0)], 0.6)      # clear of the source ground via
rect("Metal1", ox2 + 0.07, oy2 - 3.8, ox2 + 0.23, oy2); rect("Metal1", ox2 - 1.6, oy2 - 3.8, ox2 + 0.23, oy2 - 3.4)
gnd_via(ox2 - 1.3, oy2 - 3.6, "Metal1")
# cascode divider under the coil's VCC stub: Rc1 VCC -> vcas, Rc2 vcas -> ground; vcas bar joins the cascode base bar
place("Rc1", "rppd", 288.8, 243.5, w="1u", l="3.21u"); place("Rc2", "rppd", 295.6, 240.8, w="1u", l="5.92u")
rc10, rc11 = ends("Rc1"); rc20, rc21 = ends("Rc2")
via(rc10.center().x, rc10.center().y, "Metal1", "TopMetal2", n=1)                # Rc1 bottom -> VCC stub (TopMetal2) above it
rect("Metal1", rc10.left, rc11.bottom, b2.left + 0.6, b2.top)                     # vcas bar: Rc1 top, Rc2 top, Q2 base bar
gnd_via(rc20.center().x, rc20.center().y - 2.4, "Metal1"); rect("Metal1", rc20.left, rc20.bottom - 3.0, rc20.right, rc20.top)
# substrate taps -> ground
TAPS = ((284, 222), (180, 148), (30, 40), (130, 40), (60, 200), (440, 300))
for i, (x, y) in enumerate(TAPS):
    place(f"ptap{i}", "ptap1", x, y, w="2u", l="2u"); t = pins_of(f"ptap{i}", 8)[0]; gnd_via(t.center().x, t.center().y, "Metal1")

# ======================= stage 4: decap bottom plates, MIM substrate rings, ground plane =======================
for k in ("Cdec1", "Ccas"):                                   # decoupling / bypass bottom plates -> ground
    m = pin(k, "MINUS"); g = (m.right + 3.0, m.center().y); gnd_via(*g, "Metal5"); wire("Metal5", [(m.center().x, m.center().y), g], 2)
SIGNAL_MIMS = ("Cout", "C2t", "Cc1", "Cc2", "Cd", "Ci1", "Ci2")    # these sit in plane cut-outs (less plate-to-ground C)
for k, inst in list(B.DEV.items()):
    if B.ly.cell(inst.cell_index).name.startswith("rfcmim"): B.ring_ground(k, cutout_keys=SIGNAL_MIMS, coil_keys=("Lc", "L2"))
B.text("GND", 6.0, 6.0, gds=(50, 25))
B.ground_plane((0, 0, W, H), hole_keys=("Lc", "L2"), signal_mim_keys=SIGNAL_MIMS)

if __name__ == "__main__":
    keys = list(B.DEV); ov = [f"{a} x {b}" for i, a in enumerate(keys) for b in keys[i+1:] if B.DEV[a].dbbox().overlaps(B.DEV[b].dbbox())]
    print("overlaps:", ov or "none", "| block bbox", B.top.dbbox())
    P = {"col_q2": ("Metal1", qa["Q2"][1].center()), "col_q2b": ("Metal1", qa["Q2b"][1].center()), "col_lc": ("TopMetal2", (lcB.center().x, lcB.bottom - 1.0)),
         "col_cout": ("Metal5", com.center()),
         "c1_q1": ("Metal1", q1c.center()), "c1_q2": ("Metal2", e2.center()), "c1_q2b": ("Metal2", e2b.center()),
         "vcas_q2": ("Metal1", b2.center()), "vcas_q2b": ("Metal1", b2b.center()), "vcas_ccas": ("TopMetal1", ccp.center()),
         "b1_q1": ("Metal1", q1b.center()), "b1_rb": ("Metal1", rb1.center()), "b1_cc": ("Metal5", c1m.center()),
         "e1_q1": ("Metal2", q1e.center()), "e1_re": ("Metal1", re1.center()),
         "vcc_lc": ("TopMetal2", (lcA.center().x, lcA.bottom - 1.0)), "vcc_cdec": ("TopMetal1", cdp.center()),
         "out_cout": ("TopMetal1", cop.center()), "out_c2t": ("TopMetal1", c2p.center()), "out_port": ("TopMetal2", (W - 1, YO)),
         "t3_c2t": ("Metal5", c2m.center()), "t3_l2": ("TopMetal2", (l2A.center().x, l2A.top + 1.0))}
    P.update({"vcc_rail": ("TopMetal2", (XR, 100.0)), "vcc_rv1": ("Metal1", rv10.center()), "vcc_rd1": ("Metal1", rd10_.center()), "vcc_rd2": ("Metal1", rd20_.center()),
              "vbd_rv1": ("Metal1", rv11.center()), "vbd_rv2": ("Metal1", rv21.center()), "vbd_rb1": ("Metal1", rb11.center()), "vbd_rb2": ("Metal1", rb21.center()), "vbd_cvb": ("TopMetal1", cvbp.center()),
              "b1d_q": ("Metal1", qab.center()), "b1d_ci": ("Metal5", ci1m.center()), "b1d_rb": ("Metal1", rb10.center()),
              "b2d_q": ("Metal1", qbb.center()), "b2d_ci": ("Metal5", ci2m.center()), "b2d_rb": ("Metal1", rb20.center()),
              "t_qa": ("Metal2", qae.center()), "t_qb": ("Metal2", qbe.center()), "t_rt": ("Metal1", rta1.center()),
              "dp_q": ("Metal1", qac.center()), "dp_rd": ("Metal1", rd11_.center()), "dp_cc": ("TopMetal1", cc1p.center()),
              "dn_q": ("Metal1", qbc.center()), "dn_rd": ("Metal1", rd21_.center()), "dn_cc": ("TopMetal1", cc2p.center()),
              "dmy_cc": ("Metal5", c2m_.center()), "dmy_cd": ("TopMetal1", cdp_.center()), "dd_cd": ("Metal5", cdm_.center()), "dd_rd": ("Metal1", rd1.center()),
              "cr_qr": ("Metal1", qrc.center()), "cr_qf": ("Metal1", qfb.center()), "cr_rif": ("Metal1", rif0.center()),
              "br_qr": ("Metal1", qrb.center()), "br_rref": ("Metal1", rref0.center()), "er_q": ("Metal2", qre.center()), "er_r": ("Metal1", rer1.center()),
              "vbn_qf": ("Metal2", qfe.center()), "vbn_rref": ("Metal1", rref1.center()), "vbn_rief": ("Metal1", rief1.center()), "vbn_cbn": ("TopMetal1", cbp.center()), "vbn_rb": ("Metal1", rb0.center()),
              "vcc_qf": ("Metal1", qfc.center()), "vcc_rif": ("Metal1", rif1.center()),
              "enb_port": ("Metal3", (0.5, ENBY)), "enb_m1": ("Metal1", (B.DEV["M1"].dbbox().left + 0.405, B.DEV["M1"].dbbox().bottom + 0.18 + 10.68)),
              "enb_m2": ("Metal1", (B.DEV["M2"].dbbox().left + 0.405, B.DEV["M2"].dbbox().bottom + 0.18 + 8.68)),
              "cr_m1": ("Metal1", (B.DEV["M1"].dbbox().left + 0.66, B.DEV["M1"].dbbox().bottom + 5.0)),
              "vbn_m2": ("Metal1", (B.DEV["M2"].dbbox().left + 0.66, B.DEV["M2"].dbbox().bottom + 4.0)),
              "vcas_rc1": ("Metal1", rc11.center()), "vcas_rc2": ("Metal1", rc21.center()), "vcc_rc1": ("Metal1", rc10.center()),
              "gnd_plane": ("Metal4", (6.0, 6.0)), "gnd_re1": ("Metal1", re0.center()), "gnd_l2": ("TopMetal2", (l2B.center().x, l2B.top + 1.0)),
              "gnd_cdec": ("Metal5", pin("Cdec1", "MINUS").center()), "gnd_ccas": ("Metal5", pin("Ccas", "MINUS").center()),
              "gnd_cbn": ("Metal5", cbm.center()), "gnd_cvb": ("Metal5", cvbm.center()), "gnd_rtail": ("Metal1", rta0.center()),
              "gnd_rv2": ("Metal1", rv20.center()), "gnd_rief": ("Metal1", rief0.center()), "gnd_rer": ("Metal1", rer0.center()),
              "gnd_rc2": ("Metal1", rc20.center()), "gnd_rd": ("Metal1", rd0.center()),
              "gnd_m1s": ("Metal1", (B.DEV["M1"].dbbox().left + 0.15, B.DEV["M1"].dbbox().bottom + 5.0)),
              "gnd_m2s": ("Metal1", (B.DEV["M2"].dbbox().left + 0.15, B.DEV["M2"].dbbox().bottom + 4.0)),
              "gnd_tie_cout": ("Metal1", pin("Cout", "TIE").center()),
              "gnd_tie_c2t": ("Metal1", pin("C2t", "TIE").center()), "gnd_tie_ci1": ("Metal1", pin("Ci1", "TIE").center()),
              "inp_ci": ("TopMetal1", ci1p.center()), "inp_port": ("TopMetal2", (0.5, 285.0)), "inn_ci": ("TopMetal1", ci2p.center()), "inn_port": ("TopMetal2", (0.5, 296.0))})
    G_ = [("col_q2", "col_q2b", "col_lc", "col_cout"), ("c1_q1", "c1_q2", "c1_q2b"), ("vcas_q2", "vcas_q2b", "vcas_ccas", "vcas_rc1", "vcas_rc2"),
          ("b1_q1", "b1_rb", "b1_cc"), ("e1_q1", "e1_re"), ("out_cout", "out_c2t", "out_port"), ("t3_c2t", "t3_l2"),
          ("vcc_rail", "vcc_rv1", "vcc_rd1", "vcc_rd2", "vcc_lc", "vcc_cdec", "vcc_qf", "vcc_rif", "vcc_rc1"),
          ("cr_qr", "cr_qf", "cr_rif", "cr_m1"), ("enb_port", "enb_m1", "enb_m2"), ("br_qr", "br_rref"), ("er_q", "er_r"), ("vbn_qf", "vbn_rref", "vbn_rief", "vbn_cbn", "vbn_rb", "vbn_m2"), ("vbd_rv1", "vbd_rv2", "vbd_rb1", "vbd_rb2", "vbd_cvb"),
          ("b1d_q", "b1d_ci", "b1d_rb"), ("b2d_q", "b2d_ci", "b2d_rb"), ("t_qa", "t_qb", "t_rt"), ("dp_q", "dp_rd", "dp_cc"), ("dn_q", "dn_rd", "dn_cc"),
          ("dmy_cc", "dmy_cd"), ("dd_cd", "dd_rd"), ("inp_ci", "inp_port"), ("inn_ci", "inn_port"),
          ("gnd_plane", "gnd_re1", "gnd_l2", "gnd_cdec", "gnd_ccas", "gnd_cbn", "gnd_cvb", "gnd_rtail", "gnd_rv2", "gnd_rief", "gnd_rer",
           "gnd_rc2", "gnd_rd", "gnd_m1s", "gnd_m2s", "gnd_tie_cout", "gnd_tie_c2t", "gnd_tie_ci1")]
    B.connectivity(P, G_); B.mini_drc(); B.foreign_in_inductors(); B.min_area(); B.floating_metal(); B.coil_continuity(["Lc", "L2"])
    import cheese
    print("Metal4 cheesing (IHP density, RF-aware):", cheese.cheese(B.ly, B.top))
    B.write("tx_ch.gds")
