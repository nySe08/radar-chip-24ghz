.subckt varwrap g1 vtune g2 NX=10
XV1 g1 vtune g2 0 sg13_hv_svaricap l=0.3u w=9.74u Nx={NX}
.ends varwrap
.subckt lo_core BSEL GND PLLN PLLP RXLON RXLOP TXLON TXLOP VCC VTUNE
LLvcoa VCC Lvco_ma 172p
RLvcoa Lvco_ma vcop_L 1.27
LLvcob VCC Lvco_mb 172p
RLvcob Lvco_mb vcon_L 1.27
CLvcop vcop vcon 3.9f
XCvco_cv1 vcop_cv vco_g1 GND cap_rfcmim w=16u l=16u
XCvco_cv2 vcon_cv vco_g2 GND cap_rfcmim w=16u l=16u
XRvco_g1 vco_vgb vco_g1 GND rhigh w=1u l=7.0u
XRvco_g2 vco_vgb vco_g2 GND rhigh w=1u l=7.0u
XRvco_gb1 VCC vco_vgb GND rhigh w=1u l=13.3u
XRvco_gb2 vco_vgb GND GND rhigh w=1u l=13.3u
XCvco_gb vco_vgb GND GND cap_rfcmim w=33u l=33u
XCvco_var vco_g1 VTUNE vco_g2 varwrap NX=7
XCbs_1 vcop_bs bs_s1 GND cap_rfcmim w=4.5u l=4.5u
XCbs_2 vcon_bs bs_s2 GND cap_rfcmim w=4.5u l=4.5u
XMbs bs_s1 bs_g bs_s2 GND sg13_lv_nmos w=24u l=0.13u ng=12
XRbs_1 bs_s1 GND GND rhigh w=1u l=14.0u
XRbs_2 bs_s2 GND GND rhigh w=1u l=14.0u
XRbs_g BSEL bs_g GND rhigh w=1u l=14.0u
XQvco_6 vcop vco_b6 vco_tail GND npn13G2 Nx=4
XQvco_7 vcon vco_b7 vco_tail GND npn13G2 Nx=4
XCvco_b6 vcon_cb vco_b6 GND cap_rfcmim w=9u l=9u
XCvco_b7 vcop_cb vco_b7 GND cap_rfcmim w=9u l=9u
XRvco_b6 vco_vbb vco_b6 GND rppd w=1u l=7.47u
XRvco_b7 vco_vbb vco_b7 GND rppd w=1u l=7.47u
XRvco_bb1 VCC vco_vbb GND rppd w=1u l=15.21u
XRvco_bb2 vco_vbb GND GND rppd w=1u l=22.95u
XCvco_bb vco_vbb GND GND cap_rfcmim w=33u l=33u
XRvco_tail vco_tail GND GND rppd w=2u l=1.03u
XQef_1 VCC vcop_e efp GND npn13G2 Nx=2
XQef_2 VCC vcon_e efn GND npn13G2 Nx=2
XRef_1 efp GND GND rppd w=2u l=5.15u
XRef_2 efn GND GND rppd w=2u l=5.15u
XCPRX_i1 efp_rx prx_b1 GND cap_rfcmim w=12u l=12u
XCPRX_i2 efn_rx prx_b2 GND cap_rfcmim w=12u l=12u
XRPRX_v1 VCC prx_vbd GND rppd w=1u l=17.53u
XRPRX_v2 prx_vbd GND GND rppd w=1u l=20.63u
XCPRX_vb prx_vbd GND GND cap_rfcmim w=33u l=33u
XRPRX_b1 prx_vbd prx_b1 GND rppd w=1u l=19.08u
XRPRX_b2 prx_vbd prx_b2 GND rppd w=1u l=19.08u
XQPRX_a prx_dp prx_b1 prx_t GND npn13G2 Nx=2
XQPRX_b prx_dn prx_b2 prx_t GND npn13G2 Nx=2
XRPRX_t prx_t GND GND rppd w=2u l=0.53u
LLPRXa VCC LPRX_ma 257.5p
RLPRXa LPRX_ma prx_dnL 3.63
LLPRXb VCC LPRX_mb 257.5p
RLPRXb LPRX_mb prx_dpL 3.63
CLPRXp prx_dn prx_dp 8.2f
XRPRX_d1 VCC prx_dp GND rppd w=2u l=2.83u
XRPRX_d2 VCC prx_dn GND rppd w=2u l=2.83u
XCPRX_c1 prx_dpC RXLOP_c GND cap_rfcmim w=12u l=12u
XCPRX_c2 prx_dnC RXLON_c GND cap_rfcmim w=12u l=12u
XRbl_r1 RXLOP GND GND rhigh w=1u l=14.0u
XRbl_r2 RXLON GND GND rhigh w=1u l=14.0u
XCPTX_i1 efp_tx ptx_b1 GND cap_rfcmim w=12u l=12u
XCPTX_i2 efn_tx ptx_b2 GND cap_rfcmim w=12u l=12u
XRPTX_v1 VCC ptx_vbd GND rppd w=1u l=17.53u
XRPTX_v2 ptx_vbd GND GND rppd w=1u l=20.63u
XCPTX_vb ptx_vbd GND GND cap_rfcmim w=33u l=33u
XRPTX_b1 ptx_vbd ptx_b1 GND rppd w=1u l=19.08u
XRPTX_b2 ptx_vbd ptx_b2 GND rppd w=1u l=19.08u
XQPTX_a ptx_dp ptx_b1 ptx_t GND npn13G2 Nx=2
XQPTX_b ptx_dn ptx_b2 ptx_t GND npn13G2 Nx=2
XRPTX_t ptx_t GND GND rppd w=2u l=1.15u
LLPTXa VCC LPTX_ma 345p
RLPTXa LPTX_ma ptx_dpL 5.13
LLPTXb VCC LPTX_mb 345p
RLPTXb LPTX_mb ptx_dnL 5.13
CLPTXp ptx_dp ptx_dn 11.6f
XRPTX_d1 VCC ptx_dp GND rppd w=2u l=2.83u
XRPTX_d2 VCC ptx_dn GND rppd w=2u l=2.83u
XCPTX_c1 ptx_dpC TXLOP_c GND cap_rfcmim w=12u l=12u
XCPTX_c2 ptx_dnC TXLON_c GND cap_rfcmim w=12u l=12u
XRbl_t1 TXLOP GND GND rhigh w=1u l=14.0u
XRbl_t2 TXLON GND GND rhigh w=1u l=14.0u
XCDDV_i1 efp_dv ddv_b1 GND cap_rfcmim w=12u l=12u
XCDDV_i2 efn_dv ddv_b2 GND cap_rfcmim w=12u l=12u
XRDDV_v1 VCC ddv_vbd GND rppd w=1u l=17.53u
XRDDV_v2 ddv_vbd GND GND rppd w=1u l=20.63u
XCDDV_vb ddv_vbd GND GND cap_rfcmim w=33u l=33u
XRDDV_b1 ddv_vbd ddv_b1 GND rppd w=1u l=19.08u
XRDDV_b2 ddv_vbd ddv_b2 GND rppd w=1u l=19.08u
XQDDV_a ddv_dp ddv_b1 ddv_t GND npn13G2 Nx=2
XQDDV_b ddv_dn ddv_b2 ddv_t GND npn13G2 Nx=2
XRDDV_t ddv_t GND GND rppd w=4u l=1.0u
XRDDV_d1 VCC ddv_dp GND rppd w=2u l=0.89u
XRDDV_d2 VCC ddv_dn GND rppd w=2u l=0.89u
XCDDV_c1 ddv_dpC ckp_c GND cap_rfcmim w=12u l=12u
XCDDV_c2 ddv_dnC ckn_c GND cap_rfcmim w=12u l=12u
XRdiv_ref VCC div_vbt GND rppd w=1u l=11.34u
XQdiv_br div_vbt div_vbt div_ebr GND npn13G2 Nx=1
XRdiv_ebr div_ebr GND GND rppd w=2u l=2.05u
XCdiv_bt div_vbt GND GND cap_rfcmim w=25u l=25u
XRdiv_k1 VCC div_vck GND rppd w=1u l=15.21u
XRdiv_k2 div_vck GND GND rppd w=1u l=22.95u
XCdiv_k div_vck GND GND cap_rfcmim w=33u l=33u
XRdiv_ck1 div_vck div_ckp GND rppd w=1u l=7.47u
XRdiv_ck2 div_vck div_ckn GND rppd w=1u l=7.47u
XRDM1_lp VCC m1q GND rppd w=4u l=1.11u
XRDM1_ln VCC m1qb GND rppd w=4u l=1.11u
XQDM1_d1 m1qb s1qb dm1_ed GND npn13G2 Nx=1
XQDM1_d2 m1q s1q dm1_ed GND npn13G2 Nx=1
XQDM1_h1 m1qb m1q dm1_eh GND npn13G2 Nx=1
XQDM1_h2 m1q m1qb dm1_eh GND npn13G2 Nx=1
XQDM1_c1 dm1_ed div_ckp dm1_et GND npn13G2 Nx=1
XQDM1_c2 dm1_eh div_ckn dm1_et GND npn13G2 Nx=1
XQDM1_t dm1_et div_vbt dm1_etr GND npn13G2 Nx=9
XRDM1_e dm1_etr GND GND rppd w=8u l=0.75u
XRDS1_lp VCC s1q GND rppd w=4u l=1.11u
XRDS1_ln VCC s1qb GND rppd w=4u l=1.11u
XQDS1_d1 s1qb m1q ds1_ed GND npn13G2 Nx=1
XQDS1_d2 s1q m1qb ds1_ed GND npn13G2 Nx=1
XQDS1_h1 s1qb s1q ds1_eh GND npn13G2 Nx=1
XQDS1_h2 s1q s1qb ds1_eh GND npn13G2 Nx=1
XQDS1_c1 ds1_ed div_ckn ds1_et GND npn13G2 Nx=1
XQDS1_c2 ds1_eh div_ckp ds1_et GND npn13G2 Nx=1
XQDS1_t ds1_et div_vbt ds1_etr GND npn13G2 Nx=9
XRDS1_e ds1_etr GND GND rppd w=8u l=0.75u
XCdiv_c1 s1q c2p GND cap_rfcmim w=8u l=8u
XCdiv_c2 s1qb c2n GND cap_rfcmim w=8u l=8u
XRdiv_b1 div_vck c2p GND rppd w=1u l=19.08u
XRdiv_b2 div_vck c2n GND rppd w=1u l=19.08u
XRDM2_lp VCC m2q GND rppd w=2u l=0.76u
XRDM2_ln VCC m2qb GND rppd w=2u l=0.76u
XQDM2_d1 m2qb s2qb dm2_ed GND npn13G2 Nx=1
XQDM2_d2 m2q s2q dm2_ed GND npn13G2 Nx=1
XQDM2_h1 m2qb m2q dm2_eh GND npn13G2 Nx=1
XQDM2_h2 m2q m2qb dm2_eh GND npn13G2 Nx=1
XQDM2_c1 dm2_ed c2p dm2_et GND npn13G2 Nx=1
XQDM2_c2 dm2_eh c2n dm2_et GND npn13G2 Nx=1
XQDM2_t dm2_et div_vbt dm2_etr GND npn13G2 Nx=6
XRDM2_e dm2_etr GND GND rppd w=8u l=1.28u
XRDS2_lp VCC s2q GND rppd w=2u l=0.76u
XRDS2_ln VCC s2qb GND rppd w=2u l=0.76u
XQDS2_d1 s2qb m2q ds2_ed GND npn13G2 Nx=1
XQDS2_d2 s2q m2qb ds2_ed GND npn13G2 Nx=1
XQDS2_h1 s2qb s2q ds2_eh GND npn13G2 Nx=1
XQDS2_h2 s2q s2qb ds2_eh GND npn13G2 Nx=1
XQDS2_c1 ds2_ed c2n ds2_et GND npn13G2 Nx=1
XQDS2_c2 ds2_eh c2p ds2_et GND npn13G2 Nx=1
XQDS2_t ds2_et div_vbt ds2_etr GND npn13G2 Nx=6
XRDS2_e ds2_etr GND GND rppd w=8u l=1.28u
XCdiv_o1 s2q div_o1 GND cap_rfcmim w=18.2u l=18.2u
XCdiv_o2 s2qb div_o2 GND cap_rfcmim w=18.2u l=18.2u
XRdiv_o1 VCC div_vbo GND rppd w=1u l=17.14u
XRdiv_o2 div_vbo GND GND rhigh w=1u l=5.53u
XCdiv_bo div_vbo GND GND cap_rfcmim w=33u l=33u
XRdiv_bo1 div_vbo div_o1 GND rppd w=1u l=19.08u
XRdiv_bo2 div_vbo div_o2 GND rppd w=1u l=19.08u
XQdiv_o1 PLLN div_o1 div_eo GND npn13G2 Nx=4
XQdiv_o2 PLLP div_o2 div_eo GND npn13G2 Nx=4
XQdiv_to1 div_eo div_vbt div_eto1 GND npn13G2 Nx=10
XQdiv_to2 div_eo div_vbt div_eto2 GND npn13G2 Nx=10
XRdiv_eo1 div_eto1 GND GND rppd w=16u l=0.97u
XRdiv_eo2 div_eto2 GND GND rppd w=16u l=0.97u
XRdiv_t1 VCC PLLP GND rppd w=10u l=1.66u
XRdiv_t2 VCC PLLN GND rppd w=10u l=1.66u
* TESTBENCH STIMULUS, simulation copy only (not in the LVS netlist / design): start-up kick for the VCO
Ikick_tb vcop 0 pulse(0 1m 0 5p 5p 10p 1)
* ======== layout interconnect (post-layout) ========
* tkpstub0: 13 um x 6 um, h=1.88 um -> Z0=37 ohm, L=2.9 pH, C=2.1 fF
L_tkpstub0 vcop_L tkpstub0_m 2.9152e-12
R_tkpstub0 tkpstub0_m vcop 0.0607
C_tkpstub0a vcop_L 0 1.0515e-15
C_tkpstub0b vcop 0 1.0515e-15
* tkp10: 22 um x 3 um, h=1.88 um -> Z0=58 ohm, L=7.4 pH, C=2.2 fF
L_tkp10 vcop tkp10_m 7.4162e-12
R_tkp10 tkp10_m vcop_x 0.2056
C_tkp10a vcop 0 1.1186e-15
C_tkp10b vcop_x 0 1.1186e-15
* tkpx0: 29 um x 4 um, h=6.68 um -> Z0=92 ohm, L=14.9 pH, C=1.8 fF
L_tkpx0 vcop_x tkpx0_m 1.4901e-11
R_tkpx0 tkpx0_m vcop_cb 0.2004
C_tkpx0a vcop_x 0 8.8185e-16
C_tkpx0b vcop_cb 0 8.8185e-16
* tkp20: 32 um x 3 um, h=1.88 um -> Z0=58 ohm, L=10.8 pH, C=3.3 fF
L_tkp20 vcop_x tkp20_m 1.0787e-11
R_tkp20 tkp20_m vcop_v 0.2990
C_tkp20a vcop_x 0 1.6270e-15
C_tkp20b vcop_v 0 1.6270e-15
* tkpcv0: 17 um x 3 um, h=1.88 um -> Z0=58 ohm, L=5.7 pH, C=1.7 fF
L_tkpcv0 vcop_v tkpcv0_m 5.7307e-12
R_tkpcv0 tkpcv0_m vcop_cv 0.1589
C_tkpcv0a vcop_v 0 8.6436e-16
C_tkpcv0b vcop_cv 0 8.6436e-16
* tkp30: 43 um x 3 um, h=1.88 um -> Z0=58 ohm, L=14.5 pH, C=4.4 fF
L_tkp30 vcop_v tkp30_m 1.4495e-11
R_tkp30 tkp30_m vcop_e 0.4018
C_tkp30a vcop_v 0 2.1863e-15
C_tkp30b vcop_e 0 2.1863e-15
* tkpbs0: 9 um x 3 um, h=1.88 um -> Z0=58 ohm, L=3.0 pH, C=0.9 fF
L_tkpbs0 vcop_e tkpbs0_m 3.0339e-12
R_tkpbs0 tkpbs0_m vcop_bs 0.0841
C_tkpbs0a vcop_e 0 4.5760e-16
C_tkpbs0b vcop_bs 0 4.5760e-16
* tknstub0: 13 um x 6 um, h=1.88 um -> Z0=37 ohm, L=2.9 pH, C=2.1 fF
L_tknstub0 vcon_L tknstub0_m 2.9152e-12
R_tknstub0 tknstub0_m vcon 0.0607
C_tknstub0a vcon_L 0 1.0515e-15
C_tknstub0b vcon 0 1.0515e-15
* tkn10: 34 um x 3 um, h=1.88 um -> Z0=58 ohm, L=11.5 pH, C=3.5 fF
L_tkn10 vcon tkn10_m 1.1461e-11
R_tkn10 tkn10_m vcon_x 0.3177
C_tkn10a vcon 0 1.7287e-15
C_tkn10b vcon_x 0 1.7287e-15
* tknx0: 28 um x 4 um, h=6.68 um -> Z0=92 ohm, L=14.7 pH, C=1.7 fF
L_tknx0 vcon_x tknx0_m 1.4693e-11
R_tknx0 tknx0_m vcon_cb 0.1976
C_tknx0a vcon_x 0 8.6952e-16
C_tknx0b vcon_cb 0 8.6952e-16
* tkn20: 20 um x 3 um, h=1.88 um -> Z0=58 ohm, L=6.7 pH, C=2.0 fF
L_tkn20 vcon_x tkn20_m 6.7420e-12
R_tkn20 tkn20_m vcon_v 0.1869
C_tkn20a vcon_x 0 1.0169e-15
C_tkn20b vcon_v 0 1.0169e-15
* tkncv0: 18 um x 3 um, h=1.88 um -> Z0=58 ohm, L=6.0 pH, C=1.8 fF
L_tkncv0 vcon_v tkncv0_m 6.0341e-12
R_tkncv0 tkncv0_m vcon_cv 0.1673
C_tkncv0a vcon_v 0 9.1012e-16
C_tkncv0b vcon_cv 0 9.1012e-16
* tkn30: 43 um x 3 um, h=1.88 um -> Z0=58 ohm, L=14.5 pH, C=4.4 fF
L_tkn30 vcon_v tkn30_m 1.4495e-11
R_tkn30 tkn30_m vcon_e 0.4018
C_tkn30a vcon_v 0 2.1863e-15
C_tkn30b vcon_e 0 2.1863e-15
* tknbs0: 9 um x 3 um, h=1.88 um -> Z0=58 ohm, L=3.0 pH, C=0.9 fF
L_tknbs0 vcon_e tknbs0_m 3.0339e-12
R_tknbs0 tknbs0_m vcon_bs 0.0841
C_tknbs0a vcon_e 0 4.5760e-16
C_tknbs0b vcon_bs 0 4.5760e-16
* bp_dv0: 115 um x 1.2 um, h=0.6 um -> Z0=50 ohm, L=34.3 pH, C=13.5 fF
L_bp_dv0 efp bp_dv0_m 3.4285e-11
R_bp_dv0 bp_dv0_m bp_dv_1 9.5872
C_bp_dv0a efp 0 6.7290e-15
C_bp_dv0b bp_dv_1 0 6.7290e-15
* bp_dv1: 115 um x 1.2 um, h=0.6 um -> Z0=50 ohm, L=34.3 pH, C=13.5 fF
L_bp_dv1 bp_dv_1 bp_dv1_m 3.4285e-11
R_bp_dv1 bp_dv1_m efp_dvd 9.5872
C_bp_dv1a bp_dv_1 0 6.7290e-15
C_bp_dv1b efp_dvd 0 6.7290e-15
* bp_dvd0: 22 um x 1.2 um, h=1.7 um -> Z0=86 ohm, L=10.8 pH, C=1.5 fF
L_bp_dvd0 efp_dvd bp_dvd0_m 1.0757e-11
R_bp_dvd0 bp_dvd0_m efp_dv 1.8341
C_bp_dvd0a efp_dvd 0 7.2969e-16
C_bp_dvd0b efp_dv 0 7.2969e-16
* bp_rx0: 39 um x 1.2 um, h=0.6 um -> Z0=50 ohm, L=11.6 pH, C=4.6 fF
L_bp_rx0 efp bp_rx0_m 1.1627e-11
R_bp_rx0 bp_rx0_m efp_rxd 3.2513
C_bp_rx0a efp 0 2.2820e-15
C_bp_rx0b efp_rxd 0 2.2820e-15
* bp_rxd0: 33 um x 1.2 um, h=1.7 um -> Z0=86 ohm, L=16.1 pH, C=2.2 fF
L_bp_rxd0 efp_rxd bp_rxd0_m 1.6136e-11
R_bp_rxd0 bp_rxd0_m efp_rx 2.7511
C_bp_rxd0a efp_rxd 0 1.0945e-15
C_bp_rxd0b efp_rx 0 1.0945e-15
* bp_tx0: 100 um x 1.2 um, h=0.6 um -> Z0=50 ohm, L=29.8 pH, C=11.7 fF
L_bp_tx0 efp bp_tx0_m 2.9813e-11
R_bp_tx0 bp_tx0_m bp_tx_1 8.3367
C_bp_tx0a efp 0 5.8513e-15
C_bp_tx0b bp_tx_1 0 5.8513e-15
* bp_tx1: 100 um x 1.2 um, h=0.6 um -> Z0=50 ohm, L=29.8 pH, C=11.7 fF
L_bp_tx1 bp_tx_1 bp_tx1_m 2.9813e-11
R_bp_tx1 bp_tx1_m bp_tx_2 8.3367
C_bp_tx1a bp_tx_1 0 5.8513e-15
C_bp_tx1b bp_tx_2 0 5.8513e-15
* bp_tx2: 100 um x 1.2 um, h=0.6 um -> Z0=50 ohm, L=29.8 pH, C=11.7 fF
L_bp_tx2 bp_tx_2 bp_tx2_m 2.9813e-11
R_bp_tx2 bp_tx2_m efp_txd 8.3367
C_bp_tx2a bp_tx_2 0 5.8513e-15
C_bp_tx2b efp_txd 0 5.8513e-15
* bp_txd0: 92 um x 1.2 um, h=1.7 um -> Z0=86 ohm, L=45.0 pH, C=6.1 fF
L_bp_txd0 efp_txd bp_txd0_m 4.4985e-11
R_bp_txd0 bp_txd0_m efp_tx 7.6697
C_bp_txd0a efp_txd 0 3.0514e-15
C_bp_txd0b efp_tx 0 3.0514e-15
* bn_dv0: 98 um x 1.2 um, h=1.7 um -> Z0=86 ohm, L=48.2 pH, C=6.5 fF
L_bn_dv0 efn bn_dv0_m 4.8163e-11
R_bn_dv0 bn_dv0_m bn_dv_1 8.2116
C_bn_dv0a efn 0 3.2670e-15
C_bn_dv0b bn_dv_1 0 3.2670e-15
* bn_dv1: 98 um x 1.2 um, h=1.7 um -> Z0=86 ohm, L=48.2 pH, C=6.5 fF
L_bn_dv1 bn_dv_1 bn_dv1_m 4.8163e-11
R_bn_dv1 bn_dv1_m efn_dv 8.2116
C_bn_dv1a bn_dv_1 0 3.2670e-15
C_bn_dv1b efn_dv 0 3.2670e-15
* bn_rx0: 73 um x 1.2 um, h=1.7 um -> Z0=86 ohm, L=35.7 pH, C=4.8 fF
L_bn_rx0 efn bn_rx0_m 3.5695e-11
R_bn_rx0 bn_rx0_m efn_rx 6.0858
C_bn_rx0a efn 0 2.4213e-15
C_bn_rx0b efn_rx 0 2.4213e-15
* bn_tx0: 136 um x 1.2 um, h=1.7 um -> Z0=86 ohm, L=66.6 pH, C=9.0 fF
L_bn_tx0 efn bn_tx0_m 6.6622e-11
R_bn_tx0 bn_tx0_m bn_tx_1 11.3587
C_bn_tx0a efn 0 4.5191e-15
C_bn_tx0b bn_tx_1 0 4.5191e-15
* bn_tx1: 136 um x 1.2 um, h=1.7 um -> Z0=86 ohm, L=66.6 pH, C=9.0 fF
L_bn_tx1 bn_tx_1 bn_tx1_m 6.6622e-11
R_bn_tx1 bn_tx1_m bn_tx_2 11.3587
C_bn_tx1a bn_tx_1 0 4.5191e-15
C_bn_tx1b bn_tx_2 0 4.5191e-15
* bn_tx2: 136 um x 1.2 um, h=1.7 um -> Z0=86 ohm, L=66.6 pH, C=9.0 fF
L_bn_tx2 bn_tx_2 bn_tx2_m 6.6622e-11
R_bn_tx2 bn_tx2_m bn_tx_3 11.3587
C_bn_tx2a bn_tx_2 0 4.5191e-15
C_bn_tx2b bn_tx_3 0 4.5191e-15
* bn_tx3: 136 um x 1.2 um, h=1.7 um -> Z0=86 ohm, L=66.6 pH, C=9.0 fF
L_bn_tx3 bn_tx_3 bn_tx3_m 6.6622e-11
R_bn_tx3 bn_tx3_m efn_tx 11.3587
C_bn_tx3a bn_tx_3 0 4.5191e-15
C_bn_tx3b efn_tx 0 4.5191e-15
* prxcp0: 82 um x 3 um, h=1.88 um -> Z0=58 ohm, L=27.6 pH, C=8.3 fF
L_prxcp0 prx_dp prxcp0_m 2.7642e-11
R_prxcp0 prxcp0_m prx_dpL 0.7662
C_prxcp0a prx_dp 0 4.1693e-15
C_prxcp0b prx_dpL 0 4.1693e-15
* prxcn0: 56 um x 3 um, h=1.88 um -> Z0=58 ohm, L=18.9 pH, C=5.7 fF
L_prxcn0 prx_dn prxcn0_m 1.8877e-11
R_prxcn0 prxcn0_m prx_dnL 0.5233
C_prxcn0a prx_dn 0 2.8473e-15
C_prxcn0b prx_dnL 0 2.8473e-15
* ptxcp0: 96 um x 3 um, h=1.88 um -> Z0=58 ohm, L=32.4 pH, C=9.8 fF
L_ptxcp0 ptx_dp ptxcp0_m 3.2361e-11
R_ptxcp0 ptxcp0_m ptx_dpL 0.8970
C_ptxcp0a ptx_dp 0 4.8811e-15
C_ptxcp0b ptx_dpL 0 4.8811e-15
* ptxcn0: 92 um x 3 um, h=1.88 um -> Z0=58 ohm, L=31.0 pH, C=9.4 fF
L_ptxcn0 ptx_dn ptxcn0_m 3.1013e-11
R_ptxcn0 ptxcn0_m ptx_dnL 0.8597
C_ptxcn0a ptx_dn 0 4.6777e-15
C_ptxcn0b ptx_dnL 0 4.6777e-15
* prxop0: 75 um x 1.0 um, h=1.7 um -> Z0=93 ohm, L=39.3 pH, C=4.6 fF
L_prxop0 prx_dp prxop0_m 3.9339e-11
R_prxop0 prxop0_m prx_dpC 7.5030
C_prxop0a prx_dp 0 2.2949e-15
C_prxop0b prx_dpC 0 2.2949e-15
* prxon0: 74 um x 1.0 um, h=1.7 um -> Z0=93 ohm, L=38.8 pH, C=4.5 fF
L_prxon0 prx_dn prxon0_m 3.8814e-11
R_prxon0 prxon0_m prx_dnC 7.4030
C_prxon0a prx_dn 0 2.2643e-15
C_prxon0b prx_dnC 0 2.2643e-15
* ptxop0: 75 um x 1.0 um, h=1.7 um -> Z0=93 ohm, L=39.3 pH, C=4.6 fF
L_ptxop0 ptx_dp ptxop0_m 3.9339e-11
R_ptxop0 ptxop0_m ptx_dpC 7.5030
C_ptxop0a ptx_dp 0 2.2949e-15
C_ptxop0b ptx_dpC 0 2.2949e-15
* ptxon0: 74 um x 1.0 um, h=1.7 um -> Z0=93 ohm, L=38.8 pH, C=4.5 fF
L_ptxon0 ptx_dn ptxon0_m 3.8814e-11
R_ptxon0 ptxon0_m ptx_dnC 7.4030
C_ptxon0a ptx_dn 0 2.2643e-15
C_ptxon0b ptx_dnC 0 2.2643e-15
* ddvop0: 75 um x 1.0 um, h=1.7 um -> Z0=93 ohm, L=39.3 pH, C=4.6 fF
L_ddvop0 ddv_dp ddvop0_m 3.9339e-11
R_ddvop0 ddvop0_m ddv_dpC 7.5030
C_ddvop0a ddv_dp 0 2.2949e-15
C_ddvop0b ddv_dpC 0 2.2949e-15
* ddvon0: 74 um x 1.0 um, h=1.7 um -> Z0=93 ohm, L=38.8 pH, C=4.5 fF
L_ddvon0 ddv_dn ddvon0_m 3.8814e-11
R_ddvon0 ddvon0_m ddv_dnC 7.4030
C_ddvon0a ddv_dn 0 2.2643e-15
C_ddvon0b ddv_dnC 0 2.2643e-15
* oRXLOP0: 139 um x 4 um, h=6.68 um -> Z0=92 ohm, L=72.4 pH, C=8.6 fF
L_oRXLOP0 RXLOP_c oRXLOP0_m 7.2423e-11
R_oRXLOP0 oRXLOP0_m RXLOP 0.9741
C_oRXLOP0a RXLOP_c 0 4.2859e-15
C_oRXLOP0b RXLOP 0 4.2859e-15
* oRXLON0: 133 um x 4 um, h=6.68 um -> Z0=92 ohm, L=69.3 pH, C=8.2 fF
L_oRXLON0 RXLON_c oRXLON0_m 6.9297e-11
R_oRXLON0 oRXLON0_m RXLON 0.9321
C_oRXLON0a RXLON_c 0 4.1009e-15
C_oRXLON0b RXLON 0 4.1009e-15
* oTXLOP0: 169 um x 4 um, h=6.68 um -> Z0=92 ohm, L=88.1 pH, C=10.4 fF
L_oTXLOP0 TXLOP_c oTXLOP0_m 8.8054e-11
R_oTXLOP0 oTXLOP0_m TXLOP 1.1844
C_oTXLOP0a TXLOP_c 0 5.2109e-15
C_oTXLOP0b TXLOP 0 5.2109e-15
* oTXLON0: 62 um x 4 um, h=6.68 um -> Z0=92 ohm, L=32.3 pH, C=3.8 fF
L_oTXLON0 TXLON_c oTXLON0_m 3.2304e-11
R_oTXLON0 oTXLON0_m TXLON 0.4345
C_oTXLON0a TXLON_c 0 1.9117e-15
C_oTXLON0b TXLON 0 1.9117e-15
* ckp10: 180 um x 3 um, h=1.88 um -> Z0=58 ohm, L=60.7 pH, C=18.3 fF
L_ckp10 ckp_c ckp10_m 6.0678e-11
R_ckp10 ckp10_m ckp_b 1.6820
C_ckp10a ckp_c 0 9.1520e-15
C_ckp10b ckp_b 0 9.1520e-15
* ckp20: 75 um x 1.0 um, h=1.7 um -> Z0=93 ohm, L=39.3 pH, C=4.6 fF
L_ckp20 ckp_b ckp20_m 3.9339e-11
R_ckp20 ckp20_m ckp2_1 7.5030
C_ckp20a ckp_b 0 2.2949e-15
C_ckp20b ckp2_1 0 2.2949e-15
* ckp21: 75 um x 1.0 um, h=1.7 um -> Z0=93 ohm, L=39.3 pH, C=4.6 fF
L_ckp21 ckp2_1 ckp21_m 3.9339e-11
R_ckp21 ckp21_m div_ckp 7.5030
C_ckp21a ckp2_1 0 2.2949e-15
C_ckp21b div_ckp 0 2.2949e-15
* ckn10: 220 um x 3 um, h=1.88 um -> Z0=58 ohm, L=74.2 pH, C=22.4 fF
L_ckn10 ckn_c ckn10_m 7.4162e-11
R_ckn10 ckn10_m ckn_b 2.0557
C_ckn10a ckn_c 0 1.1186e-14
C_ckn10b ckn_b 0 1.1186e-14
* ckn20: 80 um x 1.0 um, h=0.6 um -> Z0=56 ohm, L=26.4 pH, C=8.4 fF
L_ckn20 ckn_b ckn20_m 2.6358e-11
R_ckn20 ckn20_m ckn2_1 8.0032
C_ckn20a ckn_b 0 4.1755e-15
C_ckn20b ckn2_1 0 4.1755e-15
* ckn21: 80 um x 1.0 um, h=0.6 um -> Z0=56 ohm, L=26.4 pH, C=8.4 fF
L_ckn21 ckn2_1 ckn21_m 2.6358e-11
R_ckn21 ckn21_m div_ckn 8.0032
C_ckn21a ckn2_1 0 4.1755e-15
C_ckn21b div_ckn 0 4.1755e-15
.ends lo_core