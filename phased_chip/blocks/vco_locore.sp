.subckt varwrap g1 vtune g2 NX=10
XV1 g1 vtune g2 0 sg13_hv_svaricap l=0.3u w=9.74u Nx={NX}
.ends varwrap
.subckt lo_core BSEL GND PLLN PLLP RXLON RXLOP TXLON TXLOP VCC VTUNE
LLvcoa VCC Lvco_ma 169p
RLvcoa Lvco_ma vcop 1.11
LLvcob VCC Lvco_mb 169p
RLvcob Lvco_mb vcon 1.11
CLvcop vcop vcon 3.1f
XCvco_cv1 vcop vco_g1 GND cap_rfcmim w=16u l=16u
XCvco_cv2 vcon vco_g2 GND cap_rfcmim w=16u l=16u
XRvco_g1 vco_vgb vco_g1 GND rhigh w=1u l=7.0u
XRvco_g2 vco_vgb vco_g2 GND rhigh w=1u l=7.0u
XRvco_gb1 VCC vco_vgb GND rhigh w=1u l=13.3u
XRvco_gb2 vco_vgb GND GND rhigh w=1u l=13.3u
XCvco_gb vco_vgb GND GND cap_rfcmim w=33u l=33u
XCvco_var vco_g1 VTUNE vco_g2 varwrap NX=7
XCbs_1 vcop bs_s1 GND cap_rfcmim w=4.5u l=4.5u
XCbs_2 vcon bs_s2 GND cap_rfcmim w=4.5u l=4.5u
XMbs bs_s1 bs_g bs_s2 GND sg13_lv_nmos w=24u l=0.13u ng=12
XRbs_1 bs_s1 GND GND rhigh w=1u l=14.0u
XRbs_2 bs_s2 GND GND rhigh w=1u l=14.0u
XRbs_g BSEL bs_g GND rhigh w=1u l=14.0u
XQvco_6 vcop vco_b6 vco_tail GND npn13G2 Nx=4
XQvco_7 vcon vco_b7 vco_tail GND npn13G2 Nx=4
XCvco_b6 vcon vco_b6 GND cap_rfcmim w=9u l=9u
XCvco_b7 vcop vco_b7 GND cap_rfcmim w=9u l=9u
XRvco_b6 vco_vbb vco_b6 GND rppd w=1u l=7.47u
XRvco_b7 vco_vbb vco_b7 GND rppd w=1u l=7.47u
XRvco_bb1 VCC vco_vbb GND rppd w=1u l=15.21u
XRvco_bb2 vco_vbb GND GND rppd w=1u l=22.95u
XCvco_bb vco_vbb GND GND cap_rfcmim w=33u l=33u
XRvco_tail vco_tail GND GND rppd w=2u l=1.03u
XQef_1 VCC vcop efp GND npn13G2 Nx=2
XQef_2 VCC vcon efn GND npn13G2 Nx=2
XRef_1 efp GND GND rppd w=2u l=5.15u
XRef_2 efn GND GND rppd w=2u l=5.15u
XCPRX_i1 efp prx_b1 GND cap_rfcmim w=12u l=12u
XCPRX_i2 efn prx_b2 GND cap_rfcmim w=12u l=12u
XRPRX_v1 VCC prx_vbd GND rppd w=1u l=17.53u
XRPRX_v2 prx_vbd GND GND rppd w=1u l=20.63u
XCPRX_vb prx_vbd GND GND cap_rfcmim w=33u l=33u
XRPRX_b1 prx_vbd prx_b1 GND rppd w=1u l=19.08u
XRPRX_b2 prx_vbd prx_b2 GND rppd w=1u l=19.08u
XQPRX_a prx_dp prx_b1 prx_t GND npn13G2 Nx=2
XQPRX_b prx_dn prx_b2 prx_t GND npn13G2 Nx=2
XRPRX_t prx_t GND GND rppd w=2u l=0.53u
LLPRXa VCC LPRX_ma 257.5p
RLPRXa LPRX_ma prx_dn 3.63
LLPRXb VCC LPRX_mb 257.5p
RLPRXb LPRX_mb prx_dp 3.63
CLPRXp prx_dn prx_dp 8.2f
XRPRX_d1 VCC prx_dp GND rppd w=2u l=2.83u
XRPRX_d2 VCC prx_dn GND rppd w=2u l=2.83u
XCPRX_c1 prx_dp RXLOP GND cap_rfcmim w=12u l=12u
XCPRX_c2 prx_dn RXLON GND cap_rfcmim w=12u l=12u
XRbl_r1 RXLOP GND GND rhigh w=1u l=14.0u
XRbl_r2 RXLON GND GND rhigh w=1u l=14.0u
XCPTX_i1 efp ptx_b1 GND cap_rfcmim w=12u l=12u
XCPTX_i2 efn ptx_b2 GND cap_rfcmim w=12u l=12u
XRPTX_v1 VCC ptx_vbd GND rppd w=1u l=17.53u
XRPTX_v2 ptx_vbd GND GND rppd w=1u l=20.63u
XCPTX_vb ptx_vbd GND GND cap_rfcmim w=33u l=33u
XRPTX_b1 ptx_vbd ptx_b1 GND rppd w=1u l=19.08u
XRPTX_b2 ptx_vbd ptx_b2 GND rppd w=1u l=19.08u
XQPTX_a ptx_dp ptx_b1 ptx_t GND npn13G2 Nx=2
XQPTX_b ptx_dn ptx_b2 ptx_t GND npn13G2 Nx=2
XRPTX_t ptx_t GND GND rppd w=2u l=1.15u
LLPTXa VCC LPTX_ma 345p
RLPTXa LPTX_ma ptx_dp 5.13
LLPTXb VCC LPTX_mb 345p
RLPTXb LPTX_mb ptx_dn 5.13
CLPTXp ptx_dp ptx_dn 11.6f
XRPTX_d1 VCC ptx_dp GND rppd w=2u l=2.83u
XRPTX_d2 VCC ptx_dn GND rppd w=2u l=2.83u
XCPTX_c1 ptx_dp TXLOP GND cap_rfcmim w=12u l=12u
XCPTX_c2 ptx_dn TXLON GND cap_rfcmim w=12u l=12u
XRbl_t1 TXLOP GND GND rhigh w=1u l=14.0u
XRbl_t2 TXLON GND GND rhigh w=1u l=14.0u
XCDDV_i1 efp ddv_b1 GND cap_rfcmim w=12u l=12u
XCDDV_i2 efn ddv_b2 GND cap_rfcmim w=12u l=12u
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
XCDDV_c1 ddv_dp div_ckp GND cap_rfcmim w=12u l=12u
XCDDV_c2 ddv_dn div_ckn GND cap_rfcmim w=12u l=12u
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
.ends lo_core
