#!/usr/bin/env python3
"""
density_preview.py - early warning for IHP's density rules, run on a BLOCK before chip assembly.

IHP's precheck (the foundry's rejection test) contains global density rules, e.g. Metal1..Metal5 35-60 %,
Activ 35-55 %, GatPoly >= 15 %, and window rules (Activ 25-65 % in any 800 x 800 um area). They are judged on the
finished, FILLED chip, so a block cannot pass them on its own - but:
  * a layer ABOVE the maximum cannot be fixed by fill (fill only adds metal): the design must change
    (e.g. cheese a solid ground plane), and that changes parasitics, so do it BEFORE the final extraction;
  * a layer below the minimum is normally fine: IHP's filler.py adds it. Fill under a solid ground plane is shielded
    from RF lines above it; fill between the plane and the RF lines must be kept away from them or extracted.
usage: python3 density_preview.py lo_core.gds [--window 800 --step 200]
"""
import argparse, sys
import klayout.db as pya

RULES = {  # name: ((layer, datatype), global min %, global max %)   from IHP precheck_rules.md
    "Activ": ((1, 0), 35, 55), "GatPoly": ((5, 0), 15, None), "Metal1": ((8, 0), 35, 60), "Metal2": ((10, 0), 35, 60),
    "Metal3": ((30, 0), 35, 60), "Metal4": ((50, 0), 35, 60), "Metal5": ((67, 0), 35, 60),
    "TopMetal1": ((126, 0), None, None), "TopMetal2": ((134, 0), None, None)}

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("gds"); ap.add_argument("--cell"); ap.add_argument("--window", type=float, default=800.0)
    ap.add_argument("--step", type=float, default=200.0); ap.add_argument("--margin", type=float, default=5.0,
                    help="aim this many %% below a maximum, so the chip keeps margin (default 5)")
    a = ap.parse_args()
    ly = pya.Layout(); ly.read(a.gds); top = ly.cell(a.cell) if a.cell else ly.top_cell(); bb = top.dbbox(); A = bb.area()
    print(f"density preview: {top.name}, {bb.width():.0f} x {bb.height():.0f} um (before fill)")
    hard = 0
    for name, ((l, d), lo, hi) in RULES.items():
        li = ly.find_layer(l, d)
        r = pya.Region(top.begin_shapes_rec(li)) if li is not None else pya.Region(); r.merge()
        g = r.area() * ly.dbu ** 2 / A * 100
        # densest window (block-local view of the window rules)
        w = min(a.window, bb.width(), bb.height()); wmax = 0.0; y = bb.bottom
        while y + w <= bb.top + 1e-6:
            x = bb.left
            while x + w <= bb.right + 1e-6:
                win = pya.Region(pya.DBox(x, y, x + w, y + w).to_itype(ly.dbu))
                wmax = max(wmax, (r & win).area() * ly.dbu ** 2 / (w * w) * 100); x += a.step
            y += a.step
        if hi is not None and g > hi - a.margin:
            verdict = f"TOO DENSE (max {hi} %): fill cannot fix this - reduce it in the design (cheesing/slots)"; hard += 1
        elif lo is not None and g < lo:
            verdict = f"below min {lo} %: fill adds this (keep fill away from RF lines/coils, or extract with fill)"
        else:
            verdict = "within the global rule" if (lo or hi) else "no global density rule"
        print(f"  {name:9s} global {g:5.1f} %, densest {w:.0f} um window {wmax:5.1f} %  -> {verdict}")
    print(f"\nverdict: {'no layer needs a design change' if not hard else f'{hard} layer(s) need a design change before the final extraction'}")
    sys.exit(1 if hard else 0)

if __name__ == "__main__":
    main()
