* ---------------- LO distribution, REALIZED (no ideal sources; ideal L only where a small EM-checkable spiral is planned) ----------------
* generic realized driver: tail resistor, divider bias, PDK R/C; L=1u means 'no inductor' (resistive load)
.subckt lodrv_g inp inn outp outn vcc params: L=1u CPAR=0 RDL=2.83u RTL=1.86u QL=12
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
RL1 d1 dp {1.5158e11*L/QL}
L2 vcc d2 {L}
RL2 d2 dn {1.5158e11*L/QL}
XR1 vcc dp 0 rppd w=2u l={RDL}
XR2 vcc dn 0 rppd w=2u l={RDL}
Cp1 dp 0 {CPAR}
Cp2 dn 0 {CPAR}
XCc1 dp outp 0 cap_rfcmim w=12u l=12u
XCc2 dn outn 0 cap_rfcmim w=12u l=12u
.ends lodrv_g

.subckt lodist_em vinp vinn m1p m1n m2p m2n m3p m3n m4p m4n pa1p pa1n pa2p pa2n divp divn vcc params: PAL=1u PACP=0 PARD=0.89u PART=0.79u PRL=300p PRT=1.15u
* emitter followers with real emitter resistors (~1.1 kohm -> ~1.5 mA)
XQe1 vcc vinp ef1 0 npn13G2 Nx=2
XQe2 vcc vinn ef2 0 npn13G2 Nx=2
XRe1 ef1 0 0 rppd w=2u l=8.24u
XRe2 ef2 0 0 rppd w=2u l=8.24u
* RX tree: pre-driver keeps a small (250 pH) load inductor; 4 resistive channel drivers
* RX pre-driver coil: EM-fitted (inductor3 2 turns w4 d65.36): 257.5 pH/side, Q 10.8, self-cap
Xprx ef1 ef2 rp rn vcc lodrv_g L=257.5p CPAR=16.4f QL=10.8 RDL=2.83u RTL={PRT}
XRr1 rp 0 0 rhigh w=1u l=14.0u
XRr2 rn 0 0 rhigh w=1u l=14.0u
Xd1 rp rn m1p m1n vcc lodrv_res
Xd2 rp rn m2p m2n vcc lodrv_res
Xd3 rp rn m3p m3n vcc lodrv_res
Xd4 rp rn m4p m4n vcc lodrv_res
* TX tree: pre-driver keeps a small (400 pH) load inductor; 2 PA drivers (load chosen by parameters)
* TX pre-driver coil: EM-fitted (inductor3 2 turns w4 d83.47): 345 pH/side, Q 10.2, self-cap
Xptx ef1 ef2 tp tn vcc lodrv_g L=345p CPAR=23.2f QL=10.2 RDL=2.83u RTL=1.86u
XRt1 tp 0 0 rhigh w=1u l=14.0u
XRt2 tn 0 0 rhigh w=1u l=14.0u
Xpd1 tp tn pa1p pa1n vcc lodrv_g L={PAL} CPAR={PACP} RDL={PARD} RTL={PART}
Xpd2 tp tn pa2p pa2n vcc lodrv_g L={PAL} CPAR={PACP} RDL={PARD} RTL={PART}
* divider driver: resistive (the divider needs only ~0.05 V)
Xdv ef1 ef2 divp divn vcc lodrv_g L=1u RDL=2.05u RTL=1.86u
.ends lodist_em
