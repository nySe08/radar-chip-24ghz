* ---------------- PA with enable (TDM-MIMO): en_b high (1.2 V) = PA off ----------------
* ports: in (one side of a PA driver, AC-coupled)  out (to TX antenna)  enb  vcc
.subckt pa_en in out enb vcc
.param RE1=5 IREF=0.777m RB=1k RREF=8k VCAS=1.6 CBYP=5p LC=543p COUT=71f QL=15 W0=1.5158e11
Cin  in b1 1p
Iref vcc cr {IREF}
XQr  cr br er 0 npn13G2 Nx=1
Rer  er 0 {8*RE1}
XQf  vcc cr vbn 0 npn13G2 Nx=1
Ief  vbn 0 50u
Rref vbn br {RREF}
Rb   vbn b1 {RB}
Cbn  vbn 0 {CBYP}
XM1 cr  enb 0 0 sg13_lv_nmos w=10u l=0.13u ng=1
XM2 vbn enb 0 0 sg13_lv_nmos w=8u l=0.13u ng=1
XQ1  c1 b1 e1 0 npn13G2 Nx=8
Re1  e1 0 {RE1}
XQ2  col vcas c1 0 npn13G2v Nx=8
Vcas vcas 0 {VCAS}
Ccas vcas 0 {CBYP}
Lc   vcc lx {LC}
RLc  lx col {W0*LC/QL}
Cout col out {COUT}
.ends pa_en
