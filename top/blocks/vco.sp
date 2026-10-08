* ---------------- VCO: cross-coupled LC, AC-coupled MOS varactor ----------------
* ports: outp outn (tank)  vtune (from PLL)  vcc
.subckt vco outp outn vtune vcc
.param LH=330p QL=15 W0=1.5158e11 ITAIL=3m VBB=1.5 CCB=200f RBB=2k CCV=250f VGB=1.25 RGB=10k
L1  vcc t1 {LH}
R1  t1 outp {W0*LH/QL}
L2  vcc t2 {LH}
R2  t2 outn {W0*LH/QL}
Ccv1 outp g1 {CCV}
Ccv2 outn g2 {CCV}
Rg1 vgb g1 {RGB}
Rg2 vgb g2 {RGB}
Vgb vgb 0 {VGB}
XV1 g1 vtune g2 0 sg13_hv_svaricap l=0.3u w=9.74u Nx=10
XQ6 outp b6 tail 0 npn13G2 Nx=4
XQ7 outn b7 tail 0 npn13G2 Nx=4
Cb6 outn b6 {CCB}
Cb7 outp b7 {CCB}
Rb6 vbb b6 {RBB}
Rb7 vbb b7 {RBB}
Vbb vbb 0 {VBB}
It  tail 0 {ITAIL}
Ik  outp 0 pulse(0 1m 0 5p 5p 10p 1)
.ends vco
