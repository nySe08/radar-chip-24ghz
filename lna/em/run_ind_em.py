########################################################################
# EM verification of a TopMetal2 spiral inductor with IHP's gds2openEMS workflow.
# Based on run_inductor_diffport.py from github.com/VolkerMuehlhaus/openems_ihp_sg13g2
# (GPL-3.0). One differential port between the two inductor terminals.
#
# Needs:  ind_lb.gds   (flattened, with a port box on layer 201 between the two terminals)
#         SG13G2.xml   (stackup file from the gds2openEMS workflow folder)
#         pip install gds2openEMS   (if not already installed)
# Run:    python3 run_ind_em.py ind_lb.gds 605 22.3          -> 3-D preview (check the port!)
#         python3 run_ind_em.py ind_lb.gds 605 22.3 --run    -> full simulation (about 30-60 min)
#         (arguments: GDS file, model L in pH, model Q at 24 GHz - only used for the comparison)
########################################################################
import os, sys
from gds2openEMS import *
from openEMS import openEMS
import numpy as np
import matplotlib
import matplotlib.pyplot as plt

settings = {}
settings['preview_only'] = '--run' not in sys.argv

args = [a for a in sys.argv[1:] if not a.startswith("--")]
gds_filename = args[0] if args else "ind_lb.gds"
NAME = os.path.splitext(os.path.basename(gds_filename))[0]
XML_filename = "SG13G2.xml"
PORT_METAL   = "TopMetal2"     # metal layer of the two terminals the port connects
PORT_DIR     = "x"             # direction of the port: from one terminal to the other

# model prediction for comparison (from indmodel.py / lna_ind.spice)
MODEL = dict(L_pH=float(args[1]) if len(args) > 1 else 0.0, Q=float(args[2]) if len(args) > 2 else 0.0)
F_TARGET = 24.125e9

settings['preprocess_gds'] = False
settings['merge_polygon_size'] = 1.0
script_path = utilities.get_script_path(__file__)
model_basename = NAME
sim_path = utilities.create_sim_path(script_path, model_basename)
os.chdir(os.path.dirname(os.path.abspath(__file__)))

settings['unit']   = 1e-6
settings['margin'] = 200
settings['fstart']  = 0
settings['fstop']   = 40e9
settings['numfreq'] = 401
settings['refined_cellsize'] = 1.0     # 1 um: needed for accurate R and Q (IHP measured-vs-simulated study)
settings['Boundaries'] = ['PEC', 'PEC', 'PEC', 'PEC', 'PEC', 'PEC']
settings['cells_per_wavelength'] = 20
settings['energy_limit'] = -60          # -60 dB: needed for accurate R (IHP study)

simulation_ports = simulation_setup.all_simulation_ports()
simulation_ports.add_port(simulation_setup.simulation_port(portnumber=1, voltage=1, port_Z0=50,
                          source_layernum=201, target_layername=PORT_METAL, direction=PORT_DIR))

materials_list, dielectrics_list, metals_list = stackup_reader.read_substrate(XML_filename)
layernumbers = metals_list.getlayernumbers()
layernumbers.extend(simulation_ports.portlayers)
allpolygons = gds_reader.read_gds(gds_filename, layernumbers, purposelist=[0], metals_list=metals_list,
                                  preprocess=settings['preprocess_gds'], merge_polygon_size=settings['merge_polygon_size'])

FDTD = openEMS(EndCriteria=np.exp(settings['energy_limit']/10 * np.log(10)))
FDTD.SetGaussExcite((settings['fstart']+settings['fstop'])/2, (settings['fstop']-settings['fstart'])/2)
FDTD.SetBoundaryCond(settings['Boundaries'])
settings.update(simulation_ports=simulation_ports, materials_list=materials_list, dielectrics_list=dielectrics_list,
                metals_list=metals_list, layernumbers=layernumbers, allpolygons=allpolygons,
                sim_path=sim_path, model_basename=model_basename, excite_portnumbers=[1])
simulation_setup.setupSimulation(FDTD=FDTD, settings=settings)
simulation_setup.runSimulation(FDTD=FDTD, settings=settings)

if not settings['preview_only']:
    f = np.linspace(settings['fstart'], settings['fstop'], settings['numfreq'])
    s11 = utilities.calculate_Sij(1, 1, f, sim_path, simulation_ports)
    Z0 = simulation_ports.get_reference_impedance()
    utilities.write_snp(np.array([s11]), f, os.path.join(sim_path, model_basename + '.s1p'), z0=Z0)
    np.seterr(divide='ignore', invalid='ignore')
    z = Z0 * (1 + s11) / (1 - s11)
    L, R, Q = z.imag / (2*np.pi*f), z.real, z.imag / z.real
    i = np.argmin(abs(f - F_TARGET))
    print(f"\n{NAME} at {f[i]/1e9:.2f} GHz:   EM  L = {L[i]*1e12:6.1f} pH   R = {R[i]:5.2f} ohm   Q = {Q[i]:5.1f}")
    print(f"                    model L = {MODEL['L_pH']:6.1f} pH                 Q = {MODEL['Q']:5.1f}")
    if MODEL['L_pH'] and MODEL['Q']:
        print(f"Difference: L {100*(L[i]*1e12/MODEL['L_pH']-1):+.1f} %,  Q {100*(Q[i]/MODEL['Q']-1):+.1f} %")
    sel = f > 0.5e9
    fig, ax = plt.subplots(1, 2, figsize=(11, 4))
    ax[0].plot(f[sel]/1e9, L[sel]*1e12); ax[0].axhline(MODEL['L_pH'], ls='--', c='r', label='model')
    ax[0].set_xlabel('Frequency [GHz]'); ax[0].set_ylabel('L [pH]'); ax[0].set_ylim(0, 2*max(MODEL['L_pH'], L[i]*1e12)); ax[0].grid(alpha=.3); ax[0].legend()
    ax[1].plot(f[sel]/1e9, Q[sel]); ax[1].axhline(MODEL['Q'], ls='--', c='r', label='model at 24 GHz')
    ax[1].set_xlabel('Frequency [GHz]'); ax[1].set_ylabel('Q'); ax[1].set_ylim(0, 1.5*max(MODEL['Q'], Q[i])); ax[1].grid(alpha=.3); ax[1].legend()
    for a in ax: a.axvline(F_TARGET/1e9, c='g', ls=':')
    plt.tight_layout(); plt.savefig(NAME + '_em.png', dpi=150); print('Saved', NAME + '_em.png')
