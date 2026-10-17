# TX channel: driver + power amplifier (24 GHz)

One transmit channel: a resistively loaded differential driver (`blocks/txdrv_real.sp`) fed by the LO core's TX output,
followed by a single-ended cascode power amplifier (`blocks/pa_final.sp`), the TX output pad and its ESD coil.
Every element is a real IHP SG13G2 device; the coils are EM-fitted models of `inductor2` PCells.

## Results (post-layout LO drive, real pad + ESD coil, 50 Ω load)

| Corner | Output power | 2nd harmonic | Supply current |
|---|---|---|---|
| Slow (85 °C, VCC −5%) | **+4.99 dBm** | −21.1 dBm | 13.9 mA |
| Typical (27 °C) | +6.78 dBm | −18.6 dBm | 18.1 mA |
| Fast (−40 °C, VCC +5%) | +5.50 dBm | −21.9 dBm | 24.4 mA |

Target: at least +4.5 dBm at every corner. Reproduce with `python3 run_tx_final.py` (about 1 minute, inside IIC-OSIC-TOOLS).

## Design decisions, and why

1. **Cascode = two 8-finger high-voltage HBTs in parallel.** The original single `npn13G2v` (Nx = 8, kept as
   `blocks/pa_baseline_single_cascode.sp`) reached high injection (Kirk effect) at the fast corner's current density:
   its gain collapsed and the output *fell* with more drive (+2.4 dBm worst case). Waveform analysis ruled out
   saturation and tank detuning; halving the current density fixed it (+2.4 → +7.8 dBm at the fast corner).
2. **Output coil re-centred to 333 pH** (1 turn, w 12 µm, d 147 µm; EM: Q 24.8) for the larger cascode's capacitance.
3. **Second-harmonic trap on the 50 Ω side** (series ~175 pH coil + 6.4 µm MIM, resonant near 48.3 GHz). A
   collector-side trap cost ~1 dB at every corner; on the output side it costs far less. The MIM size balances the
   trap across the ±10% MIM corners.
4. **Inductive ESD on the output pad** (2 turns, w 7 µm, d 77 µm; EM: ≈730 pH, Q 14.8 at 24.1 GHz). It is a
   low-resistance ESD path with no diode capacitance, and it cancels part of the trap's capacitive loading.
5. **More driver gain and PA bias** (driver load 1.6 µm, mirror reference 2.0 µm), affordable once the fast corner
   no longer collapses; they lift the slow corner.

## Files

| File | Content |
|---|---|
| `blocks/txdrv_real.sp` | TX driver (differential pair, dummy load for balance) |
| `blocks/pa_final.sp` | Final PA, final values as defaults |
| `blocks/pa_baseline_single_cascode.sp` | Original PA, for comparison |
| `tx_tb.spice` | Testbench: LO drive → driver → PA → pad + ESD coil → 50 Ω |
| `txrun.py` | Runs one transient, returns output power, current and 2nd harmonic |
| `run_tx_final.py` | Reproduces the table above at the three corners |

Status: circuit final; layout next (same generator and sign-off flow as the other blocks).
