"""
lna_gen.py - layout generator for the 24 GHz LNA test cell (IHP SG13G2).
v3b: + bias network (mirror from the Iref pad, cascode bias), substrate contacts. Electrically complete.

All devices are IHP PCells with the parameters of the EM-verified netlist (lna_ind.spice).
Pins are found from the PCells' own labels, so wiring lands exactly on them after rotation.
Coordinates in um; origin at the bottom-left of the cell.
"""
import ihp
pya = ihp.pya

ly = pya.Layout(); ly.dbu = 0.001
top = ly.create_cell("lna")
LY = {n: ly.layer(*v) for n, v in ihp.L.items()}
DEV = {}

GRID = 0.005
def G(v): return round(round(v / GRID) * GRID, 3)          # snap to the 5 nm manufacturing grid
def place(key, name, x, y, rot=0, **params):
    x, y = G(x), G(y)
    if name in ("rppd", "rhigh", "rsil"):
        # IHP resistor PCells default to Calculate='l' (length derived from R). With only w/l given, the GUI
        # callbacks would shrink the resistor to the default R. So: Calculate='R', and store the matching R.
        params = dict(params, Calculate="R")
        probe = ly.cell(ihp.pcell(ly, name, **params))
        for li in ly.layer_indexes():
            for sh in probe.shapes(li).each():
                if sh.is_text() and " r=" in sh.text.string:
                    params["R"] = sh.text.string.split("r=")[1].strip()
    DEV[key] = top.insert(pya.DCellInstArray(ihp.pcell(ly, name, **params), pya.DCplxTrans(1, rot, False, x, y)))

def pin(key, label):
    """Box (um) of the pin shape of instance `key` that carries `label`."""
    inst = DEV[key]; cell = ly.cell(inst.cell_index); tr = inst.dcplx_trans
    pos = None
    for li in ly.layer_indexes():
        si = cell.begin_shapes_rec(li)
        while not si.at_end():
            s = si.shape()
            if s.is_text() and s.text.string.strip() == label:
                pos = si.dtrans() * s.dtext.trans.disp
                break
            si.next()
        if pos: break
    if pos is None: raise KeyError(f"{key}: no label {label}")
    best = None
    for li in ly.layer_indexes():
        if ly.get_info(li).datatype != 2: continue
        si = cell.begin_shapes_rec(li)
        while not si.at_end():
            b = si.shape().dbbox().transformed(si.dtrans())
            if b.contains(pya.DPoint(pos.x, pos.y)) and (best is None or b.area() < best[0].area()):
                best = (b, ly.get_info(li).layer)
            si.next()
    if best is None: raise KeyError(f"{key}: no pin shape under label {label}")
    return best[0].transformed(tr), best[1]

def pins_of(key, gds_layer):
    """All pin boxes (datatype 2) of an instance on one layer, transformed - for PCells without pin labels."""
    inst = DEV[key]; cell = ly.cell(inst.cell_index); li = ly.find_layer(gds_layer, 2); out = []
    if li is None: return out
    for sh in cell.begin_shapes_rec(li).each() if hasattr(cell.begin_shapes_rec(li), "each") else []:
        pass
    si = cell.begin_shapes_rec(li)
    while not si.at_end():
        b = si.shape().dbbox().transformed(si.dtrans()).transformed(inst.dcplx_trans)
        if b not in out: out.append(b)
        si.next()
    return out

GPATCH = []          # small Metal4 patches/straps that tie ground vias to the plane (they also fill slits)
ORDER = ["Metal1", "Metal2", "Metal3", "Metal4", "Metal5", "TopMetal1", "TopMetal2"]
def gnd_via(x, y, layer, patch=None):
    """Via stack from `layer` to the Metal4 ground plane (upwards or downwards), plus a plane patch."""
    if ORDER.index(layer) < 3: via(x, y, layer, "Metal4")
    else: via(x, y, "Metal4", layer)
    GPATCH.append(patch or (x - 3, y - 3, x + 3, y + 3))

def rect(layer, x1, y1, x2, y2):
    x1, y1, x2, y2 = G(x1), G(y1), G(x2), G(y2)
    top.shapes(LY[layer]).insert(pya.DBox(min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2)))
def wire(layer, pts, w, start_ext=None, end_ext=None):
    pts = [pya.DPoint(G(p[0]), G(p[1])) for p in pts]
    top.shapes(LY[layer]).insert(pya.DPath(pts, w, w/2 if start_ext is None else start_ext, w/2 if end_ext is None else end_ext))
VIAS = []
def via(x, y, b, t, n=4, nt=2):
    x, y = G(x), G(y)
    p = dict(b_layer=b, t_layer=t, vn_columns=n, vn_rows=n, vt1_columns=nt, vt1_rows=nt, vt2_columns=nt, vt2_rows=nt)
    top.insert(pya.DCellInstArray(ihp.pcell(ly, "via_stack", **p), pya.DCplxTrans(1, 0, False, x, y)))
    VIAS.append((x, y, b, t))

# ======================= placement =======================
for i, y in enumerate((160, 260, 360)):
    place(f"pin{i}", "bondpad", 50, y, shape="square"); place(f"pout{i}", "bondpad", 650, y, shape="square")
for x, n in zip((170, 280, 390, 500), ("Iref", "GND1", "VCC", "GND2")):
    place(f"p{n}", "bondpad", x, 50, shape="square")
place("Lb", "inductor2", 220, 300, w="7u", s="2.1u", d="68.66u", nr_r=2, subE=False)
place("Lc", "inductor2", 400, 300, w="6.5u", s="2.1u", d="63.15u", nr_r=2, subE=False)
place("Cin", "rfcmim", 190, 285, rot=180, w="33u", l="33u")      # PLUS (TM1) faces Lb, MINUS (M5) faces the pad
place("Q1", "npn13G2", 240, 280, rot=180, Nx=8)                   # base faces up (towards Lb), collector down
place("Q2", "npn13G2", 262, 280, Nx=8)                            # collector up (towards Lc), base down
place("Cout", "rfcmim", 385, 278, rot=180, w="7u", l="7u")        # MINUS (M5) faces the out node, PLUS faces the pad
place("RP", "rppd", 409, 283, rot=90, w="2u", l="2.66u")          # rotated: pins left (out) and right (VCC)
place("Cdec1", "rfcmim", 430, 205, w="33u", l="33u")              # on-chip VCC decoupling (VCC -> GND)
place("Cdec2", "rfcmim", 430, 150, w="33u", l="33u")

# ---- bias mirror (near the Iref pad)                     netlist: Iref->cr, Qr(cr,br,0), Qf(vcc,cr,vbn), Rref(vbn,br),
place("Qr", "npn13G2", 130, 118, Nx=1)                     #          Rief(vbn,0) [was ideal Ief], Rb(vbn,b1), Cbn(vbn,0)
place("Qf", "npn13G2", 155, 118, Nx=1)
place("Rref", "rhigh", 175, 101, w="1u", l="28.12u")
place("Rief", "rhigh", 190, 110, w="1u", l="12.03u")       # replaces the ideal 50 uA Ief sink: 0.86 V / 50 uA ~ 17 kohm
place("Rb", "rppd", 205, 215, w="1u", l="19.08u")
place("Cbn", "rfcmim", 150, 196, rot=180, w="33u", l="33u")  # one MIM (layout space); low-frequency bias bypass only
# ---- cascode bias (below Q2)                               netlist: R1(vcc,b2), R2(b2,0), Ccas1/2(b2,0)
place("Ccas1", "rfcmim", 275, 200, w="33u", l="33u")
place("Ccas2", "rfcmim", 330, 200, w="33u", l="33u")
place("R1", "rppd", 395, 241.5, w="1u", l="22.95u")
place("R2", "rhigh", 405, 226, w="1u", l="13.30u")
# ---- substrate contacts (p+ taps to ground), next to each device group
for i, (x, y) in enumerate(((228, 268), (262, 268), (140, 128), (180, 140), (400, 218))):
    place(f"ptap{i}", "ptap1", x, y, w="2u", l="2u")

# ======================= RF core wiring =======================
# --- RF in: S pad -> Cin MINUS (Metal5)
cm, _ = pin("Cin", "MINUS"); cp, _ = pin("Cin", "PLUS")
wire("TopMetal2", [(90, 260), (cm.center().x - 6, 260), (cm.center().x - 6, cm.center().y)], 10)
via(cm.center().x - 3, cm.center().y, "Metal5", "TopMetal2")
wire("Metal5", [(cm.center().x - 3, cm.center().y), (cm.center().x, cm.center().y)], 3)
# --- in: Cin PLUS (TM1) -> Lb LA lead (TM1)
la, _ = pin("Lb", "LA"); lb, _ = pin("Lb", "LB")
wire("TopMetal1", [(cp.center().x, cp.center().y), (la.center().x, cp.center().y), (la.center().x, la.bottom)], 5, end_ext=0)
# --- b1: Q1 base (M1, top edge after rotation) -> Lb LB lead (TM1)
qb, _ = pin("Q1", "B")
rect("Metal1", qb.left, qb.bottom, qb.right, qb.top + 5.5)                  # base bar pulled up
vb = (qb.center().x, qb.top + 4.2); via(*vb, "Metal1", "TopMetal1")
wire("TopMetal1", [vb, (vb[0], 293), (lb.center().x, 293), (lb.center().x, lb.bottom)], 4, end_ext=0)
# --- e1 + Le: Q1 emitter (M2) -> right -> via to TM2 -> Le strip (47 um) -> ground plane
qe, _ = pin("Q1", "E")
rect("Metal2", qe.right - 1, qe.bottom - 0.5, qe.right + 8, qe.top + 0.5)
ve = (qe.right + 6.5, qe.center().y); via(*ve, "Metal2", "TopMetal2")
LE_W, LE_L = 10, 47
rect("TopMetal2", ve[0] - LE_W/2, ve[1] + 2, ve[0] + LE_W/2, ve[1] + 2 - LE_L)
vg_le = (G(ve[0]), G(ve[1] + 2 - LE_L + 3)); via(*vg_le, "Metal4", "TopMetal2")   # Le ends on the ground plane (Metal4)
# --- c1: Q1 collector (M1, bottom after rotation) -> Metal3 -> Q2 emitter (M2)
qc, _ = pin("Q1", "C"); q2e, _ = pin("Q2", "E")
rect("Metal1", qc.left, qc.bottom - 5.0, qc.right, qc.top)
vc1 = (qc.center().x, qc.bottom - 3.6); via(*vc1, "Metal1", "Metal3")
rect("Metal2", q2e.left - 6, q2e.bottom - 0.5, q2e.left + 1, q2e.top + 0.5)
vc2 = (q2e.left - 4.5, q2e.center().y); via(*vc2, "Metal2", "Metal3")
wire("Metal3", [vc1, (vc2[0], vc1[1]), vc2], 2)
# --- out: Q2 collector (M1, top) -> TM2 -> Lc LA lead (TM1)
q2c, _ = pin("Q2", "C"); lca, _ = pin("Lc", "LA"); lcb, _ = pin("Lc", "LB")
rect("Metal1", q2c.left, q2c.bottom, q2c.right, q2c.top + 6.5)
vo = (q2c.center().x, q2c.top + 4.6); via(*vo, "Metal1", "TopMetal2")
# Lc leads: TopMetal1 stubs that only touch the lead ends; vias stay outside the inductor marker area
rect("TopMetal1", lca.left, lca.bottom - 9.5, lca.right, lca.bottom)
rect("TopMetal1", lcb.left, lcb.bottom - 9.5, lcb.right, lcb.bottom)
vla = (lca.center().x, lca.bottom - 7.0); via(*vla, "TopMetal1", "TopMetal2")
wire("TopMetal2", [vo, (vo[0], 292), (vla[0], 292), vla], 6)
# --- VCC: Lc LB lead (TM1) -> TM2 -> VCC pad
vlb = (lcb.center().x, lcb.bottom - 5.5); via(*vlb, "TopMetal1", "TopMetal2")
wire("TopMetal2", [vlb, (vlb[0] + 12, vlb[1]), (vlb[0] + 12, 110), (390, 110), (390, 90)], 8, start_ext=0)
# --- out node: extend the TM2 out line down next to Lc's lead, for RP and Cout
rect("TopMetal2", vla[0] - 3, 283, vla[0] + 3, 292)
# --- RP (rotated 90): left pin -> out (via up to TM2), right pin -> VCC line (via up to TM2)
rpp = sorted(pins_of("RP", 8), key=lambda b: b.center().x)
vrp_o = (vla[0], 284.0); via(*vrp_o, "Metal1", "TopMetal2")
vrp_v = (vlb[0] + 12, 284.0); via(*vrp_v, "Metal1", "TopMetal2")
wire("Metal1", [(rpp[0].center().x, 284.0), vrp_o], 1.0)
wire("Metal1", [(rpp[-1].center().x, 284.0), vrp_v], 1.0)
# --- Cout: MINUS (M5, left) <- out line (TM2 stub + via down to M5); PLUS (TM1, right) -> RF-out pad
com, _ = pin("Cout", "MINUS"); cop, _ = pin("Cout", "PLUS")
rect("TopMetal2", 365, 283.5, 371, 292)
vco = (368.0, 285.5); via(*vco, "Metal5", "TopMetal2")
wire("Metal5", [vco, (com.center().x, vco[1]), (com.center().x, com.center().y)], 2)
wire("TopMetal1", [(cop.center().x, cop.center().y), (432, cop.center().y)], 5)
vro = (432.0, cop.center().y); via(*vro, "TopMetal1", "TopMetal2")
wire("TopMetal2", [vro, (600, vro[1]), (600, 260), (612, 260)], 10)
# --- VCC decoupling: PLUS (TM1) -> VCC line; MINUS (M5) -> ground plane
for k in ("Cdec1", "Cdec2"):
    dp, _ = pin(k, "PLUS"); dm, _ = pin(k, "MINUS")
    v = (vlb[0] + 12, dp.center().y); via(*v, "TopMetal1", "TopMetal2")
    wire("TopMetal1", [(dp.center().x, dp.center().y), v], 3)
    g = (dm.right + 3, dm.center().y); gnd_via(*g, "Metal5")
    wire("Metal5", [(dm.center().x, dm.center().y), g], 2)
# ======================= bias network wiring =======================
def ends(key):  # (bottom, top) Metal1 pins of an unrotated resistor
    p = sorted(pins_of(key, 8), key=lambda b: b.center().y); return p[0], p[-1]
qrc, _ = pin("Qr", "C"); qrb, _ = pin("Qr", "B"); qre, _ = pin("Qr", "E")
qfc, _ = pin("Qf", "C"); qfb, _ = pin("Qf", "B"); qfe, _ = pin("Qf", "E")
rref0, rref1 = ends("Rref"); rief0, rief1 = ends("Rief"); rb0, rb1 = ends("Rb")
# --- cr: Iref pad -> TM2 riser -> Metal3 bus (y=104) -> Qr collector (top) and Qf base (bottom)
rect("TopMetal2", 165, 88, 175, 106)
via(170, 104, "Metal3", "TopMetal2")
wire("Metal3", [(170, 104), (qrc.center().x, 104)], 1.5)
rect("Metal1", qrc.left, qrc.bottom, qrc.right, qrc.top + 3.0); via(qrc.center().x, qrc.top + 2.2, "Metal1", "Metal3")
wire("Metal3", [(qrc.center().x, 104), (qrc.center().x, qrc.top + 2.2)], 1.5)
rect("Metal1", qfb.left, qfb.bottom - 4.5, qfb.right, qfb.top); via(qfb.center().x, qfb.bottom - 3.8, "Metal1", "Metal3")
wire("Metal3", [(qfb.center().x, 104), (qfb.center().x, qfb.bottom - 3.8)], 1.5)
# --- br: Qr base (bottom) -> Metal1 (y=107) -> Rref bottom
rect("Metal1", qrb.left, qrb.bottom - 10.5, qrb.right, qrb.top)
wire("Metal1", [(qrb.center().x, 107), (rref0.center().x, 107), (rref0.center().x, rref0.center().y)], 1.0)
# --- Qr emitter -> ground
rect("Metal2", qre.left - 6, qre.bottom, qre.right, qre.top); gnd_via(qre.left - 5, qre.center().y, "Metal2")
# --- vbn: Metal2 spine at x=200: Qf emitter, Rref top, Rief top, Cbn top plate, Rb bottom
SP = 200.0
wire("Metal2", [(qfe.center().x, qfe.center().y), (SP, qfe.center().y)], 1.2)
via(rref1.center().x, rref1.center().y, "Metal1", "Metal2"); wire("Metal2", [(rref1.center().x, rref1.center().y), (SP, rref1.center().y)], 1.0)
via(rief1.center().x, rief1.center().y, "Metal1", "Metal2"); wire("Metal2", [(rief1.center().x, rief1.center().y), (SP, rief1.center().y)], 1.0)
cbp, _ = pin("Cbn", "PLUS"); cbm, _ = pin("Cbn", "MINUS")
vcb = (cbp.right + 4.5, cbp.center().y); via(*vcb, "Metal2", "TopMetal1")
wire("TopMetal1", [(cbp.center().x, cbp.center().y), vcb], 3)
wire("Metal2", [vcb, (SP, vcb[1])], 1.0)
via(rb0.center().x, rb0.center().y, "Metal1", "Metal2"); wire("Metal2", [(SP, rb0.center().y), (rb0.center().x, rb0.center().y)], 1.0)
wire("Metal2", [(SP, qfe.center().y), (SP, rb0.center().y)], 1.2)
# --- Rief bottom, Cbn bottom plate -> ground
wire("Metal1", [(rief0.center().x, rief0.center().y), (rief0.center().x, 105)], 1.0); gnd_via(rief0.center().x, 105, "Metal1")
g = (cbm.left - 3, cbm.center().y); gnd_via(*g, "Metal5"); wire("Metal5", [(cbm.center().x, cbm.center().y), g], 2)
# --- b1: Rb top -> Metal1 -> Q1 base bar (from the left, under the 'in' TopMetal1 route)
wire("Metal1", [(rb1.center().x, rb1.center().y), (rb1.center().x, 285.5), (qb.left + 0.5, 285.5)], 1.0)
# --- VCC to Qf collector: TM2 branch from the VCC line (y=110) to Qf
rect("Metal1", qfc.left, qfc.bottom, qfc.right, qfc.top + 5.0); vqf = (qfc.center().x, qfc.top + 4.0); via(*vqf, "Metal1", "TopMetal2")
wire("TopMetal2", [vqf, (vqf[0], 125), (390, 125), (390, 110)], 4)
# --- b2: Q2 base bar down -> Metal1 bus (y=241) -> Ccas top plates, R1 bottom, R2 top
q2b, _ = pin("Q2", "B")
rect("Metal1", q2b.left, q2b.bottom - 6.0, q2b.right, q2b.top)
BUS = 241.0
r10, r11 = ends("R1"); r20, r21 = ends("R2")
wire("Metal1", [(q2b.center().x, q2b.bottom - 5.5), (q2b.center().x, BUS), (r21.center().x + 0.5, BUS)], 1.5)
for k in ("Ccas1", "Ccas2"):
    cp_, _ = pin(k, "PLUS"); cm_, _ = pin(k, "MINUS")
    via(cp_.center().x, BUS, "Metal1", "TopMetal1"); wire("TopMetal1", [(cp_.center().x, BUS), (cp_.center().x, cp_.center().y)], 2)
    g = (cm_.right + 3, cm_.center().y); gnd_via(*g, "Metal5"); wire("Metal5", [(cm_.center().x, cm_.center().y), g], 2)
r10, r11 = ends("R1"); r20, r21 = ends("R2")
wire("Metal1", [(r21.center().x, r21.center().y), (r21.center().x, BUS)], 1.0)
wire("Metal1", [(r20.center().x, r20.center().y), (r20.center().x, 221)], 1.0); gnd_via(r20.center().x, 221, "Metal1")
vr1 = (vlb[0] + 12, r11.center().y); via(*vr1, "Metal1", "TopMetal2")
wire("Metal1", [(r11.center().x, r11.center().y), vr1], 1.0)
# --- substrate contacts -> ground
for i in range(5):
    t = pins_of(f"ptap{i}", 8)[0]; gnd_via(t.center().x, t.center().y, "Metal1")

# --- MIM substrate rings (TIE, Metal1) -> ground
for k in ("Cdec1", "Cdec2", "Ccas1", "Ccas2"):
    t, _ = pin(k, "TIE"); gnd_via(t.center().x, t.center().y, "Metal1")
t, _ = pin("Cbn", "TIE"); gnd_via(t.center().x, t.center().y, "Metal1")
t, _ = pin("Cin", "TIE"); gnd_via(t.center().x, t.center().y, "Metal1", patch=(t.center().x - 3, t.center().y - 3, t.center().x + 3, 297))
t, _ = pin("Cout", "TIE"); gnd_via(t.center().x - 5, t.center().y, "Metal1", patch=(t.center().x - 8, t.center().y - 3, t.center().x - 2, 291))

# ======================= ground plane (Metal4) =======================
plane = pya.Region(pya.Box(0, 0, 700_000, 470_000))
holes = pya.Region()
for k in ("Lb", "Lc"): holes.insert(DEV[k].bbox())                          # inductor keep-outs
for k in ("Cin", "Cout"): holes.insert(DEV[k].bbox().enlarged(3000))        # signal MIMs
for k in ("pin1", "pout1", "pIref", "pVCC"): holes.insert(DEV[k].bbox().enlarged(10000))   # S and DC pads
for k in ("pin0", "pin2", "pout0", "pout2", "pGND1", "pGND2"): holes.insert(DEV[k].bbox().enlarged(4000))  # ground pads: gap...
GVIA = {(G(p[0] + 3), G(p[1] + 3)) for p in GPATCH}                           # (centres of default ground patches)
for (x, y, b, t) in VIAS:                                                   # signal via stacks crossing Metal4
    if t == "Metal4" or b == "Metal4": continue                             # ground vias end on the plane
    order = ["Metal1", "Metal2", "Metal3", "Metal4", "Metal5", "TopMetal1", "TopMetal2"]
    if order.index(b) < 3 < order.index(t) and (G(x), G(y)) != vg_le:
        holes.insert(pya.Box(int(round((x-4)*1000)), int(round((y-4)*1000)), int(round((x+4)*1000)), int(round((y+4)*1000))))
# signal wires on Metal4 / crossing: TM2 out & VCC lines are above Metal4 (no hole needed)
slits = pya.Region()
for xs in range(10_000, 700_000, 20_000):                                   # 3 x 10 um slits on a 20 um grid:
    for ys in range(10_000, 470_000, 20_000):                               # no plane region wider than 30 um (Slt.c)
        slits.insert(pya.Box(xs, ys, xs + 3_000, ys + 10_000))
straps = pya.Region()      # ...then 20 um straps (< 30 um: no slit needed), >= 7 um solid exit from the pad (Pad.fR)
for k in ("pin0", "pin2"):  b = DEV[k].bbox(); straps.insert(pya.Box(b.right - 2000, b.center().y - 10000, b.right + 10000, b.center().y + 10000))
for k in ("pout0", "pout2"): b = DEV[k].bbox(); straps.insert(pya.Box(b.left - 10000, b.center().y - 10000, b.left + 2000, b.center().y + 10000))
for k in ("pGND1", "pGND2"): b = DEV[k].bbox(); straps.insert(pya.Box(b.center().x - 10000, b.top - 2000, b.center().x + 10000, b.top + 10000))
# keep only slits with >= 8 um of plane metal around them: slits must never cut narrow strips into islands
slits = slits.inside((plane - holes).sized(-8000))
patches = pya.Region()
for (x1, y1, x2, y2) in GPATCH: patches.insert(pya.Box(int(round(x1*1000)), int(round(y1*1000)), int(round(x2*1000)), int(round(y2*1000))))
gnd = ((plane - holes - slits) + straps + patches).merged()
# any area still wider than 30 um (e.g. squeezed between cut-outs): add a slit at its centre, repeat until none left
exempt = pya.Region()
for k, inst in DEV.items():
    if k.startswith("p") or k.startswith("C"): exempt.insert(inst.bbox())
for _ in range(10):
    wide = (gnd.sized(-15000).sized(15000) & gnd) - exempt
    if wide.is_empty(): break
    for p in wide.each():
        c = p.bbox().center(); sx, sy = (c.x // 5) * 5, (c.y // 5) * 5
        gnd -= pya.Region(pya.Box(sx - 1500, sy - 5000, sx + 1500, sy + 5000))
    gnd.merge()
# store the plane as simple abutting rectangles instead of one huge keyhole polygon (robust for DRC/LVS tools)
top.shapes(LY["Metal4"]).insert(gnd.decompose_trapezoids_to_region(1))

# ======================= port labels for LVS (TopMetal2 text, 134/25) on the pads =======================
lt = ly.layer(134, 25)
for name, key in (("RFIN", "pin1"), ("RFOUT", "pout1"), ("VCC", "pVCC"), ("IREF", "pIref"), ("GND", "pGND1")):
    c = DEV[key].dbbox().center(); top.shapes(lt).insert(pya.DText(name, c.x, c.y))

# editable version (PCells regenerate from their parameters) ...
ly.write("lna_layout_pcells.gds")
# ... and the delivered version: fixed geometry, exactly what was checked (no regeneration on opening)
# (the inductor PCells' LA/LB labels on IND:text 27/25 must stay: the LVS deck needs them to recognise the inductors)
opt = pya.SaveLayoutOptions(); opt.write_context_info = False
ly.write("lna_layout.gds", opt)
print("wrote lna_layout.gds, cell", top.dbbox())

# ======================= self-check: metal connectivity =======================
def check():
    l2n = pya.LayoutToNetlist(pya.RecursiveShapeIterator(ly, top, []))
    stack = [("Metal1", 8), ("Via1", 19), ("Metal2", 10), ("Via2", 29), ("Metal3", 30), ("Via3", 49), ("Metal4", 50),
             ("Via4", 66), ("Metal5", 67), ("TopVia1", 125), ("TopMetal1", 126), ("TopVia2", 133), ("TopMetal2", 134)]
    R = {n: l2n.make_layer(ly.layer(g, 0), n) for n, g in stack}
    for n in R: l2n.connect(R[n])
    for i in range(0, len(stack) - 2, 2):
        l2n.connect(R[stack[i][0]], R[stack[i+1][0]]); l2n.connect(R[stack[i+1][0]], R[stack[i+2][0]])
    l2n.extract_netlist()
    def net(layer, p):
        n = l2n.probe_net(R[layer], pya.DPoint(p.x, p.y) if hasattr(p, "x") else pya.DPoint(*p))
        return n.cluster_id if n else None
    P = {  # probe name: (layer, point)
        "RF-in pad": ("TopMetal2", (50, 260)), "Cin MINUS": ("Metal5", cm.center()), "Cin PLUS": ("TopMetal1", cp.center()),
        "Lb LA": ("TopMetal1", la.center()), "Lb LB": ("TopMetal1", lb.center()), "Q1 B": ("Metal1", qb.center()),
        "Q1 E": ("Metal2", qe.center()), "Q1 C": ("Metal1", qc.center()), "Q2 E": ("Metal2", q2e.center()),
        "Q2 C": ("Metal1", q2c.center()), "Q2 B": ("Metal1", pin("Q2", "B")[0].center()),
        "Lc LA": ("TopMetal1", lca.center()), "Lc LB": ("TopMetal1", lcb.center()), "VCC pad": ("TopMetal2", (390, 50)),
        "GND plane": ("Metal4", (5, 465)), "G pad in-low": ("TopMetal2", (50, 160)), "G pad in-high": ("TopMetal2", (50, 360)),
        "G pad out-low": ("TopMetal2", (650, 160)), "G pad out-high": ("TopMetal2", (650, 360)),
        "GND pad 1": ("TopMetal2", (280, 50)), "GND pad 2": ("TopMetal2", (500, 50)), "Iref pad": ("TopMetal2", (170, 50)),
        "RF-out pad": ("TopMetal2", (650, 260)), "Cout PLUS": ("TopMetal1", cop.center()), "Cout MINUS": ("Metal5", com.center()),
        "RP left": ("Metal1", rpp[0].center()), "RP right": ("Metal1", rpp[-1].center()),
        "Cdec1 PLUS": ("TopMetal1", pin("Cdec1", "PLUS")[0].center()), "Cdec1 MINUS": ("Metal5", pin("Cdec1", "MINUS")[0].center()),
        "Cdec2 PLUS": ("TopMetal1", pin("Cdec2", "PLUS")[0].center()), "Cdec2 MINUS": ("Metal5", pin("Cdec2", "MINUS")[0].center()),
        "Cin TIE": ("Metal1", pin("Cin", "TIE")[0].center()), "Cout TIE": ("Metal1", pin("Cout", "TIE")[0].center()),
        "Cdec1 TIE": ("Metal1", pin("Cdec1", "TIE")[0].center()),
        "Qr C": ("Metal1", qrc.center()), "Qf B": ("Metal1", qfb.center()), "Qr B": ("Metal1", qrb.center()),
        "Rref bot": ("Metal1", rref0.center()), "Rref top": ("Metal1", rref1.center()), "Qf E": ("Metal2", qfe.center()),
        "Rief top": ("Metal1", rief1.center()), "Rief bot": ("Metal1", rief0.center()), "Rb bot": ("Metal1", rb0.center()),
        "Rb top": ("Metal1", rb1.center()), "Cbn PLUS": ("TopMetal1", cbp.center()), "Cbn MINUS": ("Metal5", cbm.center()),
        "Qr E": ("Metal2", qre.center()), "Qf C": ("Metal1", qfc.center()),
        "Ccas1 PLUS": ("TopMetal1", pin("Ccas1", "PLUS")[0].center()), "Ccas2 PLUS": ("TopMetal1", pin("Ccas2", "PLUS")[0].center()),
        "Ccas1 MINUS": ("Metal5", pin("Ccas1", "MINUS")[0].center()), "Ccas2 MINUS": ("Metal5", pin("Ccas2", "MINUS")[0].center()),
        "R1 bot": ("Metal1", r10.center()), "R1 top": ("Metal1", r11.center()), "R2 top": ("Metal1", r21.center()),
        "R2 bot": ("Metal1", r20.center()), "ptap0": ("Metal1", pins_of("ptap0", 8)[0].center()),
        "ptap3": ("Metal1", pins_of("ptap3", 8)[0].center()), "Cbn TIE": ("Metal1", pin("Cbn", "TIE")[0].center()),
        "Ccas1 TIE": ("Metal1", pin("Ccas1", "TIE")[0].center())}
    ids = {k: net(*v) for k, v in P.items()}
    expected = [["RF-in pad", "Cin MINUS"], ["Cin PLUS", "Lb LA", "Lb LB", "Q1 B", "Rb top"],
                ["Q1 E", "GND plane", "G pad in-low", "G pad in-high", "G pad out-low", "G pad out-high", "GND pad 1", "GND pad 2",
                 "Cdec1 MINUS", "Cdec2 MINUS", "Cin TIE", "Cout TIE", "Cdec1 TIE", "Qr E", "Rief bot", "Cbn MINUS",
                 "Ccas1 MINUS", "Ccas2 MINUS", "R2 bot", "ptap0", "ptap3", "Cbn TIE", "Ccas1 TIE"],
                ["Q1 C", "Q2 E"], ["Q2 C", "Lc LA", "Lc LB", "VCC pad", "RP left", "RP right", "Cout MINUS", "Cdec1 PLUS", "Cdec2 PLUS", "Qf C", "R1 top"],
                ["Q2 B", "Ccas1 PLUS", "Ccas2 PLUS", "R1 bot", "R2 top"], ["Iref pad", "Qr C", "Qf B"], ["Qr B", "Rref bot"],
                ["Qf E", "Rref top", "Rief top", "Rb bot", "Cbn PLUS"], ["RF-out pad", "Cout PLUS"]]
    ok = True
    for g in expected:
        s = {ids[k] for k in g}
        if None in s or len(s) != 1:
            ok = False; print("OPEN  :", ", ".join(f"{k}={ids[k]}" for k in g))
    reps = [ids[g[0]] for g in expected]
    for i in range(len(expected)):
        for j in range(i+1, len(expected)):
            if reps[i] is not None and reps[i] == reps[j]:
                ok = False; print("SHORT :", expected[i][0], "<->", expected[j][0])
    print("connectivity check:", "PASS" if ok else "FAIL")
check()

# ======================= mini-DRC (a few key rules; the full IHP deck remains the reference) =======================
def mini_drc():
    rules = {"Metal1": (8, 0.16, 0.18), "Metal2": (10, 0.20, 0.21), "Metal3": (30, 0.20, 0.21), "Metal4": (50, 0.20, 0.21),
             "Metal5": (67, 0.20, 0.21), "TopMetal1": (126, 1.64, 1.64), "TopMetal2": (134, 2.00, 2.00)}
    bad = 0
    for name, (g, w, sp) in rules.items():
        li = ly.find_layer(g, 0)
        if li is None: continue
        r = pya.Region(top.begin_shapes_rec(li)); r.merge()
        ng = sum(1 for p in r.each() for q in p.each_point_hull() if q.x % 5 or q.y % 5)
        nw = r.width_check(int(round(w*1000))).count(); ns = r.space_check(int(round(sp*1000))).count()
        exempt = pya.Region()                                              # pads and MIM plates need no slits
        for k, inst in DEV.items():
            if k.startswith("p") or k.startswith("C"): exempt.insert(inst.bbox())
        nslt = 0 if name == "TopMetal2" else ((r.sized(-15000).sized(15000) & r) - exempt).count()
        if ng or nw or ns or nslt: print(f"  {name:9s}: off-grid {ng}, width<{w} {nw}, space<{sp} {ns}, >30um without slit {nslt}")
        bad += ng + nw + ns + nslt
    print("mini-DRC:", "CLEAN" if bad == 0 else f"{bad} findings")
mini_drc()
