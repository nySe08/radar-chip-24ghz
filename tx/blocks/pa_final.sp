* 24 GHz PA (final): single-ended cascode, real IHP devices, cascode = 2 x npn13G2v Nx=8 in parallel
* (one 8-finger high-voltage HBT reaches high injection at the fast corner -> gain collapse; see ../README.md)
* Output coil: EM model of inductor2, 1 turn, w 12 um, d 147 um (333 pH, Q 24.8 at 24.1 GHz)
* 2nd-harmonic trap on the 50 ohm side: EM coil (1 turn, w 12, d 85 um: ~175 pH near 48 GHz) + rfcmim 6.4 um
* Final values are the defaults below (PA mirror reference 2.0 um, output MIM 7 um).
.subckt pa_final in out enb vcc RREFL=2.0u RC1=3.21u LC=330p QL=24.8 L2=175p R2=1.9 W2=6.4u WC=7u
XCin  in b1 0 cap_rfcmim w=25.8u l=25.8u
* bias: reference mirror with beta helper (Qf), enable switches pull the bias down
XRif  vcc cr 0 rppd w=1u l={RREFL}
XQr   cr br er 0 npn13G2 Nx=1
XRer  er 0 0 rsil w=1u l=4.47u
XQf   vcc cr vbn 0 npn13G2 Nx=1
XRief vbn 0 0 rhigh w=1u l=12.6u
XRref vbn br 0 rhigh w=1u l=5.53u
XRb   vbn b1 0 rppd w=1u l=3.60u
XCbn  vbn 0 0 cap_rfcmim w=37u l=37u
XM1 cr  enb 0 0 sg13_lv_nmos w=10u l=0.13u ng=1
XM2 vbn enb 0 0 sg13_lv_nmos w=8u l=0.13u ng=1
* gain stage
XQ1   c1 b1 e1 0 npn13G2 Nx=8
XRe1  e1 0 0 rsil w=4u l=1.58u
XQ2   col vcas c1 0 npn13G2v Nx=8
XQ2b  col vcas c1 0 npn13G2v Nx=8
* cascode bias: VCC divider (tracks the supply) + MIM bypass
XRc1  vcc vcas 0 rppd w=1u l={RC1}
XRc2  vcas 0 0 rppd w=1u l=5.92u
XCcas vcas 0 0 cap_rfcmim w=37u l=37u
* load: EM model of the 1-turn coil, plus collector parasitic estimate; output MIM
Lc    vcc lx {LC}
RLc   lx col {1.5158e11*LC/QL}
Ccl   col 0 7.1f
XCout col out 0 cap_rfcmim w={WC} l={WC}
* 2nd-harmonic trap, 50 ohm output side: EM trap coil (1t w12 d85: ~175 pH, Q~28 at 48 GHz) + REAL rfcmim
L2t   out t2 {L2}
R2t   t2 t3 {R2}
XC2t  t3 0 0 cap_rfcmim w={W2} l={W2}
.ends pa_final
