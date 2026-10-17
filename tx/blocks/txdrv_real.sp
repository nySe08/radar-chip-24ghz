* per-channel TX driver, ALL REAL DEVICES: resistively loaded pair (the 1 uH ideal choke removed),
* unused output (outn) loaded with a dummy matching the PA input (18 ohm + 74 fF ~ 18 - j89 ohm at 24 GHz)
.subckt txdrv_real inp inn outp outn vcc RDL=0.89u RTL=0.79u
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
XR1 vcc dp 0 rppd w=2u l={RDL}
XR2 vcc dn 0 rppd w=2u l={RDL}
XCc1 dp outp 0 cap_rfcmim w=12u l=12u
XCc2 dn outn 0 cap_rfcmim w=12u l=12u
XCd  outn dd 0 cap_rfcmim w=7u l=7u
XRd  dd 0 0 rsil w=1u l=1.30u
.ends txdrv_real
