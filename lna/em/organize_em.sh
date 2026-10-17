#!/bin/bash
# Tidy the EM folder: keep the FINAL coil files, move superseded ones to superseded/, write FINAL_COILS.md.
# Usage (inside lna/em):  bash organize_em.sh       (safe: only moves files that exist, deletes nothing)
mkdir -p superseded
for f in ind_lb.gds ind_lb_clean.gds ind_lb2.gds ind_lb2_c.gds ind_lb3_c.gds \
         ind_lc.gds ind_lc_c.gds ind_lc_p.gds ind_lc5.gds \
         ind_lo4.gds ind_vco.gds ind_vco2.gds ind_pa.gds; do
    base="${f%.gds}"
    for g in "$f" "${base}_em.png"; do [ -e "$g" ] && mv "$g" superseded/ && echo "moved $g -> superseded/"; done
    [ -d "$base" ] && mv "$base" superseded/ && echo "moved $base/ -> superseded/"
done
cat > FINAL_COILS.md <<'MD'
# Final EM-verified coils (openEMS, 1 um mesh, -60 dB) — 2TX/4RX 24 GHz radar chip

| Coil | File | PCell / geometry | EM at 24.1 GHz | Used in |
|---|---|---|---|---|
| LNA Lb | ind_lb3_p.gds | inductor2, 2 turns, w 7u, s 2.1u, d 68.66u | 602 pH, Q 14.3 | lna_ind.spice / lna layout |
| LNA Lc | ind_lc6.gds | inductor2, 2 turns, w 5u, s 2.1u, d 55.83u | 448 pH, Q 11.3 | lna_ind.spice / lna layout |
| RX pre-driver | ind_rxpre.gds | inductor3, 2 turns, w 4u, d 65.36u | 570 pH diff, Q 11.9 | phased_chip/blocks/lodist_em.sp |
| TX pre-driver | ind_txpre.gds | inductor3, 2 turns, w 4u, d 83.47u | 846 pH diff, Q 12.5 | phased_chip/blocks/lodist_em.sp |
| PA Lc | ind_pa2.gds | inductor2, 1 turn, w 12u, d 213.05u | 550 pH, Q 26.4 | phased_chip/blocks/pa_em.sp |
| VCO tank | ind_vco3.gds | inductor3, 2 turns, w 6u, d 70.88u | 622 pH diff, Q 15.3 | phased_chip/blocks/vco_em.sp |

Channel LO drivers: resistive load, no coil.

Superseded (kept in superseded/ as design history):
- 1-turn Lb (Q 37, too large), 2-turn Lb versions with overlapping port (non-physical R)
- Lc 6.5u versions (post-layout re-tune needed a smaller coil)
- 4-turn 3.6 nH LO-driver coil: self-resonance 12 GHz -> resistive driver instead
- 1-turn inductor3 VCO coil: PCell produced an open coil (continuity check added since)
- 2-turn w8 VCO coil: too inductive at 24 GHz; first PA coil: 8 % low, resized
MD
echo "wrote FINAL_COILS.md"
