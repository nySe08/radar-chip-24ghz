"""tile_place.py - RX channel tile, step 1: placement of every device (LNA vertical, mixer, LO driver).
Origin bottom-left; RF input enters at the bottom, LO from the top. Width <= 300 um."""
import ihp; pya = ihp.pya
ly = pya.Layout(); ly.dbu = 0.001
top = ly.create_cell("rx_tile")
DEV = {}
def place(key, name, x, y, rot=0, **p):
    if name in ("rppd", "rhigh", "rsil"): p = dict(p, Calculate="R")
    DEV[key] = top.insert(pya.DCellInstArray(ihp.pcell(ly, name, **p), pya.DCplxTrans(1, rot, False, round(x/0.005)*0.005, round(y/0.005)*0.005)))
MIM = lambda w: dict(w=f"{w}u", l=f"{w}u")
# ---------------- LNA (vertical: Lb leads up, Lc leads down, RF core in the band between) ----------------
place("Lb", "inductor2", 80.5, 161.9, rot=180, w="7u", s="2.1u", d="68.66u", nr_r=2, subE=False)     # y 0..162, leads at the top
place("Lc", "inductor2", 80.5, 233.0, w="5u", s="2.1u", d="55.83u", nr_r=2, subE=False)             # y 232..373, leads at the bottom
place("Q1", "npn13G2", 86.0, 176.0, Nx=8)            # base (bottom) faces Lb's lead
place("Q2", "npn13G2", 86.0, 208.0, Nx=8)            # collector (top) faces Lc's lead
place("Cin", "rfcmim", 175, 8, **MIM(33))            # near the RF pad, bottom of the side column
place("Ccas1", "rfcmim", 172, 172, **MIM(33))        # cascode base bypass, level with Q2
place("Ccas2", "rfcmim", 222, 172, **MIM(33))
place("Cout", "rfcmim", 128, 214, **MIM(7))          # out node -> mixer link
place("RP", "rppd", 113, 222, rot=90, w="2u", l="5.37u")
place("Cdec1", "rfcmim", 172, 245, **MIM(33))        # VCC decoupling next to Lc's VCC lead
place("Cdec2", "rfcmim", 222, 245, **MIM(33))
place("R1", "rppd", 268, 175, w="1u", l="22.95u"); place("R2", "rhigh", 282, 180, w="1u", l="13.30u")
# bias mirror (side column, between Cin and Ccas)
place("Qr", "npn13G2", 180, 70, Nx=1); place("Qf", "npn13G2", 200, 70, Nx=1)
place("Rref", "rhigh", 222, 62, w="1u", l="28.12u"); place("Rief", "rhigh", 236, 62, w="1u", l="12.03u")
place("Rb", "rppd", 252, 62, w="1u", l="19.08u")
place("Cbn", "rfcmim", 180, 105, **MIM(33))
# ---------------- mixer (above Lc) ----------------
Y = 385
place("Cdc", "rfcmim", 10, Y, **MIM(33)); place("Cb3", "rfcmim", 62, Y, **MIM(33))
place("Rt", "rsil", 114, Y, w="1u", l="7.55u"); place("Rrf", "rppd", 120, Y, w="1u", l="4.37u")
place("Qrf", "npn13G2", 130, Y + 4, Nx=1); place("Rerf", "rsil", 140, Y, w="1u", l="38.2u")
place("Q3", "npn13G2", 152, Y + 4, Nx=4); place("Re", "rsil", 170, Y, w="1u", l="9.55u")
place("Q4", "npn13G2", 152, Y + 24, Nx=2); place("Q5", "npn13G2", 166, Y + 24, Nx=2)
place("RLp", "rppd", 180, Y + 20, w="2u", l="2.05u"); place("RLn", "rppd", 186, Y + 20, w="2u", l="2.05u")
place("CLp", "cmim", 196, Y, **MIM(34.3)); place("CLn", "cmim", 236, Y, **MIM(34.3))
place("Cvl", "rfcmim", 196, Y + 42, **MIM(33))
place("Rd1", "rppd", 246, Y + 40, w="1u", l="22.95u"); place("Rd2", "rhigh", 252, Y + 40, w="1u", l="13.30u")
place("Rl1", "rppd", 260, Y + 40, w="1u", l="7.47u"); place("Rl2", "rppd", 266, Y + 40, w="1u", l="7.47u")
# ---------------- channel LO driver (top; LO arrives from the H-tree above) ----------------
Y2 = 478
place("Ci1", "rfcmim", 10, Y2, **MIM(25)); place("Ci2", "rfcmim", 52, Y2, **MIM(25))
place("Cvb", "rfcmim", 94, Y2, **MIM(33))
place("Rv1", "rppd", 146, Y2, w="1u", l="17.53u"); place("Rv2", "rppd", 152, Y2, w="1u", l="20.63u")
place("Rb1", "rppd", 158, Y2, w="1u", l="19.08u"); place("Rb2", "rppd", 164, Y2, w="1u", l="19.08u")
place("Qa", "npn13G2", 176, Y2 + 6, Nx=2); place("Qb", "npn13G2", 190, Y2 + 6, Nx=2)
place("Rtail", "rppd", 204, Y2, w="2u", l="0.79u")
place("RD1", "rppd", 212, Y2, w="2u", l="1.28u"); place("RD2", "rppd", 218, Y2, w="2u", l="1.28u")
place("Cc1", "rfcmim", 230, Y2, **MIM(12)); place("Cc2", "rfcmim", 262, Y2, **MIM(12))
# substrate taps
for i, (x, y) in enumerate(((60, 200), (120, 190), (205, 90), (116, 440), (200, 500))):
    place(f"ptap{i}", "ptap1", x, y, w="2u", l="2u")
# ---------------- checks ----------------
boxes = {k: v.dbbox() for k, v in DEV.items()}
bad = []
for i, a in enumerate(boxes):
    for b in list(boxes)[i+1:]:
        if boxes[a].enlarged(1.0, 1.0).overlaps(boxes[b]): bad.append((a, b))
bb = top.dbbox()
print(f"tile size: {bb.width():.0f} x {bb.height():.0f} um  ({len(DEV)} devices), overlaps: {bad if bad else 'none'}")
ly.write("rx_tile_place.gds")
