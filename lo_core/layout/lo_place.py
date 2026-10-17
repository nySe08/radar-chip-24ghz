"""lo_place.py - LO core placement: VCO (centre-top), emitter followers, RX pre-driver (H-tree root at the bottom),
TX pre-driver (right, output up to the PAs), divider driver + /4 divider (left, output to the PLL pads)."""
from layoutlib import Builder
B = Builder("lo_core"); place = B.place
MIM = lambda w: dict(w=f"{w}u", l=f"{w}u")
def R(key, kind, x, y, w, l, rot=0): place(key, kind, x, y, rot=rot, w=f"{w}u", l=f"{l}u")
X0 = 440.0                                              # symmetry axis of the VCO / emitter followers / RX pre-driver
# ---------------- VCO ----------------
place("Lvco", "inductor3", X0, 400, w="6u", s="2.1u", d="70.88u", nr_r=2, subE=False)     # leads down at y~400
place("Qvco_6", "npn13G2", X0 - 26, 378, Nx=4); place("Qvco_7", "npn13G2", X0 + 14, 378, Nx=4)
place("Cvco_b6", "rfcmim", X0 - 48, 342, **MIM(11.5)); place("Cvco_b7", "rfcmim", X0 + 30, 342, **MIM(11.5))
place("Cvar", "SVaricap", X0 - 6, 318, w="9.74u", l="0.3u", Nx=10)
place("Cvco_cv1", "rfcmim", X0 - 72, 312, **MIM(11.3)); place("Cvco_cv2", "rfcmim", X0 + 54, 312, **MIM(11.3))
R("Rvco_g1", "rhigh", X0 - 22, 300, 1, 7.0); R("Rvco_g2", "rhigh", X0 + 21, 300, 1, 7.0)
R("Rvco_b6", "rppd", X0 - 60, 370, 1, 7.47); R("Rvco_b7", "rppd", X0 + 59, 370, 1, 7.47)
R("Rvco_tail", "rppd", X0 - 1, 360, 2, 1.41)
place("Cvco_gb", "rfcmim", X0 - 134, 330, **MIM(33)); R("Rvco_gb1", "rhigh", X0 - 88, 330, 1, 13.30); R("Rvco_gb2", "rhigh", X0 - 84, 330, 1, 13.30)
place("Cvco_bb", "rfcmim", X0 + 92, 330, **MIM(33)); R("Rvco_bb1", "rppd", X0 + 140, 330, 1, 15.21); R("Rvco_bb2", "rppd", X0 + 145, 330, 1, 22.95)
# ---------------- emitter followers ----------------
place("Qef_1", "npn13G2", X0 - 14, 280, Nx=2); place("Qef_2", "npn13G2", X0 + 8, 280, Nx=2)
R("Ref_1", "rppd", X0 - 26, 262, 2, 8.24); R("Ref_2", "rppd", X0 + 23, 262, 2, 8.24)
# ---------------- drivers (generic: inputs from the emitter followers, outputs via 12 um coupling caps) ----------------
def driver(tag, x, y, rtl, rdl, coil=None, coil_xy=None, coil_rot=0):
    up = tag.upper()
    place(f"C{up}_i1", "rfcmim", x - 50, y + 40, **MIM(25)); place(f"C{up}_i2", "rfcmim", x + 22, y + 40, **MIM(25))
    place(f"Q{up}_a", "npn13G2", x - 14, y + 20, Nx=2); place(f"Q{up}_b", "npn13G2", x + 8, y + 20, Nx=2)
    R(f"R{up}_b1", "rppd", x - 24, y - 8, 1, 19.08); R(f"R{up}_b2", "rppd", x + 23, y - 8, 1, 19.08)
    R(f"R{up}_t", "rppd", x - 1, y - 4, 2, rtl)
    R(f"R{up}_d1", "rppd", x - 30, y + 18, 2, rdl); R(f"R{up}_d2", "rppd", x + 27, y + 18, 2, rdl)
    place(f"C{up}_c1", "rfcmim", x - 44, y - 40, **MIM(12)); place(f"C{up}_c2", "rfcmim", x + 26, y - 40, **MIM(12))
    place(f"C{up}_vb", "rfcmim", x - 105, y - 44, **MIM(33)); R(f"R{up}_v1", "rppd", x - 64, y - 30, 1, 17.53); R(f"R{up}_v2", "rppd", x - 59, y - 30, 1, 20.63)
    if coil: place(f"L{up}", "inductor3", *coil_xy, rot=coil_rot, w=f"{coil[0]}u", s="2.1u", d=f"{coil[1]}u", nr_r=2, subE=False)
driver("prx", X0, 160, 0.94, 2.83, coil=(4, 65.36), coil_xy=(X0 + 64, 192), coil_rot=270)       # RX pre-driver, coil to the right
place("Rbl_r1", "rhigh", X0 - 8, 80, w="1u", l="14.0u"); place("Rbl_r2", "rhigh", X0 + 7, 80, w="1u", l="14.0u")
driver("ptx", X0 + 330, 300, 1.86, 2.83, coil=(4, 83.47), coil_xy=(X0 + 330, 420), coil_rot=0)  # TX pre-driver, coil above
place("Rbl_t1", "rhigh", X0 + 291, 225, w="1u", l="14.0u"); place("Rbl_t2", "rhigh", X0 + 361, 225, w="1u", l="14.0u")
driver("ddv", X0 - 200, 230, 1.86, 2.05)                                                           # divider driver (resistive)
# ---------------- /4 divider (left): bias, 4 latches, output stage ----------------
def latch(tag, x, y, nt, rll, re):
    up = tag.upper()
    R(f"R{up}_lp", "rppd", x, y + 22, 2, rll); R(f"R{up}_ln", "rppd", x + 8, y + 22, 2, rll)
    for i, n in enumerate(("d1", "d2", "h1", "h2")): place(f"Q{up}_{n}", "npn13G2", x + i * 10, y + 10, Nx=1)
    place(f"Q{up}_c1", "npn13G2", x + 5, y, Nx=1); place(f"Q{up}_c2", "npn13G2", x + 25, y, Nx=1)
    place(f"Q{up}_t", "npn13G2", x + 13, y - 12, Nx=nt); R(f"R{up}_e", "rppd", x + 33, y - 16, 4, re)
DX = 12
for i, (tag, nt, rll, re) in enumerate((("dm1", 3, 1.79, 1.28), ("ds1", 3, 1.79, 1.28), ("dm2", 2, 2.83, 2.05), ("ds2", 2, 2.83, 2.05))):
    latch(tag, DX, 60 + i * 50, nt, rll, re)
R("Rdiv_ref", "rppd", 60, 20, 1, 11.34); place("Qdiv_br", "npn13G2", 70, 24, Nx=1); R("Rdiv_ebr", "rppd", 80, 20, 2, 2.05)
place("Cdiv_bt", "rfcmim", 95, 20, **MIM(25))
place("Cdiv_k", "rfcmim", 62, 70, **MIM(33)); R("Rdiv_k1", "rppd", 112, 70, 1, 15.21); R("Rdiv_k2", "rppd", 117, 70, 1, 22.95)
R("Rdiv_ck1", "rppd", 122, 70, 1, 7.47); R("Rdiv_ck2", "rppd", 127, 70, 1, 7.47)
place("Cdiv_c1", "rfcmim", 62, 128, **MIM(18.2)); place("Cdiv_c2", "rfcmim", 94, 128, **MIM(18.2))
R("Rdiv_b1", "rppd", 122, 120, 1, 19.08); R("Rdiv_b2", "rppd", 127, 120, 1, 19.08)
place("Cdiv_bo", "rfcmim", 62, 172, **MIM(33)); R("Rdiv_o1", "rppd", 112, 172, 1, 17.14); R("Rdiv_o2", "rhigh", 117, 172, 1, 5.53)
place("Cdiv_o1", "rfcmim", 12, 280, **MIM(18.2)); place("Cdiv_o2", "rfcmim", 44, 280, **MIM(18.2))
R("Rdiv_bo1", "rppd", 76, 274, 1, 19.08); R("Rdiv_bo2", "rppd", 81, 274, 1, 19.08)
place("Qdiv_o1", "npn13G2", 20, 340, Nx=4); place("Qdiv_o2", "npn13G2", 44, 340, Nx=4)
place("Qdiv_to1", "npn13G2", 16, 324, Nx=10); place("Qdiv_to2", "npn13G2", 44, 324, Nx=10)
R("Rdiv_eo1", "rppd", 18, 310, 8, 0.66); R("Rdiv_eo2", "rppd", 46, 310, 8, 0.66)
R("Rdiv_t1", "rppd", 20, 354, 10, 1.66); R("Rdiv_t2", "rppd", 44, 354, 10, 1.66)
# ---------------- checks ----------------
if __name__ == "__main__":
    boxes = {k: v.dbbox() for k, v in B.DEV.items()}
    bad = [(a, b) for i, a in enumerate(boxes) for b in list(boxes)[i+1:] if boxes[a].enlarged(1.0, 1.0).overlaps(boxes[b])]
    bb = B.top.dbbox()
    print(f"{len(B.DEV)} devices placed, block {bb.width():.0f} x {bb.height():.0f} um (x {bb.left:.0f}..{bb.right:.0f}, y {bb.bottom:.0f}..{bb.top:.0f})")
    print("overlaps:", len(bad)); [print("  ", a, b) for a, b in bad[:25]]
    B.ly.write("lo_place.gds")
