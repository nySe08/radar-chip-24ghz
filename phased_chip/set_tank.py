"""set_tank.py - experiment knobs for the VCO tank in a simulation copy: coil model (per side), cross-coupling cap size."""
import re
def set_tank(Ls=None, Rs=None, Cs=None, cb=None, f="blocks/vco_locore_post.sp"):
    s = open(f).read()
    if Ls: s = re.sub(r"^(LLvco[ab] \S+ \S+) \S+$", rf"\1 {Ls}", s, flags=re.M)
    if Rs: s = re.sub(r"^(RLvco[ab] \S+ \S+) \S+$", rf"\1 {Rs}", s, flags=re.M)
    if Cs: s = re.sub(r"^(CLvcop \S+ \S+) \S+$", rf"\1 {Cs}", s, flags=re.M)
    if cb: s = re.sub(r"^(XCvco_b[67] \S+ \S+ \S+ cap_rfcmim) w=\S+ l=\S+", rf"\1 w={cb}u l={cb}u", s, flags=re.M)
    open(f, "w").write(s)
