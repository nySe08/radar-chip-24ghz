"""tx_postlayout.py - post-layout model of the signed-off TX channel (v2): output power, 2nd harmonic and stability.

Flat netlist with the LVS net names, plus every capacitance KLayout-PEX (2.5D) extracted from tx_ch.gds
(tx_ch_k25d_pex_netlist.csv, from the sign-off run of the v2 layout). Rules, as for the other blocks:
  - MIM plate-to-plate entries are dropped (the blackboxed top plate lets the extractor see Metal5 through it);
  - capacitance to the substrate (VSUBS) is bracketed: 0 %, 50 % and 100 % of it to ground, because the extractor
    treats the substrate as an ideal ground. Every spec is checked at all three.
Stability: two-port S-parameters 0.1-100 GHz, port 1 at the driver input (txinn = -txinp through an ideal inverter),
port 2 at OUT after the pad and ESD coil; Rollett K and Edwards-Sinsky mu (mu > 1: unconditionally stable).
Run inside IIC-OSIC-TOOLS (PDK_ROOT/PDK set): python3 tx_postlayout.py   (about 1 minute)
Expected (ngspice 42; ngspice 47 differs by up to ~0.2 dB at the fast corner):
  substrate   0 %: slow +4.58 | typ +6.57 | fast +5.60 dBm
  substrate  50 %: slow +3.68 | typ +6.11 | fast +5.56 dBm
  substrate 100 %: slow +2.57 | typ +5.56 | fast +5.50 dBm      2nd harmonic <= -19.5 dBm, min mu 1.10
"""
import os, shutil, subprocess, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); NG = os.environ.get("NGSPICE", "ngspice")
# layout net ids in the extraction -> LVS net names (recovered from the gate's net totals and the v1 cross-reference)
NET = {'$31':'b1','$46':'dp','$49':'dn','$33':'t3','$9':'br','$5':'er','$6':'cr','$59':'c1','$60':'col','$67':'e1','$68':'vbd',
       '$69':'vcas','$55':'b2d','$53':'b1d','$29':'dd','$45':'t','$7':'vbn','$32':'dmy',
       'ENB':'enb','GND':'0','OUT':'out','VCC':'vcc','TXINN':'txinn','TXINP':'txinp','VSUBS':'SUB'}
MIM_PAIRS = {frozenset(p) for p in (('txinp','b1d'),('txinn','b2d'),('dp','b1'),('dn','dmy'),('dmy','dd'),('out','col'),('out','t3'))}
CORNERS = {"slow": (('hbt_wcs','cap_wcs','res_wcs','mos_ss'), 85, 2.375, 0.194), "typ": (('hbt_typ','cap_typ','res_typ','mos_tt'), 27, 2.5, 0.255),
           "fast": (('hbt_bcs','cap_bcs','res_bcs','mos_ff'), -40, 2.625, 0.312)}
DEVICES = """XCi1 txinp b1d 0 cap_rfcmim w=25u l=25u
XCi2 txinn b2d 0 cap_rfcmim w=25u l=25u
XRv1 vcc vbd 0 rppd w=1u l=17.53u
XRv2 vbd 0 0 rppd w=1u l=20.63u
XCvb vbd 0 0 cap_rfcmim w=33u l=33u
XRb1 vbd b1d 0 rppd w=1u l=19.08u
XRb2 vbd b2d 0 rppd w=1u l=19.08u
XQa dp b1d t 0 npn13G2 Nx=2
XQb dn b2d t 0 npn13G2 Nx=2
XRt t 0 0 rppd w=2.2u l=0.5u
XR1 vcc dp 0 rppd w=2u l=0.9u
XR2 vcc dn 0 rppd w=2u l=0.9u
XCc1 dp b1 0 cap_rfcmim w=16u l=16u
XCc2 dn dmy 0 cap_rfcmim w=16u l=16u
XCd dmy dd 0 cap_rfcmim w=7u l=7u
XRd dd 0 0 rsil w=1u l=1.30u
XRif vcc cr 0 rppd w=1u l=2.0u
XQr cr br er 0 npn13G2 Nx=1
XRer er 0 0 rsil w=1u l=4.47u
XQf vcc cr vbn 0 npn13G2 Nx=1
XRief vbn 0 0 rhigh w=1u l=12.6u
XRref vbn br 0 rhigh w=1u l=5.53u
XRb vbn b1 0 rppd w=1u l=3.60u
XCbn vbn 0 0 cap_rfcmim w=37u l=37u
XM1 cr enb 0 0 sg13_lv_nmos w=10u l=0.13u ng=1
XM2 vbn enb 0 0 sg13_lv_nmos w=8u l=0.13u ng=1
XQ1 c1 b1 e1 0 npn13G2 Nx=8
XRe1 e1 0 0 rsil w=4u l=1.58u
XQ2 col vcas c1 0 npn13G2v Nx=8
XQ2b col vcas c1 0 npn13G2v Nx=8
XRc1 vcc vcas 0 rppd w=1u l=3.21u
XRc2 vcas 0 0 rppd w=1u l=5.92u
XCcas vcas 0 0 cap_rfcmim w=37u l=37u
* output coil, EM model (1 turn, w 12 um, d 147 um: 333 pH, Q 24.8)
Lc vcc lx 330p
RLc lx col {1.5158e11*330p/24.8}
XCout out col 0 cap_rfcmim w=7u l=7u
* 2nd-harmonic trap (layout order): OUT -> MIM 6.0 um -> t3 -> trap coil (EM: ~175 pH near 48 GHz) -> ground
XC2t out t3 0 cap_rfcmim w=6.0u l=6.0u
L2t t3 t2 175p
R2t t2 0 1.9
* TX output pad and ESD coil (EM fit: 580 pH + loss, self-capacitance for f_sr ~ 51 GHz)
Cpadt out spt 41.6f
Rsubt spt 0 60
Lesd out le1 580p
Rlesd le1 0 4.8
Cesds out 0 16.8f"""
def spiceinit():
    dst = os.path.join(HERE, ".spiceinit")
    if not os.path.exists(dst):
        shutil.copy(os.path.join(os.environ.get("PDK_ROOT", "/foss/pdks"), os.environ.get("PDK", "ihp-sg13g2"), "libs.tech", "ngspice", ".spiceinit"), dst)
def extracted(ksub):
    out = []
    for l in open(os.path.join(HERE, "tx_ch_k25d_pex_netlist.csv")):
        if not l.startswith("C"): continue
        r = l.strip().rstrip(";").split(";"); a, b, v = NET[r[1]], NET[r[2]], float(r[3])
        if frozenset((a, b)) in MIM_PAIRS: continue
        if "SUB" in (a, b):
            if ksub == 0: continue
            a, b, v = (b if a == "SUB" else a), "0", v*ksub
        if a != b: out.append(f"Cx{len(out)+1} {a} {b} {v:.4f}f")
    return out
def netlist(corner, ksub, ports, control):
    (h, c, r, mo), T, vcc, atx = CORNERS[corner]
    return "\n".join([f"* TX channel v2, post-layout (substrate x{ksub}), {corner}", f".lib cornerHBT.lib {h}", f".lib cornerCAP.lib {c}",
                      f".lib cornerRES.lib {r}", f".lib cornerMOSlv.lib {mo}", f".param temp={T}", f".options temp={T}",
                      f"Vcc vcc 0 {vcc}", "Ven enb 0 0", DEVICES] + extracted(ksub) + ports(atx) + [".control", "set noaskquit"] + control + ["quit", ".endc", ".end"])
def ngspice(txt, tag, out):
    open(os.path.join(HERE, f"_{tag}.spice"), "w").write(txt); f = os.path.join(HERE, out)
    if os.path.exists(f): os.remove(f)
    p = subprocess.run([NG, "-b", f"_{tag}.spice"], capture_output=True, text=True, cwd=HERE, timeout=900)
    if not os.path.exists(f): raise RuntimeError(f"ngspice failed ({tag}):\n" + p.stdout[-800:])
    return np.loadtxt(f)
def power(corner, ksub):
    tb = lambda atx: [f"Vtp txinp 0 dc 0 sin(0 {atx} 24.15e9)", f"Vtn txinn 0 dc 0 sin(0 {-atx} 24.15e9)", "Rtx1 out 0 50"]
    d = ngspice(netlist(corner, ksub, tb, ["option rshunt=1e12", "tran 0.2p 3n 0 0.2p", "wrdata tr.txt v(out) i(Vcc)"]), "tr", "tr.txt")
    if d[-1, 0] < 2.99e-9: raise RuntimeError("transient stopped early")
    m = d[:, 0] > 2e-9; t, v, i = d[m, 0], d[m, 1], d[m, 3]; w = 2*np.pi*24.15e9
    a1, a2 = 2*abs(np.mean(v*np.exp(-1j*w*t))), 2*abs(np.mean(v*np.exp(-2j*w*t)))
    return 10*np.log10(a1**2/100/1e-3), 10*np.log10(a2**2/100/1e-3), -np.mean(i)*1e3
def stability(corner, ksub, Z0=50.0):
    ctl = ["option rshunt=1e12", "ac dec 40 0.1e9 100e9", "wrdata ac.txt real(v(txinp)) imag(v(txinp)) real(v(out)) imag(v(out)) real(v(px)) imag(v(px))"]
    inv = "Etn txinn 0 txinp 0 -1"
    A = ngspice(netlist(corner, ksub, lambda a: ["Vpx px 0 dc 0 ac 1", f"Rs1 px txinp {Z0}", inv, f"Rl2 out 0 {Z0}"], ctl), "aca", "ac.txt")
    B = ngspice(netlist(corner, ksub, lambda a: [f"Rs1 txinp 0 {Z0}", inv, "Vpx px 0 dc 0 ac 1", f"Rs2 px out {Z0}"], ctl), "acb", "ac.txt")
    cx = lambda d, k: d[:, 4*k+1] + 1j*d[:, 4*k+3]
    v1a, v2a, vxa, v1b, v2b, vxb = cx(A, 0), cx(A, 1), cx(A, 2), cx(B, 0), cx(B, 1), cx(B, 2)
    a_ = lambda V, I: (V + Z0*I)/(2*np.sqrt(Z0)); b_ = lambda V, I: (V - Z0*I)/(2*np.sqrt(Z0))
    I1a, I2a, I1b, I2b = (vxa - v1a)/Z0, -v2a/Z0, -v1b/Z0, (vxb - v2b)/Z0
    S11, S21 = b_(v1a, I1a)/a_(v1a, I1a), b_(v2a, I2a)/a_(v1a, I1a)
    S22, S12 = b_(v2b, I2b)/a_(v2b, I2b), b_(v1b, I1b)/a_(v2b, I2b)
    D = S11*S22 - S12*S21
    K = (1 - abs(S11)**2 - abs(S22)**2 + abs(D)**2)/(2*abs(S12*S21))
    mu = (1 - abs(S11)**2)/(abs(S22 - D*np.conj(S11)) + abs(S12*S21))
    return A[:, 0], K, mu
if __name__ == "__main__":
    spiceinit()
    print(f"{'substrate':>9s} {'corner':>6s} {'Pout [dBm]':>11s} {'H2 [dBm]':>9s} {'I [mA]':>7s} {'min mu':>7s} {'min K':>7s}")
    for k in (0.0, 0.5, 1.0):
        for c in ("slow", "typ", "fast"):
            p, h2, i = power(c, k); f, K, mu = stability(c, k)
            print(f"{int(k*100):8d}% {c:>6s} {p:11.2f} {h2:9.1f} {i:7.1f} {mu.min():7.2f} {K.min():7.1f}")
