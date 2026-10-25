#!/usr/bin/env python3
"""Exact class-weighted V296 bank admission law; synthetic model, not GPU data.

The same greedy issue trace is predicted for V296 and serial one-hot at equal
resources and clock. Each slot is valid with p; bank A follows a class-weighted
categorical distribution. B=A with probability rho, otherwise B is drawn
independently from the same distribution. Requests are independent across slots.
"""
import argparse
import itertools
import json
import math
import random
from collections import defaultdict
from fractions import Fraction


def probability(value):
    if isinstance(value, bool):
        raise ValueError('boolean probability')
    try:
        f = Fraction(str(value))
    except (TypeError, ValueError, ZeroDivisionError) as e:
        raise ValueError('invalid probability') from e
    if not 0 <= f <= 1:
        raise ValueError('probability outside [0,1]')
    return f


def exact_grouped(groups, slots=4, ports=2, p='0.8', rho='0.2'):
    """groups = [(bank_count, probability_per_bank), ...]."""
    if isinstance(slots, bool) or isinstance(ports, bool) or not isinstance(slots, int) or not isinstance(ports, int) or not 1 <= slots <= 12 or not 1 <= ports <= 4:
        raise ValueError('invalid slots/ports')
    if not groups or len(groups) > 8:
        raise ValueError('invalid classes')
    classes = []
    for n, w in groups:
        if isinstance(n, bool) or not isinstance(n, int) or not 1 <= n <= 64:
            raise ValueError('invalid class bank count')
        classes.append((n, probability(w)))
    if sum((n*w for n, w in classes), Fraction(0)) != 1:
        raise ValueError('per-bank probabilities must sum to one')
    p, rho = probability(p), probability(rho)
    width = ports+1
    initial = tuple(x for n, _ in classes for x in [n]+[0]*ports)
    states = {initial: Fraction(1)}
    by_slot = []
    for _ in range(slots):
        nxt = defaultdict(Fraction)
        admitted = Fraction(0)
        for state, mass in states.items():
            moves = defaultdict(Fraction)
            # Same physical bank: consumes two ports, including in rho branch.
            for c, (_, w) in enumerate(classes):
                for l in range(ports-1):
                    i = c*width+l
                    if not state[i]:
                        continue
                    t = list(state)
                    t[i] -= 1
                    t[i+2] += 1
                    moves[tuple(t)] += state[i]*(rho*w+(1-rho)*w*w)
            # Distinct banks: unordered category pairs, both ordered draws.
            categories = [(c, l, state[c*width+l], w)
                          for c, (_, w) in enumerate(classes)
                          for l in range(ports)]
            for i, (c, l, count, w) in enumerate(categories):
                if not count:
                    continue
                for j in range(i, len(categories)):
                    d, m, other_count, v = categories[j]
                    ways = count*(count-1) if i == j else 2*count*other_count
                    if not ways:
                        continue
                    t = list(state)
                    a, b = c*width+l, d*width+m
                    t[a] -= 1
                    t[b] -= 1
                    t[a+1] += 1
                    t[b+1] += 1
                    moves[tuple(t)] += (1-rho)*ways*w*v
            compatibility = sum(moves.values(), Fraction(0))
            u = sum((state[c*width+l]*w for c, (_, w) in enumerate(classes) for l in range(ports)), Fraction(0))
            d = sum((state[c*width+l]*w for c, (_, w) in enumerate(classes) for l in range(ports-1)), Fraction(0))
            last = sum((state[c*width+ports-1]*w*w for c, (_, w) in enumerate(classes)), Fraction(0))
            closed_form = rho*d+(1-rho)*(u*u-last)
            if compatibility != closed_form or not 0 <= compatibility <= 1:
                raise AssertionError('weighted compatibility identity failed')
            admitted += mass*p*compatibility
            nxt[state] += mass*(1-p*compatibility)
            for t, weight in moves.items():
                nxt[t] += mass*p*weight
        if len(nxt) > 50000:
            raise ValueError('exact grouped state budget exceeded')
        if sum(nxt.values(), Fraction(0)) != 1:
            raise AssertionError('lost probability mass')
        by_slot.append(admitted)
        states = nxt
    q = sum(by_slot, Fraction(0))
    return {'q': float(q), 'q_exact': str(q), 'by_slot': [float(x) for x in by_slot],
            'terminal_states': len(states), 'bank_count': sum(n for n,_ in classes),
            'evidence': 'EXACT_IID_CLASS_WEIGHTED_SYNTHETIC_NOT_GPU_MEASUREMENT'}


def independent_oracle(requests, banks, ports):
    used = [0]*banks
    total = 0
    for valid, a, b in requests:
        if not valid:
            continue
        if a == b:
            ok = used[a]+2 <= ports
        else:
            ok = used[a] < ports and used[b] < ports
        if ok:
            used[a] += 1
            used[b] += 1
            total += 1
    return total


def exhaustive_oracle(weights, slots, ports, p, rho):
    """Enumerates concrete per-bank traces, independent of class histogram DP."""
    p, rho = probability(p), probability(rho)
    weights = [probability(w) for w in weights]
    if sum(weights) != 1:
        raise ValueError('invalid weights')
    choices = [(a, b, weights[a]*(rho if a==b else 0)+(1-rho)*weights[a]*weights[b])
               for a in range(len(weights)) for b in range(len(weights))]
    total = Fraction(0)
    for valid_bits in itertools.product((0,1), repeat=slots):
        pv = math.prod((p if v else 1-p for v in valid_bits), start=Fraction(1))
        if not pv:
            continue
        for picks in itertools.product(choices, repeat=slots):
            w = pv*math.prod((x[2] for x in picks), start=Fraction(1))
            if w:
                total += w*independent_oracle([(v,x[0],x[1]) for v,x in zip(valid_bits,picks)],len(weights),ports)
    return total


def monte_carlo(weights, slots, ports, p, rho, n, seed):
    rng = random.Random(seed)
    cdf = []
    t = 0.0
    for w in weights:
        t += float(w)
        cdf.append(t)
    def bank():
        z = rng.random()
        for i, upper in enumerate(cdf):
            if z < upper:
                return i
        return len(cdf)-1
    total = 0
    for _ in range(n):
        requests = []
        for _ in range(slots):
            a = bank()
            b = a if rng.random() < rho else bank()
            requests.append((rng.random()<p,a,b))
        total += independent_oracle(requests,len(weights),ports)
    return total/n


def experiment():
    # All are declared synthetic distributions; no prospective trace opened.
    b,s,ports,p,rho = 16,4,2,'0.8','0.2'
    uniform = exact_grouped([(16,'0.0625')],s,ports,p,rho)
    cases = {}
    for hot in ('0.0625','0.125','0.25','0.5','0.75'):
        hot_f = Fraction(hot)
        cold = (1-hot_f)/15
        r = exact_grouped([(1,hot_f),(15,cold)],s,ports,p,rho)
        cases[hot] = {'q_exact':r['q_exact'], 'q':r['q'],
                      'relative_uniform_prediction_error':(uniform['q']/r['q']-1) if r['q'] else None,
                      'terminal_states':r['terminal_states']}
    # Independent synthetic samples, not GPU holdouts.
    validations = []
    for hot, seed in [('0.25',541),('0.5',542),('0.75',543)]:
        h = Fraction(hot)
        weights = [h]+[(1-h)/15]*15
        actual = monte_carlo(weights,s,ports,float(p),float(rho),50000,seed)
        expected = cases[hot]['q']
        tolerance = s*math.sqrt(math.log(2000)/(2*50000))
        if abs(actual-expected) >= tolerance:
            raise AssertionError(('Monte Carlo mismatch',hot,actual,expected,tolerance))
        validations.append({'hot_bank_mass':hot,'seed':seed,'cycles':50000,
                            'exact_prediction':expected,'independent_sample':actual,
                            'abs_error':abs(actual-expected),'hoeffding_99p9_bound':tolerance})
    return {'uniform_q':uniform['q'], 'nominal':{'banks':b,'slots':s,'ports':ports,'p':p,'rho':rho},
            'hotspot_sweep':cases, 'independent_synthetic_validations':validations,
            'claim_limit':'No real GPU traces, equal-resource tile throughput or power measured; V296 and serial admissions identical.'}


def self_test():
    for groups, slots, ports, p, rho in [
        ([(1,'0.5'),(1,'0.5')],2,1,'0.75','0.25'),
        ([(1,'0.75'),(2,'0.125')],2,2,'0.5','0.5'),
        ([(2,'0.5')],3,3,'0.8','1'),
        ([(1,'1')],3,2,'1','0')]:
        expected = exact_grouped(groups,slots,ports,p,rho)
        weights = [Fraction(w) for n,w in groups for _ in range(n)]
        direct = exhaustive_oracle(weights,slots,ports,p,rho)
        assert Fraction(expected['q_exact']) == direct, (groups,expected,direct)
    from importlib.util import spec_from_file_location, module_from_spec
    from pathlib import Path
    path = Path(__file__).with_name('exact_bank_admission_law.py')
    if path.exists():
        spec = spec_from_file_location('v296_uniform',path)
        mod = module_from_spec(spec)
        spec.loader.exec_module(mod)
        assert exact_grouped([(16,'0.0625')],4,2,'0.8','0.2')['q_exact'] == mod.exact_law(16,4,2,'0.8','0.2')['exact_fraction']
    for invalid in [([(2,'0.2')],2,2,'0.8','0.2'), ([(True,'1')],2,2,'0.8','0.2'),
                    ([(1,'nan')],2,2,'0.8','0.2'), ([(1,'1')],0,2,'0.8','0.2')]:
        try:
            exact_grouped(*invalid)
        except ValueError:
            pass
        else:
            raise AssertionError(('invalid accepted',invalid))
    result = experiment()
    print('V296_BANK_SKEW_LAW_SELFTEST_PASS')
    print(json.dumps(result,indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--self-test',action='store_true')
    args = parser.parse_args()
    if args.self_test:
        self_test()
    else:
        print(json.dumps(experiment(),indent=2))
