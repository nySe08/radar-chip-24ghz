"""Helpers to use IHP SG13G2 PCells from Python.

Works in two ways:
  - inside KLayout (klayout -b -r script.py): uses KLayout's built-in pya, PDK PCell library from the container
  - plain python with the 'klayout' pip module: loads the PCell library from the PDK source tree
Set PDK_ROOT if the PDK is not in /foss/pdks.
"""
import sys, os, io, contextlib
PDK = os.path.join(os.environ.get("PDK_ROOT", "/foss/pdks"), "ihp-sg13g2", "libs.tech", "klayout", "python")
for p in (PDK, os.path.join(PDK, "pycell4klayout-api", "source", "python"),
          "/home/claude/pcapi/source/python", "/home/claude",                       # (generator author's sandbox)
          "/home/claude/pdkdev/ihp-sg13g2/libs.tech/klayout/python"):
    if os.path.isdir(p) and p not in sys.path: sys.path.insert(0, p)
try:
    import pya                                   # running inside KLayout
except ImportError:
    import klayout.db as pya                     # plain python + klayout pip module
    sys.modules["pya"] = pya
LIB = pya.Library.library_by_name("SG13_dev", "sg13g2")
if LIB is None:
    with contextlib.redirect_stdout(io.StringIO()):
        import sg13g2_pycell_lib
    LIB = pya.Library.library_by_name("SG13_dev", "sg13g2")

# GDS layer numbers (from sg13g2.lyp)
L = dict(Activ=(1,0), GatPoly=(5,0), Cont=(6,0), Metal1=(8,0), Via1=(19,0), Metal2=(10,0), Via2=(29,0),
         Metal3=(30,0), Via3=(49,0), Metal4=(50,0), Via4=(66,0), Metal5=(67,0), TopVia1=(125,0),
         TopMetal1=(126,0), TopVia2=(133,0), TopMetal2=(134,0), TEXT=(63,0))

def pcell(ly, name, **params):
    return ly.add_pcell_variant(LIB, LIB.layout().pcell_id(name), params)
