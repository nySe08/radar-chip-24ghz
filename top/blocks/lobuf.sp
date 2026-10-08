* ---------------- LO buffer: emitter followers + three tuned differential drivers ----------------
* ports: vinp vinn (from VCO)  mixp mixn / pap pan / divp divn (AC-coupled outputs)  vcc
.subckt lobuf vinp vinn mixp mixn pap pan divp divn vcc
.param IEF=1.5m ID1=2m ID2=2m ID3=1.5m LD1=1.3n LD2=1.1n LD3=1.5n RD=400 CC=500f CDB=1p RDB=2k VBD=1.35
XQe1 vcc vinp ef1 0 npn13G2 Nx=2
XQe2 vcc vinn ef2 0 npn13G2 Nx=2
Ie1  ef1 0 {IEF}
Ie2  ef2 0 {IEF}
Cdb1 ef1 b1 {CDB}
Cdb2 ef2 b2 {CDB}
Rdb1 vbd b1 {RDB}
Rdb2 vbd b2 {RDB}
Vbd  vbd 0 {VBD}
* driver 1 -> mixer LO
XQ11 d1p b2 dt1 0 npn13G2 Nx=2
XQ12 d1n b1 dt1 0 npn13G2 Nx=2
It1  dt1 0 {ID1}
L11  vcc d1p {LD1}
L12  vcc d1n {LD1}
R11  vcc d1p {RD}
R12  vcc d1n {RD}
* driver 2 -> PA
XQ21 d2p b2 dt2 0 npn13G2 Nx=2
XQ22 d2n b1 dt2 0 npn13G2 Nx=2
It2  dt2 0 {ID2}
L21  vcc d2p {LD2}
L22  vcc d2n {LD2}
R21  vcc d2p {RD}
R22  vcc d2n {RD}
* driver 3 -> divider
XQ31 d3p b2 dt3 0 npn13G2 Nx=2
XQ32 d3n b1 dt3 0 npn13G2 Nx=2
It3  dt3 0 {ID3}
L31  vcc d3p {LD3}
L32  vcc d3n {LD3}
R31  vcc d3p {RD}
R32  vcc d3n {RD}
* AC-coupled outputs (each load sets its own DC bias)
Cm1 d1p mixp {CC}
Cm2 d1n mixn {CC}
Cp1 d2p pap {CC}
Cp2 d2n pan {CC}
Cd1 d3p divp {CC}
Cd2 d3n divn {CC}
.ends lobuf
