* ---------------- VCO, REALIZED: no ideal sources; PDK R/C; EM-fitted tank coil ----------------
* cross-coupled HBT pair (capacitively coupled bases), AC-coupled MOS varactor, resistor tail.
* ports: outp outn (tank)  vtune (from PLL)  vcc
* (no start-up kick inside: on silicon the oscillator starts from noise; testbenches add their own kick)
.subckt vco_real outp outn vtune vcc SELFT=1 LS=275p RS=3.08 CS=9.24f CCVW=11.3u RTL=1.41u
* EM-fitted tank coil: inductor3, 2 turns, w 6u, d 70.88u (openEMS: 622.5 pH / Q 15.3 at 24.1 GHz)
L1 vcc t1 {LS}
R1 t1 outp {RS}
L2 vcc t2 {LS}
R2 t2 outn {RS}
Ccoil outp outn {CS}
* varactor branch: 280 fF coupling caps, 10 kohm gate-bias feeds, 1.25 V gate bias from a divider
XCcv1 outp g1 0 cap_rfcmim w={CCVW} l={CCVW}
XCcv2 outn g2 0 cap_rfcmim w={CCVW} l={CCVW}
XRg1 vgb g1 0 rhigh w=1u l=7.0u
XRg2 vgb g2 0 rhigh w=1u l=7.0u
XRgb1 vcc vgb 0 rhigh w=1u l=13.30u
XRgb2 vgb 0 0 rhigh w=1u l=13.30u
XCgb vgb 0 0 cap_rfcmim w=33u l=33u
XV1 g1 vtune g2 0 sg13_hv_svaricap l=0.3u w=9.74u Nx=10
* cross-coupled pair: 200 fF base coupling, 2 kohm base feeds, 1.5 V base bias from a divider
XQ6 outp b6 tail 0 npn13G2 Nx=4 selft={SELFT}
XQ7 outn b7 tail 0 npn13G2 Nx=4 selft={SELFT}
XCb6 outn b6 0 cap_rfcmim w=11.5u l=11.5u
XCb7 outp b7 0 cap_rfcmim w=11.5u l=11.5u
XRb6 vbb b6 0 rppd w=1u l=7.47u
XRb7 vbb b7 0 rppd w=1u l=7.47u
XRbb1 vcc vbb 0 rppd w=1u l=15.21u
XRbb2 vbb 0 0 rppd w=1u l=22.95u
XCbb vbb 0 0 cap_rfcmim w=33u l=33u
* tail: resistor (~218 ohm -> ~3 mA); no transistor current source to add noise
XRtail tail 0 0 rppd w=2u l={RTL}
.ends vco_real
