"""
24 GHz FMCW radar transceiver - Phase 1 system model
=====================================================
Single source of truth for the system-level numbers. Change an assumption
in CONFIG, re-run, and every derived spec and requirement check updates.

Run:  python radar_system_model.py
Out:  console report + link_budget.png + if_spectrum.png
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

C = 3e8          # speed of light [m/s]
K_T0 = 4.0e-21   # kT0 at 290 K [W/Hz]  (-174 dBm/Hz)

def db(x):   return 10 * np.log10(x)
def lin(x):  return 10 ** (x / 10)

# ---------------------------------------------------------------- CONFIG
CONFIG = {
    # waveform
    "f_start_hz": 24.00e9,
    "bandwidth_hz": 250e6,
    "t_chirp_s": 128e-6,
    "n_chirps": 128,
    "adc_fs_hz": 5e6,
    # TX / antennas
    "pt_dbm": 5.0,              # PA output
    "g_tx_dbi": 10.0,
    "g_rx_dbi": 10.0,
    "tx_rx_isolation_db": 35.0,
    # RX chain (Friis cascade, in order)
    "input_loss_db": 1.5,       # pads / bondwire / matching
    "lna_gain_db": 18.0, "lna_nf_db": 5.0, "lna_ip1db_dbm": -20.0,
    "mixer_gain_db": 10.0, "mixer_nf_db": 15.0,
    # detection
    "processing_loss_db": 3.0,
    "snr_required_db": 13.0,    # ~Pd 0.9, Pfa 1e-6, non-fluctuating
    # targets: name -> RCS [m^2]
    "targets": {"small drone": 0.01, "person": 1.0},
}

REQUIREMENTS = {
    "R2 drone range >= 40 m":       ("small drone", 40.0),
    "R3 person range >= 100 m":     ("person", 100.0),
}

# ---------------------------------------------------------------- MODEL
def waveform(cfg):
    fc = cfg["f_start_hz"] + cfg["bandwidth_hz"] / 2
    lam = C / fc
    slope = cfg["bandwidth_hz"] / cfg["t_chirp_s"]
    t_frame = cfg["n_chirps"] * cfg["t_chirp_s"]
    return {
        "fc_hz": fc,
        "lambda_m": lam,
        "slope_hz_per_s": slope,
        "t_frame_s": t_frame,
        "range_res_m": C / (2 * cfg["bandwidth_hz"]),
        "v_max_mps": lam / (4 * cfg["t_chirp_s"]),
        "v_res_mps": lam / (2 * t_frame),
        "r_max_adc_m": (cfg["adc_fs_hz"] / 2) * C / (2 * slope),
    }

def beat_freq(r_m, slope):
    return 2 * r_m * slope / C

def rx_cascade(cfg):
    """Friis: returns total NF [dB] and total gain [dB]."""
    stages = [  # (gain_db, nf_db)
        (-cfg["input_loss_db"], cfg["input_loss_db"]),
        (cfg["lna_gain_db"], cfg["lna_nf_db"]),
        (cfg["mixer_gain_db"], cfg["mixer_nf_db"]),
    ]
    f_tot, g_acc = 1.0, 1.0
    for i, (g, nf) in enumerate(stages):
        f = lin(nf)
        f_tot += (f - 1) / g_acc if i else (f - 1)
        g_acc *= lin(g)
    return db(f_tot), db(g_acc)

def snr_db(cfg, wf, nf_db, rcs, r_m):
    """FMCW radar equation with coherent integration over one frame."""
    pt_w = lin(cfg["pt_dbm"] - 30)
    num = (pt_w * lin(cfg["g_tx_dbi"]) * lin(cfg["g_rx_dbi"])
           * wf["lambda_m"] ** 2 * rcs * wf["t_frame_s"])
    den = ((4 * np.pi) ** 3 * np.asarray(r_m) ** 4 * K_T0
           * lin(nf_db) * lin(cfg["processing_loss_db"]))
    return db(num / den)

def max_range(cfg, wf, nf_db, rcs):
    """Range where SNR equals the required SNR (R^4 scaling)."""
    snr_1m = snr_db(cfg, wf, nf_db, rcs, 1.0)
    return 10 ** ((snr_1m - cfg["snr_required_db"]) / 40)

# ---------------------------------------------------------------- REPORT
def main(cfg=CONFIG):
    wf = waveform(cfg)
    nf_db, g_rx_db = rx_cascade(cfg)
    eirp = cfg["pt_dbm"] + cfg["g_tx_dbi"]
    leak_dbm = cfg["pt_dbm"] - cfg["tx_rx_isolation_db"]
    leak_margin = cfg["lna_ip1db_dbm"] - leak_dbm

    print("=" * 60)
    print("WAVEFORM")
    print(f"  Center frequency      {wf['fc_hz']/1e9:8.3f} GHz")
    print(f"  Wavelength            {wf['lambda_m']*1e3:8.2f} mm")
    print(f"  Chirp slope           {wf['slope_hz_per_s']/1e12:8.3f} MHz/us")
    print(f"  Range resolution      {wf['range_res_m']:8.2f} m")
    print(f"  Max velocity          {wf['v_max_mps']:8.1f} m/s")
    print(f"  Velocity resolution   {wf['v_res_mps']:8.2f} m/s")
    print(f"  Max range (ADC limit) {wf['r_max_adc_m']:8.1f} m")
    for r in (1, 50, 150):
        print(f"  Beat freq @ {r:3d} m     {beat_freq(r, wf['slope_hz_per_s'])/1e3:8.1f} kHz")

    print("\nRX CHAIN (Friis)")
    print(f"  System noise figure   {nf_db:8.2f} dB")
    print(f"  RF-to-IF gain         {g_rx_db:8.2f} dB")
    print(f"  TX leakage at LNA     {leak_dbm:8.1f} dBm  (margin to IP1dB: {leak_margin:.1f} dB)")

    print("\nDETECTION RANGE")
    ranges = {}
    for name, rcs in cfg["targets"].items():
        ranges[name] = max_range(cfg, wf, nf_db, rcs)
        print(f"  {name:12s} ({rcs:5.2f} m^2)  {ranges[name]:7.1f} m")

    print("\nREQUIREMENT CHECKS")
    checks = {
        "R1 band 24.00-24.25 GHz": cfg["f_start_hz"] >= 24.00e9
            and cfg["f_start_hz"] + cfg["bandwidth_hz"] <= 24.25e9,
        "R4 range res <= 1 m":     wf["range_res_m"] <= 1.0,
        "R5 v_max >= 20 m/s":      wf["v_max_mps"] >= 20.0,
        "R6 EIRP <= 20 dBm":       eirp <= 20.0,
        "LNA linear vs leakage (>=10 dB margin)": leak_margin >= 10.0,
    }
    for label, (tgt, r_req) in REQUIREMENTS.items():
        checks[label] = ranges[tgt] >= r_req
    for label, ok in checks.items():
        print(f"  [{'PASS' if ok else 'FAIL'}] {label}")
    print(f"\n  EIRP = {eirp:.1f} dBm")
    print("=" * 60)

    # --- plot 1: SNR vs range
    r = np.linspace(5, 250, 500)
    plt.figure(figsize=(8, 5))
    for name, rcs in cfg["targets"].items():
        plt.plot(r, snr_db(cfg, wf, nf_db, rcs, r), label=f"{name} ({rcs} m²)")
    plt.axhline(cfg["snr_required_db"], ls="--", c="k", label="Required SNR")
    plt.xlabel("Range [m]"); plt.ylabel("SNR after integration [dB]")
    plt.title("24 GHz FMCW link budget"); plt.grid(alpha=0.3); plt.legend()
    plt.ylim(-10, 50); plt.tight_layout(); plt.savefig("link_budget.png", dpi=150)

    # --- plot 2: simulated IF signal -> range FFT (sanity check of the math)
    fs, tc = cfg["adc_fs_hz"], cfg["t_chirp_s"]
    t = np.arange(int(fs * tc)) / fs
    rng = np.random.default_rng(0)
    test_targets = [(20.0, 1.0), (45.0, 0.3)]          # (range m, rel. amplitude)
    sig = sum(a * np.cos(2 * np.pi * beat_freq(R, wf["slope_hz_per_s"]) * t)
              for R, a in test_targets)
    sig += 0.05 * rng.standard_normal(t.size)
    n_fft = 4096
    spec = np.abs(np.fft.rfft(sig * np.hanning(t.size), n_fft))
    f_axis = np.fft.rfftfreq(n_fft, 1 / fs)
    r_axis = f_axis * C / (2 * wf["slope_hz_per_s"])
    plt.figure(figsize=(8, 4))
    plt.plot(r_axis, 20 * np.log10(spec / spec.max() + 1e-12))
    for R, _ in test_targets:
        plt.axvline(R, ls=":", c="r")
    plt.xlim(0, 80); plt.ylim(-60, 3)
    plt.xlabel("Range [m]"); plt.ylabel("Normalized magnitude [dB]")
    plt.title("Simulated IF beat signal -> range FFT (targets at 20 m and 45 m)")
    plt.grid(alpha=0.3); plt.tight_layout(); plt.savefig("if_spectrum.png", dpi=150)
    print("Saved: link_budget.png, if_spectrum.png")

if __name__ == "__main__":
    main()
