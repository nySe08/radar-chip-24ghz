* channel LO driver - IDEAL version (as verified in the LO tree)
.subckt lodrv inp inn outp outn vcc params: I=2m L=1.8n R=400 RB=5k
Cin1 inp b1 1p
Cin2 inn b2 1p
Rb1 vbd b1 {RB}
Rb2 vbd b2 {RB}
Vbd vbd 0 1.35
XQa dp b1 t 0 npn13G2 Nx=2
XQb dn b2 t 0 npn13G2 Nx=2
It t 0 {I}
L1 vcc dp {L}
L2 vcc dn {L}
R1 vcc dp {R}
R2 vcc dn {R}
Cc1 dp outp 500f
Cc2 dn outn 500f
.ends lodrv
* channel LO driver - REALIZED: tail resistor, divider bias, PDK R/C (inductors still ideal, Q=15)
.subckt lodrv_real inp inn outp outn vcc params: L=1.8n CPAR=0 RDL=2.83u
XCi1 inp b1 0 cap_rfcmim w=25u l=25u
XCi2 inn b2 0 cap_rfcmim w=25u l=25u
XRv1 vcc vbd 0 rppd w=1u l=17.53u
XRv2 vbd 0 0 rppd w=1u l=20.63u
XCvb vbd 0 0 cap_rfcmim w=33u l=33u
XRb1 vbd b1 0 rppd w=1u l=19.08u
XRb2 vbd b2 0 rppd w=1u l=19.08u
XQa dp b1 t 0 npn13G2 Nx=2
XQb dn b2 t 0 npn13G2 Nx=2
XRt t 0 0 rppd w=2u l={RTL}
L1 vcc d1 {L}
RL1 d1 dp {1.5158e11*L/15}
L2 vcc d2 {L}
RL2 d2 dn {1.5158e11*L/15}
XR1 vcc dp 0 rppd w=2u l={RDL}
XR2 vcc dn 0 rppd w=2u l={RDL}
* inductor self-capacitance (per side)
Cp1 dp 0 {CPAR}
Cp2 dn 0 {CPAR}
XCc1 dp outp 0 cap_rfcmim w=12u l=12u
XCc2 dn outn 0 cap_rfcmim w=12u l=12u
.ends lodrv_real

* channel LO driver - FINAL REALIZED VERSION: resistive load, no inductor
* (EM showed a 3.6 nH centre-tapped spiral self-resonates at ~12 GHz; with 200-ohm loads and a 4 mA tail
*  the limiting driver still delivers 0.33-0.40 V per side to the mixer at all corners, with no spiral)
.subckt lodrv_res inp inn outp outn vcc
XCi1 inp b1 0 cap_rfcmim w=25u l=25u
XCi2 inn b2 0 cap_rfcmim w=25u l=25u
XRv1 vcc vbd 0 rppd w=1u l=17.53u
XRv2 vbd 0 0 rppd w=1u l=20.63u
XCvb vbd 0 0 cap_rfcmim w=33u l=33u
XRb1 vbd b1 0 rppd w=1u l=19.08u
XRb2 vbd b2 0 rppd w=1u l=19.08u
XQa dp b1 t 0 npn13G2 Nx=2
XQb dn b2 t 0 npn13G2 Nx=2
XRt t 0 0 rppd w=2u l=0.79u
XR1 vcc dp 0 rppd w=2u l=1.28u
XR2 vcc dn 0 rppd w=2u l=1.28u
XCc1 dp outp 0 cap_rfcmim w=12u l=12u
XCc2 dn outn 0 cap_rfcmim w=12u l=12u
.ends lodrv_res
