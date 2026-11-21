#!/usr/bin/env python3
"""Exact finite-sample falsification of iid workload-share certificates under dependence.

No Monte Carlo or GPU measurements. A single latent Bernoulli Z is repeated n times,
so every observed batch has the same regime indicator. Marginal share remains p.
"""
from fractions import Fraction
from math import log, sqrt

N=10000
ALPHA=0.05
THRESHOLD=Fraction(4182118219409,29448873950865)
RADIUS=sqrt(log(2/ALPHA)/(2*N))

def verdict(x):
    if x-RADIUS>float(THRESHOLD): return "possible-oracle-win"
    if x+RADIUS<float(THRESHOLD): return "oracle-no-win"
    return "indeterminate"

def audit(p):
    # Exact probability mass over two possible *entire* observation sequences.
    outcomes=((0,Fraction(1)-p),(1,p))
    coverage=sum((prob for x,prob in outcomes
                  if abs(x-float(p))<=RADIUS),Fraction(0))
    false_win=sum((prob for x,prob in outcomes
                   if p<THRESHOLD and verdict(x)=="possible-oracle-win"),Fraction(0))
    false_no_win=sum((prob for x,prob in outcomes
                      if p>THRESHOLD and verdict(x)=="oracle-no-win"),Fraction(0))
    return coverage,false_win,false_no_win

def main():
    assert verdict(0)=="oracle-no-win" and verdict(1)=="possible-oracle-win"
    assert audit(Fraction(1,10))==(0,Fraction(1,10),0)
    assert audit(Fraction(1,5))==(0,0,Fraction(4,5))
    print("PASS exact correlated-batch counterexample")
    print("n",N,"nominal_alpha",ALPHA,"radius",format(RADIUS,'.9f'))
    print("true_share=0.10: coverage=0, false_possible_win_probability=0.10")
    print("true_share=0.20: coverage=0, false_no_win_probability=0.80")
    print("Interpretation: iid Hoeffding gate is invalid for perfectly correlated batches.")
    print("This is a mathematical falsification, not evidence about GPU workload dependence.")

if __name__=="__main__": main()
