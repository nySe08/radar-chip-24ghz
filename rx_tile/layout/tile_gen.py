"""tile_gen.py - RX channel tile layout generator (LNA vertical + mixer + resistive LO driver), IHP SG13G2."""
from layoutlib import Builder, G, pya
B = Builder("rx_tile")
place, pin, pins_of, ends = B.place, B.pin, B.pins_of, B.ends
rect, wire, via, gnd_via = B.rect, B.wire, B.via, B.gnd_via
MIM = lambda w: dict(w=f"{w}u", l=f"{w}u")
# ======================= placement =======================
# ---------------- LNA (vertical: Lb leads up, Lc leads down, RF core in the band between) ----------------
place("Lb", "inductor2", 80.5, 161.9, rot=180, w="7u", s="2.1u", d="68.66u", nr_r=2, subE=False)     # y 0..162, leads at the top
place("Lc", "inductor2", 80.5, 233.0, w="5u", s="2.1u", d="55.83u", nr_r=2, subE=False)             # y 232..373, leads at the bottom
place("Q1", "npn13G2", 86.0, 176.0, Nx=8)            # base (bottom) faces Lb's lead
place("Q2", "npn13G2", 86.0, 208.0, Nx=8)            # collector (top) faces Lc's lead
place("Cin", "rfcmim", 175, 8, **MIM(33))            # near the RF pad, bottom of the side column
place("Ccas1", "rfcmim", 172, 172, **MIM(33))        # cascode base bypass, level with Q2
place("Ccas2", "rfcmim", 222, 172, **MIM(33))
place("Cout", "rfcmim", 141, 225, rot=180, **MIM(7))  # rotated: bottom plate (MINUS) faces the out node
place("RP", "rppd", 82.6, 226.5, rot=90, w="2u", l="5.37u")    # under Lc's leads: left pin = VCC lead, right pin = out lead
place("Cdec1", "rfcmim", 172, 245, **MIM(33))        # VCC decoupling next to Lc's VCC lead
place("Cdec2", "rfcmim", 222, 245, **MIM(33))
place("R1", "rppd", 268, 207, w="1u", l="22.95u"); place("R2", "rhigh", 278, 211, w="1u", l="13.30u")
# bias mirror (side column, between Cin and Ccas)
place("Qr", "npn13G2", 180, 70, Nx=1); place("Qf", "npn13G2", 200, 70, Nx=1)
place("Rref", "rhigh", 222, 62, w="1u", l="28.12u"); place("Rief", "rhigh", 236, 62, w="1u", l="12.03u")
place("Rb", "rppd", 252, 62, w="1u", l="19.08u")
place("Cbn", "rfcmim", 180, 105, **MIM(33))
# ---------------- mixer (signal flow: link arrives at x~155, y~378 beside Lc) ----------------
place("Q3", "npn13G2", 224, 396, Nx=4)                      # transconductor, right of Cdc
place("Rt", "rsil", 217.5, 383, w="1u", l="7.55u")          # 60-ohm termination b3 -> vb3
place("Re", "rsil", 241, 383, w="1u", l="9.55u")            # emitter degeneration
place("Q4", "npn13G2", 230, 426, Nx=2); place("Q5", "npn13G2", 246, 426, Nx=2)   # switching pair above Q3
place("Rl1", "rppd", 222, 404, w="1u", l="7.47u"); place("Rl2", "rppd", 262, 404, w="1u", l="7.47u")  # LO-port bias feeds
place("RLp", "rppd", 235, 434, w="2u", l="2.05u"); place("RLn", "rppd", 253, 434, w="2u", l="2.05u")  # IF loads, beside the collectors
place("CLp", "cmim", 20, 382, **MIM(34.3)); place("CLn", "cmim", 62, 382, **MIM(34.3))                # IF filter caps
# mixer bias, in the free area right of Lc
place("Cb3", "rfcmim", 220, 300, **MIM(33)); place("Qrf", "npn13G2", 266, 362, Nx=1)
place("Rrf", "rppd", 276, 350, w="1u", l="4.37u"); place("Rerf", "rsil", 268, 300, w="1u", l="38.2u")
place("Cvl", "rfcmim", 174, 330, **MIM(33))
place("Rd1", "rppd", 232, 342, w="1u", l="22.95u"); place("Rd2", "rhigh", 240, 345, w="1u", l="13.30u")
# ---------------- channel LO driver (top; bases up toward the LO ports, collectors down toward the coupling caps) ----------------
place("Cvb", "rfcmim", 120, 495, **MIM(33))
place("Rv1", "rppd", 172, 497, w="1u", l="17.53u"); place("Rv2", "rppd", 180, 494, w="1u", l="20.63u")
place("Rb1", "rppd", 190, 497, w="1u", l="19.08u"); place("Rb2", "rppd", 236, 497, w="1u", l="19.08u")
place("Ci1", "rfcmim", 200, 534, rot=270, **MIM(25)); place("Ci2", "rfcmim", 246, 534, rot=270, **MIM(25))
place("Qa", "npn13G2", 212, 494, rot=180, Nx=2); place("Qb", "npn13G2", 258, 494, rot=180, Nx=2)
place("Rtail", "rppd", 233, 487, w="2u", l="0.79u")
place("RD1", "rppd", 204, 487.4, w="2u", l="1.28u"); place("RD2", "rppd", 250, 487.4, w="2u", l="1.28u")
place("Cc1", "rfcmim", 205.6, 479.9, rot=270, **MIM(12)); place("Cc2", "rfcmim", 251.6, 479.9, rot=270, **MIM(12))  # PLUS up, MINUS down
# substrate taps
for i, (x, y) in enumerate(((60, 200), (120, 190), (190, 92), (110, 440), (106, 500))):
    place(f"ptap{i}", "ptap1", x, y, w="2u", l="2u")

# ======================= RF path wiring =======================
lbA, lbB = pin("Lb", "LA"), pin("Lb", "LB")          # Lb (rot 180): LA right -> Q1 base (b1), LB left -> input (in)
lcA, lcB = pin("Lc", "LA"), pin("Lc", "LB")          # Lc: LA left -> VCC, LB right -> out
q1b, q1c, q1e = pin("Q1", "B"), pin("Q1", "C"), pin("Q1", "E")
q2b, q2c, q2e = pin("Q2", "B"), pin("Q2", "C"), pin("Q2", "E")
cip, cim = pin("Cin", "PLUS"), pin("Cin", "MINUS")
cop, com = pin("Cout", "PLUS"), pin("Cout", "MINUS")
# --- RFIN port -> Cin MINUS (Metal5)
vrf = (cim.right + 2.2, cim.center().y); via(*vrf, "Metal5", "TopMetal2")
wire("Metal5", [(cim.center().x, cim.center().y), vrf], 2)
wire("TopMetal2", [vrf, (vrf[0], 0)], 10, end_ext=0)
B.text("RFIN", vrf[0], 2)
# --- in: Cin PLUS (TM1) -> TM2 up beside Lb -> across -> Lb left lead
vin = (cip.left - 4.5, cip.center().y); via(*vin, "TopMetal1", "TopMetal2")
wire("TopMetal1", [(cip.center().x, cip.center().y), vin], 3)
YIN = 166.0
wire("TopMetal2", [vin, (vin[0], YIN), (lbB.center().x, YIN)], 5)
via(lbB.center().x, YIN, "TopMetal1", "TopMetal2")
rect("TopMetal1", lbB.left, lbB.top, lbB.right, YIN + 2.5)
# --- b1: Lb right lead -> TM1 stub -> via -> Q1 base bar (pulled down)
rect("Metal1", q1b.left, q1b.bottom - 6.2, q1b.right, q1b.top)
vb1 = (q1b.left + 2.0, q1b.bottom - 5.0); via(*vb1, "Metal1", "TopMetal1")
rect("TopMetal1", lbA.left, lbA.top, lbA.right, vb1[1] + 1.4)
# --- Le: Q1 emitter (M2) -> left -> via -> TM2 strip 47 um -> ground
rect("Metal2", q1e.left - 9.5, q1e.bottom, q1e.left + 1, q1e.top)
vle = (q1e.left - 8.0, q1e.center().y); via(*vle, "Metal2", "TopMetal2")
LEY = 177.0
rect("TopMetal2", vle[0] + 2, LEY - 5, vle[0] + 2 - 47, LEY + 5)
gnd_via(vle[0] + 2 - 44, LEY, "TopMetal2")
# --- c1: Q1 collector (top) -> Metal2 -> Q2 emitter (escape right)
rect("Metal1", q1c.left, q1c.bottom, q1c.right, q1c.top + 11.5)
vc1 = (q1c.right - 2.0, q1c.top + 10.3); via(*vc1, "Metal1", "Metal2")
rect("Metal2", q2e.right - 1, q2e.bottom, q2e.right + 6, q2e.top)
wire("Metal2", [vc1, (q2e.right + 4.5, vc1[1]), (q2e.right + 4.5, q2e.center().y)], 2)
# --- b2: Q2 base (bottom) -> Metal3 bus -> Ccas1 / Ccas2 top plates
rect("Metal1", q2b.left, q2b.bottom - 6.5, q2b.right, q2b.top)
vb2 = (q2b.left + 3.0, q2b.bottom - 5.3); via(*vb2, "Metal1", "Metal3")
YB2 = vb2[1]
for k in ("Ccas1", "Ccas2"):
    p = pin(k, "PLUS"); vx = p.center().x
    via(vx, YB2, "Metal3", "TopMetal1"); wire("TopMetal1", [(vx, YB2), (vx, p.center().y)], 2)
wire("Metal3", [vb2, (pin("Ccas2", "PLUS").center().x, YB2)], 2)
# --- out: Q2 collector (top) -> TM1 -> Lc right lead; branches to RP (right pin) and Cout (bottom plate)
rect("Metal1", q2c.left, q2c.bottom, q2c.right, q2c.top + 5.0)
vo = (q2c.right - 3.0, q2c.top + 3.8); via(*vo, "Metal1", "TopMetal1")
rect("TopMetal1", lcB.left, YOUT := 224.5 - 1.5, lcB.right, lcB.bottom)
wire("TopMetal1", [vo, (vo[0], 224.5), (lcB.center().x, 224.5)], 4)
rpl, rpr = ends("RP")
via(rpr.center().x, rpr.center().y, "Metal1", "TopMetal1")
vco = (com.left - 3.0, com.center().y); via(*vco, "Metal5", "TopMetal1")
wire("TopMetal1", [(vo[0], 224.5), (vco[0], 224.5), vco], 3)
wire("Metal5", [vco, (com.center().x, com.center().y)], 2)
# --- VCC: Lc left lead -> TM1 stub (with RP's left pin) -> via -> TM2 trunk right -> up the gap -> Cdec1/2
rect("TopMetal1", lcA.left, 211.0, lcA.right, lcA.bottom)
via(rpl.center().x, rpl.center().y, "Metal1", "TopMetal1")
vvc = (lcA.center().x, 213.0); via(*vvc, "TopMetal1", "TopMetal2")
XV = 162.5
wire("TopMetal2", [vvc, (XV, vvc[1]), (XV, 290)], 5)
for k in ("Cdec1", "Cdec2"):
    p = pin(k, "PLUS"); v = (XV, p.center().y + 6); via(*v, "TopMetal1", "TopMetal2")
    wire("TopMetal1", [v, (p.center().x, v[1]), (p.center().x, p.center().y)], 2)
# --- LNA -> mixer link: Cout PLUS -> via -> TM2 up the gap beside Lc (to the mixer input, wired with the mixer)
vlk = (cop.right + 3.5, cop.center().y); via(*vlk, "TopMetal1", "TopMetal2")
wire("TopMetal1", [(cop.center().x, cop.center().y), vlk], 3)
XL = 154.5
wire("TopMetal2", [vlk, (XL, vlk[1]), (XL, 378)], 5)
LINK_END = (XL, 376)
# ======================= stage A: LNA bias mirror, cascode bias, taps, VCC rail, IREF port =======================
XR = 279.0                                                    # VCC rail (TM2) along the tile's right edge
wire("TopMetal2", [(XR, 75), (XR, 545)], 5, end_ext=0)
qrb, qrc, qre = pin("Qr", "B"), pin("Qr", "C"), pin("Qr", "E")
qfb, qfc, qfe = pin("Qf", "B"), pin("Qf", "C"), pin("Qf", "E")
rref0, rref1 = ends("Rref"); rief0, rief1 = ends("Rief"); rb0, rb1 = ends("Rb")
cbp, cbm = pin("Cbn", "PLUS"), pin("Cbn", "MINUS")
# cr: Qr collector (top) + Qf base (bottom) + IREF port (Metal3 to the bottom edge)
rect("Metal1", qrc.left, qrc.bottom, qrc.right, 76.0)
wire("Metal1", [(qrc.center().x, 75.5), (196.0, 75.5), (196.0, 65.5), (qfb.center().x, 65.5)], 1.0)
rect("Metal1", qfb.left, 65.0, qfb.right, qfb.top)
via(190.0, 75.5, "Metal1", "Metal3")
wire("Metal3", [(190.0, 75.5), (240.0, 75.5), (240.0, 4.0)], 1.5)
via(240.0, 4.0, "Metal3", "TopMetal2"); wire("TopMetal2", [(240.0, 4.0), (240.0, 0)], 4, end_ext=0); B.text("IREF", 240.0, 1.5)
# br: Qr base (bottom) -> Metal2 -> Rref bottom
rect("Metal1", qrb.left, 62.0, qrb.right, qrb.top); via(qrb.center().x, 63.0, "Metal1", "Metal2")
via(rref0.center().x, 63.0, "Metal1", "Metal2"); rect("Metal1", rref0.left, rref0.bottom, rref0.right, 63.5)
wire("Metal2", [(qrb.center().x, 63.0), (rref0.center().x, 63.0)], 1.0)
# Qr emitter -> ground (escape left)
rect("Metal2", qre.left - 6.5, qre.bottom, qre.right, qre.top); gnd_via(qre.left - 5.0, qre.center().y, "Metal2")
# vbn: Metal2 bus at y=95 - Qf emitter, Rref top, Rief top, Rb bottom, Cbn top plate
YV = 95.0
rect("Metal2", qfe.left, qfe.bottom, qfe.right + 6.0, qfe.top)
wire("Metal2", [(qfe.right + 5.0, qfe.center().y), (qfe.right + 5.0, YV)], 1.2)
via(rref1.center().x, rref1.center().y, "Metal1", "Metal2"); wire("Metal2", [(rref1.center().x, rref1.center().y), (rref1.center().x, YV)], 1.0)
via(rief1.center().x, rief1.center().y, "Metal1", "Metal2"); wire("Metal2", [(rief1.center().x, rief1.center().y), (rief1.center().x, YV)], 1.0)
via(rb0.center().x, rb0.center().y, "Metal1", "Metal2")
wire("Metal2", [(rb0.center().x, rb0.center().y), (rb0.center().x + 5.5, rb0.center().y), (rb0.center().x + 5.5, YV)], 1.0)
vcb = (cbp.left - 3.5, cbp.center().y); via(*vcb, "Metal2", "TopMetal1")
wire("TopMetal1", [(cbp.center().x, cbp.center().y), vcb], 2)
wire("Metal2", [vcb, (vcb[0], YV), (rb0.center().x + 5.5, YV)], 1.0)
# Rief bottom, Cbn bottom plate -> ground
wire("Metal1", [(rief0.center().x, rief0.center().y), (rief0.center().x, 57.0)], 1.0); gnd_via(rief0.center().x, 57.0, "Metal1")
g = (cbm.right + 3.0, cbm.center().y); gnd_via(*g, "Metal5"); wire("Metal5", [(cbm.center().x, cbm.center().y), g], 2)
# Qf collector -> VCC (TM2 branch from the rail)
rect("Metal1", qfc.left, qfc.bottom, qfc.right, 81.0); via(qfc.center().x, 80.0, "Metal1", "TopMetal2")
wire("TopMetal2", [(qfc.center().x, 80.0), (XR, 80.0)], 4)
# b1 feed: Rb top -> Metal3 -> Q1 base bar (from the right)
via(rb1.center().x, rb1.center().y, "Metal1", "Metal3")
wire("Metal3", [(rb1.center().x, rb1.center().y), (rb1.center().x, 164.5), (q1b.right - 1.5, 164.5), (q1b.right - 1.5, q1b.bottom - 4.0)], 1.0)
via(q1b.right - 1.5, q1b.bottom - 4.0, "Metal1", "Metal3")
# cascode bias: b2 bus -> R1 bottom, R2 bottom; R1 top -> VCC; R2 top -> ground
r10, r11 = ends("R1"); r20, r21 = ends("R2")
wire("Metal3", [(pin("Ccas2", "PLUS").center().x, YB2), (r20.center().x, YB2)], 2)
for r in (r10, r20):
    via(r.center().x, r.center().y, "Metal1", "Metal3"); wire("Metal3", [(r.center().x, YB2), (r.center().x, r.center().y)], 1.0)
via(r11.center().x, r11.center().y + 1.0, "Metal1", "TopMetal2"); rect("Metal1", r11.left, r11.bottom, r11.right, r11.top + 1.6)
wire("TopMetal2", [(r11.center().x, r11.center().y + 1.0), (XR, r11.center().y + 1.0)], 4)
gnd_via(r21.center().x, r21.center().y + 2.0, "Metal1"); rect("Metal1", r21.left, r21.bottom, r21.right, r21.top + 2.6)
# substrate taps -> ground
for i in range(5):
    t = pins_of(f"ptap{i}", 8)[0]; gnd_via(t.center().x, t.center().y, "Metal1")
# VCC trunk (from Lc) joins the rail
wire("TopMetal2", [(XV, 290.0), (XV, 292.0), (XR, 292.0)], 5)
# ======================= stage B: mixer =======================
q3b, q3c, q3e = pin("Q3", "B"), pin("Q3", "C"), pin("Q3", "E")
q4b, q4c, q4e = pin("Q4", "B"), pin("Q4", "C"), pin("Q4", "E")
q5b, q5c, q5e = pin("Q5", "B"), pin("Q5", "C"), pin("Q5", "E")
rt0, rt1 = ends("Rt"); re0, re1 = ends("Re"); rl10, rl11 = ends("Rl1"); rl20, rl21 = ends("Rl2")
rlp0, rlp1 = ends("RLp"); rln0, rln1 = ends("RLn"); rrf0, rrf1 = ends("Rrf"); rer0, rer1 = ends("Rerf")
rd10, rd11 = ends("Rd1"); rd20, rd21 = ends("Rd2")
qrfb, qrfc, qrfe = pin("Qrf", "B"), pin("Qrf", "C"), pin("Qrf", "E")
# link (Cout's top plate) -> straight to the mixer input b3: TM2 up, via, TM1 across, via down to the Q3 base pad
# (no separate mixer DC block: Cout already blocks DC; two series caps would leave a floating node)
wire("TopMetal2", [LINK_END, (XL, 400.5)], 5)
via(XL, 400.5, "TopMetal1", "TopMetal2")
vb3m = (217.6, 400.5); via(*vb3m, "Metal1", "TopMetal1")
wire("TopMetal1", [(XL, 400.5), vb3m], 3)
rect("Metal1", vb3m[0] - 1.05, rt1.bottom, vb3m[0] + 1.05, vb3m[1] + 1.1)
rect("Metal1", vb3m[0] - 1.05, rt1.bottom, q3b.right, q3b.top)
# vb3: Rt bottom -> Metal2 -> Cb3 top plate, Qrf (diode), Rrf bottom
via(rt0.center().x, rt0.center().y, "Metal1", "Metal2")
XU = 262.0
wire("Metal2", [(rt0.center().x, rt0.center().y), (rt0.center().x, 372.0), (XU, 372.0), (XU, rrf0.center().y)], 1.5)
cb3p, cb3m = pin("Cb3", "PLUS"), pin("Cb3", "MINUS")
v = (cb3p.center().x, 343.0); via(*v, "Metal2", "TopMetal1")
wire("Metal2", [(rt0.center().x, 372.0), (rt0.center().x, 346.0), (v[0], 346.0), v], 1.5)
wire("TopMetal1", [v, (cb3p.center().x, cb3p.center().y)], 2)
rect("Metal1", qrfb.left, qrfb.bottom - 4.2, qrfb.right, qrfb.top); via(qrfb.center().x, qrfb.bottom - 3.5, "Metal1", "Metal2")
rect("Metal1", qrfc.left, qrfc.bottom, qrfc.right, qrfc.top + 4.0); via(qrfc.center().x, qrfc.top + 3.2, "Metal1", "Metal2")
wire("Metal2", [(qrfc.center().x, qrfc.top + 3.2), (XU, qrfc.top + 3.2)], 1.0)
wire("Metal2", [(qrfb.center().x, qrfb.bottom - 3.5), (XU, qrfb.bottom - 3.5)], 1.0)
wire("Metal1", [(rrf0.center().x, rrf0.center().y), (XU, rrf0.center().y)], 1.0); via(XU, rrf0.center().y, "Metal1", "Metal2")
# Qrf emitter -> Rerf top; Rerf bottom -> ground; Rrf top -> VCC rail; Cb3 bottom plate -> ground
XE = 270.5
rect("Metal2", qrfe.left, qrfe.bottom, XE + 0.5, qrfe.top)
via(rer1.center().x, rer1.center().y, "Metal1", "Metal2")
wire("Metal2", [(XE, qrfe.center().y), (XE, rer1.center().y), (rer1.center().x, rer1.center().y)], 1.0)
wire("Metal1", [(rer0.center().x, rer0.center().y), (rer0.center().x, 295.5)], 1.0); gnd_via(rer0.center().x, 295.5, "Metal1")
rect("Metal1", rrf1.left, rrf1.bottom, XR + 1.0, rrf1.top + 2.6); via(XR, rrf1.center().y + 1.6, "Metal1", "TopMetal2")
g = (cb3m.right + 3.0, cb3m.center().y); gnd_via(*g, "Metal5"); wire("Metal5", [(cb3m.center().x, cb3m.center().y), g], 2)
# Q3 emitter -> Re -> ground
rect("Metal2", q3e.left, q3e.bottom, re1.center().x + 0.6, q3e.top)
via(re1.center().x, re1.center().y, "Metal1", "Metal2"); rect("Metal2", re1.center().x - 0.6, re1.center().y - 0.6, re1.center().x + 0.6, q3e.top)
wire("Metal1", [(re0.center().x, re0.center().y), (re0.center().x, 378.5)], 1.0); gnd_via(re0.center().x, 378.5, "Metal1")
# x node: Q3 collector -> Metal2 -> Q4/Q5 emitters
rect("Metal1", q3c.left, q3c.bottom, q3c.right, q3c.top + 5.0); vx = (q3c.left + 3.7, q3c.top + 4.0); via(*vx, "Metal1", "Metal2")
XN = 238.5
wire("Metal2", [vx, (XN, vx[1]), (XN, q4e.center().y)], 1.5)
rect("Metal2", q4e.left, q4e.bottom, q5e.right, q5e.top)
# LO-port bias: base pads (Metal1) join Q4/Q5 bases with Rl1/Rl2 tops; lop/lon from the coupling caps on Metal5
rect("Metal1", rl11.left - 0.5, rl11.bottom, q4b.right, q4b.top)
rect("Metal1", q5b.left, rl21.bottom, 267.0, q5b.top)
for cc, xv in (("Cc1", 224.5), ("Cc2", 265.5)):
    m = pin(cc, "MINUS")
    via(xv, 418.0, "Metal1", "Metal5"); wire("Metal5", [(m.center().x, m.center().y), (m.center().x, 430.0), (xv, 430.0), (xv, 418.0)], 2)
# vlo: Metal3 bus - Rl1/Rl2 bottoms, Rd1 bottom, Rd2 top, Cvl top plate
YL = 404.0; XLV = 236.0
for r in (rl10, rl20): via(r.center().x, r.center().y, "Metal1", "Metal3")
wire("Metal3", [(rl10.center().x, rl10.center().y), (rl20.center().x, rl20.center().y)], 1.0)
wire("Metal3", [(XLV, rl10.center().y), (XLV, rd10.center().y), (rd10.center().x, rd10.center().y)], 1.0)
via(rd10.center().x, rd10.center().y, "Metal1", "Metal3")
via(rd21.center().x, rd21.center().y, "Metal1", "Metal3"); wire("Metal3", [(XLV, rd21.center().y), (rd21.center().x, rd21.center().y)], 1.0)
cvp, cvm = pin("Cvl", "PLUS"), pin("Cvl", "MINUS")
vcv = (cvp.left - 3.0, cvp.center().y); via(*vcv, "Metal3", "TopMetal1")
wire("TopMetal1", [vcv, (cvp.center().x, cvp.center().y)], 2)
wire("Metal3", [vcv, (XLV, vcv[1])], 1.0)
# Rd1 top -> VCC (TM2 branch); Rd2 bottom -> ground; Cvl bottom plate -> ground
rect("Metal1", rd11.left, rd11.bottom, rd11.right, rd11.top + 1.6); via(rd11.center().x, rd11.center().y + 1.0, "Metal1", "TopMetal2")
wire("TopMetal2", [(rd11.center().x, rd11.center().y + 1.0), (XR, rd11.center().y + 1.0)], 4)
wire("Metal1", [(rd20.center().x, rd20.center().y), (rd20.center().x, 340.0)], 1.0); gnd_via(rd20.center().x, 340.0, "Metal1")
wire("Metal5", [(cvm.center().x, cvm.center().y), (cvm.center().x, 357.0)], 2); gnd_via(cvm.center().x, 357.0, "Metal5")
# IF: collectors -> IF loads (beside) -> VCC bus; IF+ on Metal3, IF- on Metal2 -> IF caps (bottom plates) and top ports
rect("Metal1", q4c.left, q4c.bottom, q4c.right, 446.0); rect("Metal1", q4c.right - 0.5, rlp0.bottom, rlp0.right, rlp0.top)
rect("Metal1", q5c.left, q5c.bottom, q5c.right, 452.0); rect("Metal1", q5c.right - 0.5, rln0.bottom, rln0.right, rln0.top)
YVB = 440.0
wire("TopMetal2", [(XR, YVB), (37.0, YVB)], 4)
for r in (rlp1, rln1):
    rect("Metal1", r.left, r.bottom, r.right, YVB + 1.0); via(r.center().x, YVB, "Metal1", "TopMetal2")
clp_t, cln_t = pins_of("CLp", 126)[0], pins_of("CLn", 126)[0]
clp_b, cln_b = pins_of("CLp", 67)[0], pins_of("CLn", 67)[0]
for t in (clp_t, cln_t):
    x = t.center().x; via(x, 400.0, "TopMetal1", "TopMetal2"); wire("TopMetal2", [(x, YVB), (x, 400.0)], 4)
via(q4c.center().x, 445.0, "Metal1", "Metal3")
wire("Metal3", [(q4c.center().x, 445.0), (2.5, 445.0), (2.5, 541.5)], 1.5)
wire("Metal3", [(clp_b.right + 2.6, 445.0), (clp_b.right + 2.6, 400.0)], 1.5)
via(clp_b.right + 2.6, 400.0, "Metal3", "Metal5"); wire("Metal5", [(clp_b.right - 0.3, 400.0), (clp_b.right + 2.6, 400.0)], 2)
via(2.5, 541.5, "Metal3", "TopMetal2"); wire("TopMetal2", [(2.5, 541.5), (2.5, 545.0)], 4, end_ext=0); B.text("IFP", 2.5, 544)
via(q5c.center().x, 451.5, "Metal1", "Metal2")
XIN = 100.0
wire("Metal2", [(q5c.center().x, 451.5), (XIN, 451.5)], 1.0)
wire("Metal2", [(XIN, 400.0), (XIN, 541.5)], 1.0)
via(XIN, 400.0, "Metal2", "Metal5"); wire("Metal5", [(cln_b.right - 0.3, 400.0), (XIN, 400.0)], 2)
via(XIN, 541.5, "Metal2", "TopMetal2"); wire("TopMetal2", [(XIN, 541.5), (XIN, 545.0)], 4, end_ext=0); B.text("IFN", XIN, 544)
B.text("VCC", XR, 544)
# ======================= stage C: channel LO driver + LO ports =======================
qab, qac, qae = pin("Qa", "B"), pin("Qa", "C"), pin("Qa", "E")
qbb, qbc, qbe = pin("Qb", "B"), pin("Qb", "C"), pin("Qb", "E")
c1p, c2p = pin("Cc1", "PLUS"), pin("Cc2", "PLUS")
ci1p, ci1m, ci2p, ci2m = pin("Ci1", "PLUS"), pin("Ci1", "MINUS"), pin("Ci2", "PLUS"), pin("Ci2", "MINUS")
rv10, rv11 = ends("Rv1"); rv20, rv21 = ends("Rv2"); rb10, rb11 = ends("Rb1"); rb20, rb21 = ends("Rb2")
rta0, rta1 = ends("Rtail"); rd10_, rd11_ = ends("RD1"); rd20_, rd21_ = ends("RD2")
YVD = 487.0                                                     # driver VCC bus (TM2) from the rail
wire("TopMetal2", [(XR, YVD), (rv10.center().x, YVD), (rv10.center().x, rv10.center().y)], 4)
via(rv10.center().x, rv10.center().y, "Metal1", "TopMetal2")
for (qc, cp, r0, r1) in ((qac, c1p, rd10_, rd11_), (qbc, c2p, rd20_, rd21_)):
    # collector pad (pulled down) joins the load resistor's top pin; via down to the coupling cap's top plate
    rect("Metal1", r1.left, r1.bottom - 0.3, qc.right, qc.top)
    vd = (cp.center().x, 490.0); via(*vd, "Metal1", "TopMetal1"); rect("TopMetal1", cp.left, cp.bottom, cp.right, vd[1] + 1.05)
    via(r0.center().x, r0.center().y - 0.2, "Metal1", "TopMetal2")                       # load resistor bottom -> VCC bus
for (qb_, cim_, rbb) in ((qab, ci1m, rb10), (qbb, ci2m, rb20)):
    # base pad (pulled up) joins the input cap's bottom plate and the base-bias resistor
    rect("Metal1", qb_.left, qb_.bottom, ci1m.right if qb_ is qab else ci2m.right, 501.6)
    vb_ = (cim_.center().x, 500.5); via(*vb_, "Metal1", "Metal5"); wire("Metal5", [(cim_.center().x, cim_.center().y), vb_], 2)
    wire("Metal1", [(rbb.center().x, rbb.center().y), (rbb.center().x, 497.5), (qb_.left + 0.5, 497.5)], 1.0)
# emitters joined (Metal2) -> tail resistor -> ground
rect("Metal2", qae.left, qae.bottom, qbe.right, qae.top)
rect("Metal1", rta1.left, rta1.bottom, rta1.right, qae.center().y + 0.8); via(rta1.center().x, qae.center().y, "Metal1", "Metal2")
wire("Metal1", [(rta0.center().x, rta0.center().y), (rta0.center().x, 482.5)], 1.0); gnd_via(rta0.center().x, 482.5, "Metal1")
# vbd: Metal2 bus at y=519 - Rv1/Rv2/Rb1/Rb2 tops, Cvb top plate; Rv2 bottom -> ground; Cvb bottom plate -> ground
YBD = 519.0
for r in (rv11, rv21, rb11, rb21):
    rect("Metal1", r.left, r.bottom, r.right, YBD + 0.6); via(r.center().x, YBD, "Metal1", "Metal2")
cvbp, cvbm = pin("Cvb", "PLUS"), pin("Cvb", "MINUS")
vcvb = (cvbp.left - 3.0, cvbp.center().y); via(*vcvb, "Metal2", "TopMetal1"); wire("TopMetal1", [vcvb, (cvbp.center().x, cvbp.center().y)], 2)
wire("Metal2", [vcvb, (vcvb[0], YBD), (rb21.center().x, YBD)], 1.0)
wire("Metal1", [(rv20.center().x, rv20.center().y), (rv20.center().x, 490.0)], 1.0); gnd_via(rv20.center().x, 490.0, "Metal1")
g = (cvbm.right + 3.0, cvbm.center().y); gnd_via(*g, "Metal5"); wire("Metal5", [(cvbm.center().x, cvbm.center().y), g], 2)
# LO ports: input caps' top plates -> TM2 stubs at the top edge
for cp, name in ((ci1p, "LOP"), (ci2p, "LON")):
    x = cp.center().x; rect("TopMetal1", cp.left, cp.bottom, cp.right, 542.6); via(x, 541.5, "TopMetal1", "TopMetal2")
    wire("TopMetal2", [(x, 541.5), (x, 545.0)], 4, end_ext=0); B.text(name, x, 544)
# ======================= decap bottom plates + MIM substrate rings (TIE) -> ground =======================
for k in ("Ccas1", "Ccas2", "Cdec1", "Cdec2"):
    m = pin(k, "MINUS"); g = (m.right + 3.0, m.center().y); gnd_via(*g, "Metal5"); wire("Metal5", [(m.center().x, m.center().y), g], 2)
RFMIMS = [k for k, inst in B.DEV.items() if B.ly.cell(inst.cell_index).name.startswith("rfcmim")]
SIGNAL_MIMS = ("Cin", "Cout", "Cc1", "Cc2")
for k in RFMIMS:
    t = pin(k, "TIE"); c = B.DEV[k].dbbox().center(); tc = t.center()
    if k in SIGNAL_MIMS:            # ring sits in a plane cut-out: strap out (shortest direction that ends on real plane)
        cut = B.DEV[k].dbbox().enlarged(3.0, 3.0)
        blocked = [B.DEV[q].dbbox() for q in ("Lb", "Lc")] + [B.DEV[q].dbbox().enlarged(3.0, 3.0) for q in SIGNAL_MIMS]
        best = None
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            d = {(1, 0): cut.right - tc.x, (-1, 0): tc.x - cut.left, (0, 1): cut.top - tc.y, (0, -1): tc.y - cut.bottom}[(dx, dy)] + 6.0
            ex, ey = tc.x + dx * d, tc.y + dy * d
            if not (3 < ex < 287 and 3 < ey < 545): continue
            if any(bb.contains(pya.DPoint(ex, ey)) for bb in blocked): continue
            if best is None or d < best[0]: best = (d, dx, dy)
        d, dx, dy = best
        if dx: patch = (min(tc.x, tc.x + dx * d), tc.y - 3, max(tc.x, tc.x + dx * d), tc.y + 3)
        else: patch = (tc.x - 3, min(tc.y, tc.y + dy * d), tc.x + 3, max(tc.y, tc.y + dy * d))
        gnd_via(tc.x, tc.y, "Metal1", patch=patch)
    else:
        gnd_via(tc.x, tc.y, "Metal1")
# GND label on the Metal4 plane (Metal4 text layer)
B.text("GND", 6, 520, gds=(50, 25))
# ======================= ground plane + checks =======================
B.ground_plane((0, 0, 290, 548), hole_keys=("Lb", "Lc"), signal_mim_keys=("Cin", "Cout", "Cc1", "Cc2"))
P = {"RFIN": ("TopMetal2", (vrf[0], 1)), "Cin MINUS": ("Metal5", cim.center()), "Cin PLUS": ("TopMetal1", cip.center()),
     "Lb left (in)": ("TopMetal1", lbB.center()), "Lb right (b1)": ("TopMetal1", lbA.center()), "Q1 B": ("Metal1", q1b.center()),
     "Q1 E": ("Metal2", q1e.center()), "GND plane": ("Metal4", (5, 520)), "Q1 C": ("Metal1", q1c.center()), "Q2 E": ("Metal2", q2e.center()),
     "Q2 B": ("Metal1", q2b.center()), "Ccas1 +": ("TopMetal1", pin("Ccas1", "PLUS").center()), "Ccas2 +": ("TopMetal1", pin("Ccas2", "PLUS").center()),
     "Q2 C": ("Metal1", q2c.center()), "Lc right (out)": ("TopMetal1", lcB.center()), "Lc left (VCC)": ("TopMetal1", lcA.center()),
     "RP right": ("Metal1", rpr.center()), "RP left": ("Metal1", rpl.center()), "Cout MINUS": ("Metal5", com.center()),
     "Cdec1 +": ("TopMetal1", pin("Cdec1", "PLUS").center()), "Cdec2 +": ("TopMetal1", pin("Cdec2", "PLUS").center()),
     "Cout PLUS": ("TopMetal1", cop.center()), "link end": ("TopMetal2", LINK_END),
     "IREF": ("TopMetal2", (240, 1)), "Qr C": ("Metal1", qrc.center()), "Qf B": ("Metal1", qfb.center()), "Qr B": ("Metal1", qrb.center()),
     "Rref bot": ("Metal1", rref0.center()), "Rref top": ("Metal1", rref1.center()), "Qf E": ("Metal2", qfe.center()),
     "Rief top": ("Metal1", rief1.center()), "Rief bot": ("Metal1", rief0.center()), "Rb bot": ("Metal1", rb0.center()), "Rb top": ("Metal1", rb1.center()),
     "Cbn +": ("TopMetal1", cbp.center()), "Cbn -": ("Metal5", cbm.center()), "Qr E": ("Metal2", qre.center()), "Qf C": ("Metal1", qfc.center()),
     "R1 bot": ("Metal1", r10.center()), "R1 top": ("Metal1", r11.center()), "R2 bot": ("Metal1", r20.center()), "R2 top": ("Metal1", r21.center()),
     "VCC rail": ("TopMetal2", (XR, 500)), "Q3 B": ("Metal1", q3b.center()), "Rt top": ("Metal1", rt1.center()), "Rt bot": ("Metal1", rt0.center()),
     "Cb3 +": ("TopMetal1", cb3p.center()), "Cb3 -": ("Metal5", cb3m.center()), "Qrf B": ("Metal1", qrfb.center()), "Qrf C": ("Metal1", qrfc.center()),
     "Rrf bot": ("Metal1", rrf0.center()), "Rrf top": ("Metal1", rrf1.center()), "Qrf E": ("Metal2", qrfe.center()),
     "Rerf top": ("Metal1", rer1.center()), "Rerf bot": ("Metal1", rer0.center()), "Q3 E": ("Metal2", q3e.center()),
     "Re top": ("Metal1", re1.center()), "Re bot": ("Metal1", re0.center()), "Q3 C": ("Metal1", q3c.center()),
     "Q4 E": ("Metal2", q4e.center()), "Q5 E": ("Metal2", q5e.center()), "Q4 B": ("Metal1", q4b.center()), "Q5 B": ("Metal1", q5b.center()),
     "Rl1 top": ("Metal1", rl11.center()), "Rl2 top": ("Metal1", rl21.center()), "Cc1 -": ("Metal5", pin("Cc1", "MINUS").center()),
     "Cc2 -": ("Metal5", pin("Cc2", "MINUS").center()), "Rl1 bot": ("Metal1", rl10.center()), "Rl2 bot": ("Metal1", rl20.center()),
     "Rd1 bot": ("Metal1", rd10.center()), "Rd2 top": ("Metal1", rd21.center()), "Cvl +": ("TopMetal1", cvp.center()),
     "Rd1 top": ("Metal1", rd11.center()), "Rd2 bot": ("Metal1", rd20.center()), "Cvl -": ("Metal5", cvm.center()),
     "Q4 C": ("Metal1", q4c.center()), "RLp bot": ("Metal1", rlp0.center()), "CLp bottom": ("Metal5", (clp_b.left + 0.3, clp_b.center().y)),
     "IFP": ("TopMetal2", (2.5, 544.5)), "Q5 C": ("Metal1", q5c.center()), "RLn bot": ("Metal1", rln0.center()),
     "CLn bottom": ("Metal5", (cln_b.left + 0.3, cln_b.center().y)), "IFN": ("TopMetal2", (XIN, 544.5)),
     "RLp top": ("Metal1", rlp1.center()), "RLn top": ("Metal1", rln1.center()), "CLp top": ("TopMetal1", clp_t.center()), "CLn top": ("TopMetal1", cln_t.center()),
     "Qa C": ("Metal1", qac.center()), "Qb C": ("Metal1", qbc.center()), "Cc1 +": ("TopMetal1", c1p.center()), "Cc2 +": ("TopMetal1", c2p.center()),
     "RD1 top": ("Metal1", rd11_.center()), "RD2 top": ("Metal1", rd21_.center()), "RD1 bot": ("Metal1", rd10_.center()), "RD2 bot": ("Metal1", rd20_.center()),
     "Qa B": ("Metal1", qab.center()), "Qb B": ("Metal1", qbb.center()), "Ci1 -": ("Metal5", ci1m.center()), "Ci2 -": ("Metal5", ci2m.center()),
     "Rb1 bot": ("Metal1", rb10.center()), "Rb2 bot": ("Metal1", rb20.center()), "Qa E": ("Metal2", qae.center()), "Qb E": ("Metal2", qbe.center()),
     "Rtail top": ("Metal1", rta1.center()), "Rtail bot": ("Metal1", rta0.center()), "Rv1 top": ("Metal1", rv11.center()), "Rv2 top": ("Metal1", rv21.center()),
     "Rb1 top": ("Metal1", rb11.center()), "Rb2 top": ("Metal1", rb21.center()), "Cvb +": ("TopMetal1", cvbp.center()), "Rv1 bot": ("Metal1", rv10.center()),
     "Rv2 bot": ("Metal1", rv20.center()), "Cvb -": ("Metal5", cvbm.center()), "LOP": ("TopMetal2", (ci1p.center().x, 544.5)), "LON": ("TopMetal2", (ci2p.center().x, 544.5)),
     "Ci1 +": ("TopMetal1", ci1p.center()), "Ci2 +": ("TopMetal1", ci2p.center()),
     **{f"{k} TIE": ("Metal1", pin(k, "TIE").center()) for k in RFMIMS},
     **{f"{k} -": ("Metal5", pin(k, "MINUS").center()) for k in ("Ccas1", "Ccas2", "Cdec1", "Cdec2")},
     **{f"ptap{i}": ("Metal1", pins_of(f"ptap{i}", 8)[0].center()) for i in range(5)}}
G_ = [["RFIN", "Cin MINUS"], ["Cin PLUS", "Lb left (in)", "Lb right (b1)", "Q1 B", "Rb top"],
      ["Q1 E", "GND plane", "Qr E", "Rief bot", "Cbn -", "R2 top", "Rerf bot", "Cb3 -", "Re bot", "Rd2 bot", "Cvl -", "Rtail bot", "Rv2 bot", "Cvb -"] + [f"{k} TIE" for k in RFMIMS] + [f"{k} -" for k in ("Ccas1", "Ccas2", "Cdec1", "Cdec2")] + [f"ptap{i}" for i in range(5)], ["Q1 C", "Q2 E"],
      ["Q2 B", "Ccas1 +", "Ccas2 +", "R1 bot", "R2 bot"],
      ["Q2 C", "Lc right (out)", "Lc left (VCC)", "RP right", "RP left", "Cout MINUS", "Cdec1 +", "Cdec2 +", "VCC rail", "Qf C", "R1 top", "Rrf top", "Rd1 top", "RLp top", "RLn top", "CLp top", "CLn top", "RD1 bot", "RD2 bot", "Rv1 bot"],
      ["Cout PLUS", "link end", "Q3 B", "Rt top"], ["Rt bot", "Cb3 +", "Qrf B", "Qrf C", "Rrf bot"],
      ["Qrf E", "Rerf top"], ["Q3 E", "Re top"], ["Q3 C", "Q4 E", "Q5 E"], ["Q4 B", "Rl1 top", "Cc1 -"], ["Q5 B", "Rl2 top", "Cc2 -"],
      ["Rl1 bot", "Rl2 bot", "Rd1 bot", "Rd2 top", "Cvl +"], ["Q4 C", "RLp bot", "CLp bottom", "IFP"], ["Q5 C", "RLn bot", "CLn bottom", "IFN"],
      ["Qa C", "Cc1 +", "RD1 top"], ["Qb C", "Cc2 +", "RD2 top"], ["Qa B", "Ci1 -", "Rb1 bot"], ["Qb B", "Ci2 -", "Rb2 bot"],
      ["Qa E", "Qb E", "Rtail top"], ["Rv1 top", "Rv2 top", "Rb1 top", "Rb2 top", "Cvb +"], ["LOP", "Ci1 +"], ["LON", "Ci2 +"],
      ["IREF", "Qr C", "Qf B"], ["Qr B", "Rref bot"], ["Qf E", "Rref top", "Rief top", "Rb bot", "Cbn +"]]
if __name__ == "__main__":
    B.connectivity(P, G_); B.mini_drc(); B.foreign_in_inductors(); B.floating_metal()
    B.write("rx_tile.gds")
