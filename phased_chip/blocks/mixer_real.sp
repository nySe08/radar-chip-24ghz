* ---------------- Mixer, REALIZED: PDK resistors/caps, real bias (no ideal sources) ----------------
* ports: rfin  lop lon (LO, AC-coupled)  ifp ifn  vcc
.subckt mixer_real rfin lop lon ifp ifn vcc
* RF input: DC block (self-resonant RF MIM) + 60-ohm termination to the bias node vb3
XCdc rfin b3 0 cap_rfcmim w=33u l=33u
XRt  vb3 b3 0 rsil w=1u l=7.55u
* Q3 bias: mirror reference (x4 ratio, matched emitter degeneration), from VCC
XRrf vcc vb3 0 rppd w=1u l=4.37u
XQrf vb3 vb3 erf 0 npn13G2 Nx=1
XRerf erf 0 0 rsil w=1u l=38.2u
XCb3 vb3 0 0 cap_rfcmim w=33u l=33u
* transconductor
XQ3  x b3 e3 0 npn13G2 Nx=4
XRe  e3 0 0 rsil w=1u l=9.55u
* LO-port bias 1.9 V: divider from VCC + bypass, 2k into each base
XRd1 vcc vlo 0 rppd w=1u l=22.95u
XRd2 vlo 0 0 rhigh w=1u l=13.30u
XCvl vlo 0 0 cap_rfcmim w=33u l=33u
XRl1 vlo lop 0 rppd w=1u l=7.47u
XRl2 vlo lon 0 rppd w=1u l=7.47u
* switching pair + IF loads
XQ4  ifp lop x 0 npn13G2 Nx=2
XQ5  ifn lon x 0 npn13G2 Nx=2
XRLp vcc ifp 0 rppd w=2u l=2.05u
XRLn vcc ifn 0 rppd w=2u l=2.05u
XCLp vcc ifp cap_cmim w=34.3u l=34.3u
XCLn vcc ifn cap_cmim w=34.3u l=34.3u
.ends mixer_real
