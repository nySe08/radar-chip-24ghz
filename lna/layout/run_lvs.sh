#!/bin/bash
# LVS of the LNA layout against lna_lvs.cdl (IHP SG13G2 deck).  Usage: bash run_lvs.sh
# --ignore_top_ports_mismatch: the inductor PCells' LA/LB labels (required for inductor recognition)
# would otherwise be counted as extra top-level ports; nets and devices are still compared fully.
DIR=lvs_$(date +%H%M%S)
python3 /foss/pdks/ihp-sg13g2/libs.tech/klayout/tech/lvs/run_lvs.py \
    --layout=lna_layout.gds --netlist=lna_lvs.cdl --topcell=lna --run_dir=$DIR --ignore_top_ports_mismatch
echo "Results in: $DIR   (open the .lvsdb file in KLayout: Tools > Netlist Browser)"
