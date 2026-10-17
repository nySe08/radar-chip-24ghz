#!/bin/bash
# EM of the final VCO coil (inductor3, 2 turns, w 6u, d 70.88u). Expect ~ 650-690 pH effective at 24 GHz.
python3 run_ind_em_tm1.py ind_vco3.gds 672 15 --run 2>&1 | grep -A3 " at 24"
