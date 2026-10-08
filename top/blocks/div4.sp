* ---------------- Divider /4: two CML static /2 stages + 50-ohm output driver ----------------
* ports: ckp ckn (from LO buffer, AC-coupled)  padp padn (to PLL, 50 ohm back-terminated)  vcc
.subckt cml_latch d db ck ckb q qb vcc params: IT=2.5m RL=160 NX=1
RLp vcc q  {RL}
RLn vcc qb {RL}
* data pair (transparent when ck high): D high -> current through Qd1 -> qb low, q high
Xd1 qb d  ed 0 npn13G2 Nx={NX}
Xd2 q  db ed 0 npn13G2 Nx={NX}
* hold pair (cross-coupled, active when ck low)
Xh1 qb q  eh 0 npn13G2 Nx={NX}
Xh2 q  qb eh 0 npn13G2 Nx={NX}
* clock pair
Xc1 ed ck  et 0 npn13G2 Nx={NX}
Xc2 eh ckb et 0 npn13G2 Nx={NX}
It et 0 {IT}
.ends

.subckt div4 ckp ckn padp padn vcc
.param IT1=1.5m RL1=266 IT2=1m RL2=400 VCK=1.2 CC=500f RB=5k IOUT=8m ROUT=50 VBO=1.6
* clock input DC bias (the buffer output is AC-coupled)
Rck1 vck ckp 2k
Rck2 vck ckn 2k
Vck  vck 0 {VCK}
Xm1 s1qb s1q ckp ckn m1q m1qb vcc cml_latch IT={IT1} RL={RL1} NX=1
Xs1 m1q m1qb ckn ckp s1q s1qb vcc cml_latch IT={IT1} RL={RL1} NX=1
Cc1 s1q  c2p {CC}
Cc2 s1qb c2n {CC}
Rb1 vck c2p {RB}
Rb2 vck c2n {RB}
Xm2 s2qb s2q c2p c2n m2q m2qb vcc cml_latch IT={IT2} RL={RL2} NX=1
Xs2 m2q m2qb c2n c2p s2q s2qb vcc cml_latch IT={IT2} RL={RL2} NX=1
Co1 s2q  o1 {CC}
Co2 s2qb o2 {CC}
Rbo1 vbo o1 {RB}
Rbo2 vbo o2 {RB}
Vbo  vbo 0 {VBO}
Xo1 padn o1 eo 0 npn13G2 Nx=4
Xo2 padp o2 eo 0 npn13G2 Nx=4
Io  eo 0 {IOUT}
Rt1 vcc padp {ROUT}
Rt2 vcc padn {ROUT}
Ik1 s1q 0 pulse(0 0.5m 0 5p 5p 20p 1)
Ik2 s2q 0 pulse(0 0.5m 0 5p 5p 20p 1)
.ends div4
