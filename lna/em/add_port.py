"""
add_port.py - place the EM port box (layer 201/0) exactly in the gap between the two inductor leads.

Finds the lowest ends of the lead metal (default TopMetal1, GDS 126/0), takes a 5 um tall band
at the bottom, and draws a box from the inner edge of the left lead to the inner edge of the
right lead (filling the gap, NOT overlapping the metal). Removes any old port boxes first.

Run (KLayout batch mode):
  klayout -b -r add_port.py -rd input=ind_lb3_c.gds -rd output=ind_lb3_p.gds
  (for TopMetal2 leads add:  -rd layer=134)
"""
import pya

inp = globals().get("input", "in.gds")
out = globals().get("output", inp.replace(".gds", "_p.gds"))
lead_layer = int(globals().get("layer", 126))
band_um = 5.0

ly = pya.Layout(); ly.read(inp)
top = ly.top_cell(); top.flatten(True)
dbu = ly.dbu
li = ly.find_layer(lead_layer, 0)
if li is None: raise SystemExit(f"no shapes on layer {lead_layer}/0")

metal = pya.Region(top.begin_shapes_rec(li)); metal.merge()
bb = metal.bbox()
band = pya.Region(pya.Box(bb.left, bb.bottom, bb.right, bb.bottom + int(round(band_um/dbu))))
ends = sorted((metal & band).each_merged(), key=lambda p: p.bbox().left)
if len(ends) != 2:
    raise SystemExit(f"expected 2 lead ends at the bottom on layer {lead_layer}/0, found {len(ends)}")
left, right = ends[0].bbox(), ends[1].bbox()
port = pya.Box(left.right, bb.bottom, right.left, bb.bottom + int(round(band_um/dbu)))

lp = ly.layer(201, 0)
top.shapes(lp).clear()
top.shapes(lp).insert(port)
ly.write(out)
print(f"Leads on {lead_layer}/0: left x {left.left*dbu:.3f}..{left.right*dbu:.3f} um, right x {right.left*dbu:.3f}..{right.right*dbu:.3f} um")
print(f"Port box (201/0): x {port.left*dbu:.3f}..{port.right*dbu:.3f} um (gap {port.width()*dbu:.3f} um), "
      f"y {port.bottom*dbu:.3f}..{port.top*dbu:.3f} um")
print("Wrote", out)
