"""make_coil.py - VCO tank coil candidate for EM: inductor3 PCell, flattened, with the differential port (layer 201/0)
in the gap between the two TopMetal1 leads (same procedure as add_port.py)."""
import sys, ihp; pya = ihp.pya
d = float(sys.argv[1]) if len(sys.argv) > 1 else 67.2
w = float(sys.argv[2]) if len(sys.argv) > 2 else 6.0
nr = int(sys.argv[3]) if len(sys.argv) > 3 else 2
ly = pya.Layout(); ly.dbu = 0.001
top = ly.create_cell(f"vco_coil_w{w:g}_n{nr}_d{d}")
cell = ihp.pcell(ly, "inductor3", w=f"{w}u", s="2.1u", d=f"{d}u", nr_r=nr, subE=False)
top.insert(pya.CellInstArray(cell, pya.Trans())); top.flatten(True)
li = ly.find_layer(126, 0); metal = pya.Region(top.begin_shapes_rec(li)); metal.merge(); bb = metal.bbox()
band = pya.Region(pya.Box(bb.left, bb.bottom, bb.right, bb.bottom + 5000))
ends = sorted((metal & band).each_merged(), key=lambda p: p.bbox().left)
assert len(ends) == 2, f"expected 2 TopMetal1 lead ends, found {len(ends)}"
l, r = ends[0].bbox(), ends[1].bbox()
port = pya.Box(l.right, max(l.bottom, r.bottom), r.left, min(l.top, r.top))
top.shapes(ly.layer(201, 0)).insert(port)
out = f"vco_coil_w{w:g}_n{nr}_d{d}_p.gds"; ly.write(out)
print(f"{out}: coil bbox {top.dbbox().width():.1f} x {top.dbbox().height():.1f} um, port {port.to_dtype(0.001)} (gap {port.width()/1000:.2f} um)")
