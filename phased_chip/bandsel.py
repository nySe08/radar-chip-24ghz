"""bandsel.py - the switched-capacitor band select (experiment netlist, attached at the varactor taps of the post-layout VCO)."""
def branch(cw=2.5, W=8, vsel=0.0, ccv=None):
    ng = max(1, int(round(W / 2.0)))
    s = f"""XCsw1 vcop_v bs_s1 GND cap_rfcmim w={cw}u l={cw}u
XCsw2 vcon_v bs_s2 GND cap_rfcmim w={cw}u l={cw}u
XMsw bs_s1 bs_g bs_s2 GND sg13_lv_nmos w={W}u l=0.13u ng={ng}
XRsw1 bs_s1 GND GND rhigh w=1u l=14u
XRsw2 bs_s2 GND GND rhigh w=1u l=14u
XRswg bs_sel bs_g GND rhigh w=1u l=14u
Vbsel_tb bs_sel GND dc {vsel}"""
    return s
