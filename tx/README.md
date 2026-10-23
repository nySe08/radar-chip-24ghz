# TX channel: driver + power amplifier (24 GHz)

One transmit channel: a resistively loaded differential driver (`blocks/txdrv_real.sp`) fed by the LO core's TX output,
then a single-ended cascode power amplifier (`blocks/pa_final.sp`), the TX output pad and its ESD coil. Every element is
a real IHP SG13G2 device; the coils are EM-fitted models of `inductor2` PCells. The layout is in [`../tx_ch/layout`](../tx_ch/layout)
and is signed off: DRC, antenna, LVS (IHP's deck and KLayout-PEX's own) and the extraction gate, with no waivers.

## Results after layout (the specification)

Post-layout model: the schematic plus every capacitance KLayout-PEX extracted from the signed-off layout, with the
substrate's share bracketed between 0 % and 100 %, because the extractor treats the substrate as an ideal ground.

| Corner | Output power (substrate 0 % / **50 %** / 100 %) | 2nd harmonic | Supply | Stability |
|---|---|---|---|---|
| Slow (85 °C, VCC −5%) | 4.58 / **3.68** / 2.57 dBm | ≤ −24 dBm | 15 mA | μ ≥ 1.10 |
| Typical (27 °C) | 6.57 / **6.11** / 5.56 dBm | ≤ −21.8 dBm | 19.6 mA | μ ≥ 1.10 |
| Fast (−40 °C, VCC +5%) | 5.60 / **5.56** / 5.50 dBm | ≤ −19.5 dBm | 26 mA | μ ≥ 1.10 |

**Unconditionally stable** from 0.1 to 100 GHz at every corner and bound (μ ≥ 1.10, K ≥ 5.3): no passive source or
load can make it oscillate. The specification is met at the mid-bound (+3.5 dBm at the hot, low-supply corner);
at the pessimistic bound that corner reaches +2.6 dBm. Reproduce: `cd post_layout && python3 tx_postlayout.py` (about 1 minute).

`run_tx_final.py` simulates the schematic netlists alone (no parasitics): +6.22 / +7.29 / +4.92 dBm. It only confirms
the netlists; its fast-corner 2nd harmonic (−12.8 dBm) is higher because the trap MIM is sized for the layout's parasitics.

## Design decisions, and why

1. **Cascode = two 8-finger high-voltage HBTs in parallel.** The original single `npn13G2v` (kept as
   `blocks/pa_baseline_single_cascode.sp`) reached high injection (Kirk effect) at the fast corner: its gain collapsed and
   the output *fell* with more drive (+2.4 dBm). Halving the current density fixed it (+7.8 dBm at that corner).
2. **Output coil re-centred to 333 pH** (1 turn, w 12 µm, d 147 µm; EM: Q 24.8) for the larger cascode's capacitance.
3. **Second-harmonic trap on the 50 Ω side** (series MIM + ~175 pH coil, resonant near 48.3 GHz), which costs far less
   power than a trap on the collector.
4. **Inductive ESD on the output pad** (2 turns, w 7 µm, d 77 µm; EM: ≈730 pH, Q 14.8): a low-resistance ESD path with
   no diode capacitance, which also cancels part of the trap's loading.
5. **Post-layout re-tune.** The first signed-off layout lost 3.6 dB at the hot corner after extraction, mostly to
   ~83 fF on the PA's input path: a capacitive divider the hot, drive-limited corner could not afford. The fix:
   the PA's input MIM removed (the driver's coupling MIM now drives the base directly, cutting the input path to 60 fF),
   the base line rerouted below the supply decoupling MIM instead of under it, the driver re-tuned for more current into
   a lower-resistance load (load 0.9 µm, tail 2.2 × 0.5 µm), 16 µm coupling MIMs, and the trap MIM re-centred to 6.0 µm.
   Net result: +2.3 dB at the hot corner and +1.3 dB typical.

## Files

| File | Content |
|---|---|
| `blocks/txdrv_real.sp` | TX driver, final values |
| `blocks/pa_final.sp` | Final PA (input port = the base; trap and output MIM in the layout's order) |
| `blocks/pa_baseline_single_cascode.sp` | Original PA, for comparison |
| `tx_tb.spice`, `txrun.py` | Testbench and runner: LO drive → driver → PA → pad + ESD coil → 50 Ω |
| `run_tx_final.py` | Schematic-level check of the netlists |
| `post_layout/tx_postlayout.py` | Post-layout power, harmonic and stability at all corners and bounds |
| `post_layout/tx_ch_k25d_pex_netlist.csv` | The extraction of the signed-off layout |
