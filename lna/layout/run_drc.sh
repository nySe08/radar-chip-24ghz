#!/bin/bash
# DRC on the LNA layout (IHP SG13G2 rule deck, no density checks).
# Usage (in the layout folder):  bash run_drc.sh
# If KLayout crashes in the default (deep) mode, run:  bash run_drc.sh flat
MODE=${1:-deep}
DIR=drc_$(date +%H%M%S)_$MODE
python3 /foss/pdks/ihp-sg13g2/libs.tech/klayout/tech/drc/run_drc.py \
    --path=lna_layout.gds --no_density --run_mode=$MODE --run_dir=$DIR
echo "Results in: $DIR"
