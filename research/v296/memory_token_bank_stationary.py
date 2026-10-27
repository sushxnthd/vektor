#!/usr/bin/env python3
"""Exact finite-bandwidth bank-admission Markov law for existing V296 arbitration.

SYNTHETIC ONLY. Identical arbitration decisions imply identical V296/serial
admissions/cycle. No GPU speedup, RF macro, physical timing or power claim.
Frozen protocol: MEMORY_TOKEN_BANK_STATIONARY_LAW_PREREG_20261028.md.
"""
import argparse
import itertools
import json
import math
import random
from collections import defaultdict
from pathlib import Path

REGIMES = (
    ("sparse_low_bw", 0.25, 0.0, 1),
    ("uniform_low_bw", 0.75, 0.0, 1),
    ("correlated_low_bw", 0.75, 0.5, 1),
    ("hot_low_bw", 0.95, 0.8, 1),
    ("uniform_high_bw", 0.75, 0.0, 3),
    ("hot_high_bw", 0.95, 0.8, 3),
)
PROSPECTIVE_SEEDS = (812731, 812737)
CYCLES, BURN = 100000, 10000
TOL = 0.035


def validate(B, S, P, p, rho, refill, capacity):
    for name, value in (("banks", B), ("slots", S), ("ports", P),
                        ("refill", refill), ("capacity", capacity)):
        if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
            raise ValueError("invalid " + name)
    if B > 64 or S > 12 or P > 4 or capacity > 16 or refill > capacity:
        raise ValueError("resource bounds exceeded")
    if any(isinstance(v, bool) or not isinstance(v, (int, float)) or
           not math.isfinite(v) or not 0 <= v <= 1 for v in (p, rho)):
        raise ValueError("invalid probabilities")
    if not 0 < p < 1:
        raise ValueError("require 0<p<1 for unique stationary law")


def _admissible_transitions(h, B, P, rho):
    """Probability of a randomly drawn pair and updated bank-load histogram."""
    trans = defaultdict(float)
    for i in range(P - 1):
        if h[i]:
            weight = h[i] * (rho / B + (1-rho) / (B*B))
            nxt = list(h)
            nxt[i] -= 1
            nxt[i+2] += 1
            trans[tuple(nxt)] += weight
    for i in range(P):
        for j in range(i, P):
            ways = h[i] * (h[i]-1) if i == j else 2 * h[i] * h[j]
            if ways <= 0:
                continue
            nxt = list(h)
            nxt[i] -= 1
            nxt[i+1] += 1
            nxt[j] -= 1
            nxt[j+1] += 1
            trans[tuple(nxt)] += (1-rho) * ways / (B*B)
    if sum(trans.values()) > 1+1e-12:
        raise AssertionError("invalid compatibility probability")
    return trans


def conditional_kernel(B, S, P, p, rho, available):
    """Exact probability Q_available(k) of k admitted waves in one cycle."""
    if isinstance(available, bool) or not isinstance(available, int) or available < 0:
        raise ValueError("invalid available tokens")
    states = {((B,) + (0,)*P, 0): 1.0}
    for _ in range(S):
        nxt = defaultdict(float)
        for (hist, accepted), mass in states.items():
            if accepted >= available:
                nxt[(hist, accepted)] += mass
                continue
            trans = _admissible_transitions(hist, B, P, rho)
            compatible = sum(trans.values())
            nxt[(hist, accepted)] += mass * (1-p*compatible)
            for h2, weight in trans.items():
                nxt[(h2, accepted+1)] += mass*p*weight
        states = nxt
        if len(states) > 100000:
            raise ValueError("histogram DP state budget exceeded")
        if abs(sum(states.values())-1) > 1e-10:
            raise AssertionError("cycle probability mass not conserved")
    out = [0.] * (min(S, available)+1)
    for (_, k), mass in states.items():
        out[k] += mass
    if abs(sum(out)-1) > 1e-10 or min(out) < -1e-12:
        raise AssertionError("invalid conditional distribution")
    return out


def _linear_solve(A, b):
    """Independent small dense Gaussian elimination with pivoting."""
    n = len(b)
    M = [list(row)+[rhs] for row,rhs in zip(A,b)]
    for col in range(n):
        pivot = max(range(col,n), key=lambda i: abs(M[i][col]))
        if abs(M[pivot][col]) < 1e-12:
            raise ValueError("singular stationary system")
        M[col],M[pivot] = M[pivot],M[col]
        factor = M[col][col]
        for j in range(col,n+1):
            M[col][j] /= factor
        for i in range(n):
            if i == col:
                continue
            factor = M[i][col]
            for j in range(col,n+1):
                M[i][j] -= factor*M[col][j]
    return [M[i][n] for i in range(n)]


def exact(B=16, S=4, P=2, p=0.75, rho=0.0, refill=1, capacity=4):
    validate(B,S,P,p,rho,refill,capacity)
    kernels = {t: conditional_kernel(B,S,P,p,rho,t)
               for t in {min(capacity,x+refill) for x in range(capacity+1)}}
    transition = [[0.]*(capacity+1) for _ in range(capacity+1)]
    reward = [0.] * (capacity+1)
    for x in range(capacity+1):
        t = min(capacity,x+refill)
        for k,prob in enumerate(kernels[t]):
            transition[x][t-k] += prob
            reward[x] += k*prob
        if abs(sum(transition[x])-1)>1e-10:
            raise AssertionError("Markov row not stochastic")
    n=capacity+1
    A=[[transition[j][i]-(1. if i==j else 0.) for j in range(n)]
       for i in range(n-1)]
    A.append([1.]*n)
    pi=_linear_solve(A,[0.]*(n-1)+[1.])
    if min(pi) < -1e-10 or abs(sum(pi)-1)>1e-10:
        raise AssertionError("invalid stationary distribution")
    residual=max(abs(sum(pi[x]*transition[x][y] for x in range(n))-pi[y])
                 for y in range(n))
    if residual>1e-10:
        raise AssertionError("stationary residual")
    q=sum(pi[x]*reward[x] for x in range(n))
    if not -1e-10<=q<=min(S*p,refill)+1e-10:
        raise AssertionError("conservation upper bound")
    return {"q_admitted_per_cycle":q,
            "stationary_post_cycle_token_probabilities":pi,
            "stationary_residual":residual,
            "bandwidth_upper_bound":min(S*p,refill),
            "identical_clock_v296_serial_ratio":1.0,
            "kernel":{str(k):v for k,v in kernels.items()}}


def brute_conditional(B,S,P,p,rho,available):
    """Independent direct enumeration of bank-indexed requests, no histograms."""
    opts=[(False,0,0,1-p)]
    for a in range(B):
        for b in range(B):
            opts.append((True,a,b,p/B*(rho*(a==b)+(1-rho)/B)))
    out=[0.]*(min(S,available)+1)
    for sequence in itertools.product(opts,repeat=S):
        mass=math.prod(x[3] for x in sequence)
        used=[0]*B
        admitted=0
        for valid,a,b,_ in sequence:
            if not valid or admitted>=available:
                continue
            if used[a]+1+(a==b)>P or (a!=b and used[b]+1>P):
                continue
            used[a]+=1
            used[b]+=1
            admitted+=1
        out[admitted]+=mass
    return out


def simulate(B,S,P,p,rho,refill,capacity,seed,cycles=CYCLES,burn=BURN):
    """Independent bank-index Monte Carlo, not DP or a fitted approximation."""
    rng=random.Random(seed)
    tokens=0
    total=0
    if not 0<=burn<cycles:
        raise ValueError("invalid burn-in")
    for cycle in range(cycles):
        tokens=min(capacity,tokens+refill)
        used=[0]*B
        admitted=0
        for _ in range(S):
            if rng.random()>=p:
                continue
            a=rng.randrange(B)
            b=a if rng.random()<rho else rng.randrange(B)
            if tokens==0 or used[a]+1+(a==b)>P or (a!=b and used[b]+1>P):
                continue
            used[a]+=1
            used[b]+=1
            tokens-=1
            admitted+=1
        if max(used)>P:
            raise AssertionError("bank-port oversubscription")
        if cycle>=burn:
            total+=admitted
    return total/(cycles-burn)


def self_test():
    for rho in (0.,0.3,1.):
        for tokens in (0,1,2):
            a=conditional_kernel(2,2,2,0.7,rho,tokens)
            b=brute_conditional(2,2,2,0.7,rho,tokens)
            assert max(abs(x-y) for x,y in zip(a,b))<1e-12,(rho,tokens,a,b)
    for p,rho,r in ((0.25,0.,1),(0.75,0.5,1),(0.95,0.8,3)):
        row=exact(p=p,rho=rho,refill=r)
        assert row['stationary_residual']<1e-10
        assert row['q_admitted_per_cycle']<=min(4*p,r)+1e-10
    for invalid in ((0,4,2,.7,0,1,4),(16,4,0,.7,0,1,4),
                    (16,4,2,1.1,0,1,4),(16,4,2,.7,float('nan'),1,4),
                    (16,4,2,.7,0,5,4),(16,4,2,.7,0,1,True)):
        try: exact(*invalid)
        except ValueError: pass
        else: raise AssertionError("invalid input accepted")
    print('V296_MEMORY_TOKEN_STATIONARY_INDEPENDENT_ORACLE_PASS')


def evaluate(output):
    self_test()
    rows=[]
    for name,p,rho,r in REGIMES:
        pred=exact(p=p,rho=rho,refill=r)
        for seed in PROSPECTIVE_SEEDS:
            observed=simulate(16,4,2,p,rho,r,4,seed)
            err=abs(observed-pred['q_admitted_per_cycle'])
            rows.append({"regime":name,"p":p,"rho":rho,"refill":r,
                         "capacity":4,"seed":seed,"cycles":CYCLES,
                         "burn":BURN,"predicted":pred['q_admitted_per_cycle'],
                         "observed":observed,"absolute_error":err,
                         "frozen_tolerance":TOL,"pass":err<=TOL,
                         "stationary_residual":pred['stationary_residual'],
                         "bandwidth_upper_bound":pred['bandwidth_upper_bound']})
    result={"protocol":"MEMORY_TOKEN_BANK_STATIONARY_LAW_PREREG_20261028.md",
            "evidence":"SYNTHETIC_PROSPECTIVE_EXACT_MARKOV_VS_DIRECT_MONTE_CARLO_NOT_GPU",
            "seeds":list(PROSPECTIVE_SEEDS),"parameters_fitted":False,
            "real_gpu_holdouts":"SEALED_UNOPENED",
            "v296_vs_serial_same_clock_gain":0.0,
            "all_pass":all(row['pass'] for row in rows),"rows":rows}
    Path(output).write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps({"all_pass":result['all_pass'],
                      "regimes":[{"name":name,"predicted":next(row['predicted'] for row in rows if row['regime']==name),
                                  "max_abs_error":max(row['absolute_error'] for row in rows if row['regime']==name)}
                                 for name,*_ in REGIMES]},indent=2))
    if not result['all_pass']:
        raise AssertionError('frozen prospective law failed; result preserved')
    return result


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--self-test',action='store_true')
    ap.add_argument('--evaluate',action='store_true')
    ap.add_argument('--output',default='research/v296/MEMORY_TOKEN_BANK_STATIONARY_LAW_RESULT_20261028.json')
    args=ap.parse_args()
    if args.self_test: self_test()
    if args.evaluate: evaluate(args.output)
    if not (args.self_test or args.evaluate): ap.error('choose --self-test or --evaluate')

if __name__=='__main__':
    main()
