"""Octagonal TopMetal2 spiral inductor model for IHP SG13G2 (first-pass design before EM).
L : current-sheet formula (Mohan et al., IEEE JSSC 1999), octagon coefficients.
R : skin effect in 3 um TopMetal2 (sigma 3.03e7 S/m), plus leads/underpass factor.
Parasitics: Yue-Wong pi-model: oxide (TM2 is ~11.2 um above silicon), lossy substrate."""
import numpy as np
MU0, EPS0 = 4e-7*np.pi, 8.854e-12
SIG, T_TM2 = 3.03e7, 3e-6          # TopMetal2 conductivity, thickness (IHP openEMS stack)
T_OX, EPS_OX = 11.23e-6, 4.1       # oxide below TopMetal2
C_SUB_A, G_SUB_A = 1.0e-3*1e-15/1e-12, 2.0e-9/1e-12   # substrate cap, conductance: calibrated so Lb Q is ~9% below EM (conservative)
K_LEAD = 1.8                       # extra series resistance from leads/underpass (calibrated: PCell default 577.7 mOhm)
# AC calibration against openEMS (Lb: 1 turn, w=16u, d=230.97u; 1 um mesh, -60 dB end criterion):
#   EM R(24.1 GHz) = 2.44 ohm vs. 5.19 ohm from the formula below -> scale the AC resistance by 0.47.
#   Calibrated on ONE geometry: re-check other widths/turn counts with EM.
K_AC = 2.44/5.19

def geometry(w, s, din, n):
    dout = din + 2*n*w + 2*(n-1)*s
    davg = (din + dout)/2; rho = (dout - din)/(dout + din)
    length = n * 8*np.tan(np.pi/8) * davg       # octagon perimeter per turn x turns
    return dout, davg, rho, length

def inductance(w, s, din, n):
    dout, davg, rho, _ = geometry(w, s, din, n)
    return MU0 * n**2 * davg * 1.07/2 * (np.log(2.29/rho) + 0.19*rho**2)

def pi_model(w, s, din, n, f):
    dout, davg, rho, l = geometry(w, s, din, n)
    Ls = inductance(w, s, din, n)
    delta = 1/np.sqrt(np.pi*f*MU0*SIG)
    teff = delta*(1 - np.exp(-T_TM2/delta))
    Rs = K_AC * K_LEAD * l/(SIG*w*teff)
    A = l*w
    Cox = EPS0*EPS_OX*A/(2*T_OX); Csi = C_SUB_A*A/2; Rsi = 2/(G_SUB_A*A)
    return dict(Ls=Ls, Rs=Rs, Rdc=K_LEAD*l/(SIG*w*T_TM2), Cox=Cox, Csi=Csi, Rsi=Rsi, dout=dout)

def q_factor(w, s, din, n, f):
    """Single-ended Q (port 2 grounded), Yue-Wong."""
    m = pi_model(w, s, din, n, f); wo = 2*np.pi*f
    Ls, Rs, Cox, Csi, Rsi = m['Ls'], m['Rs'], m['Cox'], m['Csi'], m['Rsi']
    Rp = 1/(wo**2*Cox**2*Rsi) + Rsi*(Cox + Csi)**2/Cox**2
    Cp = Cox*(1 + wo**2*(Cox + Csi)*Csi*Rsi**2)/(1 + wo**2*(Cox + Csi)**2*Rsi**2)
    q = wo*Ls/Rs * Rp/(Rp + ((wo*Ls/Rs)**2 + 1)*Rs) * (1 - Rs**2*Cp/Ls - wo**2*Ls*Cp)
    srf = 1/(2*np.pi*np.sqrt(Ls*Cp))
    return q, srf, m

if __name__ == "__main__":
    # calibration against the PCell defaults
    print("inductor2 default (w2 s2.1 d15.48 n1): L = %.1f pH  (PCell: 33.3 pH)" % (inductance(2e-6,2.1e-6,15.48e-6,1)*1e12))
    print("inductor3 default (w2 s2.1 d25.84 n2): L = %.1f pH  (PCell: 221.5 pH)" % (inductance(2e-6,2.1e-6,25.84e-6,2)*1e12))
    print("Rdc default inductor2: %.0f mOhm (PCell: 577.7)" % (pi_model(2e-6,2.1e-6,15.48e-6,1,1e3)['Rdc']*1e3))
