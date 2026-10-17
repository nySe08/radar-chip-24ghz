* 24 GHz PA, single-ended cascode, ALL REAL IHP DEVICES (no ideal sources, R or C); coil = EM model of inductor2 1t w12 d213
.subckt pa_baseline in out enb vcc RREFL=2.8u RC1=3.21u
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
* cascode bias: VCC divider (tracks the supply) + MIM bypass
XRc1  vcc vcas 0 rppd w=1u l={RC1}
XRc2  vcas 0 0 rppd w=1u l=5.92u
XCcas vcas 0 0 cap_rfcmim w=37u l=37u
* load: EM model of the 1-turn coil, plus collector parasitic estimate; output MIM
Lc    vcc lx 505p
RLc   lx col {1.5158e11*505p/24.3}
Ccl   col 0 7.1f
XCout col out 0 cap_rfcmim w=7u l=7u
.ends pa_baseline
