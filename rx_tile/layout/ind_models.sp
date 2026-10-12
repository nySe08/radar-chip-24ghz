.subckt ind_lb p1 p2
* octagonal TopMetal2 spiral: w=7.0u s=2.1u d_in=68.66u turns=2  L=602.0p Q(24GHz)=14.3 (EM-cal.)  d_out=100.9u
Ls p1 mid 6.020276e-10
Rs mid p2 6.37063
Cox1 p1 s1 6.3555e-15
Rsi1 s1 0 254311.92
Csi1 s1 0 1.9661e-15
Cox2 p2 s2 6.3555e-15
Rsi2 s2 0 254311.92
Csi2 s2 0 1.9661e-15
.ends ind_lb
.subckt ind_le p1 p2
* straight TopMetal2 strip: l=47u w=10u  L=24.0p
Ls p1 mid 2.3994e-11
Rs mid p2 0.3459
Cox1 p1 0 7.624e-16
Cox2 p2 0 7.624e-16
.ends ind_le
.subckt ind_lc p1 p2
* octagonal TopMetal2 spiral: w=5.0u s=2.1u d_in=55.83u turns=2  L=441.9p Q(24GHz)=11.3 (EM-cal.)  d_out=80.0u
Ls p1 mid 4.419081e-10
Rs mid p2 5.95304
Cox1 p1 s1 3.6382e-15
Rsi1 s1 0 444246.57
Csi1 s1 0 1.1255e-15
Cox2 p2 s2 3.6382e-15
Rsi2 s2 0 444246.57
Csi2 s2 0 1.1255e-15
.ends ind_lc
