"""
run_chirp.py - END-TO-END RADAR DEMO at transistor level (~2-3 minutes).

The complete chip (VCO, LO buffer, PA, LNA, mixer, divider) runs a chirp: Vtune is ramped,
the VCO sweeps in frequency, the PA transmits it. Two targets are delayed copies of the
transmitted signal (4 ns and 8 ns) arriving at the RX antenna together with TX leakage.
The mixer output must contain one beat tone per target, at  f_beat = chirp slope x delay.

Time-scaled chirp (80 ns instead of 128 us): identical physics, simulates in minutes.
Usage:  python3 run_chirp.py            (simulate + analyse + plot)
        python3 run_chirp.py --reuse    (analyse a previous run saved in chirp.npy)
"""
import sys, os
import numpy as np
import run_top as R
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt

DELAYS = (4e-9, 8e-9)       # must match TD1, TD2 in chirp_tb.spice
T0, T1 = 22e-9, 90e-9       # analysis window: both echoes present, chirp running
C = 3e8

if "--reuse" in sys.argv and os.path.exists("chirp.npy"):
    d = np.load("chirp.npy")
else:
    print("Simulating the full chip through one chirp (2-3 minutes) ...", flush=True)
    d, itot = R.simulate(netlist="chirp_tb.spice", outfile="chirp_tran.txt", tstop="90n")
    np.save("chirp.npy", d)
t, vco, vif, vt = d[:, 0], d[:, 1], d[:, 3], d[:, 7]

# 1) the chirp: instantaneous VCO frequency from zero crossings (smoothed over 8 cycles)
zc = np.where((vco[:-1] < 0) & (vco[1:] >= 0))[0]
tz = t[zc] - vco[zc] * (t[zc+1] - t[zc]) / (vco[zc+1] - vco[zc])
fi, tm = 1 / np.diff(tz), (tz[1:] + tz[:-1]) / 2
k = 8; fs = np.convolve(fi, np.ones(k)/k, "valid"); ts = np.convolve(tm, np.ones(k)/k, "valid")
w = (ts > T0) & (ts < T1 - 2e-9)
slope = np.polyfit(ts[w], fs[w], 1)[0]

# 2) prediction: f_beat(t) = f(t) - f(t - delay), averaged over the window
pred = [np.mean(np.interp(ts[w], ts, fs) - np.interp(ts[w] - td, ts, fs)) for td in DELAYS]

# 3) measurement: spectrum of the mixer IF output in the window
m = (t > T0) & (t < T1)
tu = np.linspace(T0, T1, 4096); y = np.interp(tu, t[m], vif[m]); dc = y.mean(); y = y - dc
N = 1 << 16; Y = np.abs(np.fft.rfft(y * np.hanning(len(y)), N)); f = np.fft.rfftfreq(N, tu[1] - tu[0])
peaks = []
for p in pred:                                    # strongest bin within +-10 MHz of each prediction
    s = (f > p - 10e6) & (f < p + 10e6); i = np.argmax(np.where(s, Y, 0)); peaks.append((f[i], Y[i]))

print(f"\nChirp: {np.interp(T0, ts, fs)/1e9:.3f} -> {np.interp(T1-2e-9, ts, fs)/1e9:.3f} GHz, slope {slope/1e15:.2f} MHz/ns")
print("target   delay   predicted beat   measured peak   delay from measurement   'distance' (c*tau/2)")
for n, (td, p, (fm, a)) in enumerate(zip(DELAYS, pred, peaks), 1):
    print(f"  {n}      {td*1e9:4.1f} ns   {p/1e6:7.1f} MHz      {fm/1e6:7.1f} MHz        {fm/slope*1e9:5.2f} ns               {C*fm/slope/2:5.2f} m")
print(f"Target 2 is {20*np.log10(peaks[0][1]/peaks[1][1]):.1f} dB weaker than target 1 (set to 6 dB weaker)")
print(f"IF DC offset from TX leakage: {dc*1e3:+.1f} mV  (removed by AC coupling in the real IF path)")

# figure
fig, ax = plt.subplots(1, 3, figsize=(17, 4.6))
ax[0].plot(ts*1e9, fs/1e9, lw=1.2)
ax[0].set_xlabel("Time [ns]"); ax[0].set_ylabel("VCO frequency [GHz]"); ax[0].grid(alpha=0.3)
ax[0].set_title("1. The chip chirps (Vtune ramped)")
a2 = ax[0].twinx(); a2.plot(t*1e9, vt, ":", c="gray", lw=0.8, alpha=0.7); a2.set_ylabel("Vtune [V] (dotted)", color="gray")
# light low-pass for display only (averages out the residual 24 GHz LO ripple)
yl = np.convolve(y, np.ones(4)/4, "same")
ax[1].plot(tu*1e9, yl*1e3, lw=1.2)
ax[1].set_xlabel("Time [ns]"); ax[1].set_ylabel("Mixer IF output (DC removed) [mV]")
ax[1].set_title("2. Beat signal at the IF output"); ax[1].grid(alpha=0.3)
sel = (f > 5e6) & (f < 150e6)
ax[2].plot(f[sel]/1e6, 20*np.log10(Y[sel]/Y[sel].max()), lw=1.3)
for n, (p, (fm, a)) in enumerate(zip(pred, peaks), 1):
    ax[2].axvline(p/1e6, ls="--", c="r", lw=1)
    ax[2].annotate(f"target {n}\n{DELAYS[n-1]*1e9:.0f} ns delay\n{fm/1e6:.1f} MHz", (fm/1e6, 20*np.log10(a/Y[sel].max())),
                   xytext=(8, -28), textcoords="offset points", fontsize=8.5)
ax[2].set_ylim(-40, 3); ax[2].set_xlabel("IF frequency [MHz]"); ax[2].set_ylabel("Relative level [dB]")
ax[2].set_title("3. Two targets -> two peaks (red: predicted)"); ax[2].grid(alpha=0.3)
fig.suptitle("Transistor-level 24 GHz FMCW transceiver: end-to-end chirp with two targets (time-scaled chirp)", fontsize=12)
plt.tight_layout(); plt.savefig("chirp_demo.png", dpi=150); print("Saved chirp_demo.png")
