"""floorplan.py - to-scale floorplans of the TEST chip and the FULL 2TX/4RX chip (IHP SG13G2).

Real blocks are placed as their own GDS cells (LO core, RX tile); blocks not laid out yet are placeholders on a marker
layer, sized from their design (TX channel: two coils of 231 and 170 um footprint plus devices; H-tree LO driver).
Pads: IHP bondpad PCell (80 x 80 um), GSG groups at 100 um pitch (the LNA's proven style). Seal ring: IHP PCell.
Block placement follows the pins: LO core control/PLL pins on its left edge, RX LO outputs at its bottom centre,
TX LO outputs on its right edge; RX tile LO inputs at its top, RF input at its bottom.
Outputs: floorplan_<chip>.gds and floorplan_<chip>.png, plus a printed area summary.
"""
import sys
sys.path.insert(0, '/home/claude/vcocoil')
import ihp
pya = ihp.pya
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

BLOCKS = {"lo_core": ("/home/claude/logen/lo_core.gds", 860, 640), "rx_tile": ("/home/claude/tilegen/rx_tile.gds", 290, 548)}
PH = {"tx_ch": (440, 400), "lodrv": (150, 150)}          # placeholders: TX channel, LO driver (H-tree branch)
PAD, PITCH, EDGE, RING = 80.0, 100.0, 110.0, 200.0       # pad size, GSG pitch, pad centre from die edge, keep-out to core
MARK = (235, 4)                                          # marker layer for placeholders

def chip(name, W, H, place, pads):
    ly = pya.Layout(); ly.dbu = 0.001; top = ly.create_cell(name.upper())
    cells = {}
    for k, (g, w, h) in BLOCKS.items():
        src = pya.Layout(); src.read(g); c = ly.create_cell(k); c.copy_tree(src.top_cell()); cells[k] = c
    for k, (w, h) in PH.items():
        c = ly.create_cell(f"{k}_PLACEHOLDER"); c.shapes(ly.layer(*MARK)).insert(pya.DBox(0, 0, w, h)); cells[k] = c
    rects = []
    for k, x, y, lbl in place:
        top.insert(pya.DCellInstArray(cells[k].cell_index(), pya.DTrans(x, y)))
        w, h = (BLOCKS[k][1:] if k in BLOCKS else PH[k]); rects.append((x, y, w, h, lbl, k in PH))
    pc = ly.cell(ihp.pcell(ly, "bondpad", shape="square")); lt = ly.layer(134, 25)
    for nm, x, y in pads:
        top.insert(pya.DCellInstArray(pc.cell_index(), pya.DTrans(x, y))); top.shapes(lt).insert(pya.DText(nm, x, y))
    sr = ly.cell(ihp.pcell(ly, "sealring", w=f"{W - 50}u", l=f"{H - 50}u")); top.insert(pya.DCellInstArray(sr.cell_index(), pya.DTrans(0, 0)))
    ly.write(f"floorplan_{name}.gds")
    # overlap / keep-out sanity: blocks must not overlap each other or the pad ring
    bad = []
    for i, a in enumerate(rects):
        A = pya.DBox(a[0], a[1], a[0] + a[2], a[1] + a[3])
        if A.left < RING - 1 or A.bottom < RING - 1 or A.right > W - RING + 1 or A.top > H - RING + 1: bad.append(f"{a[4]} enters the pad ring")
        for b in rects[i + 1:]:
            if A.overlaps(pya.DBox(b[0], b[1], b[0] + b[2], b[1] + b[3])): bad.append(f"{a[4]} overlaps {b[4]}")
    # drawing
    fig, ax = plt.subplots(figsize=(7, 7 * H / W)); ax.add_patch(Rectangle((0, 0), W, H, fill=False, lw=2, ec="k"))
    ax.add_patch(Rectangle((25, 25), W - 50, H - 50, fill=False, lw=1, ec="0.6", ls="--"))
    for x, y, w, h, lbl, ph in rects:
        ax.add_patch(Rectangle((x, y), w, h, fc=("#f5d6a8" if ph else "#a8c8f0"), ec="k", lw=1, hatch=("//" if ph else None)))
        ax.text(x + w / 2, y + h / 2, lbl, ha="center", va="center", fontsize=8)
    for nm, x, y in pads:
        col = "#3a7" if nm.startswith("G") else ("#d33" if nm[:2] in ("RF", "TX", "PL") else "#777")
        ax.add_patch(Rectangle((x - PAD / 2, y - PAD / 2), PAD, PAD, fc=col, ec="k", lw=0.5))
        ax.text(x, y, nm, ha="center", va="center", fontsize=4.5, color="w")
    ax.set_xlim(-20, W + 20); ax.set_ylim(-20, H + 20); ax.set_aspect("equal"); ax.set_xlabel("um")
    ax.set_title(f"{name}: {W:.0f} x {H:.0f} um = {W*H/1e6:.2f} mm2   (blue: laid out, hatched: placeholder)", fontsize=9)
    fig.tight_layout(); fig.savefig(f"floorplan_{name}.png", dpi=170); plt.close(fig)
    return W * H / 1e6, len(pads), bad

def row(names, x0, y, horizontal=True, step=PITCH):
    return [(n, x0 + i * step, y) if horizontal else (n, y, x0 + i * step) for i, n in enumerate(names)]

# ------------------------------------------------------------------ TEST CHIP
# LO core top; RX tile bottom-left (RF in on the bottom edge) fed by one LO driver above it (short jog from the LO core's
# bottom-centre RX LO outputs); TX channel bottom-right, fed from the LO core's right-edge TX LO outputs; TX out right edge.
Wt, Ht = 1260.0, 1800.0
lo = (200.0, Ht - 200.0 - 640)
place_t = [("lo_core", lo[0], lo[1], "LO core"),
           ("lodrv", 200.0 + 235 - 75, lo[1] - 40 - 150, "LO drv"),
           ("rx_tile", 200.0, 200.0, "RX tile"),
           ("tx_ch", Wt - 200 - 440, 290.0, "TX channel")]
pads_t = (row(["GND", "RFIN", "GND"], 200.0 + 216 - PITCH, EDGE)                       # RX input GSG under the tile's RFIN
          + row(["IREF"], 640.0, EDGE)
          + row(["GND", "TXOUT", "GND"], 290.0 + 200 - PITCH, Wt - EDGE, horizontal=False)  # TX output GSG, right edge
          + row(["EN"], 290.0 + 400 + 100, Wt - EDGE, horizontal=False)
          + row(["GND", "PLLP", "GND", "PLLN", "GND"], lo[1] + 311 - 2 * PITCH, EDGE, horizontal=False)  # PLL out GSGSG
          + row(["VTUNE", "BSEL"], lo[1] + 311 - 4 * PITCH, EDGE, horizontal=False)
          + row(["IFP", "IFN"], 300.0, EDGE, horizontal=False)                         # IF out (low frequency)
          + row(["VCC", "GND", "VCC", "GND", "VCC"], Wt / 2 - 2 * PITCH, Ht - EDGE))    # supply, top edge
# ------------------------------------------------------------------ FULL CHIP
# LO core top-left of centre; TX1/TX2 stacked on its right (outputs on the right edge, enables beside them);
# H-tree band under the LO core: 4 LO drivers feeding 4 RX tiles in a row; RF inputs on the bottom edge.
Wf, Hf = 1760.0, 2000.0
tile_y = 200.0; tile_x0 = (Wf - (4 * 290 + 3 * 40)) / 2
htree_y = tile_y + 548 + 40
lof = (220.0, htree_y + 150 + 60)
place_f = [("lo_core", lof[0], lof[1], "LO core")]
place_f += [("lodrv", tile_x0 + i * 330 + 235 - 75, htree_y, f"drv{i+1}") for i in range(4)]
place_f += [("rx_tile", tile_x0 + i * 330, tile_y, f"RX{i+1}") for i in range(4)]
tx1y, tx2y = Hf - 200 - 400, Hf - 200 - 400 - 420
place_f += [("tx_ch", Wf - 200 - 440, tx1y, "TX1"), ("tx_ch", Wf - 200 - 440, tx2y, "TX2")]
pads_f = []
for i in range(4):
    pads_f += row(["GND", f"RF{i+1}", "GND"], tile_x0 + i * 330 + 216 - PITCH, EDGE)
pads_f += row(["GND", "TX1", "GND"], tx1y + 200 - PITCH, Wf - EDGE, horizontal=False)
pads_f += row(["GND", "TX2", "GND"], tx2y + 200 - PITCH, Wf - EDGE, horizontal=False)
pads_f += row(["EN2", "EN1"], tx2y - 2 * PITCH, Wf - EDGE, horizontal=False)
pads_f += row(["GND", "PLLP", "GND", "PLLN", "GND"], lof[1] + 311 - 2 * PITCH, EDGE, horizontal=False)
pads_f += row(["VTUNE", "BSEL"], lof[1] + 311 - 4 * PITCH, EDGE, horizontal=False)
pads_f += row(["IF1P", "IF1N", "IF2P", "IF2N"], 300.0, EDGE, horizontal=False)
pads_f += row(["IF3P", "IF3N", "IF4P", "IF4N"], 300.0, Wf - EDGE, horizontal=False)
pads_f += row(["VCC", "GND", "VCC", "GND", "VCC", "GND", "VCC"], 360.0, Hf - EDGE)

if __name__ == "__main__":
    for name, W, H, pl, pd in (("test_chip", Wt, Ht, place_t, pads_t), ("full_chip", Wf, Hf, place_f, pads_f)):
        a, n, bad = chip(name, W, H, pl, pd)
        print(f"{name}: {W:.0f} x {H:.0f} um = {a:.2f} mm2, {n} pads, checks: {'OK' if not bad else bad}")
