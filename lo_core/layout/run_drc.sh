#!/bin/bash
# DRC with the IHP SG13G2 deck (no density).  Usage: bash run_drc.sh <file.gds> [flat]
GDS=${1:?usage: bash run_drc.sh <file.gds> [flat]}; MODE=${2:-deep}
DIR=drc_$(basename ${GDS%.gds})_$(date +%H%M%S)_$MODE
python3 /foss/pdks/ihp-sg13g2/libs.tech/klayout/tech/drc/run_drc.py --path=$GDS --no_density --run_mode=$MODE --run_dir=$DIR
echo "Results in: $DIR"
