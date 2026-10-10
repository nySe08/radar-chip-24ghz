"""
mimo_scene.py - 2 TX / 4 RX TDM-MIMO version of the 24 GHz radar (system model).

Chip performance from the transistor-level simulations (PA power, RX gain, noise figure),
plus: antenna geometry (8-element virtual array), patch-column element patterns,
TX1/TX2 alternating chirps (TDM-MIMO), and digital beamforming in the "FPGA".
Processing: range FFT -> Doppler FFT -> non-coherent sum over channels -> 2-D CA-CFAR
-> TDM Doppler compensation -> angle by beam scan across the 8 virtual channels.

Run:  python3 mimo_scene.py                    (calibrated channels)
      python3 mimo_scene.py --phase-err 15     (uncalibrated: random 15 deg rms LO phase errors per RX)
Out:  mimo_scene.png + detection table
"""
import argparse
import numpy as np
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt

ap = argparse.ArgumentParser(); ap.add_argument("--phase-err", type=float, default=0.0)
args = ap.parse_args()
rng = np.random.default_rng(3)
c, k, T0 = 3e8, 1.380649e-23, 290.0
db = lambda x: 10*np.log10(x); lin = lambda x: 10**(x/10)

# ---------------- waveform ----------------
F0, B, TC, FS = 24.0e9, 250e6, 128e-6, 5e6
NPT = 128                                   # chirps PER TRANSMITTER (TX1, TX2 alternate -> 256 chirps per frame)
lam = c/(F0 + B/2); S = B/TC; NS = int(TC*FS)

# ---------------- chip (transistor-level results) ----------------
PT_DBM, RX_GAIN = 5.5, 27.6
NF_LOSS, NF_LNA, G_LNA, NF_MIX = 1.5, 2.04, 20.3, 13.0
F_SYS = lin(NF_LOSS) + (lin(NF_LNA)-1)/lin(-NF_LOSS) + (lin(NF_MIX)-1)/(lin(-NF_LOSS)*lin(G_LNA))

# ---------------- antennas ----------------
G_EL = 11.0                                  # patch column (4 series-fed patches): peak gain [dBi]
def el_pattern(th):                          # azimuth power pattern of one column, ~100 deg beamwidth
    return np.clip(np.cos(th), 0, None)**1.3
x_rx = np.arange(4) * lam/2                  # RX positions
x_tx = np.array([0, 4]) * lam/2              # TX positions (4 * lambda/2 apart)
x_v = (x_tx[:, None] + x_rx[None, :]).ravel()   # 8 virtual positions, lambda/2 apart
phase_err = np.deg2rad(rng.normal(0, args.phase_err, 4)) if args.phase_err else np.zeros(4)

# ---------------- scene ----------------
targets = [  # name, range [m], speed [m/s] (+ approaching), azimuth [deg] (+ right), RCS [m^2]
    ("drone A", 45.0,  8.0,  20.0, 0.01),
    ("drone B", 35.0, -4.0, -30.0, 0.01),
    ("person",  60.0,  1.4,   0.0, 1.0),
    ("wall",    25.0,  0.0, -10.0, 5.0),
]

def amp_if(R, rcs, th):
    pt = lin(PT_DBM)*1e-3
    g = lin(G_EL)*el_pattern(th)
    pr = pt * g * g * lam**2 * rcs / ((4*np.pi)**3 * R**4)
    return np.sqrt(2*50*pr) * 10**(RX_GAIN/20)

t = np.arange(NS)/FS
cube = np.zeros((2, 4, NPT, NS))             # [tx, rx, chirp, sample]
for name, R, v, az, rcs in targets:
    th = np.deg2rad(az); a = amp_if(R, rcs, th); fb = 2*R*S/c
    for tx in range(2):
        for n in range(NPT):
            p = 2*n + tx                      # global chirp index (TX1 even, TX2 odd)
            Rp = R - v*p*TC
            for rx in range(4):
                ph = 2*np.pi*fb*t - 4*np.pi*Rp/lam - 2*np.pi*(x_tx[tx] + x_rx[rx])*np.sin(th)/lam + phase_err[rx]
                cube[tx, rx, n] += a*np.cos(ph)
vn = np.sqrt(k*T0*F_SYS*(FS/2)*50) * 10**(RX_GAIN/20)
cube += rng.normal(0, vn, cube.shape)

# ---------------- processing ----------------
NR = NS//2
rf = np.fft.rfft(cube*np.hanning(NS), axis=-1)[..., :NR]
rd = np.fft.fftshift(np.fft.fft(rf*np.hanning(NPT)[:, None], axis=2), axes=2)     # [tx, rx, doppler, range]
r_axis = np.arange(NR)*FS/NS*c/(2*S)
v_axis = np.fft.fftshift(np.fft.fftfreq(NPT, 2*TC))*lam/2                       # chirp period per TX = 2*TC
P = np.sum(np.abs(rd)**2, axis=(0, 1))                                          # non-coherent over 8 channels

def ca_cfar(P, guard=(2, 2), train=(6, 8), pfa=1e-6):
    from numpy.lib.stride_tricks import sliding_window_view as sw
    gd, gr = guard; td, tr = train; hd, hr = gd+td, gr+tr
    tot = sw(np.pad(P, ((hd, hd), (hr, hr)), mode="wrap"), (2*hd+1, 2*hr+1)).sum(axis=(-1, -2))
    inn = sw(np.pad(P, ((gd, gd), (gr, gr)), mode="wrap"), (2*gd+1, 2*gr+1)).sum(axis=(-1, -2))
    n = (2*hd+1)*(2*hr+1) - (2*gd+1)*(2*gr+1)
    # noise in a cell = sum of 8 channel powers (Gamma(8)); threshold for the wanted false-alarm rate,
    # plus ~15 % for the uncertainty of the noise estimate from the training cells
    from scipy.stats import gamma
    alpha = gamma.isf(pfa, 8)/8 * 1.15
    return P > alpha*(tot - inn)/n, (tot - inn)/n

det, noise = ca_cfar(P); det[:, r_axis < 3] = False
th_grid = np.deg2rad(np.linspace(-80, 80, 641))
steer = np.exp(-2j*np.pi*np.outer(np.sin(th_grid), x_v)/lam)                  # [angle, virtual element]

dets = []
for i, j in zip(*np.nonzero(det)):
    if P[i, j] < P[max(i-2, 0):i+3, max(j-2, 0):j+3].max(): continue
    y = rd[:, :, i, j].copy()                                                   # [tx, rx]
    y[1] *= np.exp(-1j*4*np.pi*v_axis[i]*TC/lam)                               # TDM: TX2 chirps are TC later
    beam = np.abs(steer.conj() @ y.ravel())**2
    dets.append((r_axis[j], v_axis[i], np.rad2deg(th_grid[np.argmax(beam)]), db(P[i, j]/noise[i, j]), beam))

# ---------------- report ----------------
print(f"System NF {db(F_SYS):.2f} dB, PA {PT_DBM:+.1f} dBm, element gain {G_EL} dBi, "
      f"virtual array 8 x lambda/2 ({x_v[-1]*1e3:.1f} mm aperture)")
print(f"Max unambiguous speed +-{lam/(4*2*TC):.1f} m/s (halved by TDM), angular resolution ~{np.rad2deg(2/8):.0f} deg at boresight")
if args.phase_err: print(f"Uncalibrated LO phase errors per RX: {np.round(np.rad2deg(phase_err), 1)} deg")
print("\nTarget     range    speed    azimuth  |  detected: range    speed    azimuth  (error)")
for name, R, v, az, rcs in targets:
    hit = [d for d in dets if abs(d[0]-R) < 1.5 and abs(d[1]-v) < 1.0]
    if hit:
        r, vv, a, s, _ = hit[0]
        print(f"{name:9s} {R:5.1f} m {v:+5.1f} m/s {az:+6.1f}°  |  {r:5.1f} m  {vv:+6.2f} m/s  {a:+6.1f}°  ({a-az:+.1f}°)")
    else:
        print(f"{name:9s} {R:5.1f} m {v:+5.1f} m/s {az:+6.1f}°  |  not detected")
false = [d for d in dets if not any(abs(d[0]-R) < 1.5 and abs(d[1]-v) < 1.0 for _, R, v, _, _ in targets)]
print(f"False alarms: {len(false)}")

# max drone range vs azimuth (link budget with 8-channel coherent gain, 13 dB detection threshold)
def snr(R, rcs, az):
    th = np.deg2rad(az); g = lin(G_EL)*el_pattern(th)
    s1 = lin(PT_DBM)*1e-3*g*g*lam**2*rcs*NPT*TC / ((4*np.pi)**3*R**4*k*T0*F_SYS)   # one virtual channel
    return db(8*s1) - 3.0                                                           # coherent over 8, minus processing loss
print("\nDrone (0.01 m^2) detection range vs azimuth:",
      ", ".join(f"{az}°: {10**((snr(1, 0.01, az)-13)/40):.0f} m" for az in (0, 30, 45, 60)))

# ---------------- figure ----------------
fig = plt.figure(figsize=(17, 5.4))
ax1 = fig.add_subplot(1, 3, 1)
for steer_to in (0, 30):
    w = np.exp(-2j*np.pi*np.sin(np.deg2rad(steer_to))*x_v/lam)
    af = np.abs(steer.conj() @ w)**2; af /= af.max()
    ax1.plot(np.rad2deg(th_grid), db(af*el_pattern(th_grid)+1e-6), label=f"beam steered to {steer_to}°")
ax1.set_ylim(-30, 1); ax1.set_xlabel("Azimuth [deg]"); ax1.set_ylabel("Normalized gain [dB]")
ax1.set_title("1. Virtual 8-element array: beams steered\nelectronically (digital beamforming)"); ax1.grid(alpha=.3); ax1.legend(fontsize=8)

ax2 = fig.add_subplot(1, 3, 2)
im = ax2.imshow(db(P/np.median(P)), aspect="auto", origin="lower", cmap="viridis", vmin=0, vmax=50,
                extent=[r_axis[0], r_axis[-1], v_axis[0], v_axis[-1]])
ax2.set_xlim(0, 80); ax2.set_xlabel("Range [m]"); ax2.set_ylabel("Radial velocity [m/s]")
ax2.set_title("2. Range-Doppler (all 8 channels)"); plt.colorbar(im, ax=ax2, label="dB above noise")
for r, vv, a, s, _ in dets: ax2.plot(r, vv, "o", mfc="none", mec="r", ms=11, mew=1.4)

# bird's-eye view: range-azimuth map from all Doppler bins except the static (zero-speed) ones
ax3 = fig.add_subplot(1, 3, 3)
ri = r_axis < 80
y = rd[:, :, :, ri].copy()
y[1] *= np.exp(-1j*4*np.pi*v_axis[:, None]*TC/lam)
Y = y.reshape(8, NPT, -1)
taper = np.hanning(10)[1:-1]                               # amplitude taper across the 8 virtual elements -> low sidelobes
ra = np.einsum("av,vdr->adr", (steer*taper).conj(), Y)
RA = np.sum(np.abs(ra)**2, axis=1)                                      # sum over Doppler
TH, RR = np.meshgrid(th_grid, r_axis[ri], indexing="ij")
pc = ax3.pcolormesh(RR*np.sin(TH), RR*np.cos(TH), db(RA/np.median(RA)), cmap="viridis", vmin=0, vmax=45, shading="gouraud")
for name, R, v, az, rcs in targets:
    ax3.annotate(name, (R*np.sin(np.deg2rad(az)), R*np.cos(np.deg2rad(az))), xytext=(8, 8),
                 textcoords="offset points", color="w", fontsize=9)
for r, vv, a, s_, _ in dets:
    ax3.plot(r*np.sin(np.deg2rad(a)), r*np.cos(np.deg2rad(a)), "o", mfc="none", mec="r", ms=11, mew=1.4)
ax3.set_aspect("equal"); ax3.set_xlabel("Cross-range x [m]"); ax3.set_ylabel("Down-range y [m]")
ax3.set_title("3. Bird's-eye view (red = detections)"); plt.colorbar(pc, ax=ax3, label="dB")
fig.suptitle("2 TX / 4 RX TDM-MIMO radar with the simulated chip performance (24 GHz, 8 virtual channels)"
             + (f" — UNCALIBRATED phase errors {args.phase_err:g}° rms" if args.phase_err else ""), fontsize=12)
plt.tight_layout()
out = "mimo_scene.png" if not args.phase_err else "mimo_scene_uncal.png"
plt.savefig(out, dpi=150); print("Saved", out)
