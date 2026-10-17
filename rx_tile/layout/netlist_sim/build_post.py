"""build_post.py - post-layout model of the LNA: EM-calibrated netlist + layout interconnect parasitics.

Interconnect: microstrip over the Metal4 ground plane (IHP SG13G2 stack: SiO2 er=4.1;
TopMetal2 bottom 6.68 um above Metal4, TopMetal1 1.88 um), Hammerstad formulas, one pi-section
per line. Lengths/widths taken from the generated layout (lna_gen.py).
"""
import numpy as np, sys
C0 = 2.998e8; ER = 4.1; MU0 = 4e-7*np.pi
def microstrip(w, h):
    u = w/h
    ee = (ER+1)/2 + (ER-1)/2/np.sqrt(1+12/u)
    z0 = 60/np.sqrt(ee)*np.log(8/u+u/4) if u <= 1 else 120*np.pi/np.sqrt(ee)/(u+1.393+0.667*np.log(u+1.444))
    return z0, ee
def line(name, n1, n2, length_um, w_um, h_um, sigma=3.03e7, t=3e-6):
    z0, ee = microstrip(w_um, h_um)
    L = z0*np.sqrt(ee)/C0*length_um*1e-6; C = np.sqrt(ee)/(z0*C0)*length_um*1e-6
    delta = 1/np.sqrt(np.pi*24.125e9*MU0*sigma); R = length_um*1e-6/(sigma*w_um*1e-6*2*delta)   # two-sided skin
    return (f"* {name}: {length_um:.0f} um x {w_um} um, h={h_um} um -> Z0={z0:.0f} ohm, L={L*1e12:.1f} pH, C={C*1e15:.1f} fF\n"
            f"L_{name} {n1} {name}_m {L:.4e}\nR_{name} {name}_m {n2} {R:.4f}\n"
            f"C_{name}a {n1} 0 {C/2:.4e}\nC_{name}b {n2} 0 {C/2:.4e}\n"), (L, C)
H_TM2, H_TM1 = 6.68, 1.88
def build(pad="TM1", out="lna_post.spice"):
    s = open("lna_ind.spice").read()
    s = s.replace("* 24 GHz LNA - REALIZATION step 2: + modelled TopMetal2 spiral inductors (pi-models)",
                  f"* 24 GHz LNA - POST-LAYOUT model: EM-calibrated devices + layout interconnect + pads (RF pads: {pad} bottom)")
    # pads: 80x80 um signal pads, plate capacitance to the substrate under the plane opening (+15 % fringe), lossy substrate
    hb = {"M3": 3.04, "TM1": 6.43}[pad]
    cpad = 8.854e-12*ER*80e-6*80e-6/(hb*1e-6)*1.15
    parts = [f"* ---- RF signal pads (bottom metal {pad}): C = {cpad*1e15:.0f} fF each, via the lossy substrate\n"
             f"Cpad1 pad1 sp1 {cpad:.4e}\nRsp1 sp1 0 20\nCpad2 pad2 sp2 {cpad:.4e}\nRsp2 sp2 0 20\n"]
    t, _ = line("rfin", "pad1", "p1", 64, 10, H_TM2); parts.append(t)                 # pad -> Cin (TM2)
    t, _ = line("cin_lb", "in", "inL", 51, 5, H_TM1); parts.append(t)                 # Cin PLUS -> Lb lead (TM1)
    t, _ = line("lb_q1", "bL", "b1v", 21, 4, H_TM1); parts.append(t)                  # Lb lead -> Q1 base via (TM1)
    parts.append("Lv_b1 b1v b1 4p\n")                                                 # via stack M1-TM1
    parts.append("* Q1 emitter -> Le: M2 stub + via M2-TM2 + TM2 strip (47 um over the plane) + via to the plane\n"
                 "Lle_v1 e1 e1a 4p\n"); t, _ = line("le_strip", "e1a", "e1b", 47, 10, H_TM2); parts.append(t)
    parts.append("Lle_v2 e1b 0 3p\nCc1 c1 0 5.5f\n")                                   # c1: Metal3 run under the plane
    parts.append("Lv_q2c q2c q2cv 5p\n"); t, _ = line("out", "q2cv", "outT", 127, 6, H_TM2); parts.append(t)
    parts.append("Lv_lca outT out 3p\n")                                              # TM2-TM1 via + lead stub
    # VCC: Lc lead -> TM2 line -> RP tap -> Cdec1 -> Cdec2 -> VCC pad
    t, _ = line("vcc1", "vccL", "vccR", 12, 8, H_TM2); parts.append(t)
    t, _ = line("vcc2", "vccR", "vd1", 72, 8, H_TM2); parts.append(t)
    t, _ = line("vcc3", "vd1", "vd2", 55, 8, H_TM2); parts.append(t)
    t, _ = line("vcc4", "vd2", "vcc", 102, 8, H_TM2); parts.append(t)
    parts.append("XCdec1 vd1 0 0 cap_rfcmim w=33u l=33u\nXCdec2 vd2 0 0 cap_rfcmim w=33u l=33u\n")
    # RF out: Cout PLUS -> TM1 (42 um) -> via -> TM2 (185 um) -> pad
    t, _ = line("rfo1", "p2c", "p2v", 42, 5, H_TM1); parts.append(t)
    parts.append("Lv_rfo p2v p2w 3p\n"); t, _ = line("rfo2", "p2w", "pad2", 185, 10, H_TM2); parts.append(t)
    # re-wire the netlist
    s = s.replace("V1 p1 0 dc 0 ac 1 portnum 1 z0 50", "V1 pad1 0 dc 0 ac 1 portnum 1 z0 50")
    s = s.replace("V2 p2 0 dc 0 ac 0 portnum 2 z0 50", "V2 pad2 0 dc 0 ac 0 portnum 2 z0 50")
    s = s.replace("Xlb in b1 ind_lb", "Xlb inL bL ind_lb")
    s = s.replace("Xle e1 0 ind_le", "")
    s = s.replace("XQ2 out b2 c1 0 npn13G2 Nx={NX2}", "XQ2 q2c b2 c1 0 npn13G2 Nx={NX2}")
    s = s.replace("Xlc vcc out ind_lc", "Xlc vccL out ind_lc")
    s = s.replace("XRp  vcc out 0 rppd w=2u l={LRP}", "XRp  vccR out 0 rppd w=2u l={LRP}")
    s = s.replace("XCout p2 out 0 cap_rfcmim w={WCOUT} l={WCOUT}", "XCout p2c out 0 cap_rfcmim w={WCOUT} l={WCOUT}")
    # realization changes, as in the layout
    s = s.replace("Ief  vbn 0 50u", "XRief vbn 0 0 rhigh w=1u l=12.03u")
    s = s.replace("XCbn2 vbn 0 0 cap_rfcmim w=33u l=33u\n", "")
    s = s.replace("XCout p2c out", "\n* ======== layout interconnect (post-layout) ========\n" + "".join(parts) + "XCout p2c out", 1)
    s = s.replace("lna_ind.txt", "lna_post.txt").replace("lna_ind_stab.txt", "lna_post_stab.txt")
    open(out, "w").write(s)
if __name__ == "__main__":
    build(sys.argv[1] if len(sys.argv) > 1 else "TM1")
