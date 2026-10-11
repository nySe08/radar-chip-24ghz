"""
lna_gen.py - layout generator for the 24 GHz LNA test cell (IHP SG13G2).
v2.1: placement + RF-core wiring + slotted ground plane; 5 nm grid snapping; built-in mini-DRC.

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

def rect(layer, x1, y1, x2, y2):
    x1, y1, x2, y2 = G(x1), G(y1), G(x2), G(y2)
    top.shapes(LY[layer]).insert(pya.DBox(min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2)))
def wire(layer, pts, w, start_ext=None):
    pts = [pya.DPoint(G(p[0]), G(p[1])) for p in pts]
    top.shapes(LY[layer]).insert(pya.DPath(pts, w, w/2 if start_ext is None else start_ext, w/2))
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
place("Cout", "rfcmim", 470, 296, rot=180, w="7u", l="7u")        # MINUS (M5) faces the out node, PLUS faces the pad
place("RP", "rppd", 425, 286, w="2u", l="2.66u")

# ======================= RF core wiring =======================
# --- RF in: S pad -> Cin MINUS (Metal5)
cm, _ = pin("Cin", "MINUS"); cp, _ = pin("Cin", "PLUS")
wire("TopMetal2", [(90, 260), (cm.center().x - 6, 260), (cm.center().x - 6, cm.center().y)], 10)
via(cm.center().x - 3, cm.center().y, "Metal5", "TopMetal2")
wire("Metal5", [(cm.center().x - 3, cm.center().y), (cm.center().x, cm.center().y)], 3)
# --- in: Cin PLUS (TM1) -> Lb LA lead (TM1)
la, _ = pin("Lb", "LA"); lb, _ = pin("Lb", "LB")
wire("TopMetal1", [(cp.center().x, cp.center().y), (la.center().x, cp.center().y), (la.center().x, la.top)], 5)
# --- b1: Q1 base (M1, top edge after rotation) -> Lb LB lead (TM1)
qb, _ = pin("Q1", "B")
rect("Metal1", qb.left, qb.bottom, qb.right, qb.top + 5.5)                  # base bar pulled up
vb = (qb.center().x, qb.top + 4.2); via(*vb, "Metal1", "TopMetal1")
wire("TopMetal1", [vb, (vb[0], 293), (lb.center().x, 293), (lb.center().x, lb.top)], 4)
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
vla = (lca.center().x, lca.top + 3); via(*vla, "TopMetal1", "TopMetal2")
wire("TopMetal2", [vo, (vo[0], 292), (vla[0], 292), vla], 6)
# --- VCC: Lc LB lead (TM1) -> TM2 -> VCC pad
vlb = (lcb.center().x, lcb.top + 3); via(*vlb, "TopMetal1", "TopMetal2")
wire("TopMetal2", [vlb, (vlb[0] + 12, vlb[1]), (vlb[0] + 12, 110), (390, 110), (390, 90)], 8, start_ext=0)
# --- RP between out (Lc LA lead) and VCC (Lc LB lead) - pins found from the PCell (M1 at both ends)
# --- Cout: out (Lc LA via) -> Cout MINUS (M5); Cout PLUS (TM1) -> RF out S pad
# (RP and Cout wiring: next step, together with the bias network)

# ======================= ground plane (Metal4) =======================
plane = pya.Region(pya.Box(0, 0, 700_000, 470_000))
holes = pya.Region()
for k in ("Lb", "Lc"): holes.insert(DEV[k].bbox())                          # inductor keep-outs
for k in ("Cin", "Cout"): holes.insert(DEV[k].bbox().enlarged(3000))        # signal MIMs
for k in ("pin1", "pout1", "pIref", "pVCC"): holes.insert(DEV[k].bbox().enlarged(10000))   # S and DC pads
for k in ("pin0", "pin2", "pout0", "pout2", "pGND1", "pGND2"): holes.insert(DEV[k].bbox().enlarged(4000))  # ground pads: gap...
for (x, y, b, t) in VIAS:                                                   # signal via stacks crossing Metal4
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
gnd = ((plane - holes - slits) + straps).merged()
# store the plane as simple abutting rectangles instead of one huge keyhole polygon (robust for DRC/LVS tools)
top.shapes(LY["Metal4"]).insert(gnd.decompose_trapezoids_to_region(1))

ly.write("lna_layout.gds")
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
        "RF-out pad": ("TopMetal2", (650, 260))}
    ids = {k: net(*v) for k, v in P.items()}
    expected = [["RF-in pad", "Cin MINUS"], ["Cin PLUS", "Lb LA", "Lb LB", "Q1 B"],
                ["Q1 E", "GND plane", "G pad in-low", "G pad in-high", "G pad out-low", "G pad out-high", "GND pad 1", "GND pad 2"],
                ["Q1 C", "Q2 E"], ["Q2 C", "Lc LA", "Lc LB", "VCC pad"], ["Q2 B"], ["Iref pad"], ["RF-out pad"]]
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
