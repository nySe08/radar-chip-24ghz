#!/usr/bin/env python3
"""
pex_gate.py - sign-off gate between LVS / KLayout-PEX and simulation. Exit code 0 = all checks pass.

Catches the failure modes that silently corrupt a post-layout model:
  1. LVS (your run_lvs.sh result): every net and device must match            (--lvsdb lo_core.lvsdb)
  2. the extractor's OWN LVS: its net names are only trustworthy if it matched  (pex_out/<cell>__<cell>/<cell>.lvsdb.gz)
     every net AND every device (a symmetric circuit can match nets crosswise: then devices fail)
  3. MIM integrity: in whitebox mode the plate-to-plate capacitance of every MIM must appear between the two
     nets the reference netlist gives it (crossed net names show up here), within --mim_tol of area*1.5 fF/um2
  4. extractor log: errors, 'No overlap cap specified' (silently dropped C before klayout-pex PR #242),
     whitebox mode (device geometry re-extracted -> double counting with device models unless removed)
  5. inductor parameters: LVS-extracted vs reference (single-turn inductor3 is read differently by the deck)
  6. optional regression: per-net extracted C vs a stored baseline (--baseline net_c.json, --update_baseline)

usage: python3 pex_gate.py --cdl lo_core_lvs.cdl --lvsdb lo_core.lvsdb --cir lo_core_extracted.cir \
                           --pex pex_out/lo_core__lo_core --cell lo_core [--baseline net_c.json]
"""
import argparse, collections, csv, glob, gzip, json, os, re, sys

FAIL, WARN, WAIVED, WAIVERS = [], [], [], []
def fail(m):
    # a reviewed finding is waived only on an EXACT message match: if anything changes, it fails again for a new review
    for pat, why in WAIVERS:
        if pat == m.split(" - ")[0].strip():
            WAIVED.append(m); print("  WAIVED", m.split(" - ")[0], f"[reviewed: {why}]"); return
    FAIL.append(m); print("  FAIL ", m)
def warn(m): WARN.append(m); print("  WARN ", m)
def ok(m): print("  ok   ", m)

def opentext(p): return gzip.open(p, "rt").read() if p.endswith(".gz") else open(p).read()

def lvsdb_names(s):
    iH, iZ = s.index("\nH("), s.index("\nZ(")
    def names(t): return {m.group(1): m.group(2).strip("'") for m in re.finditer(r"N\((\d+)(?: R\([^)]*\))*\s*(?:I\(([^)]*)\))?", t) if m.group(2)}
    return names(s[:iH]), names(s[iH:iZ]), s[iZ:]

def check_lvsdb(path, label, ignore_ports=True):
    s = opentext(path); L, S, z = lvsdb_names(s)
    st = collections.Counter(re.findall(r"^\s*([NDP])\([^()]* (\S+)\)", z, re.M))
    badn = [(L.get(a, a), S.get(b, b)) for a, b, x in re.findall(r"N\((\S+) (\S+) (\S+)\)", z) if x not in ("1", "W")]
    badd = [(a, b) for a, b, x in re.findall(r"D\((\S+) (\S+) (\S+)\)", z) if x not in ("1", "W")]
    # order-independent wording: the pairing order of unmatched symmetric items is arbitrary between runs, the SETS are not
    key = lambda v: (len(v), v)
    if badn:
        ref = sorted({b for _, b in badn if b != "()"}, key=key)
        fail(f"{label}: {len(badn)} unmatched net(s), reference nets {{{', '.join(ref)}}}")
    if badd:
        ld = sorted({a for a, _ in badd if a != "()"}, key=key); rd = sorted({b for _, b in badd if b != "()"}, key=key)
        fail(f"{label}: {len(badd)} unmatched device(s), layout ids {{{', '.join(ld)}}} / reference ids {{{', '.join(rd)}}}"
             " - with all nets matched this means crosswise pairing or a parameter mismatch")
    if not badn and not badd: ok(f"{label}: all {st[('N','1')]+st[('N','W')]} nets and {st[('D','1')]+st[('D','W')]} devices match")
    xmap = {}
    for a, b, x in re.findall(r"N\((\S+) (\S+) (\S+)\)", z):
        if a in L and b in S: xmap[L[a]] = S[b]
    return xmap

def ref_devices(cdl):
    devs = []
    for line in open(cdl):
        t = line.split()
        if len(t) > 3 and not line.startswith(("*", ".", "+")): devs.append(t)
    return devs

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--cdl", required=True); ap.add_argument("--lvsdb"); ap.add_argument("--cir")
    ap.add_argument("--pex", required=True, help="pex_out/<cell>__<cell> directory"); ap.add_argument("--cell", required=True)
    ap.add_argument("--mim_tol", type=float, default=0.30); ap.add_argument("--baseline"); ap.add_argument("--update_baseline", action="store_true")
    ap.add_argument("--nets", nargs="*", default=[], help="critical nets for the regression report (default: all)")
    ap.add_argument("--reg_tol", type=float, default=0.10)
    ap.add_argument("--waivers", help="file of reviewed findings: '<exact FAIL message> | <reason>' per line")
    a = ap.parse_args()
    if a.waivers and os.path.exists(a.waivers):
        for line in open(a.waivers):
            if "|" in line and not line.lstrip().startswith("#"):
                p, why = line.rsplit("|", 1); WAIVERS.append((p.strip(), why.strip()))
    print("== 1. LVS ==")
    if a.lvsdb: check_lvsdb(a.lvsdb, "LVS")
    else: warn("no --lvsdb given: LVS result not checked")
    print("== 2. extractor's own LVS ==")
    kdb = glob.glob(os.path.join(a.pex, f"{a.cell}.lvsdb*"))
    xmap = check_lvsdb(kdb[0], "kpex LVS") if kdb else (fail("extractor LVS database not found") or {})
    nm = lambda n: xmap.get(n, n).upper()
    print("== 3. MIM integrity (plate-to-plate C between the reference nets) ==")
    rows = list(csv.DictReader(open(glob.glob(os.path.join(a.pex, "*_pex_netlist.csv"))[0]), delimiter=";"))
    pair = collections.Counter(); netc = collections.Counter()
    for r in rows:
        if not r["Device"].startswith("C") or not r.get("Capacitance [fF]"): continue
        x, y, c = nm(r["Net1"]), nm(r["Net2"]), float(r["Capacitance [fF]"])
        pair[frozenset((x, y))] += c; netc[x] += c; netc[y] += c
    expect = collections.Counter(); names = collections.defaultdict(list)
    for t in ref_devices(a.cdl):
        if any("cmim" in x for x in t):
            kv = dict(re.findall(r"(\w+)=([0-9.eE+-]+)u?", " ".join(t)))
            w, l = float(kv.get("w", 0)), float(kv.get("l", 0))
            k = frozenset((t[1].upper(), t[2].upper())); expect[k] += w * l * 1.5 + 2 * (w + l) * 0.04; names[k].append(t[0])
    # a SPICE netlist only counts if complete: kpex's writer crash leaves a header-only fragment without '.ends'
    spice = [p for p in glob.glob(os.path.join(a.pex, "*_pex_netlist.spice")) if re.search(r"(?im)^\s*\.ends", opentext(p))]
    logs0 = [p for p in glob.glob(os.path.join(a.pex, "kpex*.log")) if "bak" not in p]
    log0 = opentext(next((p for p in logs0 if "plain" in p), logs0[0])) if logs0 else ""
    n_wb = log0.count("Removing whiteboxed device")
    if spice:
        n_dev = sum(len(re.findall(r"(?im)^\S+\s.*cmim", opentext(p))) for p in spice)
    else:
        # kpex < 0.6 crashes writing the SPICE netlist when MIMs are blackboxed ("Invalid parameter name: 'C'"), after the
        # CSV is complete. Without the SPICE file, the log tells the mode: no whitebox removals = devices kept.
        n_dev = sum(len(v) for v in names.values()) if n_wb == 0 else 0
        warn("no SPICE netlist (kpex < 0.6 writer bug with blackboxed MIMs) - the CSV is complete; upgrade kpex for the netlist")
    n_ref = sum(len(v) for v in names.values()); got = sum(pair[k] for k in expect); want = sum(expect.values())
    if not expect: ok("no MIM capacitors in the reference netlist")
    elif n_dev >= n_ref:
        if got > 0.2 * want: warn(f"MIM devices kept AND {got:.0f} fF plate C extracted: double counting - drop the plate pairs")
        else:
            ok(f"{n_ref} MIM devices kept as devices (blackboxed)")
            if got > 0.01 * want:
                warn(f"{got:.0f} fF ({got/want:.1%} of the MIM values) still extracted between MIM plate nets: with the top plate "
                     "blackboxed the extractor sees Metal5 through it to the TopMetal1 strap, a coupling the plate shields in "
                     "reality - drop MIM plate-pair entries before simulating (the hybrid model does)")
    else:
        # whitebox: the devices were removed, so their capacitance must now come from the extraction itself
        bad = [(names[k], pair[k], e) for k, e in expect.items() if abs(pair[k] - e) > a.mim_tol * e]
        if bad:
            fail(f"whitebox extraction removed {n_ref - n_dev} MIM devices but holds only {got:.0f} of {want:.0f} fF ({got/want:.0%}) "
                 f"between their plates: the extracted SPICE netlist is missing capacitors (MIM coefficients only reached klayout-pex in PR #248). "
                 f"Use --blackbox y, or keep simulating the hybrid (reference MIMs + extracted wiring C)")
            for n, g, e in sorted(bad, key=lambda x: -x[2])[:5]: print(f"         {','.join(n)}: {g:.1f} of {e:.1f} fF")
        else: ok(f"whitebox: all {n_ref} MIMs re-extracted between the right nets within {a.mim_tol:.0%}")
    print("== 4. extractor log ==")
    logs = [p for p in glob.glob(os.path.join(a.pex, "kpex*.log")) if "bak" not in p]
    log = opentext(next((p for p in logs if "plain" in p), logs[0])) if logs else ""        # one log: kpex.log duplicates kpex_plain.log
    n_ov = log.count("No overlap cap specified")
    if n_ov: fail(f"'No overlap cap specified' x{n_ov}: layer-pair capacitance was dropped (klayout-pex < PR #242) - upgrade and rerun")
    errs = [l for l in log.splitlines() if re.search(r"\b(ERROR|Traceback|Exception)\b", l) and "Netlists don't match" not in l]
    if errs: fail(f"{len(errs)} error line(s) in the extractor log, first: {errs[0][:120]}")
    if not n_ov and not errs: ok("no dropped-capacitance warnings or errors in the extractor log")
    nwb = log.count("Removing whiteboxed device")
    if nwb: warn(f"{nwb} devices were whiteboxed (prototype default) - make the choice explicit with --blackbox y|n")
    print("== 5. inductor parameters (LVS-extracted vs reference) ==")
    if a.cir:
        ext = [l.split() for l in open(a.cir) if re.match(r"^L\S*\s", l) and "inductor" in l]
        ref = [t for t in ref_devices(a.cdl) if any(x.startswith("inductor") for x in t)]
        def par(t): return {k: float(v) for k, v in re.findall(r"\b(w|d|nr_r)=([0-9.eE+-]+)", " ".join(t))}
        def same(p, q): return p.keys() == q.keys() and all(abs(p[k] - q[k]) <= 0.005 * max(abs(q[k]), 1e-9) for k in p)
        miss = [r[0] for r in ref if not any(same(par(e), par(r)) for e in ext)]   # 0.5 % tolerance: the deck rounds
        if miss: fail(f"inductor(s) {miss} have no extracted twin with the same w/d/nr_r - read the deck's values from {os.path.basename(a.cir)}")
        else: ok(f"all {len(ref)} inductors: extracted parameters equal the reference")
        for e in ext:
            if "nr_r=1" in e: warn(f"{e[0]}: single-turn inductor3 - IHP's nr_r=1 PCell is malformed (ring closed where the leads attach); "
                                   "LVS cannot see inside a coil, so confirm the layout's coil topology check (LA-LB path length)")
    print("== 6. regression vs baseline ==")
    sel = {n.upper() for n in a.nets} or set(netc)
    cur = {n: round(netc[n], 3) for n in sel if n in netc}
    if a.baseline and os.path.exists(a.baseline) and not a.update_baseline:
        base = json.load(open(a.baseline)); moved = [(n, base[n], cur[n]) for n in cur if n in base and base[n] > 1 and abs(cur[n] / base[n] - 1) > a.reg_tol]
        for n, b, c in sorted(moved, key=lambda x: -abs(x[2] / x[1] - 1))[:12]: warn(f"net {n}: {b:.1f} -> {c:.1f} fF ({(c/b-1)*100:+.0f} %)")
        if not moved: ok(f"no net moved by more than {a.reg_tol:.0%} vs {a.baseline}")
    if a.baseline and (a.update_baseline or not os.path.exists(a.baseline)):
        json.dump(cur, open(a.baseline, "w"), indent=1, sort_keys=True); ok(f"baseline written: {a.baseline} ({len(cur)} nets)")
    print(f"\nGATE: {'PASS' if not FAIL else 'FAIL'}  ({len(FAIL)} fail, {len(WAIVED)} waived, {len(WARN)} warn)")
    sys.exit(1 if FAIL else 0)

if __name__ == "__main__":
    main()
