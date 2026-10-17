"""render.py - draw a GDS layout to PNG (selected layers), for quick previews."""
import sys, klayout.db as pya
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection
LAYERS = [  # (gds layer, datatype, name, color, alpha)
    ((1, 0), "Activ", "#2ca02c", 0.5), ((5, 0), "GatPoly (resistors)", "#d62728", 0.7),
    ((8, 0), "Metal1", "#1f77b4", 0.35), ((10, 0), "Metal2", "#17becf", 0.35),
    ((67, 0), "Metal5", "#9467bd", 0.35), ((36, 0), "MIM", "#bcbd22", 0.6),
    ((126, 0), "TopMetal1", "#7f7f7f", 0.55), ((134, 0), "TopMetal2", "#ff7f0e", 0.45)]
def render(gds, png, title, window=None, labels=None):
    ly = pya.Layout(); ly.read(gds); top = ly.top_cell()
    fig, ax = plt.subplots(figsize=(15, 10.5))
    for (l, d), name, col, a in LAYERS:
        li = ly.find_layer(l, d)
        if li is None: continue
        reg = pya.Region(top.begin_shapes_rec(li)); reg.merge(); reg = reg.decompose_trapezoids_to_region(1)   # holes drawn correctly
        polys = [Polygon([(p.x*ly.dbu, p.y*ly.dbu) for p in poly.each_point_hull()], closed=True) for poly in reg.each()]
        if polys: ax.add_collection(PatchCollection(polys, fc=col, ec=col, alpha=a, lw=0.3))
        ax.plot([], [], "s", color=col, alpha=min(1, a+0.3), label=name, ms=10)
    for txt, (x, y) in (labels or {}).items():
        ax.text(x, y, txt, fontsize=9, weight="bold", ha="center", va="center",
                bbox=dict(fc="white", ec="none", alpha=0.75, pad=1))
    bb = top.dbbox()
    ax.set_xlim(*(window[:2] if window else (bb.left-5, bb.right+5)))
    ax.set_ylim(*(window[2:] if window else (bb.bottom-5, bb.top+5)))
    ax.set_aspect("equal"); ax.set_xlabel("x [µm]"); ax.set_ylabel("y [µm]"); ax.set_title(title)
    ax.legend(loc="upper center", ncol=8, fontsize=8, bbox_to_anchor=(0.5, -0.06))
    plt.tight_layout(); plt.savefig(png, dpi=130); plt.close(fig)
if __name__ == "__main__":
    render(sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else sys.argv[1])
