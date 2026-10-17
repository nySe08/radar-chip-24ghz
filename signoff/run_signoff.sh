#!/bin/bash
# run_signoff.sh - one ordered sign-off pass for a block. Stops at the first failing stage.
# usage (inside <block>/layout):  bash run_signoff.sh lo_core
#   expects: <cell>.gds, <cell>_lvs.cdl (LVS reference), <cell>_lvs_kpex.cdl (extraction reference),
#            optional ../stab/*.spice testbenches with SP ports for stability.py, and zscan targets in ZSCAN_ARGS.
set -euo pipefail
CELL=${1:?cell name}; SIGN=$(dirname "$(readlink -f "$0")"); STAMP=$(date +%Y%m%d_%H%M%S)
LOG=signoff_${CELL}_${STAMP}.log; exec > >(tee "$LOG") 2>&1
START=.signoff_start_${STAMP}; touch "$START"     # fixed reference time (the log itself keeps changing while it is written)
echo "== sign-off $CELL  $STAMP"; echo "tools: $(klayout -v 2>/dev/null) | kpex $(kpex --version 2>/dev/null || echo '?') | $(ngspice -v 2>/dev/null | grep -m1 -o 'ngspice-[0-9]*')"
echo "inputs:"; sha256sum "$CELL.gds" "${CELL}_lvs.cdl" "${CELL}_lvs_kpex.cdl" | sed 's/^/  /'

echo "== 1/6 DRC";  bash run_drc.sh "$CELL.gds" flat 2>&1 | tee .stage_out
# a check only counts if it printed its verdict (a wrong local script can "finish" without running anything)
grep -q "DRC Check Passed" .stage_out || { echo "  STOP: DRC did not report 'DRC Check Passed' - it failed or did not run (check run_drc.sh)"; exit 1; }
echo "== 1b antenna rules (block nets; repeat at chip level)"
python3 "${PDK_ROOT:-/foss/pdks}/ihp-sg13g2/libs.tech/klayout/tech/drc/run_drc.py" --path="$CELL.gds" --topcell="$CELL" \
        --run_mode=flat --antenna_only --run_dir="drc_${CELL}_antenna" 2>&1 | tee .stage_out
grep -q "DRC Check Passed" .stage_out || { echo "  STOP: the antenna check did not report a pass"; exit 1; }
echo "== 1c density preview (IHP precheck densities: fill fixes 'too sparse', the design must fix 'too dense')"
python3 "$SIGN/density_preview.py" "$CELL.gds" || echo "  (density preview: a layer needs a design change - see above; not a block failure yet)"
echo "== 2/6 LVS";  bash run_lvs.sh "$CELL.gds" "${CELL}_lvs.cdl" "$CELL" 2>&1 | tee .stage_out
grep -q "Comparison mode: PASS" .stage_out || { echo "  STOP: LVS did not report 'Comparison mode: PASS'"; exit 1; }
# find THIS run's LVS results whatever the local run_lvs.sh calls its folder: newest .lvsdb / extracted .cir written
# after the log was created (the extractor's own database is .lvsdb.gz and comes later, so it is not picked up)
newest() { find . -maxdepth 3 -name "$1" -newer "$START" -printf "%T@ %p\n" 2>/dev/null | sort -rn | head -1 | cut -d' ' -f2-; }
LVSDB=$(newest "*.lvsdb"); CIR=$(newest "*extracted*.cir")
echo "  LVS results used by the gate: ${LVSDB:-none found} | ${CIR:-none found}"

echo "== 3/6 extraction (devices BLACKBOXED: models keep the MIMs; kpex adds only wiring C)"
rm -rf pex_out
if ! kpex extract --pdk ihp-sg13g2 --gds "$CELL.gds" --cell "$CELL" --schematic "${CELL}_lvs_kpex.cdl" \
     --2.5D --blackbox y --out_dir pex_out; then
  # kpex < 0.6 crashes writing the SPICE netlist with blackboxed MIMs ("Invalid parameter name: 'C'") AFTER the CSV
  if ls pex_out/${CELL}__${CELL}/*_pex_netlist.csv >/dev/null 2>&1; then
    echo "  kpex exited with an error after writing the CSV (SPICE writer bug in kpex < 0.6): continuing, the gate decides"
  else echo "  extraction failed before writing the CSV"; exit 1; fi
fi
# optional QA of the 2.5D engine on a cropped critical region (slow; field solver):
#   kpex extract --pdk ihp-sg13g2 --gds tank_crop.gds --cell tank_crop --fastercap --blackbox y --out_dir pex_fc

echo "== 4/6 extraction gate"
python3 "$SIGN/pex_gate.py" --cdl "${CELL}_lvs_kpex.cdl" ${LVSDB:+--lvsdb "$LVSDB"} ${CIR:+--cir "$CIR"} \
        --pex "pex_out/${CELL}__${CELL}" --cell "$CELL" --baseline "net_c_${CELL}.json" ${GATE_NETS:+--nets $GATE_NETS} \
        $( [ -f "${CELL}_waivers.txt" ] && echo --waivers "${CELL}_waivers.txt" )

echo "== 5/6 two-port stability (all corners, 0.1-100 GHz)"
for tb in ../stab/*.spice; do
  [ -e "$tb" ] || { echo "  (no ../stab/*.spice two-port testbenches - skipped)"; break; }
  python3 "$SIGN/stability.py" "$tb" --corner hbt_typ hbt_wcs hbt_bcs --vswr 2 3 6 inf --fstop 100e9
done

echo "== 6/6 internal-node impedance scan"
if [ -n "${ZSCAN_TB:-}" ]; then python3 "$SIGN/zscan.py" "$ZSCAN_TB" $ZSCAN_ARGS --fstop 100e9
else echo "  (set ZSCAN_TB and ZSCAN_ARGS, e.g. ZSCAN_ARGS='--node xq.base --diff xlo.efp xlo.efn') - skipped"; fi
echo "== SIGN-OFF PASSED: $LOG"
