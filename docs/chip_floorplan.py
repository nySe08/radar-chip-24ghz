"""chip_floorplan.py - floorplan of the 2TX/4RX 24 GHz phased-array radar chip (IHP SG13G2).
Block sizes estimated from the LNA layout (generator) and the inductor sizes; pads 80x80 um.
Run: python3 chip_floorplan.py  -> chip_floorplan.png + pad list"""
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle
W, H = 2000, 1900                     # die size [um]
PAD, PITCH_RF, PITCH_DC = 80, 150, 110
fig, ax = plt.subplots(figsize=(13, 12.5)); ax.set_aspect("equal")
ax.add_patch(Rectangle((0, 0), W, H, fc="#f4f6f8", ec="k", lw=1.5))
pads = []
def pad(x, y, name, kind):
    col = {"S": "#e8a33d", "G": "#9aa6b2", "DC": "#c9a0dc", "IF": "#7fc8a9"}[kind]
    ax.add_patch(Rectangle((x - PAD/2, y - PAD/2), PAD, PAD, fc=col, ec="k", lw=0.8))
    ax.text(x, y, name, ha="center", va="center", fontsize=6.5, rotation=0 if abs(y - H/2) > H/2 - 120 else 90)
    pads.append((name, kind, x, y))
def block(x, y, w, h, name, col, fs=8):
    ax.add_patch(Rectangle((x, y), w, h, fc=col, ec="k", lw=1)); ax.text(x + w/2, y + h/2, name, ha="center", va="center", fontsize=fs)
# ---- bottom edge: 4 RX GSG with shared grounds (G S G S G S G S G)
xr = [W/2 - 4*PITCH_RF*1.0 + i*PITCH_RF for i in range(9)]
xr = [W/2 + (i - 4)*PITCH_RF*1.1 for i in range(9)]
for i, x in enumerate(xr): pad(x, 70, f"RX{i//2+1}" if i % 2 else "G", "S" if i % 2 else "G")
# ---- top edge: 2 TX GSG with shared grounds (G S G S G), far apart from RX
xt = [W/2 + (i - 2)*PITCH_RF*1.4 for i in range(5)]
for i, x in enumerate(xt): pad(x, H - 70, f"TX{i//2+1}" if i % 2 else "G", "S" if i % 2 else "G")
# ---- left / right edges: IF outputs (channels 1,2 left; 3,4 right) and DC
left  = ["IF1+", "IF1-", "IF2+", "IF2-", "VCC_RX", "IREF_RX", "GND", "VTUNE", "PLL+", "PLL-", "GND", "VCC_LO", "EN1B"]
right = ["IF4+", "IF4-", "IF3+", "IF3-", "VCC_RX", "GND", "VCC_TX", "IREF_TX", "GND", "VCC_TX", "GND", "VCC_LO", "EN2B"]
for i, n in enumerate(left):  pad(70, 260 + i*PITCH_DC, n, "IF" if n.startswith("IF") else ("G" if n == "GND" else "DC"))
for i, n in enumerate(right): pad(W - 70, 260 + i*PITCH_DC, n, "IF" if n.startswith("IF") else ("G" if n == "GND" else "DC"))
# ---- RX channel tiles (LNA + mixer + channel LO driver), one per RX pad, identical
TW, TH = 300, 560
for k in range(4):
    xs = xr[2*k + 1]
    block(xs - TW/2, 150, TW, 340, f"LNA {k+1}\n(Lb, Lc,\nQ1/Q2, bias)", "#cfe8ff", 8)
    block(xs - TW/2, 500, TW, 110, f"mixer {k+1}", "#d9f2d0", 8)
    block(xs - TW/2, 620, TW, 90, f"ch. LO driver {k+1}", "#fff2cc", 7)
# ---- LO H-tree (symmetric) from the RX pre-driver to the 4 channel drivers
yt, yb = 830, 710
xc = W/2
block(xc - 90, 840, 180, 90, "RX pre-driver", "#ffe08a", 7.5)
ax.plot([xc, xc], [840, yt], "r-", lw=2.5)
for side in (-1, 1):
    xm = (xr[1] + xr[3]) / 2 if side < 0 else (xr[5] + xr[7]) / 2
    ax.plot([xc, xm], [yt, yt], "r-", lw=2.5); ax.plot([xm, xm], [yt, 770], "r-", lw=2.5)
    a, b = (xr[1], xr[3]) if side < 0 else (xr[5], xr[7])
    ax.plot([a, b], [770, 770], "r-", lw=2.5)
    for x in (a, b): ax.plot([x, x], [770, yb], "r-", lw=2.5)
ax.text(xc + 110, 780, "LO H-tree:\nequal length to all 4 channels", color="r", fontsize=8)
# ---- LO core: VCO, emitter followers, divider, TX pre-driver
block(xc - 160, 960, 320, 260, "VCO\n(centre-tapped\ninductor3 tank,\nvaractor)", "#f7c6c6", 8.5)
block(xc - 160, 1230, 320, 60, "emitter followers", "#fff2cc", 7.5)
block(xc + 200, 980, 220, 180, "divider /4\n+ driver", "#e6d6f0", 8)
ax.plot([xc + 420, W - 120], [1070, 1070], ":", color="purple"); ax.text(xc + 470, 1085, "to PLL pads", fontsize=7, color="purple")
block(xc - 120, 1300, 240, 80, "TX pre-driver", "#ffe08a", 7.5)
for k, xs in enumerate((xt[1], xt[3])):
    block(xs - 160, 1430, 320, 300, f"PA {k+1}\n(enable switch)\n+ PA driver", "#ffd6b0", 8.5)
    ax.plot([xc, xs], [1380, 1430], "r-", lw=2)
# ---- isolation: ground ring between TX and RX sections, VCC domains
ax.plot([140, W - 140], [1265 - 340, 1265 - 340], color="#555", lw=0, alpha=0)
ax.add_patch(Rectangle((140, 140), W - 280, 600, fc="none", ec="#1f77b4", ls="--", lw=1.4))
ax.text(150, 745, "RX domain (VCC_RX)", color="#1f77b4", fontsize=8.5)
ax.add_patch(Rectangle((140, 1410), W - 280, 345, fc="none", ec="#d62728", ls="--", lw=1.4))
ax.text(150, 1760, "TX domain (VCC_TX)", color="#d62728", fontsize=8.5)
ax.add_patch(Rectangle((560, 820), W - 1120, 570, fc="none", ec="#2ca02c", ls="--", lw=1.4))
ax.text(570, 1395, "LO domain (VCC_LO)", color="#2ca02c", fontsize=8.5)
ax.annotate("", xy=(W - 260, 1420), xytext=(W - 260, 730), arrowprops=dict(arrowstyle="<->", color="k"))
ax.text(W - 250, 1080, "~0.7 mm\nTX-RX\nseparation", fontsize=8)
ax.set_xlim(-20, W + 20); ax.set_ylim(-20, H + 20); ax.set_xlabel("x [um]"); ax.set_ylabel("y [um]")
ax.set_title(f"2TX / 4RX 24 GHz phased-array radar chip - floorplan ({W/1000:.1f} x {H/1000:.1f} mm, {len(pads)} pads)", fontsize=12)
plt.tight_layout(); plt.savefig("chip_floorplan.png", dpi=140)
kinds = {}
for n, k, x, y in pads: kinds[k] = kinds.get(k, 0) + 1
print("die %.1f x %.1f mm = %.2f mm2, pads: %d" % (W/1000, H/1000, W*H/1e6, len(pads)), kinds)
