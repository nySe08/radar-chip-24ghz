"""coilfix.py - IHP inductor3 with nr_r=1 is OPEN: the TopMetal1 leads overlap the TopMetal2 ring with no TopVia2.
patch(cell, ly, ox, oy): adds 5x5 TopVia2 arrays (0.9 um cuts, 1.96 um pitch, 0.63 um enclosure - the PCell's own style)
on every TM1/TM2 overlap that sits on a lead (not at the top crossover). Returns the cut count."""
import klayout.db as pya
def patch(ly, top, inst_box_filter=None):
    tm1 = pya.Region(top.begin_shapes_rec(ly.find_layer(126, 0))); tm2 = pya.Region(top.begin_shapes_rec(ly.find_layer(134, 0)))
    tv2 = pya.Region(top.begin_shapes_rec(ly.find_layer(133, 0)))
    li = ly.layer(133, 0); n = 0; dbu = ly.dbu
    for p in (tm1 & tm2).each():
        b = p.bbox()
        if not tv2.interacting(pya.Region(b)).is_empty(): continue          # crossover: already has cuts
        if inst_box_filter and not inst_box_filter(b.to_dtype(dbu)): continue
        bb = b.to_dtype(dbu); enc, cut, pitch = 0.63, 0.9, 1.96
        x0, y0 = bb.left + enc, bb.bottom + enc
        nx = int((bb.width() - 2 * enc - cut) / pitch + 1e-6) + 1; ny = int((bb.height() - 2 * enc - cut) / pitch + 1e-6) + 1
        for i in range(nx):
            for j in range(ny):
                x, y = x0 + i * pitch, y0 + j * pitch
                top.shapes(li).insert(pya.DBox(x, y, x + cut, y + cut)); n += 1
    return n
