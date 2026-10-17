"""layoutlib.py - shared layout helpers for the radar chip generators (IHP SG13G2, KLayout Python API).
Extracted from the verified LNA generator: PCell placement on the 5 nm grid, label-based pin finding,
wires / rects / via stacks, ground vias + patches, slotted Metal4 ground plane, connectivity check, mini-DRC."""
import ihp
pya = ihp.pya
GRID = 0.005
ORDER = ["Metal1", "Metal2", "Metal3", "Metal4", "Metal5", "TopMetal1", "TopMetal2"]
STACK = [("Metal1", 8), ("Via1", 19), ("Metal2", 10), ("Via2", 29), ("Metal3", 30), ("Via3", 49), ("Metal4", 50),
         ("Via4", 66), ("Metal5", 67), ("TopVia1", 125), ("TopMetal1", 126), ("TopVia2", 133), ("TopMetal2", 134)]
def G(v): return round(round(v / GRID) * GRID, 3)

class Builder:
    def __init__(self, name):
        self.ly = pya.Layout(); self.ly.dbu = 0.001
        self.top = self.ly.create_cell(name)
        self.LY = {n: self.ly.layer(*v) for n, v in ihp.L.items()}
        self.DEV, self.VIAS, self.GPATCH = {}, [], []
    # ---------------- devices ----------------
    def place(self, key, name, x, y, rot=0, **p):
        if name in ("rppd", "rhigh", "rsil"):                      # resistor PCells: length is given, R is derived
            p = dict(p, Calculate="R")
            probe = self.ly.cell(ihp.pcell(self.ly, name, **p))
            for li in self.ly.layer_indexes():
                for sh in probe.shapes(li).each():
                    if sh.is_text() and " r=" in sh.text.string: p["R"] = sh.text.string.split("r=")[1].strip()
        self.DEV[key] = self.top.insert(pya.DCellInstArray(ihp.pcell(self.ly, name, **p), pya.DCplxTrans(1, rot, False, G(x), G(y))))
    def pin(self, key, label):
        inst = self.DEV[key]; cell = self.ly.cell(inst.cell_index); pos = None
        for li in self.ly.layer_indexes():
            si = cell.begin_shapes_rec(li)
            while not si.at_end():
                s = si.shape()
                if s.is_text() and s.text.string.strip() == label: pos = si.dtrans() * s.dtext.trans.disp; break
                si.next()
            if pos: break
        if pos is None: raise KeyError(f"{key}: no label {label}")
        best = None
        for li in self.ly.layer_indexes():
            if self.ly.get_info(li).datatype != 2: continue
            si = cell.begin_shapes_rec(li)
            while not si.at_end():
                b = si.shape().dbbox().transformed(si.dtrans())
                if b.contains(pya.DPoint(pos.x, pos.y)) and (best is None or b.area() < best.area()): best = b
                si.next()
        return best.transformed(inst.dcplx_trans)
    def pins_of(self, key, gds_layer):
        inst = self.DEV[key]; cell = self.ly.cell(inst.cell_index); li = self.ly.find_layer(gds_layer, 2); out = []
        if li is None: return out
        si = cell.begin_shapes_rec(li)
        while not si.at_end():
            b = si.shape().dbbox().transformed(si.dtrans()).transformed(inst.dcplx_trans)
            if b not in out: out.append(b)
            si.next()
        return out
    def ends(self, key):            # resistor end pins (Metal1), sorted bottom->top or left->right
        p = self.pins_of(key, 8)
        horiz = abs(p[0].center().x - p[-1].center().x) > abs(p[0].center().y - p[-1].center().y)
        return sorted(p, key=lambda b: b.center().x if horiz else b.center().y)
    # ---------------- drawing ----------------
    def rect(self, layer, x1, y1, x2, y2):
        x1, y1, x2, y2 = G(x1), G(y1), G(x2), G(y2)
        self.top.shapes(self.LY[layer]).insert(pya.DBox(min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2)))
    def wire(self, layer, pts, w, start_ext=None, end_ext=None):
        pts = [pya.DPoint(G(p[0]), G(p[1])) for p in pts]
        self.top.shapes(self.LY[layer]).insert(pya.DPath(pts, w, w/2 if start_ext is None else start_ext, w/2 if end_ext is None else end_ext))
    def via(self, x, y, b, t, n=4, nt=2):
        x, y = G(x), G(y)
        p = dict(b_layer=b, t_layer=t, vn_columns=n, vn_rows=n, vt1_columns=nt, vt1_rows=nt, vt2_columns=nt, vt2_rows=nt)
        self.top.insert(pya.DCellInstArray(ihp.pcell(self.ly, "via_stack", **p), pya.DCplxTrans(1, 0, False, x, y)))
        if n == 1:                                       # single-cut stacks: landings alone are below the min metal area (0.144 um2)
            for name in ("Metal2", "Metal3", "Metal4", "Metal5"):
                if ORDER.index(b) <= ORDER.index(name) <= ORDER.index(t): self.rect(name, x - 0.2, y - 0.2, x + 0.2, y + 0.2)
        self.VIAS.append((x, y, b, t))
    def gnd_via(self, x, y, layer, patch=None):
        x, y = G(x), G(y)                                            # snap first: the patch must be on-grid too
        if ORDER.index(layer) < 3: self.via(x, y, layer, "Metal4")
        else: self.via(x, y, "Metal4", layer)
        p = patch or (x - 3, y - 3, x + 3, y + 3)
        self.GPATCH.append(tuple(G(v) for v in p))
    def ring_ground(self, key, cutout_keys=(), coil_keys=()):
        """Ground a MIM's substrate ring (TIE). If the MIM sits in a plane cut-out, strap out in the shortest of the four
        directions whose end lands on real plane: outside every cut-out, coil area and signal-via hole."""
        t = self.pin(key, "TIE"); tc = t.center()
        if key not in cutout_keys: self.gnd_via(tc.x, tc.y, "Metal1"); return
        cuts = [self.DEV[k].dbbox().enlarged(3.0, 3.0) for k in cutout_keys] + [self.DEV[k].dbbox() for k in coil_keys]
        cuts += [pya.DBox(x - 4, y - 4, x + 4, y + 4) for (x, y, b, tt) in self.VIAS if "Metal4" not in (b, tt) and ORDER.index(b) < 3 < ORDER.index(tt)]
        own = self.DEV[key].dbbox().enlarged(3.0, 3.0); best = None
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            d = {(1, 0): own.right - tc.x, (-1, 0): tc.x - own.left, (0, 1): own.top - tc.y, (0, -1): tc.y - own.bottom}[(dx, dy)] + 6.0
            end = pya.DBox(tc.x + dx * d - 3, tc.y + dy * d - 3, tc.x + dx * d + 3, tc.y + dy * d + 3)
            if any(c.overlaps(end) for c in cuts): continue
            if best is None or d < best[0]: best = (d, dx, dy)
        d, dx, dy = best
        if dx: patch = (min(tc.x, tc.x + dx * (d + 3)), tc.y - 3, max(tc.x, tc.x + dx * (d + 3)), tc.y + 3)
        else: patch = (tc.x - 3, min(tc.y, tc.y + dy * (d + 3)), tc.x + 3, max(tc.y, tc.y + dy * (d + 3)))
        self.gnd_via(tc.x, tc.y, "Metal1", patch=patch)
    def min_area(self, rules=(("Metal2", 0.144), ("Metal3", 0.144), ("Metal4", 0.144), ("Metal5", 0.144))):
        """IHP M2.d .. M5.d: minimum metal area (whole merged polygons)"""
        bad = 0
        for name, amin in rules:
            r = pya.Region(self.top.begin_shapes_rec(self.LY[name])); r.merge()
            small = [p for p in r.each() if p.area() * self.ly.dbu ** 2 < amin]; bad += len(small)
            for p in small[:3]: print(f"  {name} area < {amin} um2 at {p.bbox().to_dtype(self.ly.dbu)}")
        print(f"min-area check: {'CLEAN' if not bad else f'{bad} findings'}"); return bad
    def coil_continuity(self, keys):
        """every coil's LA/LB(/LC) must be ONE piece of metal (its own shapes + any top-level cuts on it). Catches open PCells."""
        bad = 0
        for k in keys:
            inst = self.DEV[k]; bb = inst.dbbox()
            ly2 = pya.Layout(); ly2.dbu = self.ly.dbu; t2 = ly2.create_cell("c")
            for (g, d) in ((126, 0), (133, 0), (134, 0)):
                r = pya.Region(self.top.begin_shapes_rec(self.ly.find_layer(g, d))) & pya.Region(bb.to_itype(self.ly.dbu))
                t2.shapes(ly2.layer(g, d)).insert(r)
            l2n = pya.LayoutToNetlist(pya.RecursiveShapeIterator(ly2, t2, []))
            L = {n: l2n.make_layer(ly2.layer(g, 0), n) for n, g in (("TM1", 126), ("TV2", 133), ("TM2", 134))}
            for n in L: l2n.connect(L[n])
            l2n.connect(L["TM1"], L["TV2"]); l2n.connect(L["TV2"], L["TM2"]); l2n.extract_netlist()
            ids = []
            for lab in ("LA", "LB", "LC"):
                try: p = self.pin(k, lab)
                except Exception: continue
                c = p.center(); net = None
                for n in ("TM1", "TM2"):
                    net = net or l2n.probe_net(L[n], pya.DPoint(c.x, c.y + 0.5))
                ids.append(net.cluster_id if net else None)
            ok = len(set(ids)) == 1 and None not in ids
            if not ok: bad += 1; print(f"  coil {k}: terminals NOT connected ({ids}) - open coil!")
        print(f"coil continuity: {'CLEAN' if not bad else f'{bad} open coil(s)'}"); return bad
    def coil_topology(self, min_paths):
        """each coil's shortest LA-LB metal path must be >= its minimum (um): an OPEN coil has no path, a SHORTED one a
        short path. Connectivity alone cannot tell a shorted coil from a correct one (and LVS never looks inside a coil)."""
        import coil1t
        bad = 0
        for k, lmin in min_paths.items():
            cell = self.ly.cell(self.DEV[k].cell_index)
            tmp = self.ly.create_cell(f"_topo_{k}"); tmp.copy_tree(cell); tmp.flatten(True)
            p = coil1t.path_lengths(self.ly, tmp); self.ly.delete_cell(tmp.cell_index())
            three = any(sh.is_text() and sh.text.string == "LC" for sh in cell.shapes(self.ly.find_layer(27, 25)).each()) \
                    if self.ly.find_layer(27, 25) is not None else False
            ok = p["LA-LB"] is not None and p["LA-LB"] >= lmin and (p["LA-LC"] is not None or not three)
            print(f"  coil {k}: LA-LB {p['LA-LB']} um, LA-LC {p['LA-LC']} um (min {lmin:g}) {'ok' if ok else '<-- OPEN or SHORTED'}")
            bad += not ok
        print(f"coil topology: {'CLEAN' if not bad else f'{bad} bad coil(s)'}"); return bad
    def text(self, name, x, y, gds=(134, 25)):
        self.top.shapes(self.ly.layer(*gds)).insert(pya.DText(name, G(x), G(y)))
    # ---------------- slotted Metal4 ground plane ----------------
    def ground_plane(self, box, hole_keys=(), signal_mim_keys=(), extra_holes=(), exempt_prefixes=("p", "C")):
        um = lambda v: int(round(v * 1000))
        plane = pya.Region(pya.Box(um(box[0]), um(box[1]), um(box[2]), um(box[3])))
        holes = pya.Region()
        for k in hole_keys: holes.insert(self.DEV[k].bbox())
        for k in signal_mim_keys: holes.insert(self.DEV[k].bbox().enlarged(3000))
        for (x1, y1, x2, y2) in extra_holes: holes.insert(pya.Box(um(x1), um(y1), um(x2), um(y2)))
        sigholes = pya.Region()
        for (x, y, b, t) in self.VIAS:                               # signal via stacks crossing Metal4 get a hole
            if "Metal4" in (b, t): continue
            if ORDER.index(b) < 3 < ORDER.index(t): sigholes.insert(pya.Box(um(x - 4), um(y - 4), um(x + 4), um(y + 4)))
        holes += sigholes
        slits = pya.Region()
        for xs in range(um(box[0]) + 10000, um(box[2]), 20000):
            for ys in range(um(box[1]) + 10000, um(box[3]), 20000): slits.insert(pya.Box(xs, ys, xs + 3000, ys + 10000))
        slits = slits.inside((plane - holes).sized(-8000))
        patches = pya.Region()
        for (x1, y1, x2, y2) in self.GPATCH: patches.insert(pya.Box(um(x1), um(y1), um(x2), um(y2)))
        gnd = ((plane - holes - slits) + (patches - sigholes)).merged()   # a ground patch must never re-fill a signal via's hole
        exempt = pya.Region()
        for k, inst in self.DEV.items():
            if k.startswith(exempt_prefixes): exempt.insert(inst.bbox())
        for _ in range(20):
            wide = (gnd.sized(-15000).sized(15000) & gnd) - exempt
            if wide.is_empty(): break
            # slit centres must lie in solid metal: points >= 15 um from every edge (the shrunk region), never a bbox centre
            core = gnd.sized(-15000) & wide.sized(1000)
            for q in core.each():
                c = q.bbox().center()
                if not q.inside(c): c = next(q.each_point_hull())
                sx, sy = (c.x // 5) * 5, (c.y // 5) * 5
                gnd -= pya.Region(pya.Box(sx - 1500, sy - 5000, sx + 1500, sy + 5000))
            gnd.merge()
        gnd = (gnd.sized(-150).sized(150) & gnd).merged()             # remove slivers thinner than the 0.2 um min width
        self.top.shapes(self.LY["Metal4"]).insert(gnd.decompose_trapezoids_to_region(1))
    # ---------------- checks ----------------
    def connectivity(self, probes, groups):
        # coils are devices: their metal (LA-LC-LB is one continuous conductor) is excluded, so only the wiring is checked
        ly2 = pya.Layout(); ly2.dbu = self.ly.dbu; t2 = ly2.create_cell(self.top.name); t2.copy_tree(self.top)
        for inst in list(t2.each_inst()):
            if ly2.cell(inst.cell_index).name.startswith("inductor"): inst.delete()
        l2n = pya.LayoutToNetlist(pya.RecursiveShapeIterator(ly2, t2, []))
        R = {n: l2n.make_layer(ly2.layer(g, 0), n) for n, g in STACK}
        for n in R: l2n.connect(R[n])
        for i in range(0, len(STACK) - 2, 2):
            l2n.connect(R[STACK[i][0]], R[STACK[i+1][0]]); l2n.connect(R[STACK[i+1][0]], R[STACK[i+2][0]])
        l2n.extract_netlist()
        ids = {}
        for k, (layer, p) in probes.items():
            n = l2n.probe_net(R[layer], pya.DPoint(p.x, p.y) if hasattr(p, "x") else pya.DPoint(*p)); ids[k] = n.cluster_id if n else None
        ok = True
        for g in groups:
            s = {ids[k] for k in g}
            if None in s or len(s) != 1: ok = False; print("  OPEN :", ", ".join(f"{k}={ids[k]}" for k in g))
        reps = [ids[g[0]] for g in groups]
        for i in range(len(groups)):
            for j in range(i+1, len(groups)):
                if reps[i] is not None and reps[i] == reps[j]: ok = False; print("  SHORT:", groups[i][0], "<->", groups[j][0])
        print("connectivity check:", "PASS" if ok else "FAIL"); return ok
    def mini_drc(self, exempt_prefixes=("p", "C")):
        rules = {"Metal1": (8, 0.16, 0.18), "Metal2": (10, 0.20, 0.21), "Metal3": (30, 0.20, 0.21), "Metal4": (50, 0.20, 0.21),
                 "Metal5": (67, 0.20, 0.21), "TopMetal1": (126, 1.64, 1.64), "TopMetal2": (134, 2.00, 2.00)}
        exempt = pya.Region()
        for k, inst in self.DEV.items():
            if k.startswith(exempt_prefixes): exempt.insert(inst.bbox())
        bad = 0
        for name, (g, w, sp) in rules.items():
            li = self.ly.find_layer(g, 0)
            if li is None: continue
            r = pya.Region(self.top.begin_shapes_rec(li)); r.merge()
            ng = sum(1 for e in r.edges().each() if e.p1.x % 5 or e.p1.y % 5 or e.p2.x % 5 or e.p2.y % 5)   # outlines AND holes
            nw = r.width_check(int(round(w*1000))).count(); ns = r.space_check(int(round(sp*1000))).count()
            nslt = 0 if name == "TopMetal2" else ((r.sized(-15000).sized(15000) & r) - exempt).count()
            if ng or nw or ns or nslt: print(f"  {name:9s}: off-grid {ng}, width<{w} {nw}, space<{sp} {ns}, >30um without slit {nslt}")
            bad += ng + nw + ns + nslt
        print("mini-DRC:", "CLEAN" if bad == 0 else f"{bad} findings"); return bad == 0
    def foreign_in_inductors(self):
        ind = pya.Region(self.top.begin_shapes_rec(self.ly.find_layer(27, 0))); ind.merge(); n = 0
        for _, g in STACK[::2]:
            li = self.ly.find_layer(g, 0)
            if li is None: continue
            f = pya.Region(); it = self.top.begin_shapes_rec(li)
            while not it.at_end():
                if not it.cell().name.startswith("inductor"): f.insert(it.shape().polygon.transformed(it.trans()))
                it.next()
            n += (f & ind).count()
        print("foreign metal inside inductor areas:", n); return n == 0
    def floating_metal(self):
        """Find metal islands that touch no device terminal (leftover stubs, orphan via landings)."""
        l2n = pya.LayoutToNetlist(pya.RecursiveShapeIterator(self.ly, self.top, []))
        R = {n: l2n.make_layer(self.ly.layer(g, 0), n) for n, g in STACK}
        for n in R: l2n.connect(R[n])
        for i in range(0, len(STACK) - 2, 2):
            l2n.connect(R[STACK[i][0]], R[STACK[i+1][0]]); l2n.connect(R[STACK[i+1][0]], R[STACK[i+2][0]])
        l2n.extract_netlist()
        pins = pya.Region()
        for _, g in STACK[::2]:
            li = self.ly.find_layer(g, 2)
            if li is not None: pins.insert(pya.Region(self.top.begin_shapes_rec(li)))
        fl = []
        for net in l2n.netlist().circuit_by_name(self.top.name).each_net():
            sh = pya.Region()
            for n, _ in STACK[::2]: sh.insert(l2n.shapes_of_net(net, R[n], True))
            if not sh.is_empty() and (sh & pins).is_empty(): fl.append(sh.bbox().to_dtype(self.ly.dbu))
        print("floating metal islands:", len(fl), "" if not fl else fl[:5]); return not fl
    def write(self, fname):
        self.ly.write(fname.replace(".gds", "_pcells.gds"))
        opt = pya.SaveLayoutOptions(); opt.write_context_info = False
        self.ly.write(fname, opt)
