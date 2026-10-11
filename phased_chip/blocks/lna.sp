* ---------------- LNA: cascode HBT, inductive degeneration, mirror bias ----------------
* ports: rfin (from RX antenna, 50 ohm)  rfout (to mixer)  vcc
.subckt lna rfin rfout vcc
.param LE=32p LB=609p LC=683p COUT=51f IREF=0.92m RB=5k RREF=40k R1=6k R2=19k CBYP=5p RP=500 QL=15 W0=1.5158e11
Cin  rfin in  10p
Lb   in b1x {LB}
RLb  b1x b1 {W0*LB/QL}
Iref vcc cr {IREF}
XQr  cr br 0 0 npn13G2 Nx=1
XQf  vcc cr vbn 0 npn13G2 Nx=1
Ief  vbn 0 50u
Rref vbn br {RREF}
Rb   vbn b1 {RB}
Cbn  vbn 0 {CBYP}
XQ1  c1 b1 e1 0 npn13G2 Nx=8
Le   e1 e1x {LE}
RLe  e1x 0 {W0*LE/QL}
XQ2  out b2 c1 0 npn13G2 Nx=8
Rc1  vcc b2 {R1}
Rc2  b2 0 {R2}
Ccas b2 0 {CBYP}
Lc   vcc cx {LC}
RLc  cx out {W0*LC/QL}
Rp   vcc out {RP}
Cout out rfout {COUT}
.ends lna
