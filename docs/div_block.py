import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
fig, ax = plt.subplots(figsize=(13, 4.6)); ax.set_xlim(0, 13.3); ax.set_ylim(0, 4.6); ax.axis("off")
def box(x, y, w, h, t, s="", fc="#eef2fb", ec="#3b4f8f"):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.08", fc=fc, ec=ec, lw=1.3))
    ax.text(x+w/2, y+h/2+(0.15 if s else 0), t, ha="center", va="center", fontsize=11, weight="bold")
    if s: ax.text(x+w/2, y+h/2-0.22, s, ha="center", va="center", fontsize=8.5, color="0.3")
def arr(x1, y1, x2, y2, txt=None, dy=0.15):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1), arrowprops=dict(arrowstyle="->", lw=1.3))
    if txt: ax.text((x1+x2)/2, y1+dy, txt, ha="center", fontsize=8.5, color="0.25")
# frames for the two /2 stages
for x, lab in [(1.5, "Stage 1: ÷2  (24 GHz → 12 GHz)\nIt = 1.5 mA per latch"), (6.3, "Stage 2: ÷2  (12 GHz → 6 GHz)\nIt = 1 mA per latch")]:
    ax.add_patch(FancyBboxPatch((x, 1.0), 4.2, 2.6, boxstyle="round,pad=0.02,rounding_size=0.1", fc="none", ec="0.55", ls="--"))
    ax.text(x+2.1, 3.85, lab, ha="center", fontsize=9.5, color="0.25")
box(1.8, 1.8, 1.5, 1.0, "Master", "latch")
box(3.9, 1.8, 1.5, 1.0, "Slave", "latch")
box(6.6, 1.8, 1.5, 1.0, "Master", "latch")
box(8.7, 1.8, 1.5, 1.0, "Slave", "latch")
box(10.95, 1.8, 1.4, 1.0, "Output", "driver 8 mA", fc="#fbf1e6", ec="#8a5a1f")
# data paths
arr(3.3, 2.3, 3.9, 2.3, "Q")
arr(8.1, 2.3, 8.7, 2.3, "Q")
# inverted feedback loops
for xs, xm in [(4.65, 2.55), (9.45, 7.35)]:
    ax.plot([xs, xs, xm, xm], [1.8, 1.25, 1.25, 1.8], color="#b03030", lw=1.3)
    ax.annotate("", xy=(xm, 1.8), xytext=(xm, 1.55), arrowprops=dict(arrowstyle="->", lw=1.3, color="#b03030"))
    ax.text((xs+xm)/2, 1.07, "Q̄ fed back to D  (inversion → toggles)", ha="center", fontsize=8, color="#b03030")
# clock in
ax.text(0.1, 3.05, "CLK 24 GHz\nfrom LO buffer\n(driver 3)", fontsize=8.5, va="center")
arr(1.0, 2.6, 1.8, 2.6); ax.text(1.4, 2.72, "CLK", fontsize=8, ha="center")
ax.plot([1.2, 1.2, 4.65, 4.65], [2.6, 3.25, 3.25, 2.8], color="0.3", lw=1.0, ls=":")
ax.text(3.2, 3.33, "CLK̄ to slave (opposite phase)", fontsize=7.5, ha="center", color="0.3")
# stage 1 -> stage 2 clock
arr(5.4, 2.6, 6.6, 2.6); ax.text(6.0, 2.75, "12 GHz\nAC-coupled", fontsize=7.5, ha="center", color="0.3")
arr(10.2, 2.3, 10.95, 2.3); ax.text(10.57, 2.45, "6 GHz", fontsize=7.5, ha="center", color="0.3")
arr(12.35, 2.3, 12.95, 2.3)
ax.text(12.6, 1.25, "pads → 50 Ω\nADF4159 PLL\n−8 dBm per pin", fontsize=8, ha="center")
ax.text(6.5, 0.35, "Each latch is the CML circuit shown separately. Two latches with opposite clocks = one flip-flop; "
        "feeding its inverted output back makes it toggle every clock cycle (÷2).", ha="center", fontsize=9, color="0.25")
plt.tight_layout(); plt.savefig("div4_block.png", dpi=170, bbox_inches="tight")
