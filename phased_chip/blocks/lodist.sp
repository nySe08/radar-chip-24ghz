* ---------------- LO distribution for the 2TX/4RX chip ----------------
* VCO -> emitter followers -> { RX pre-driver -> 4 channel drivers (mixers),
*                               TX pre-driver -> 2 PA drivers,  divider driver }
* All drivers: limiting differential pairs, tuned loads (L || R), AC-coupled in and out.
.subckt lodrv inp inn outp outn vcc params: I=1.5m L=1.3n R=400 RB=5k
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

.subckt lodist vinp vinn m1p m1n m2p m2n m3p m3n m4p m4n pa1p pa1n pa2p pa2n divp divn vcc
.param IEF=1.5m LPRE_RX=250p LPRE_TX=400p
XQe1 vcc vinp ef1 0 npn13G2 Nx=2
XQe2 vcc vinn ef2 0 npn13G2 Nx=2
Ie1 ef1 0 {IEF}
Ie2 ef2 0 {IEF}
* --- RX tree
Xprx ef1 ef2 rp rn vcc lodrv I=2m L={LPRE_RX} R=400
Rbr1 rp 0 20k
Rbr2 rn 0 20k
Xd1 rp rn m1p m1n vcc lodrv I=2m L=1.8n R=400
Xd2 rp rn m2p m2n vcc lodrv I=2m L=1.8n R=400
Xd3 rp rn m3p m3n vcc lodrv I=2m L=1.8n R=400
Xd4 rp rn m4p m4n vcc lodrv I=2m L=1.8n R=400
* --- TX tree
Xptx ef1 ef2 tp tn vcc lodrv I=2m L={LPRE_TX} R=400
Rbt1 tp 0 20k
Rbt2 tn 0 20k
Xpd1 tp tn pa1p pa1n vcc lodrv I=1.3m L=1.1n R=400
Xpd2 tp tn pa2p pa2n vcc lodrv I=1.3m L=1.1n R=400
* --- divider driver
Xdv ef1 ef2 divp divn vcc lodrv I=1.5m L=1.5n R=400
.ends lodist
