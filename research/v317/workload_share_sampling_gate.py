#!/usr/bin/env python3
"""Predeclared statistical gate for workload-share transfer, V317 synthetic oracle only."""
from fractions import Fraction as F
from math import log, ceil, sqrt
P={3:153,4:212,5:61,6:4}
G={1:2,2:404,3:3511,4:6536,5:4139,6:1060,7:112,8:4}
def falling(n,k):
    x=1
    for j in range(k): x*=n-j
    return x
def poly(b,c): return F(sum(v*falling(b,k) for k,v in c.items()),b**8)
def margin(b,d): return poly(b,P)-d*poly(b,G)
def threshold(a,b,d):
    ma,mb=margin(a,d),margin(b,d)
    assert ma>0>mb
    return -mb/(ma-mb)
def hoeffding_radius(n,alpha):
    assert n>0 and 0<alpha<1
    return sqrt(log(2/alpha)/(2*n))
def classify(w_hat,n,alpha,t):
    r=hoeffding_radius(n,alpha)
    if w_hat-r>float(t): return "possible-oracle-win"
    if w_hat+r<float(t): return "oracle-no-win"
    return "indeterminate"
def required_n(distance,alpha):
    assert distance>0
    return ceil(log(2/alpha)/(2*distance**2))
if __name__=="__main__":
    t=threshold(4,64,F(1,200))
    assert t==F(4182118219409,29448873950865)
    assert classify(.20,10000,.05,t)=="possible-oracle-win"
    assert classify(.10,10000,.05,t)=="oracle-no-win"
    assert classify(float(t),10000,.05,t)=="indeterminate"
    print("PASS: exact boundary, positive/negative/indeterminate checks")
    print("threshold",float(t))
    for gap in (.01,.02,.05):
        print("gap",gap,"iid_batch_samples_95pct",required_n(gap,.05))
    print("WARNING: iid Bernoulli batch assumptions; autocorrelation invalidates bound")
