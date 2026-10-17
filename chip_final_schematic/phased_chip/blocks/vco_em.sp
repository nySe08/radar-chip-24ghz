* ---------------- VCO: cross-coupled LC, AC-coupled MOS varactor ----------------
* ports: outp outn (tank)  vtune (from PLL)  vcc
.subckt vco_em outp outn vtune vcc SELFT=1 LS=275p RS=3.08 CS=9.24f CCV=250f
.param LH=330p QL=15 W0=1.5158e11 ITAIL=3m VBB=1.5 CCB=200f RBB=2k VGB=1.25 RGB=10k
* EM-fitted tank coil: inductor3, 2 turns, w 6u, d 70.88u (openEMS: 622.5 pH / Q 15.3 at 24.1 GHz;
* fitted: 550 pH low-frequency, 9.24 fF self-capacitance, 6.16 ohm) -> per side 275 pH + 3.08 ohm
L1 vcc t1 {LS}
R1 t1 outp {RS}
L2 vcc t2 {LS}
R2 t2 outn {RS}
Ccoil outp outn {CS}
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
