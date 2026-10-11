"""angle_test.py - transistor-level angle test of the 2TX/4RX chip.
Usage: python3 angle_test.py 20 -35   (plane-wave angles in degrees; ~70 s each)"""
import run_phased_core as R, numpy as np, sys
FB = 100e6; FLO = 24.0115e9
def angle_run(theta, flo=FLO):
    d, it = R.simulate({"FECHO": f"{flo+FB:.6e}", "THETA": theta}, netlist="phased_tb.spice", outfile="phased_tran.txt", tstop="30n")
    m = d[:, 0] > 12e-9; t = d[m, 0]
    amp, ph = [], []
    for col in (3, 5, 7, 9):
        A = np.column_stack([np.cos(2*np.pi*FB*t), np.sin(2*np.pi*FB*t), np.ones_like(t)])
        c, *_ = np.linalg.lstsq(A, d[m, col], rcond=None)
        amp.append(np.hypot(c[0], c[1])); ph.append(np.degrees(np.arctan2(-c[1], c[0])))
    ph = np.unwrap(np.radians(ph)); steps = np.degrees(np.diff(ph))
    # angle estimate: beam scan over the 4 IF phasors
    z = np.array(amp) * np.exp(1j*ph)
    th = np.radians(np.linspace(-90, 90, 3601))
    k = np.arange(4)
    p = np.abs(np.exp(1j*np.pi*np.outer(np.sin(th), k)) @ z)          # IF phase follows the RF phase (-180 k sin theta)
    est = np.degrees(th[np.argmax(p)])                                 # digital beamforming: steer, pick the peak
    return amp, steps, est
for theta in [float(a) for a in sys.argv[1:]]:
    amp, steps, est = angle_run(theta)
    print(f"theta = {theta:+.0f} deg: expected step {-180*np.sin(np.radians(theta)):+.1f} deg | IF amplitudes {np.round(np.array(amp)*1e3,1)} mV | "
          f"measured steps {np.round(steps,1)} deg | angle estimate {est:+.1f} deg", flush=True)
