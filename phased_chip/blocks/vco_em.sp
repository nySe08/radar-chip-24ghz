* ---------------- VCO: cross-coupled LC, AC-coupled MOS varactor ----------------
* ports: outp outn (tank)  vtune (from PLL)  vcc
.subckt vco_em outp outn vtune vcc SELFT=1 SC=0.90
.param LH=330p QL=15 W0=1.5158e11 ITAIL=3m VBB=1.5 CCB=200f RBB=2k CCV=250f VGB=1.25 RGB=10k
* EM-fitted tank coil (inductor3 2 turns): per side L0/2 = 307.5 pH x SC, loss, self-capacitance across
L1 vcc t1 {SC*307.5p}
R1 t1 outp {SC*3.51}
L2 vcc t2 {SC*307.5p}
R2 t2 outn {SC*3.51}
Ccoil outp outn {12.5f*SC}
Ccv1 outp g1 {CCV}
Ccv2 outn g2 {CCV}
Rg1 vgb g1 {RGB}
Rg2 vgb g2 {RGB}
Vgb vgb 0 {VGB}
XV1 g1 vtune g2 0 sg13_hv_svaricap l=0.3u w=9.74u Nx=10
XQ6 outp b6 tail 0 npn13G2 Nx=4 selft={SELFT}
XQ7 outn b7 tail 0 npn13G2 Nx=4 selft={SELFT}
Cb6 outn b6 {CCB}
Cb7 outp b7 {CCB}
Rb6 vbb b6 {RBB}
Rb7 vbb b7 {RBB}
Vbb vbb 0 {VBB}
It  tail 0 {ITAIL}
Ik  outp 0 pulse(0 1m 0 5p 5p 10p 1)
.ends vco_em
