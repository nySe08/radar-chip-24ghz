* ---------------- Mixer: single-balanced active HBT ----------------
* ports: rfin (from LNA)  lop lon (LO, AC-coupled from buffer)  ifp ifn (IF out)  vcc
.subckt mixer rfin lop lon ifp ifn vcc
.param RE=75 RL=300 CL=1.76p RT=60 VB3=1.178 VLODC=1.9 RLO=2k
Cdc  rfin b3 10p
Rt   vb3 b3 {RT}
Vb3  vb3 0 {VB3}
XQ3  x b3 e3 0 npn13G2 Nx=4
Re   e3 0 {RE}
* LO port DC bias (the buffer output is AC-coupled)
Rlo1 vlo lop {RLO}
Rlo2 vlo lon {RLO}
Vlo  vlo 0 {VLODC}
XQ4  ifp lop x 0 npn13G2 Nx=2
XQ5  ifn lon x 0 npn13G2 Nx=2
RLp  vcc ifp {RL}
CLp  vcc ifp {CL}
RLn  vcc ifn {RL}
CLn  vcc ifn {CL}
.ends mixer
