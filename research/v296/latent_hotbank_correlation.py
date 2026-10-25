#!/usr/bin/env python3
"""Exact latent-hot-bank V296/serial shared-admission law.

Prospective protocol: LATENT_HOTBANK_CORRELATION_PREREG_20261025.md.
This is a synthetic cross-slot dependence falsifier, NOT GPU IPC evidence.
"""
import argparse
import itertools
import json
from collections import defaultdict
from fractions import Fraction


def prob(x):
    if isinstance(x, bool):
        raise ValueError('invalid probability')
    try:
        v = Fraction(str(x))
    except (ValueError, TypeError, ZeroDivisionError) as exc:
        raise ValueError('invalid probability') from exc
    if not 0 <= v <= 1:
        raise ValueError('probability outside [0,1]')
    return v


def exact(banks=16, slots=4, ports=2, p='0.8', rho='0.2', lam='0'):
    if any(isinstance(x, bool) or not isinstance(x, int) for x in (banks, slots, ports)):
        raise ValueError('integer resources required')
    if not (1 <= banks <= 64 and 1 <= slots <= 12 and 1 <= ports <= 4):
        raise ValueError('resource bounds')
    p, rho, lam = prob(p), prob(rho), prob(lam)
    # Condition on H=0 by permutation symmetry; h counts OTHER B-1 banks.
    initial = (0, (banks-1,) + (0,)*ports)
    states = {initial: Fraction(1)}
    admitted_by_slot = []
    a_hot = lam + (1-lam)/banks
    a_cold = (1-lam)/banks
    same = rho + (1-rho)/banks
    for _ in range(slots):
        nxt = defaultdict(Fraction)
        admitted = Fraction(0)
        for (hot, h), mass in states.items():
            transitions = defaultdict(Fraction)
            # First operand hot, or in a cold bank with occupancy i.
            first = [(True, hot, a_hot)]
            first += [(False, i, h[i]*a_cold) for i in range(ports) if h[i]]
            for first_hot, i, weight_a in first:
                if not weight_a:
                    continue
                # Second operand is the same physical bank (two reads).
                if i+2 <= ports:
                    if first_hot:
                        target = (hot+2, h)
                    else:
                        hh = list(h)
                        hh[i] -= 1
                        hh[i+2] += 1
                        target = (hot, tuple(hh))
                    transitions[target] += weight_a*same
                # Second operand is a distinct bank; each gets one read.
                if i+1 > ports:
                    continue
                if not first_hot and hot < ports:
                    hh = list(h)
                    hh[i] -= 1
                    hh[i+1] += 1
                    transitions[(hot+1, tuple(hh))] += weight_a*(1-rho)/banks
                for j in range(ports):
                    n = h[j] - (0 if first_hot or i != j else 1)
                    if n <= 0:
                        continue
                    hh = list(h)
                    if not first_hot:
                        hh[i] -= 1
                    hh[j] -= 1
                    if not first_hot:
                        hh[i+1] += 1
                    hh[j+1] += 1
                    target = (hot+1 if first_hot else hot, tuple(hh))
                    transitions[target] += weight_a*(1-rho)*n/banks
            compatible = sum(transitions.values(), Fraction(0))
            if not 0 <= compatible <= 1:
                raise AssertionError('compatibility probability')
            nxt[(hot,h)] += mass*(1-p*compatible)
            admitted += mass*p*compatible
            for target, weight in transitions.items():
                nxt[target] += mass*p*weight
        if sum(nxt.values(), Fraction(0)) != 1:
            raise AssertionError('probability conservation')
        if len(nxt) > 20000:
            raise ValueError('state explosion')
        states = nxt
        admitted_by_slot.append(admitted)
    q = sum(admitted_by_slot, Fraction(0))
    return {'banks':banks,'slots':slots,'ports':ports,'p':str(p),'rho':str(rho),
            'lambda':str(lam),'q_fraction':str(q),'q':float(q),
            'per_slot':[float(x) for x in admitted_by_slot],
            'states':len(states),
            'marginal_first_bank':'uniform',
            'marginal_same_bank_probability':str(rho+(1-rho)/banks),
            'both_architectures_same_clock_q':True,
            'evidence':'EXACT_SYNTHETIC_DEPENDENCE_MODEL_NOT_GPU'}


def direct_oracle(requests, banks, ports):
    used = [0]*banks
    count = 0
    for valid, a, b in requests:
        if not valid:
            continue
        if used[a]+(2 if a==b else 1) > ports:
            continue
        if a != b and used[b] >= ports:
            continue
        used[a] += 1
        used[b] += 1
        count += 1
    return count


def independent_enumeration(banks, slots, ports, p, rho, lam):
    p,rho,lam = prob(p),prob(rho),prob(lam)
    total = Fraction(0)
    for hotspot in range(banks):
        options = [(False,0,0,1-p)]
        for a in range(banks):
            wa = (lam if a==hotspot else 0) + (1-lam)/banks
            for b in range(banks):
                wb = (rho if a==b else 0) + (1-rho)/banks
                options.append((True,a,b,p*wa*wb))
        if sum((x[3] for x in options),Fraction(0)) != 1:
            raise AssertionError('oracle normalization')
        for seq in itertools.product(options, repeat=slots):
            weight = Fraction(1,banks)
            for item in seq:
                weight *= item[3]
            if weight:
                total += weight*direct_oracle([x[:3] for x in seq],banks,ports)
    return total


def self_test():
    # Independent full per-bank brute force, not a second histogram DP.
    for args in [(2,3,2,'0.75','0.3','0.65'),
                 (3,2,2,'0.5','0.25','0.4'),
                 (2,2,1,'1','0','1')]:
        got = exact(*args)
        assert Fraction(got['q_fraction']) == independent_enumeration(*args), args
    nominal = exact()
    assert Fraction(nominal['q_fraction']) == Fraction(957548877,320000000)
    for lam in ('0','0.25','0.5','1'):
        row = exact(lam=lam)
        assert row['marginal_first_bank'] == 'uniform'
        assert row['marginal_same_bank_probability'] == '1/4'
    for bad in [(0,4,2,.8,.2,0),(16,4,0,.8,.2,0),
                (16,4,2,1.1,.2,0),(16,4,2,.8,.2,'nan'),
                (16,4,2,.8,.2,True)]:
        try: exact(*bad)
        except ValueError: pass
        else: raise AssertionError('invalid inputs accepted')
    print('LATENT_HOTBANK_EXACT_INDEPENDENT_ORACLE_PASS')


def evaluate():
    rows = {lam: exact(lam=lam) for lam in ('0','0.25','0.5','1')}
    q = {k: v['q'] for k,v in rows.items()}
    assert q['0'] > q['0.25'] > q['0.5'] > q['1']
    assert q['0']-q['1'] > 1
    assert 2.5 < q['0.5'] < 2.8
    return {'protocol':'LATENT_HOTBANK_CORRELATION_PREREG_20261025.md',
            'result':'IID_SCALAR_LAW_FAILS_OUTSIDE_INDEPENDENCE_ASSUMPTION',
            'same_clock_v296_vs_serial_gain':0,
            'q_drop_lambda_0_to_1':q['0']-q['1'],
            'relative_q_drop':1-q['1']/q['0'],
            'rows':rows,'real_gpu_holdouts':'SEALED',
            'physical_gate':'INTEGRATED_BOTH_INFEASIBLE'}


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--self-test',action='store_true')
    parser.add_argument('--evaluate',action='store_true')
    args=parser.parse_args()
    if args.self_test: self_test()
    if args.evaluate: print(json.dumps(evaluate(),indent=2,sort_keys=True))
    if not args.self_test and not args.evaluate: parser.error('choose --self-test or --evaluate')


if __name__ == '__main__':
    main()
