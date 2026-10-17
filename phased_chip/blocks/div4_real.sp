* ---------------- Divider /4, REALIZED: mirrored HBT tail currents, divider biasing, PDK R/C, no kick sources ----------------
* ports: ckp ckn (from the divider driver, AC-coupled)  padp padn (to the PLL, 50-ohm back-terminated)  vcc
.subckt cml_latch_r d db ck ckb q qb vcc vbt params: NT=3 RLL=1.79u RE=1.28u REW=4u
XRLp vcc q  0 rppd w=2u l={RLL}
XRLn vcc qb 0 rppd w=2u l={RLL}
Xd1 qb d  ed 0 npn13G2 Nx=1
Xd2 q  db ed 0 npn13G2 Nx=1
Xh1 qb q  eh 0 npn13G2 Nx=1
Xh2 q  qb eh 0 npn13G2 Nx=1
Xc1 ed ck  et 0 npn13G2 Nx=1
Xc2 eh ckb et 0 npn13G2 Nx=1
* tail: mirrored HBT current source (ratio NT to the 0.5 mA reference) with emitter degeneration
XQt et vbt etr 0 npn13G2 Nx={NT}
XRe etr 0 0 rppd w={REW} l={RE}
.ends cml_latch_r

.subckt div4_real ckp ckn padp padn vcc
* ---- bias reference: 3 kohm from VCC into a diode-connected HBT with 300 ohm degeneration -> ~0.5 mA; vbt ~ 1.0 V
XRref vcc vbt 0 rppd w=1u l=11.34u
XQbr vbt vbt ebr 0 npn13G2 Nx=1
XRebr ebr 0 0 rppd w=2u l=2.05u
XCbt vbt 0 0 cap_rfcmim w=25u l=25u
* ---- clock-input bias 1.5 V (divider + bypass); the driver output is AC-coupled
XRk1 vcc vck 0 rppd w=1u l=15.21u
XRk2 vck 0 0 rppd w=1u l=22.95u
XCk vck 0 0 cap_rfcmim w=33u l=33u
XRck1 vck ckp 0 rppd w=1u l=7.47u
XRck2 vck ckn 0 rppd w=1u l=7.47u
* ---- stage 1: 2 latches, 1.5 mA tails (x3 mirror, 100 ohm degeneration), 267 ohm loads
Xm1 s1qb s1q ckp ckn m1q m1qb vcc vbt cml_latch_r NT=3 RLL=1.79u RE=1.28u REW=4u
Xs1 m1q m1qb ckn ckp s1q s1qb vcc vbt cml_latch_r NT=3 RLL=1.79u RE=1.28u REW=4u
* ---- stage 2: 2 latches, 1 mA tails (x2 mirror, 150 ohm degeneration), 402 ohm loads; AC-coupled from stage 1
XCc1 s1q  c2p 0 cap_rfcmim w=18.2u l=18.2u
XCc2 s1qb c2n 0 cap_rfcmim w=18.2u l=18.2u
XRb1 vck c2p 0 rppd w=1u l=19.08u
XRb2 vck c2n 0 rppd w=1u l=19.08u
Xm2 s2qb s2q c2p c2n m2q m2qb vcc vbt cml_latch_r NT=2 RLL=2.83u RE=2.05u REW=4u
Xs2 m2q m2qb c2n c2p s2q s2qb vcc vbt cml_latch_r NT=2 RLL=2.83u RE=2.05u REW=4u
* ---- output driver: 1.6 V base bias, 10 mA tail (2 x Nx=10 mirrored, 30 ohm each), 50-ohm back-termination
XCo1 s2q  o1 0 cap_rfcmim w=18.2u l=18.2u
XCo2 s2qb o2 0 cap_rfcmim w=18.2u l=18.2u
XRo1 vcc vbo 0 rppd w=1u l=17.14u
XRo2 vbo 0 0 rhigh w=1u l=5.53u
XCbo vbo 0 0 cap_rfcmim w=33u l=33u
XRbo1 vbo o1 0 rppd w=1u l=19.08u
XRbo2 vbo o2 0 rppd w=1u l=19.08u
Xo1 padn o1 eo 0 npn13G2 Nx=4
Xo2 padp o2 eo 0 npn13G2 Nx=4
XQto1 eo vbt eto1 0 npn13G2 Nx=10
XQto2 eo vbt eto2 0 npn13G2 Nx=10
XReo1 eto1 0 0 rppd w=8u l=0.66u
XReo2 eto2 0 0 rppd w=8u l=0.66u
XRt1 vcc padp 0 rppd w=10u l=1.66u
XRt2 vcc padn 0 rppd w=10u l=1.66u
.ends div4_real
