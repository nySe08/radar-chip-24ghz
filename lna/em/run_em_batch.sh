#!/bin/bash
# EM-verify the four remaining inductors in sequence (each ~10-30 min). Usage: bash run_em_batch.sh
# Needs in this folder: run_ind_em.py, run_ind_em_tm1.py, SG13G2.xml and the four ind_*.gds files.
echo "=== ind_rxpre (inductor3, 2 turn(s), w 4u, d 65.36u) ==="
python3 run_ind_em_tm1.py ind_rxpre.gds 600 14.5 --run 2>&1 | grep -A3 " at 24"
echo "=== ind_txpre (inductor3, 2 turn(s), w 4u, d 83.47u) ==="
python3 run_ind_em_tm1.py ind_txpre.gds 800 15.4 --run 2>&1 | grep -A3 " at 24"
echo "=== ind_vco (inductor3, 1 turn(s), w 12u, d 233.38u) ==="
python3 run_ind_em_tm1.py ind_vco.gds 660 27.7 --run 2>&1 | grep -A3 " at 24"
echo "=== ind_pa (inductor2, 1 turn(s), w 12u, d 198.305u) ==="
python3 run_ind_em.py ind_pa.gds 543 27.2 --run 2>&1 | grep -A3 " at 24"
echo "All done. Plots: ind_*_em.png"
