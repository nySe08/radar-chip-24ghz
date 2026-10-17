#!/bin/bash
# LVS with the IHP SG13G2 deck.  Usage: bash run_lvs.sh <layout.gds> <netlist.cdl> <topcell>
# --ignore_top_ports_mismatch: the inductor PCells' LA/LB labels (needed for inductor recognition) would otherwise
# count as extra top-level ports; devices and nets are still compared in full.
GDS=${1:?usage: bash run_lvs.sh <layout.gds> <netlist.cdl> <topcell>}; CDL=${2:?}; TOP=${3:?}
DIR=lvs_${TOP}_$(date +%H%M%S)
python3 /foss/pdks/ihp-sg13g2/libs.tech/klayout/tech/lvs/run_lvs.py --layout=$GDS --netlist=$CDL --topcell=$TOP --run_dir=$DIR --ignore_top_ports_mismatch
echo "Results in: $DIR   (extracted netlist: $DIR/*_extracted.cir)"
