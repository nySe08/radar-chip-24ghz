.subckt varwrap g1 vtune g2 NX=10
XV1 g1 vtune g2 0 sg13_hv_svaricap l=0.3u w=9.74u Nx={NX}
.ends varwrap
.subckt lo_core BSEL GND PLLN PLLP RXLON RXLOP TXLON TXLOP VCC VTUNE
LLvcoa VCC Lvco_ma 169p
RLvcoa Lvco_ma vcop_L 1.11
LLvcob VCC Lvco_mb 169p
RLvcob Lvco_mb vcon_L 1.11
CLvcop vcop vcon 3.1f
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
XRdiv_ref VCC div_vbt GND rppd w=1u l=9.5u
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
XRdiv_o1 VCC div_vbo GND rppd w=1u l=9.5u
XRdiv_o2 div_vbo GND GND rhigh w=1u l=5.53u
XCdiv_bo div_vbo GND GND cap_rfcmim w=33u l=33u
XRdiv_bo1 div_vbo div_o1 GND rppd w=1u l=19.08u
XRdiv_bo2 div_vbo div_o2 GND rppd w=1u l=19.08u
XQdiv_o1 PLLN div_o1 div_eo GND npn13G2 Nx=4
XQdiv_o2 PLLP div_o2 div_eo GND npn13G2 Nx=4
XQdiv_to1 div_eo div_vbt div_eto1 GND npn13G2 Nx=10
XQdiv_to2 div_eo div_vbt div_eto2 GND npn13G2 Nx=10
XRdiv_eo1 div_eto1 GND GND rppd w=16u l=0.68u
XRdiv_eo2 div_eto2 GND GND rppd w=16u l=0.68u
XRdiv_t1 VCC PLLP GND rppd w=10u l=1.66u
XRdiv_t2 VCC PLLN GND rppd w=10u l=1.66u
* TESTBENCH STIMULUS, simulation copy only (not in the LVS netlist / design): start-up kick for the VCO
Ikick_tb vcop 0 pulse(0 1m 0 5p 5p 10p 1)
* ======== layout interconnect (post-layout) ========
* tkpstub0: 13 um x 6 um, h=1.88 um -> Z0=37 ohm, L=2.9 pH, C=2.1 fF
L_tkpstub0 vcop_L tkpstub0_m 2.9152e-12
R_tkpstub0 tkpstub0_m vcop 0.0607
* tkp10: 22 um x 3 um, h=1.88 um -> Z0=58 ohm, L=7.4 pH, C=2.2 fF
L_tkp10 vcop tkp10_m 7.4162e-12
R_tkp10 tkp10_m vcop_x 0.2056
* tkpx0: 29 um x 4 um, h=6.68 um -> Z0=92 ohm, L=14.9 pH, C=1.8 fF
L_tkpx0 vcop_x tkpx0_m 1.4901e-11
R_tkpx0 tkpx0_m vcop_cb 0.2004
* tkp20: 32 um x 3 um, h=1.88 um -> Z0=58 ohm, L=10.8 pH, C=3.3 fF
L_tkp20 vcop_x tkp20_m 1.0787e-11
R_tkp20 tkp20_m vcop_v 0.2990
* tkpcv0: 17 um x 3 um, h=1.88 um -> Z0=58 ohm, L=5.7 pH, C=1.7 fF
L_tkpcv0 vcop_v tkpcv0_m 5.7307e-12
R_tkpcv0 tkpcv0_m vcop_cv 0.1589
* tkp30: 43 um x 3 um, h=1.88 um -> Z0=58 ohm, L=14.5 pH, C=4.4 fF
L_tkp30 vcop_v tkp30_m 1.4495e-11
R_tkp30 tkp30_m vcop_e 0.4018
* tkpbs0: 9 um x 3 um, h=1.88 um -> Z0=58 ohm, L=3.0 pH, C=0.9 fF
L_tkpbs0 vcop_e tkpbs0_m 3.0339e-12
R_tkpbs0 tkpbs0_m vcop_bs 0.0841
* tknstub0: 13 um x 6 um, h=1.88 um -> Z0=37 ohm, L=2.9 pH, C=2.1 fF
L_tknstub0 vcon_L tknstub0_m 2.9152e-12
R_tknstub0 tknstub0_m vcon 0.0607
* tkn10: 34 um x 3 um, h=1.88 um -> Z0=58 ohm, L=11.5 pH, C=3.5 fF
L_tkn10 vcon tkn10_m 1.1461e-11
R_tkn10 tkn10_m vcon_x 0.3177
* tknx0: 28 um x 4 um, h=6.68 um -> Z0=92 ohm, L=14.7 pH, C=1.7 fF
L_tknx0 vcon_x tknx0_m 1.4693e-11
R_tknx0 tknx0_m vcon_cb 0.1976
* tkn20: 20 um x 3 um, h=1.88 um -> Z0=58 ohm, L=6.7 pH, C=2.0 fF
L_tkn20 vcon_x tkn20_m 6.7420e-12
R_tkn20 tkn20_m vcon_v 0.1869
* tkncv0: 18 um x 3 um, h=1.88 um -> Z0=58 ohm, L=6.0 pH, C=1.8 fF
L_tkncv0 vcon_v tkncv0_m 6.0341e-12
R_tkncv0 tkncv0_m vcon_cv 0.1673
* tkn30: 43 um x 3 um, h=1.88 um -> Z0=58 ohm, L=14.5 pH, C=4.4 fF
L_tkn30 vcon_v tkn30_m 1.4495e-11
R_tkn30 tkn30_m vcon_e 0.4018
* tknbs0: 9 um x 3 um, h=1.88 um -> Z0=58 ohm, L=3.0 pH, C=0.9 fF
L_tknbs0 vcon_e tknbs0_m 3.0339e-12
R_tknbs0 tknbs0_m vcon_bs 0.0841
* bp_dv0: 115 um x 1.2 um, h=0.6 um -> Z0=50 ohm, L=34.3 pH, C=13.5 fF
L_bp_dv0 efp bp_dv0_m 3.4285e-11
R_bp_dv0 bp_dv0_m bp_dv_1 9.5872
* bp_dv1: 115 um x 1.2 um, h=0.6 um -> Z0=50 ohm, L=34.3 pH, C=13.5 fF
L_bp_dv1 bp_dv_1 bp_dv1_m 3.4285e-11
R_bp_dv1 bp_dv1_m efp_dvd 9.5872
* bp_dvd0: 22 um x 1.2 um, h=1.7 um -> Z0=86 ohm, L=10.8 pH, C=1.5 fF
L_bp_dvd0 efp_dvd bp_dvd0_m 1.0757e-11
R_bp_dvd0 bp_dvd0_m efp_dv 1.8341
* bp_rx0: 39 um x 1.2 um, h=0.6 um -> Z0=50 ohm, L=11.6 pH, C=4.6 fF
L_bp_rx0 efp bp_rx0_m 1.1627e-11
R_bp_rx0 bp_rx0_m efp_rxd 3.2513
* bp_rxd0: 33 um x 1.2 um, h=1.7 um -> Z0=86 ohm, L=16.1 pH, C=2.2 fF
L_bp_rxd0 efp_rxd bp_rxd0_m 1.6136e-11
R_bp_rxd0 bp_rxd0_m efp_rx 2.7511
* bp_tx0: 100 um x 1.2 um, h=0.6 um -> Z0=50 ohm, L=29.8 pH, C=11.7 fF
L_bp_tx0 efp bp_tx0_m 2.9813e-11
R_bp_tx0 bp_tx0_m bp_tx_1 8.3367
* bp_tx1: 100 um x 1.2 um, h=0.6 um -> Z0=50 ohm, L=29.8 pH, C=11.7 fF
L_bp_tx1 bp_tx_1 bp_tx1_m 2.9813e-11
R_bp_tx1 bp_tx1_m bp_tx_2 8.3367
* bp_tx2: 100 um x 1.2 um, h=0.6 um -> Z0=50 ohm, L=29.8 pH, C=11.7 fF
L_bp_tx2 bp_tx_2 bp_tx2_m 2.9813e-11
R_bp_tx2 bp_tx2_m efp_txd 8.3367
* bp_txd0: 92 um x 1.2 um, h=1.7 um -> Z0=86 ohm, L=45.0 pH, C=6.1 fF
L_bp_txd0 efp_txd bp_txd0_m 4.4985e-11
R_bp_txd0 bp_txd0_m efp_tx 7.6697
* bn_dv0: 98 um x 1.2 um, h=1.7 um -> Z0=86 ohm, L=48.2 pH, C=6.5 fF
L_bn_dv0 efn bn_dv0_m 4.8163e-11
R_bn_dv0 bn_dv0_m bn_dv_1 8.2116
* bn_dv1: 98 um x 1.2 um, h=1.7 um -> Z0=86 ohm, L=48.2 pH, C=6.5 fF
L_bn_dv1 bn_dv_1 bn_dv1_m 4.8163e-11
R_bn_dv1 bn_dv1_m efn_dv 8.2116
* bn_rx0: 73 um x 1.2 um, h=1.7 um -> Z0=86 ohm, L=35.7 pH, C=4.8 fF
L_bn_rx0 efn bn_rx0_m 3.5695e-11
R_bn_rx0 bn_rx0_m efn_rx 6.0858
* bn_tx0: 136 um x 1.2 um, h=1.7 um -> Z0=86 ohm, L=66.6 pH, C=9.0 fF
L_bn_tx0 efn bn_tx0_m 6.6622e-11
R_bn_tx0 bn_tx0_m bn_tx_1 11.3587
* bn_tx1: 136 um x 1.2 um, h=1.7 um -> Z0=86 ohm, L=66.6 pH, C=9.0 fF
L_bn_tx1 bn_tx_1 bn_tx1_m 6.6622e-11
R_bn_tx1 bn_tx1_m bn_tx_2 11.3587
* bn_tx2: 136 um x 1.2 um, h=1.7 um -> Z0=86 ohm, L=66.6 pH, C=9.0 fF
L_bn_tx2 bn_tx_2 bn_tx2_m 6.6622e-11
R_bn_tx2 bn_tx2_m bn_tx_3 11.3587
* bn_tx3: 136 um x 1.2 um, h=1.7 um -> Z0=86 ohm, L=66.6 pH, C=9.0 fF
L_bn_tx3 bn_tx_3 bn_tx3_m 6.6622e-11
R_bn_tx3 bn_tx3_m efn_tx 11.3587
* prxcp0: 82 um x 3 um, h=1.88 um -> Z0=58 ohm, L=27.6 pH, C=8.3 fF
L_prxcp0 prx_dp prxcp0_m 2.7642e-11
R_prxcp0 prxcp0_m prx_dpL 0.7662
* prxcn0: 56 um x 3 um, h=1.88 um -> Z0=58 ohm, L=18.9 pH, C=5.7 fF
L_prxcn0 prx_dn prxcn0_m 1.8877e-11
R_prxcn0 prxcn0_m prx_dnL 0.5233
* ptxcp0: 96 um x 3 um, h=1.88 um -> Z0=58 ohm, L=32.4 pH, C=9.8 fF
L_ptxcp0 ptx_dp ptxcp0_m 3.2361e-11
R_ptxcp0 ptxcp0_m ptx_dpL 0.8970
* ptxcn0: 92 um x 3 um, h=1.88 um -> Z0=58 ohm, L=31.0 pH, C=9.4 fF
L_ptxcn0 ptx_dn ptxcn0_m 3.1013e-11
R_ptxcn0 ptxcn0_m ptx_dnL 0.8597
* prxop0: 75 um x 1.0 um, h=1.7 um -> Z0=93 ohm, L=39.3 pH, C=4.6 fF
L_prxop0 prx_dp prxop0_m 3.9339e-11
R_prxop0 prxop0_m prx_dpC 7.5030
* prxon0: 74 um x 1.0 um, h=1.7 um -> Z0=93 ohm, L=38.8 pH, C=4.5 fF
L_prxon0 prx_dn prxon0_m 3.8814e-11
R_prxon0 prxon0_m prx_dnC 7.4030
* ptxop0: 75 um x 1.0 um, h=1.7 um -> Z0=93 ohm, L=39.3 pH, C=4.6 fF
L_ptxop0 ptx_dp ptxop0_m 3.9339e-11
R_ptxop0 ptxop0_m ptx_dpC 7.5030
* ptxon0: 74 um x 1.0 um, h=1.7 um -> Z0=93 ohm, L=38.8 pH, C=4.5 fF
L_ptxon0 ptx_dn ptxon0_m 3.8814e-11
R_ptxon0 ptxon0_m ptx_dnC 7.4030
* ddvop0: 75 um x 1.0 um, h=1.7 um -> Z0=93 ohm, L=39.3 pH, C=4.6 fF
L_ddvop0 ddv_dp ddvop0_m 3.9339e-11
R_ddvop0 ddvop0_m ddv_dpC 7.5030
* ddvon0: 74 um x 1.0 um, h=1.7 um -> Z0=93 ohm, L=38.8 pH, C=4.5 fF
L_ddvon0 ddv_dn ddvon0_m 3.8814e-11
R_ddvon0 ddvon0_m ddv_dnC 7.4030
* oRXLOP0: 139 um x 4 um, h=6.68 um -> Z0=92 ohm, L=72.4 pH, C=8.6 fF
L_oRXLOP0 RXLOP_c oRXLOP0_m 7.2423e-11
R_oRXLOP0 oRXLOP0_m RXLOP 0.9741
* oRXLON0: 133 um x 4 um, h=6.68 um -> Z0=92 ohm, L=69.3 pH, C=8.2 fF
L_oRXLON0 RXLON_c oRXLON0_m 6.9297e-11
R_oRXLON0 oRXLON0_m RXLON 0.9321
* oTXLOP0: 169 um x 4 um, h=6.68 um -> Z0=92 ohm, L=88.1 pH, C=10.4 fF
L_oTXLOP0 TXLOP_c oTXLOP0_m 8.8054e-11
R_oTXLOP0 oTXLOP0_m TXLOP 1.1844
* oTXLON0: 62 um x 4 um, h=6.68 um -> Z0=92 ohm, L=32.3 pH, C=3.8 fF
L_oTXLON0 TXLON_c oTXLON0_m 3.2304e-11
R_oTXLON0 oTXLON0_m TXLON 0.4345
* ckp10: 180 um x 3 um, h=1.88 um -> Z0=58 ohm, L=60.7 pH, C=18.3 fF
L_ckp10 ckp_c ckp10_m 6.0678e-11
R_ckp10 ckp10_m ckp_b 1.6820
* ckp20: 75 um x 1.0 um, h=1.7 um -> Z0=93 ohm, L=39.3 pH, C=4.6 fF
L_ckp20 ckp_b ckp20_m 3.9339e-11
R_ckp20 ckp20_m ckp2_1 7.5030
* ckp21: 75 um x 1.0 um, h=1.7 um -> Z0=93 ohm, L=39.3 pH, C=4.6 fF
L_ckp21 ckp2_1 ckp21_m 3.9339e-11
R_ckp21 ckp21_m div_ckp 7.5030
* ckn10: 220 um x 3 um, h=1.88 um -> Z0=58 ohm, L=74.2 pH, C=22.4 fF
L_ckn10 ckn_c ckn10_m 7.4162e-11
R_ckn10 ckn10_m ckn_b 2.0557
* ckn20: 80 um x 1.0 um, h=0.6 um -> Z0=56 ohm, L=26.4 pH, C=8.4 fF
L_ckn20 ckn_b ckn20_m 2.6358e-11
R_ckn20 ckn20_m ckn2_1 8.0032
* ckn21: 80 um x 1.0 um, h=0.6 um -> Z0=56 ohm, L=26.4 pH, C=8.4 fF
L_ckn21 ckn2_1 ckn21_m 2.6358e-11
R_ckn21 ckn21_m div_ckn 8.0032
* ======== hybrid: KLayout-PEX capacitances (MIM pairs excluded) ========
Chyb0 PRX_DN PRX_VBD 0.2620f
Chyb1 PRX_T PRX_VBD 0.0310f
Chyb2 PRX_DP PRX_VBD 0.3230f
Chyb3 PRX_VBD VCC 0.1910f
Chyb4 PRX_B1 PRX_DN 0.3990f
Chyb5 PRX_B1 PRX_T 0.3080f
Chyb6 GND PRX_B1 17.9330f
Chyb7 PRX_B1 VCC 0.0020f
Chyb8 PRX_B2 PRX_DN 0.8530f
Chyb9 PRX_B2 PRX_T 0.3210f
Chyb10 PRX_B2 PRX_DP 0.6860f
Chyb11 GND PRX_B2 12.0790f
Chyb12 PRX_DN PRX_T 0.2950f
Chyb13 EFN PRX_DN 0.2800f
Chyb14 GND PRX_DN 31.1550f
Chyb15 PRX_DN VCC 0.3460f
Chyb16 PRX_DP PRX_T 0.3250f
Chyb17 GND PRX_T 9.6470f
Chyb18 GND PRX_DP 27.9090f
Chyb19 PRX_DP VCC 0.9120f
Chyb20 DDV_T DDV_VBD 0.0510f
Chyb21 DDV_DP DDV_VBD 0.2620f
Chyb22 DDV_DN DDV_VBD 0.3230f
Chyb23 DDV_VBD S2QB 0.0030f
Chyb24 DDV_VBD VCC 0.1430f
Chyb25 DM2_ET M2Q 0.0390f
Chyb26 DM2_ET DM2_ETR 0.9190f
Chyb27 DM2_ET M2QB 0.0320f
Chyb28 DM2_ET S2Q 0.6180f
Chyb29 DM2_ET S2QB 0.4100f
Chyb30 DIV_VBT DM2_ET 0.0500f
Chyb31 C2N DM2_ET 0.1920f
Chyb32 DM2_ED DM2_ET 0.1580f
Chyb33 C2P DM2_ET 0.1920f
Chyb34 DM2_EH DM2_ET 0.1640f
Chyb35 DM2_ET GND 16.4530f
Chyb36 DDV_B1 DDV_T 0.3080f
Chyb37 DDV_B1 DDV_DP 0.1570f
Chyb38 BSEL DDV_B1 0.4560f
Chyb39 DDV_B1 GND 18.5920f
Chyb40 DDV_B1 VCC 0.0020f
Chyb41 DDV_B2 DDV_T 0.3290f
Chyb42 DDV_B2 DDV_DN 0.3200f
Chyb43 DDV_B2 EFP 0.3700f
Chyb44 BSEL DDV_B2 0.4180f
Chyb45 DDV_B2 GND 12.9700f
Chyb46 DDV_B2 VCC 0.0280f
Chyb47 M2Q M2QB 1.5470f
Chyb48 M2Q S2Q 0.4080f
Chyb49 M2Q S2QB 0.0120f
Chyb50 DIV_VBT M2Q 0.2110f
Chyb51 C2N M2Q 0.0670f
Chyb52 DM2_ED M2Q 0.8670f
Chyb53 DM2_EH M2Q 1.0030f
Chyb54 DS2_ET M2Q 0.4100f
Chyb55 DS2_ED M2Q 0.1660f
Chyb56 GND M2Q 30.2630f
Chyb57 M2Q VCC 0.2720f
Chyb58 DDV_DP DDV_T 0.2950f
Chyb59 DDV_DN DDV_T 0.2950f
Chyb60 DDV_T GND 11.9010f
Chyb61 DDV_T VCC 0.0040f
Chyb62 DDV_DP GND 18.2390f
Chyb63 DDV_DP VCC 0.2890f
Chyb64 DDV_DN GND 18.8390f
Chyb65 DDV_DN VCC 0.2350f
Chyb66 EFN EFP 4.8950f
Chyb67 BS_S1 EFN 0.0470f
Chyb68 BS_S2 EFN 0.2680f
Chyb69 EFN PTX_VBD 0.0680f
Chyb70 EFN VCON 0.3490f
Chyb71 EFN VCO_VGB 1.4700f
Chyb72 BSEL EFN 0.5780f
Chyb73 EFN GND 140.9730f
Chyb74 EFN TXLON 0.0500f
Chyb75 EFN TXLOP 0.1880f
Chyb76 EFN VCC 0.5920f
Chyb77 DIV_VBT DM2_ETR 0.8770f
Chyb78 C2N DM2_ETR 0.0020f
Chyb79 C2P DM2_ETR 0.0090f
Chyb80 DM2_ETR GND 6.4460f
Chyb81 BS_S1 EFP 0.4500f
Chyb82 BS_S2 EFP 0.2450f
Chyb83 EFP PTX_VBD 0.6130f
Chyb84 BS_G EFP 0.2170f
Chyb85 EFP VCOP 0.2090f
Chyb86 EFP VCO_VGB 1.4840f
Chyb87 BSEL EFP 0.9560f
Chyb88 EFP GND 156.7550f
Chyb89 EFP VCC 0.8500f
Chyb90 M2QB S2Q 0.0190f
Chyb91 M2QB S2QB 0.0100f
Chyb92 DIV_VBT M2QB 0.2200f
Chyb93 C2N M2QB 0.0010f
Chyb94 DM2_ED M2QB 0.8740f
Chyb95 DM2_EH M2QB 1.1970f
Chyb96 DS2_ET M2QB 0.6180f
Chyb97 DS2_ED M2QB 0.1500f
Chyb98 GND M2QB 29.2080f
Chyb99 M2QB VCC 0.3880f
Chyb100 DIV_ETO1 DIV_O1 0.0080f
Chyb101 DIV_O1 DIV_O2 0.0490f
Chyb102 DIV_EO DIV_O1 1.7020f
Chyb103 DIV_O1 DIV_VBT 0.0010f
Chyb104 BSEL DIV_O1 0.3900f
Chyb105 DIV_O1 GND 38.2960f
Chyb106 DIV_O1 PLLN 0.0360f
Chyb107 DIV_O1 PLLP 0.5800f
Chyb108 DIV_O1 VCC 0.7520f
Chyb109 BS_S1 BS_S2 1.3640f
Chyb110 BS_G BS_S1 0.7380f
Chyb111 BS_S1 VCON 0.0020f
Chyb112 BSEL BS_S1 0.0190f
Chyb113 BS_S1 GND 8.5390f
Chyb114 BS_G BS_S2 0.6940f
Chyb115 BS_S2 VCOP 0.0050f
Chyb116 BS_S2 GND 6.2600f
Chyb117 DM1_ET M1Q 0.0390f
Chyb118 DM1_ET M1QB 0.0320f
Chyb119 DIV_VBT DM1_ET 0.0750f
Chyb120 DM1_ET S1Q 0.6180f
Chyb121 DM1_ET S1QB 0.4100f
Chyb122 DM1_ET DM1_ETR 1.3490f
Chyb123 DM1_ED DM1_ET 0.1580f
Chyb124 DM1_EH DM1_ET 0.1640f
Chyb125 DIV_CKN DM1_ET 0.1920f
Chyb126 DIV_CKP DM1_ET 0.1920f
Chyb127 DM1_ET GND 18.6920f
Chyb128 PTX_DP PTX_VBD 0.2620f
Chyb129 PTX_T PTX_VBD 0.0240f
Chyb130 PTX_DN PTX_VBD 0.3230f
Chyb131 PTX_VBD VCC 0.1770f
Chyb132 BS_G VCOP 1.0730f
Chyb133 BS_G VCON 0.1190f
Chyb134 BS_G VCO_VGB 0.0200f
Chyb135 BSEL BS_G 0.0300f
Chyb136 BS_G GND 7.9100f
Chyb137 VCON VCOP 1.6560f
Chyb138 VCOP VCO_VGB 0.2460f
Chyb139 VCOP VCO_G2 0.0070f
Chyb140 VCOP VCO_VBB 0.5890f
Chyb141 VCOP VCO_B6 0.0440f
Chyb142 VCOP VCO_TAIL 0.8250f
Chyb143 GND VCOP 31.0500f
Chyb144 VCC VCOP 2.7670f
Chyb145 VCOP VTUNE 0.6980f
Chyb146 VCON VCO_VGB 0.2040f
Chyb147 VCON VCO_G1 0.0020f
Chyb148 VCON VCO_VBB 0.4480f
Chyb149 VCON VCO_B7 0.0590f
Chyb150 VCON VCO_TAIL 0.8380f
Chyb151 GND VCON 30.2170f
Chyb152 VCC VCON 3.0880f
Chyb153 VCON VTUNE 0.0060f
Chyb154 DIV_EO DIV_ETO1 1.4420f
Chyb155 DIV_ETO1 DIV_VBT 2.0530f
Chyb156 BSEL DIV_ETO1 0.8460f
Chyb157 DIV_ETO1 GND 10.6910f
Chyb158 DIV_EO DIV_ETO2 1.4420f
Chyb159 DIV_ETO2 DIV_VBT 2.0110f
Chyb160 BSEL DIV_ETO2 0.8460f
Chyb161 DIV_ETO2 GND 10.7670f
Chyb162 M1Q M1QB 1.5800f
Chyb163 DIV_VBT M1Q 0.2110f
Chyb164 M1Q S1Q 0.4080f
Chyb165 M1Q S1QB 0.0120f
Chyb166 DM1_ED M1Q 0.8670f
Chyb167 DM1_EH M1Q 1.0030f
Chyb168 DIV_CKN M1Q 0.0670f
Chyb169 DS1_ET M1Q 0.4100f
Chyb170 DS1_ED M1Q 0.1660f
Chyb171 GND M1Q 30.2940f
Chyb172 M1Q VCC 0.2520f
Chyb173 DIV_EO DIV_O2 1.6520f
Chyb174 DIV_O2 GND 18.4760f
Chyb175 DIV_O2 PLLP 0.0350f
Chyb176 VCO_G1 VCO_VGB 0.0120f
Chyb177 VCO_G2 VCO_VGB 0.0120f
Chyb178 VCC VCO_VGB 2.4280f
Chyb179 DIV_VBT M1QB 0.2200f
Chyb180 M1QB S1Q 0.0190f
Chyb181 M1QB S1QB 0.0100f
Chyb182 DM1_ED M1QB 0.8740f
Chyb183 DM1_EH M1QB 1.1970f
Chyb184 DIV_CKN M1QB 0.0010f
Chyb185 DS1_ET M1QB 0.6180f
Chyb186 DS1_ED M1QB 0.1500f
Chyb187 GND M1QB 29.4870f
Chyb188 M1QB VCC 0.3700f
Chyb189 DIV_EO DIV_VBT 0.1670f
Chyb190 BSEL DIV_EO 0.0170f
Chyb191 DIV_EO GND 25.1420f
Chyb192 DIV_EO PLLN 0.5970f
Chyb193 DIV_EO PLLP 0.5880f
Chyb194 DIV_VBT DIV_VCK 0.2820f
Chyb195 DIV_VCK S1QB 0.0520f
Chyb196 DIV_CKN DIV_VCK 1.8620f
Chyb197 DIV_CKP DIV_VCK 0.2260f
Chyb198 DIV_VCK VCC 0.2000f
Chyb199 VCO_G1 VCO_G2 11.1860f
Chyb200 GND VCO_G1 17.0340f
Chyb201 VCC VCO_G1 1.1290f
Chyb202 VCO_G1 VTUNE 0.2700f
Chyb203 GND VCO_G2 18.0880f
Chyb204 VCC VCO_G2 0.9710f
Chyb205 VCO_G2 VTUNE 0.1060f
Chyb206 PTX_B1 PTX_DP 0.4800f
Chyb207 PTX_B1 PTX_T 0.3080f
Chyb208 GND PTX_B1 17.6540f
Chyb209 PTX_B1 VCC 0.0020f
Chyb210 PTX_B2 PTX_T 0.3210f
Chyb211 PTX_B2 PTX_DN 0.6970f
Chyb212 GND PTX_B2 12.1150f
Chyb213 DIV_EBR DIV_VBT 0.4300f
Chyb214 DIV_EBR GND 3.7160f
Chyb215 PTX_DP PTX_T 0.2950f
Chyb216 GND PTX_DP 34.8920f
Chyb217 PTX_DP VCC 0.4400f
Chyb218 PTX_DN PTX_T 0.2950f
Chyb219 GND PTX_T 9.7100f
Chyb220 PTX_T VCC 0.0110f
Chyb221 GND PTX_DN 34.8130f
Chyb222 PTX_DN VCC 1.3630f
Chyb223 S2Q S2QB 4.9970f
Chyb224 DIV_VBT S2Q 0.2110f
Chyb225 C2N S2Q 0.2410f
Chyb226 DM2_ED S2Q 0.1500f
Chyb227 C2P S2Q 0.2590f
Chyb228 DS2_ET S2Q 0.0390f
Chyb229 DS2_ED S2Q 0.8670f
Chyb230 DS2_EH S2Q 1.0200f
Chyb231 BSEL S2Q 0.8320f
Chyb232 GND S2Q 66.5460f
Chyb233 S2Q VCC 3.3970f
Chyb234 DIV_VBO VCC 0.2030f
Chyb235 VCO_B6 VCO_VBB 0.5230f
Chyb236 VCO_B7 VCO_VBB 0.5330f
Chyb237 VCO_TAIL VCO_VBB 0.2620f
Chyb238 VCO_VBB VTUNE 0.2400f
Chyb239 VCO_B6 VCO_TAIL 0.5880f
Chyb240 GND VCO_B6 13.2680f
Chyb241 VCO_B6 VTUNE 0.2410f
Chyb242 VCO_B7 VCO_TAIL 0.5880f
Chyb243 GND VCO_B7 14.0300f
Chyb244 GND VCO_TAIL 10.6170f
Chyb245 DIV_VBT S2QB 0.2200f
Chyb246 C2N S2QB 0.3070f
Chyb247 DM2_ED S2QB 0.1660f
Chyb248 C2P S2QB 0.3960f
Chyb249 DS2_ET S2QB 0.0320f
Chyb250 DS2_ED S2QB 0.8740f
Chyb251 DS2_EH S2QB 1.1990f
Chyb252 BSEL S2QB 0.0150f
Chyb253 GND S2QB 97.0280f
Chyb254 S2QB VCC 1.9240f
Chyb255 DIV_VBT S1Q 0.2110f
Chyb256 DIV_VBT S1QB 0.2200f
Chyb257 C2N DIV_VBT 1.2350f
Chyb258 DIV_VBT DM1_ETR 1.4040f
Chyb259 C2P DIV_VBT 0.2990f
Chyb260 DIV_CKN DIV_VBT 0.7730f
Chyb261 DIV_CKP DIV_VBT 0.3030f
Chyb262 DIV_VBT DS2_ET 0.0500f
Chyb263 DIV_VBT DS2_ETR 0.8770f
Chyb264 DIV_VBT DS1_ET 0.0750f
Chyb265 DIV_VBT DS1_ETR 1.4040f
Chyb266 BSEL DIV_VBT 1.0190f
Chyb267 DIV_VBT VCC 0.0220f
Chyb268 S1Q S1QB 2.7730f
Chyb269 C2N S1Q 2.1650f
Chyb270 DM1_ED S1Q 0.1500f
Chyb271 DIV_CKN S1Q 0.2410f
Chyb272 DIV_CKP S1Q 0.2590f
Chyb273 DS1_ET S1Q 0.0390f
Chyb274 DS1_ED S1Q 0.8670f
Chyb275 DS1_EH S1Q 1.0200f
Chyb276 GND S1Q 53.9120f
Chyb277 S1Q VCC 1.3610f
Chyb278 DM1_ED S1QB 0.1660f
Chyb279 DIV_CKN S1QB 0.3070f
Chyb280 DIV_CKP S1QB 0.3960f
Chyb281 DS1_ET S1QB 0.0320f
Chyb282 DS1_ED S1QB 0.8740f
Chyb283 DS1_EH S1QB 1.1990f
Chyb284 GND S1QB 48.8880f
Chyb285 S1QB VCC 0.2410f
Chyb286 C2N C2P 5.3840f
Chyb287 C2N DM2_EH 0.0080f
Chyb288 C2N DIV_CKN 0.1540f
Chyb289 C2N DS2_ET 0.1920f
Chyb290 C2N DS2_ED 0.0080f
Chyb291 C2N GND 84.7060f
Chyb292 C2N VCC 1.0030f
Chyb293 DIV_CKN DM1_ETR 0.0030f
Chyb294 DIV_CKP DM1_ETR 0.0110f
Chyb295 DM1_ETR GND 6.5430f
Chyb296 C2P DM2_ED 0.0080f
Chyb297 DM2_ED GND 6.2850f
Chyb298 C2P DS2_ET 0.1920f
Chyb299 C2P DS2_EH 0.0080f
Chyb300 C2P GND 63.8770f
Chyb301 C2P VCC 0.7550f
Chyb302 DM2_EH GND 6.1700f
Chyb303 DIV_CKP DM1_ED 0.0080f
Chyb304 DM1_ED GND 6.2740f
Chyb305 DIV_CKN DM1_EH 0.0080f
Chyb306 DM1_EH GND 6.1120f
Chyb307 DIV_CKN DIV_CKP 2.1730f
Chyb308 DIV_CKN DS1_ET 0.1920f
Chyb309 DIV_CKN DS1_ED 0.0080f
Chyb310 DIV_CKN GND 81.0370f
Chyb311 DIV_CKN VCC 0.0140f
Chyb312 DIV_CKP DS1_ET 0.1920f
Chyb313 DIV_CKP DS1_EH 0.0080f
Chyb314 DIV_CKP GND 62.4190f
Chyb315 DS2_ET DS2_ETR 0.9190f
Chyb316 DS2_ED DS2_ET 0.1580f
Chyb317 DS2_EH DS2_ET 0.1640f
Chyb318 DS2_ET GND 16.3490f
Chyb319 DS2_ET VCC 0.0320f
Chyb320 DS2_ETR GND 6.4960f
Chyb321 DS1_ET DS1_ETR 1.3490f
Chyb322 DS1_ED DS1_ET 0.1580f
Chyb323 DS1_EH DS1_ET 0.1640f
Chyb324 DS1_ET GND 18.6770f
Chyb325 DS1_ETR GND 6.6470f
Chyb326 DS2_ED GND 6.3050f
Chyb327 DS2_ED VCC 0.0040f
Chyb328 DS2_EH GND 6.1660f
Chyb329 DS1_ED GND 6.3310f
Chyb330 DS1_EH GND 6.1670f
Chyb331 BSEL GND 78.9520f
Chyb332 GND PLLN 12.2340f
Chyb333 GND PLLP 16.5530f
Chyb334 GND RXLOP 20.7190f
Chyb335 GND RXLON 21.6960f
Chyb336 GND TXLON 14.1080f
Chyb337 GND TXLOP 21.5040f
Chyb338 GND VCC 337.1160f
Chyb339 GND VTUNE 73.3700f
Chyb340 PLLN PLLP 1.2920f
Chyb341 PLLN VCC 0.6610f
Chyb342 PLLP VCC 1.3030f
Chyb343 TXLON TXLOP 1.2170f
Chyb344 TXLOP VCC 0.0900f
Chyb345 VCC VTUNE 0.0120f
* odd-mode mutual inductance of the tank lines (tank_mutual.py)
K_tank10 L_tkp10 L_tkn10 0.172
K_tank20 L_tkp20 L_tkn20 0.167
K_tank30 L_tkp30 L_tkn30 0.220
.ends lo_core
