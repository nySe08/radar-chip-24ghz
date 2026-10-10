"""
strip_lbe.py - remove the substrate-etching layer (LBE, GDS 157/0) from a layout.

The IHP inductor PCell can leave an LBE (local backside etch) shape that is hard to
remove in the GUI, because the PCell regenerates it. This script flattens the layout
(no PCell left to regenerate anything) and deletes every shape on LBE.

Run inside the container (KLayout batch mode):
    klayout -b -r strip_lbe.py -rd input=ind_lb.gds -rd output=ind_lb_clean.gds
"""
import pya

inp = globals().get("input", "ind_lb.gds")
out = globals().get("output", inp.replace(".gds", "_clean.gds"))

ly = pya.Layout()
ly.read(inp)
top = ly.top_cell()
top.flatten(True)                                   # flatten all levels, drop the sub-cells

removed = 0
for li in ly.layer_indexes():
    info = ly.get_info(li)
    if info.layer == 157 and info.datatype == 0:    # LBE.drawing
        removed += top.shapes(li).size()
        top.shapes(li).clear()
        ly.delete_layer(li)

ly.write(out)
layers = sorted(f"{ly.get_info(li).layer}/{ly.get_info(li).datatype}" for li in ly.layer_indexes()
                if not top.shapes(li).is_empty())
print(f"Removed {removed} LBE shape(s). Wrote {out}")
print("Layers left (layer/datatype):", ", ".join(layers))
