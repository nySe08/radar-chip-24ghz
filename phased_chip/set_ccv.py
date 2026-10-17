"""set_ccv.py - set the VCO varactor coupling-cap size (square, um) in a simulation copy of the LO-core netlist."""
import re, sys
def set_ccv(w, src="blocks/vco_locore_post.sp", out="blocks/vco_locore_post.sp"):
    s = open(src).read()
    s = re.sub(r"^(XCvco_cv[12] \S+ \S+ \S+ cap_rfcmim) w=\S+ l=\S+", rf"\1 w={w}u l={w}u", s, flags=re.M)
    open(out, "w").write(s)
if __name__ == "__main__": set_ccv(sys.argv[1])
