#!/bin/bash
# EM re-run: VCO coil (2-turn) and resized PA coil. Usage: bash run_em_batch2.sh
echo "=== ind_vco2 ===" 
python3 run_ind_em_tm1.py ind_vco2.gds 660 25.0 --run 2>&1 | grep -A3 " at 24"
echo "=== ind_pa2 ===" 
python3 run_ind_em.py ind_pa2.gds 543 26.4 --run 2>&1 | grep -A3 " at 24"
echo "All done."
