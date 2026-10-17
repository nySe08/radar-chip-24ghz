"""floorplan_v2.py - to-scale floorplans of the test chip and the full 2TX/4RX chip. HYBRID pad ring: IHP sg13g2_io cells (DC + supply, silicon-proven ESD) on the top edge,
custom GSG RF pads with EM-verified ESD coils on the other edges. Real cells everywhere they exist.

Top edge (IO segment): IHP IO cells (80 x 180 um, abut at 80 um pitch), rotated so their pad side faces the die edge,
each with a 70 um bondpad (IHP bondpad PCell) between it and the seal ring. Rails: iovdd = VCC 2.5 V, iovss = GND,
core vdd/vss rails tied to GND (the analog and IOVdd/IOVss pads use only iovdd/iovss for protection).
RF edges: 80 um GSG pads (signal pad TopMetal1/2 only), ESD coils as their real inductor2 PCells
(RX: 3 turns w5 d86, ~1.48 nH, self-resonant 23.4 GHz; TX: 2 turns w7 d77, ~730 pH at 24 GHz).
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import ihp
pya = ihp.pya
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

IOGDS = os.path.join(os.environ.get("PDK_ROOT", "/foss/pdks"), "ihp-sg13g2", "libs.ref", "sg13g2_io", "gds", "sg13g2_io.gds")
BLOCKS = {"lo_core": (os.path.join(REPO, "lo_core", "layout", "lo_core.gds"), 860, 640),
          "rx_tile": (os.path.join(REPO, "rx_tile", "layout", "rx_tile.gds"), 290, 548)}
PH = {"tx_ch": (440, 400), "lodrv": (150, 150)}
SEAL, IO_PAD, IO_DEPTH, IO_PITCH = 40.0, 70.0, 180.0, 80.0
TOP_M = SEAL + 5 + IO_PAD + 5 + IO_DEPTH + 30          # 330 um: seal, bondpad, IO cell, gap to the core
RF_PAD, RF_PITCH, RF_EDGE = 80.0, 100.0, 110.0          # custom RF pads: size, GSG pitch, centre from the die edge
COIL = {"rx": dict(w="5u", d="86u", nr_r=3, size=185.0), "tx": dict(w="7u", d="77u", nr_r=2, size=170.0)}
IOCELL = {"VCC": "sg13g2_IOPadIOVdd", "GND": "sg13g2_IOPadIOVss"}        # everything else: sg13g2_IOPadAnalog
MARK = (235, 4)

class Chip:
    def __init__(self, name, W, H):
        self.name, self.W, self.H = name, W, H
        self.ly = pya.Layout(); self.ly.dbu = 0.001; self.top = self.ly.create_cell(name.upper())
        self.rects, self.pads, self.ios, self.coils = [], [], [], []
        src = pya.Layout(); src.read(IOGDS); self.io = {}
        for cn in ("sg13g2_IOPadAnalog", "sg13g2_IOPadIOVdd", "sg13g2_IOPadIOVss"):
            c = self.ly.create_cell(cn); c.copy_tree(src.cell(cn)); self.io[cn] = c
        self.cells = {}
        for k, (g, w, h) in BLOCKS.items():
            s = pya.Layout(); s.read(g); c = self.ly.create_cell(k); c.copy_tree(s.top_cell()); self.cells[k] = c
        for k, (w, h) in PH.items():
            c = self.ly.create_cell(f"{k}_PLACEHOLDER"); c.shapes(self.ly.layer(*MARK)).insert(pya.DBox(0, 0, w, h)); self.cells[k] = c
        self.bp70 = self.ly.cell(ihp.pcell(self.ly, "bondpad", shape="square", diameter="70u"))
        self.bp80 = self.ly.cell(ihp.pcell(self.ly, "bondpad", shape="square"))
        self.bp80s = self.ly.cell(ihp.pcell(self.ly, "bondpad", shape="square", bottomMetal="TM1"))
    def block(self, k, x, y, lbl):
        self.top.insert(pya.DCellInstArray(self.cells[k].cell_index(), pya.DTrans(x, y)))
        w, h = BLOCKS[k][1:] if k in BLOCKS else PH[k]; self.rects.append((x, y, w, h, lbl, k in PH))
    def io_segment_top(self, names, x0):
        """IHP IO cells along the top edge, pad side up (rotated 180 deg), bondpad above each."""
        for i, nm in enumerate(names):
            cn = IOCELL.get(nm, "sg13g2_IOPadAnalog"); x = x0 + i * IO_PITCH
            y_top = self.H - SEAL - 5 - IO_PAD - 5                       # the IO cell's pad edge
            self.top.insert(pya.DCellInstArray(self.io[cn].cell_index(), pya.DTrans(pya.DTrans.R180, x + IO_PITCH, y_top)))
            yb = self.H - SEAL - 5 - IO_PAD / 2
            self.top.insert(pya.DCellInstArray(self.bp70.cell_index(), pya.DTrans(x + IO_PITCH / 2, yb)))
            self.top.shapes(self.ly.layer(134, 25)).insert(pya.DText(nm, x + IO_PITCH / 2, yb))
            self.ios.append((nm, cn, x, y_top - IO_DEPTH))
    def rf_group(self, names, centre, edge, coil=None, coil_at=None):
        """GSG-type group of custom pads along an edge ('bottom'/'right'/'left'); signal pads TM1/TM2 only."""
        n = len(names); ofs = [(i - (n - 1) / 2) * RF_PITCH for i in range(n)]
        for nm, o in zip(names, ofs):
            if edge == "bottom": x, y = centre + o, RF_EDGE
            elif edge == "right": x, y = self.W - RF_EDGE, centre + o
            else: x, y = RF_EDGE, centre + o
            cell = self.bp80 if nm.startswith("G") else self.bp80s
            self.top.insert(pya.DCellInstArray(cell.cell_index(), pya.DTrans(x, y)))
            self.top.shapes(self.ly.layer(134, 25)).insert(pya.DText(nm, x, y)); self.pads.append((nm, x, y))
        if coil:
            p = COIL[coil]; c = self.ly.cell(ihp.pcell(self.ly, "inductor2", w=p["w"], s="2.1u", d=p["d"], nr_r=p["nr_r"], subE=False))
            cx, cy = coil_at
            self.top.insert(pya.DCellInstArray(c.cell_index(), pya.DTrans(cx - c.dbbox().center().x, cy - c.dbbox().center().y)))
            self.coils.append((coil, cx, cy, c.dbbox().width(), c.dbbox().height()))
    def finish(self, margins):
        sr = self.ly.cell(ihp.pcell(self.ly, "sealring", w=f"{self.H - 50}u", l=f"{self.W - 50}u"))   # PCell: w = Y extent, l = X extent
        self.top.insert(pya.DCellInstArray(sr.cell_index(), pya.DTrans(0, 0)))
        self.ly.write(os.path.join(HERE, f"floorplan_v2_{self.name}.gds"))
        # checks: blocks inside the core box, no overlaps between blocks, IO cells, pads and coils
        L, B, R, T = margins
        boxes = [(f"block {r[4]}", pya.DBox(r[0], r[1], r[0] + r[2], r[1] + r[3])) for r in self.rects]
        bad = [f"{n} outside the core" for n, b in boxes if b.left < L - 1 or b.bottom < B - 1 or b.right > self.W - R + 1 or b.top > self.H - T + 1]
        boxes += [(f"IO {nm}", pya.DBox(x, y, x + IO_PITCH, y + IO_DEPTH)) for nm, cn, x, y in self.ios]
        boxes += [(f"pad {nm}", pya.DBox(x - RF_PAD / 2, y - RF_PAD / 2, x + RF_PAD / 2, y + RF_PAD / 2)) for nm, x, y in self.pads]
        boxes += [(f"coil {k}", pya.DBox(cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2)) for k, cx, cy, w, h in self.coils]
        for i, (na, a) in enumerate(boxes):
            if a.left < SEAL or a.bottom < SEAL or a.right > self.W - SEAL or a.top > self.H - SEAL: bad.append(f"{na} enters the seal ring")
            for nb, b in boxes[i + 1:]:
                if a.overlaps(b) and not (na.startswith("IO") and nb.startswith("IO")): bad.append(f"{na} overlaps {nb}")
        self.draw(margins)
        return self.W * self.H / 1e6, bad
    def draw(self, margins):
        W, H = self.W, self.H
        fig, ax = plt.subplots(figsize=(7, 7 * H / W)); ax.add_patch(Rectangle((0, 0), W, H, fill=False, lw=2, ec="k"))
        ax.add_patch(Rectangle((SEAL, SEAL), W - 2 * SEAL, H - 2 * SEAL, fill=False, lw=0.8, ec="0.6", ls="--"))
        L, B, R, T = margins; ax.add_patch(Rectangle((L, B), W - L - R, H - B - T, fill=False, lw=0.6, ec="#36c", ls=":"))
        for x, y, w, h, lbl, ph in self.rects:
            ax.add_patch(Rectangle((x, y), w, h, fc=("#f5d6a8" if ph else "#a8c8f0"), ec="k", lw=1, hatch=("//" if ph else None)))
            ax.text(x + w / 2, y + h / 2, lbl, ha="center", va="center", fontsize=8)
        for nm, cn, x, y in self.ios:
            col = "#b58ad8" if "Analog" in cn else ("#d88a8a" if "Vdd" in cn else "#8ab8d8")
            ax.add_patch(Rectangle((x, y), IO_PITCH, IO_DEPTH, fc=col, ec="k", lw=0.5))
            ax.add_patch(Rectangle((x + 5, y + IO_DEPTH + 5), IO_PAD, IO_PAD, fc="#888", ec="k", lw=0.4))
            ax.text(x + IO_PITCH / 2, y + IO_DEPTH / 2, nm, ha="center", va="center", fontsize=4.5, rotation=90)
        for nm, x, y in self.pads:
            col = "#3a7" if nm.startswith("G") else "#d33"
            ax.add_patch(Rectangle((x - RF_PAD / 2, y - RF_PAD / 2), RF_PAD, RF_PAD, fc=col, ec="k", lw=0.5))
            ax.text(x, y, nm, ha="center", va="center", fontsize=4.5, color="w")
        for k, cx, cy, w, h in self.coils:
            ax.add_patch(Rectangle((cx - w / 2, cy - h / 2), w, h, fc="#fff3c4", ec="#c90", lw=1))
            ax.text(cx, cy, f"ESD\ncoil {k.upper()}", ha="center", va="center", fontsize=6)
        ax.set_xlim(-20, W + 20); ax.set_ylim(-20, H + 20); ax.set_aspect("equal"); ax.set_xlabel("um")
        ax.set_title(f"{self.name}: {W:.0f} x {H:.0f} um = {W*H/1e6:.2f} mm2  (top: IHP IO cells; red/green: custom RF pads)", fontsize=8.5)
        fig.tight_layout(); fig.savefig(os.path.join(HERE, f"floorplan_v2_{self.name}.png"), dpi=170); plt.close(fig)

def test_chip():
    L, B, R, T = 200.0, 220.0, 220.0, TOP_M
    W = L + 860 + R; H = B + 548 + 40 + 150 + 40 + 640 + T
    c = Chip("test_chip", W, H)
    lo_y = H - T - 640
    c.block("lo_core", L, lo_y, "LO core"); c.block("lodrv", L + 235 - 75, lo_y - 40 - 150, "LO drv")
    c.block("rx_tile", L, B, "RX tile"); c.block("tx_ch", W - R - 440, B + 60, "TX channel")
    io = ["GND", "VTUNE", "BSEL", "IFP", "IFN", "VCC", "GND", "IREF", "EN", "VCC", "GND"]
    c.io_segment_top(io, (W - len(io) * IO_PITCH) / 2)
    c.rf_group(["G", "RFIN", "G"], L + 216, "bottom", coil="rx", coil_at=(L + 216 + 150 + 105, SEAL + 5 + 185 / 2))
    tx_c = B + 60 + 200
    c.rf_group(["G", "TXOUT", "G"], tx_c, "right", coil="tx", coil_at=(W - SEAL - 5 - 170 / 2, tx_c + 150 + 100))
    c.rf_group(["G", "PLLP", "G", "PLLN", "G"], lo_y + 311, "left")
    return c.finish((L, B, R, T))

def full_chip():
    L, R, T = 200.0, 220.0, TOP_M; B = RF_EDGE + RF_PAD / 2 + 10 + 185 + 15         # coils behind the RX pads
    tiles_w = 4 * 290 + 3 * 40; core_w = max(tiles_w, 860 + 40 + 440)
    W = L + core_w + R; H = B + 548 + 40 + 150 + 60 + 820 + T
    c = Chip("full_chip", W, H)
    tx0 = (W - L - R - tiles_w) / 2 + L
    for i in range(4): c.block("rx_tile", tx0 + i * 330, B, f"RX{i+1}")
    hy = B + 548 + 40
    for i in range(4): c.block("lodrv", tx0 + i * 330 + 235 - 75, hy, f"drv{i+1}")
    lo_y = hy + 150 + 60; c.block("lo_core", L, lo_y + 180, "LO core")
    c.block("tx_ch", W - R - 440, lo_y + 420, "TX1"); c.block("tx_ch", W - R - 440, lo_y, "TX2")
    io = ["GND", "VTUNE", "BSEL", "IF1P", "IF1N", "IF2P", "IF2N", "VCC", "GND", "IF3P", "IF3N", "IF4P", "IF4N", "VCC", "GND", "EN1", "EN2", "VCC"]
    c.io_segment_top(io, (W - len(io) * IO_PITCH) / 2)
    for i in range(4):
        xr = tx0 + i * 330 + 216
        # coil beside the signal path (RFIN at x0+216 within the tile): centred at x0+102, ~20 um clear of the trace
        c.rf_group(["G", f"RF{i+1}", "G"], xr, "bottom", coil="rx", coil_at=(tx0 + i * 330 + 102, RF_EDGE + RF_PAD / 2 + 10 + 185 / 2))
    ty1 = lo_y + 420 + 200                      # TX1 pads level with TX1; each coil below its own pad group, staggered
    for k, ty in ((1, ty1), (2, ty1 - 490)):
        c.rf_group(["G", f"TX{k}", "G"], ty, "right", coil="tx", coil_at=(W - SEAL - 5 - 170 / 2, ty - 140 - 10 - 170 / 2))
    c.rf_group(["G", "PLLP", "G", "PLLN", "G"], lo_y + 180 + 311, "left")
    return c.finish((L, B, R, T))

if __name__ == "__main__":   # usage: python3 floorplan/floorplan_v2.py   (from the repository root, inside IIC-OSIC-TOOLS)
    for name, fn in (("test_chip", test_chip), ("full_chip", full_chip)):
        a, bad = fn(); print(f"{name}: {a:.2f} mm2, checks: {'OK' if not bad else bad[:8]}")
