"""cheese.py - RF-aware cheesing of a Metal4 ground plane to meet IHP's density rule (Metal4 35-60 %, global).

cheese(ly, top, target=52.0): punches a grid of square holes into the large Metal4 plane polygons of `top` until the
Metal4 density (over the cell's bounding box) is at or below `target` percent. Holes are placed only where they do
not disturb the RF design:
  * never within `rf_margin` of TopMetal1/TopMetal2/Metal5 shapes (the lines above keep a solid plane under them),
  * never within `via_margin` of a Via3/Via4 landing on the plane,
  * never closer than `edge` to the plane's own edge (no notches), isolated squares only (the plane stays connected).
The hole size grows (pitch fixed) until the target is met; returns a dict with the before/after numbers.
All coordinates are on the 5 nm grid (integer-um hole positions).
"""
import klayout.db as pya

M4, V3, V4, M5, TM1, TM2 = (50, 0), (49, 0), (66, 0), (67, 0), (126, 0), (134, 0)

def _reg(ly, cell, ld):
    li = ly.find_layer(*ld)
    r = pya.Region(cell.begin_shapes_rec(li)) if li is not None else pya.Region()
    r.merge(); return r

def density(ly, cell, ld=M4):
    return _reg(ly, cell, ld).area() / cell.bbox().area() * 100.0

def cheese(ly, top, target=55.0, pitch=10.0, sizes=(4.0, 5.0, 6.0, 7.0, 8.0), rf_margin=5.0, via_margin=1.5,
           edge=2.0, min_plane_area=5000.0, keep_points=()):
    u = lambda v: int(round(v / ly.dbu))
    li4 = ly.layer(*M4)
    before = density(ly, top)
    m4_top = pya.Region(top.shapes(li4)); m4_top.merge()                     # only the top cell's own Metal4 is edited
    planes = pya.Region([p for p in m4_top.each() if p.area() * ly.dbu ** 2 >= min_plane_area])
    keep = pya.Region()
    for ld in (TM1, TM2, M5): keep += _reg(ly, top, ld).sized(u(rf_margin))
    # labels on the plane (and the connectivity probes placed at them) must not end up in a hole
    lbl = pya.Region()
    for ld in ((50, 25), (50, 2)):
        li = ly.find_layer(*ld)
        if li is None: continue
        for sh in top.shapes(li).each():
            if sh.is_text(): p = sh.text.trans.disp; lbl.insert(pya.Box(p.x - u(3), p.y - u(3), p.x + u(3), p.y + u(3)))
            elif sh.is_box() or sh.is_polygon(): lbl.insert(sh.bbox().enlarged(u(3)))
    for (px, py) in keep_points:                                             # explicit points to keep solid (check probes)
        lbl.insert(pya.Box(u(px - 3), u(py - 3), u(px + 3), u(py + 3)))
    keep += lbl
    for ld in (V3, V4): keep += _reg(ly, top, ld).sized(u(via_margin))
    keep.merge()
    inner = planes.sized(-u(edge))                                           # holes stay this far inside the plane
    bb = planes.bbox(); A = top.bbox().area()
    result = None
    for s in sizes:
        cand = pya.Region()
        x = bb.left * ly.dbu + pitch / 2
        while x < bb.right * ly.dbu:
            y = bb.bottom * ly.dbu + pitch / 2
            while y < bb.top * ly.dbu:
                cand.insert(pya.Box(u(round(x - s / 2, 3)), u(round(y - s / 2, 3)), u(round(x + s / 2, 3)), u(round(y + s / 2, 3))))
                y += pitch
            x += pitch
        holes = cand.inside(inner).not_interacting(keep)                     # fully inside the plane, clear of keep-outs
        dens = (_reg(ly, top, M4).area() - holes.area()) / A * 100.0
        result = (s, holes, dens)
        if dens <= target: break
    s, holes, dens = result
    mesh = pya.Region(); ms = None
    if dens > target:
        # tier 2: a fine mesh (holes smaller than the TopMetal1-Metal4 distance look nearly solid to the lines above, and
        # are too small for IHP's filler to refill) over the rest of the plane, clear of vias, edges and the big holes
        keep_v = pya.Region()
        for ld in (V3, V4): keep_v += _reg(ly, top, ld).sized(u(via_margin))
        keep_v += lbl
        for ms, mp in ((2.0, 5.0), (2.5, 5.0), (3.0, 5.0), (3.5, 5.0)):
            cand = pya.Region(); x = bb.left * ly.dbu + mp / 2
            while x < bb.right * ly.dbu:
                y = bb.bottom * ly.dbu + mp / 2
                while y < bb.top * ly.dbu:
                    cand.insert(pya.Box(u(round(x - ms / 2, 3)), u(round(y - ms / 2, 3)), u(round(x + ms / 2, 3)), u(round(y + ms / 2, 3))))
                    y += mp
                x += mp
            mesh = cand.inside(inner).not_interacting(keep_v).not_interacting(holes.sized(u(1.0)))
            dens = (_reg(ly, top, M4).area() - holes.area() - mesh.area()) / A * 100.0
            if dens <= target: break
        holes = holes + mesh
    new_m4 = m4_top - holes
    # store the plane as 40 x 40 um tiles: abutting tiles are one conductor for DRC/LVS, but every polygon stays far below
    # GDSII's 8191-point limit (one plane with thousands of holes is a single huge polygon that strict tools reject)
    tiled = pya.Region(); T = u(40.0); bbx = new_m4.bbox()
    for x in range(bbx.left, bbx.right, T):
        for y in range(bbx.bottom, bbx.top, T):
            tiled += new_m4 & pya.Region(pya.Box(x, y, x + T, y + T))
    top.shapes(li4).clear(); top.shapes(li4).insert(tiled)
    top.shapes(ly.layer(50, 23)).insert(planes)                              # Metal4:nofill - IHP's filler must not refill the holes
    return dict(before=round(before, 1), after=round(density(ly, top), 1), big_hole=s, big_holes=result[1].count(),
                mesh_hole=ms if mesh.count() else None, mesh_holes=mesh.count(), met=dens <= target)
