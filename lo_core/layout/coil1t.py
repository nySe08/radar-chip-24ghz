"""coil1t.py - correct single-turn centre-tapped VCO coil for IHP SG13G2, plus coil verification helpers.

Why: IHP's inductor3 PCell with nr_r=1 builds a ring that is CLOSED at the bottom (where LA/LB attach) and open at
the top (bridged by a TopMetal1 crossover); its leads have no vias. Patched with vias, LA and LB land on the same
bottom segment, 52 um apart: a ~60 pH short loop instead of the ~360 pH ring (EM-confirmed).

build(ly, d, w): takes the PCell for its marker/pin/label layers (so IHP's LVS deck recognises an inductor3 the same
way: IND 27/0 + 'inductor3' text, pins 27/2 + labels 27/25, LA/LB on TopMetal1, LC on TopMetal2), deletes the PCell's
metal and draws: octagonal TopMetal2 ring (inner apothem d/2, width w), OPEN at the bottom between the leads; the
centre tap joined to the ring's TOP midpoint and run down the symmetry axis to LC; TopMetal1 leads joined to the
ring ends by TopVia2 arrays.
predict_deck_params(): reproduces the deck's calc_ind_params (custom_extractor.lvs) with KLayout's own checks.
path_lengths(): shortest metal path LA-LB and LA-LC (1 um raster): open coil -> None, short -> too small.
"""
import math
from collections import deque
import numpy as np
import klayout.db as pya

TM1, TV2, TM2 = (126, 0), (133, 0), (134, 0)

GRID = 0.005
def _g(v): return round(round(v / GRID) * GRID, 3)

def _oct(cx, cy, apothem):
    """regular octagon with flat sides at +-apothem, ON the 5 nm grid: vertices (+-a, +-s) and (+-s, +-a) keep every
    diagonal edge at exactly 45 degrees when a and s are snapped independently."""
    cx, cy, a = _g(cx), _g(cy), _g(apothem); s = _g(apothem * math.tan(math.pi / 8))
    pts = [(a, s), (s, a), (-s, a), (-a, s), (-a, -s), (-s, -a), (s, -a), (a, -s)]
    return pya.DPolygon([pya.DPoint(cx + x, cy + y) for x, y in pts])

def build(ly, d=150.0, w=10.0, ihp=None, name=None, strip_w=10.0, cut=0.9, pitch=1.96, enc=0.63):
    """returns the new cell (flat). Same footprint, pins and markers as inductor3(w, d, nr_r=1)."""
    pc = ly.cell(ihp.pcell(ly, "inductor3", w=f"{w}u", s="2.1u", d=f"{d}u", nr_r=1, subE=False))
    cell = ly.create_cell(name or f"inductor3_1t_w{w:g}_d{d:g}")   # name starts with "inductor": checks treat it as a coil
    cell.copy_tree(pc); cell.flatten(True)
    dbu = ly.dbu
    li = {k: ly.layer(*k) for k in (TM1, TV2, TM2)}
    tm1_old = pya.Region(cell.shapes(li[TM1])); tm2_old = pya.Region(cell.shapes(li[TM2])); tm2_old.merge(); tm1_old.merge()
    # keep the PCell's two TM1 leads (they carry the LA/LB pins), drop its top crossover and all its vias and TM2
    leads = [p for p in tm1_old.each() if p.bbox().bottom * dbu < 1.0]
    lead_boxes = sorted((p.bbox().to_dtype(dbu) for p in leads), key=lambda b: b.left)
    for k in (TM1, TV2, TM2): cell.shapes(li[k]).clear()
    for b in lead_boxes: cell.shapes(li[TM1]).insert(b)
    # ring geometry from the PCell's own TM2 extents: outer apothem = half the TM2 width
    bb = tm2_old.bbox().to_dtype(dbu); a_out = bb.width() / 2; a_in = a_out - w
    cx = _g((bb.left + bb.right) / 2); y_bottom_out = _g(min(b.top for b in lead_boxes) - w)   # bottom flat overlaps the lead tops
    cy = y_bottom_out + a_out
    ring = pya.Region(_oct(cx, cy, a_out).to_itype(dbu)) - pya.Region(_oct(cx, cy, a_in).to_itype(dbu))
    gap_l, gap_r = lead_boxes[0].right, lead_boxes[1].left                 # open the ring between the leads' inner edges
    ring -= pya.Region(pya.DBox(gap_l, y_bottom_out - 1, gap_r, y_bottom_out + w + 1).to_itype(dbu))
    top_inner = cy + a_in
    strip = pya.Region(pya.DBox(cx - strip_w / 2, -1.0, cx + strip_w / 2, top_inner + 0.5).to_itype(dbu))   # LC -> top midpoint
    tm2 = (ring + strip); tm2.merge(); cell.shapes(li[TM2]).insert(tm2)
    # TopVia2 arrays where each lead overlaps a ring end
    n = 0
    for b in lead_boxes:
        ov = (pya.Region(b.to_itype(dbu)) & ring).bbox().to_dtype(dbu)
        nx = int((ov.width() - 2 * enc - cut) / pitch + 1e-6) + 1; ny = int((ov.height() - 2 * enc - cut) / pitch + 1e-6) + 1
        for i in range(nx):
            for j in range(ny):
                x, y = ov.left + enc + i * pitch, ov.bottom + enc + j * pitch
                cell.shapes(li[TV2]).insert(pya.DBox(x, y, x + cut, y + cut)); n += 1
    return cell, n

def predict_deck_params(ly, cell):
    """IHP deck calc_ind_params: meas = TM2 in marker; w = min projected width; s = min projected space;
    nr_r = number of TM2 polygons; d = length of the device-extent edge not touching the pin edge - 2*nr*w - 2*(nr-1)*s."""
    dbu = ly.dbu
    mk = pya.Region(cell.shapes(ly.find_layer(27, 0))); mk.merge()
    max_mk_len = max(e.length() for e in mk.edges().each())
    tm2 = pya.Region(cell.shapes(ly.find_layer(*TM2))); tm1 = pya.Region(cell.shapes(ly.find_layer(*TM1)))
    meas = (tm2 & mk); meas.merge()
    wv = [e.distance() for e in meas.width_check(max_mk_len, False, pya.Metrics.Projection, None, 10, None).each() if e.distance() > 0]
    # the deck calls space_check(sep_val, proj) in Ruby: proj lands in the 2nd positional slot (whole_edges),
    # so it measures Euclidian spacing with whole edges - reproduce that literally
    sv = [e.distance() for e in meas.space_check(max_mk_len, True).each()]
    width = min(wv) if wv else 0; space = min(sv) if sv else 0; nr = max(1, meas.count())
    core = ((tm2 + tm1) & mk); core.merge()
    pins = pya.Region(cell.shapes(ly.find_layer(27, 2)))
    ext = pya.Region(core.bbox()).edges(); exc = ext.interacting(pins); top_edges = ext.not_interacting(exc)
    diam = top_edges.length() - 2 * (nr - 1) * space - 2 * nr * width
    return dict(w=round(width * dbu, 3), s=round(space * dbu, 3), d=round(max(diam, 0) * dbu, 3), nr_r=nr)

def path_lengths(ly, cell, pins=("LA", "LB", "LC"), res=1.0):
    """shortest metal path (um) between coil terminals over TM1/TM2 joined at TopVia2, on a res-um raster."""
    dbu = ly.dbu; R = {k: pya.Region(cell.shapes(ly.find_layer(*k))) for k in (TM1, TV2, TM2)}
    for r in R.values(): r.merge()
    bb = (R[TM1] + R[TM2]).bbox().to_dtype(dbu); nx, ny = int(bb.width() / res) + 2, int(bb.height() / res) + 2
    def raster(reg):
        g = np.zeros((nx, ny), bool)
        for p in reg.each():
            b = p.bbox().to_dtype(dbu)
            for i in range(max(0, int((b.left - bb.left) / res)), min(nx, int((b.right - bb.left) / res) + 1)):
                x = bb.left + (i + 0.5) * res
                for j in range(max(0, int((b.bottom - bb.bottom) / res)), min(ny, int((b.top - bb.bottom) / res) + 1)):
                    if p.inside(pya.DPoint(x, bb.bottom + (j + 0.5) * res).to_itype(dbu) if False else pya.Point(int(x / dbu), int((bb.bottom + (j + 0.5) * res) / dbu))):
                        g[i, j] = True
        return g
    g1, g2, gv = raster(R[TM1]), raster(R[TM2]), raster(R[TV2].sized(int(0.6 / dbu)))
    texts = {}
    for sh in cell.shapes(ly.find_layer(27, 25)).each():
        if sh.is_text() and sh.text.string in pins: texts[sh.text.string] = (sh.dtext.x, sh.dtext.y)
    def node(name):
        x, y = texts[name]; i, j = int((x - bb.left) / res), int((y - bb.bottom) / res) + 1
        for layer, g in ((0, g1), (1, g2)):
            for dj in range(0, 6):
                if 0 <= j + dj < ny and g[i, j + dj]: return (layer, i, j + dj)
        return None
    def bfs(a, b):
        if a is None or b is None: return None
        grids = (g1, g2); dist = {a: 0}; q = deque([a])
        while q:
            l, i, j = q.popleft(); dcur = dist[(l, i, j)]
            if (l, i, j) == b: return dcur * res
            nbrs = [(l, i + 1, j), (l, i - 1, j), (l, i, j + 1), (l, i, j - 1)]
            if gv[i, j]: nbrs.append((1 - l, i, j))
            for (L, I, J) in nbrs:
                if 0 <= I < nx and 0 <= J < ny and grids[L][I, J] and (L, I, J) not in dist:
                    dist[(L, I, J)] = dcur + 1; q.append((L, I, J))
        return None
    # two-terminal coils (inductor2) have no LC: report only the pairs whose terminals exist
    return {f"{p}-{q}": (bfs(node(p), node(q)) if p in texts and q in texts else None)
            for p, q in (("LA", "LB"), ("LA", "LC"), ("LB", "LC"))}
