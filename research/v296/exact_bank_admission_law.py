#!/usr/bin/env python3
"""Exact finite-slot V296 bank-admission law for a declared i.i.d request model.

This is an analytical workload *model*, not measured GPU IPC or an RTL trace.
Each offered slot is valid independently with probability p. A valid request
chooses bank a uniformly; with probability rho, b=a, otherwise b is an
independent uniform bank. Each bank has P read ports. Greedy priority admits
if both operands fit (two reads when a=b). V296 and serial one-hot make
identical decisions, so this law predicts the SAME admissions/cycle for both.
"""
import argparse
import itertools
import json
import math
import random
from collections import defaultdict
from fractions import Fraction


def rational(x, name):
    if isinstance(x, bool):
        raise ValueError(name)
    try:
        f = Fraction(str(x))
    except (TypeError, ValueError, ZeroDivisionError) as e:
        raise ValueError(name) from e
    if not 0 <= f <= 1:
        raise ValueError(name)
    return f


def exact_law(banks=16, slots=4, ports=2, valid_probability='0.8', same_bank_correlation='0'):
    if any(isinstance(v, bool) or not isinstance(v, int) for v in (banks, slots, ports)):
        raise ValueError('banks, slots, ports must be integers')
    if not (1 <= banks <= 64 and 1 <= slots <= 12 and 1 <= ports <= 4):
        raise ValueError('invalid resource bounds')
    p = rational(valid_probability, 'valid_probability')
    rho = rational(same_bank_correlation, 'same_bank_correlation')
    state0 = (banks,) + (0,) * ports
    states = {state0: Fraction(1)}
    q = Fraction(0)
    per_slot = []
    for _ in range(slots):
        nxt = defaultdict(Fraction)
        accepted = Fraction(0)
        for h, mass in states.items():
            if not mass:
                continue
            transitions = defaultdict(Fraction)
            # a=b: two reads on one bank; only possible with >=2 free ports.
            for load in range(ports - 1):
                if h[load]:
                    weight = (rho * h[load] / banks
                              + (1 - rho) * h[load] / (banks * banks))
                    t = list(h)
                    t[load] -= 1
                    t[load + 2] += 1
                    transitions[tuple(t)] += weight
            # a!=b: two distinct banks, each with >=1 free port.
            for a in range(ports):
                for b in range(a, ports):
                    ways = h[a] * (h[a] - 1) if a == b else 2 * h[a] * h[b]
                    if ways <= 0:
                        continue
                    weight = (1 - rho) * ways / (banks * banks)
                    t = list(h)
                    t[a] -= 1
                    t[a + 1] += 1
                    t[b] -= 1
                    t[b + 1] += 1
                    transitions[tuple(t)] += weight
            compatible = sum(transitions.values(), Fraction(0))
            available = sum(h[:ports])
            formula = (rho * sum(h[:max(0, ports - 1)]) / banks
                       + (1 - rho) * (available * available - h[ports - 1]) / (banks * banks))
            if compatible != formula or not 0 <= compatible <= 1:
                raise AssertionError('compatibility identity failed')
            admit = p * compatible
            accepted += mass * admit
            nxt[h] += mass * (1 - admit)
            for target, prob in transitions.items():
                nxt[target] += mass * p * prob
        if len(nxt) > 20000:
            raise ValueError('state-space exceeds safe exact-DP budget')
        if sum(nxt.values(), Fraction(0)) != 1:
            raise AssertionError('probability mass lost')
        q += accepted
        per_slot.append(accepted)
        states = nxt
    return {'banks': banks, 'slots': slots, 'read_ports_per_bank': ports,
            'valid_probability': float(p), 'same_bank_correlation': float(rho),
            'expected_admissions_per_cycle': float(q),
            'per_slot_admission_probabilities': [float(x) for x in per_slot],
            'terminal_histogram_states': len(states),
            'exact_fraction': str(q),
            'evidence_tier': 'EXACT_FOR_DECLARED_IID_MODEL_NOT_MEASURED_GPU'}


def oracle(requests, banks, ports):
    used = [0] * banks
    admitted = 0
    per_slot = []
    for valid, a, b in requests:
        fits = valid and (used[a] + (2 if a == b else 1) <= ports) and (a == b or used[b] < ports)
        if fits:
            used[a] += 1
            used[b] += 1
            admitted += 1
        per_slot.append(int(fits))
    return admitted, per_slot


def exhaustive(banks, slots, ports, p, rho):
    """Independent enumeration of full valid/bank/correlation outcomes."""
    p, rho = rational(p, 'p'), rational(rho, 'rho')
    choices = []
    for a in range(banks):
        for b in range(banks):
            weight = ((rho / banks if a == b else 0) + (1 - rho) / (banks * banks))
            choices.append((a, b, weight))
    total = Fraction(0)
    by_slot = [Fraction(0) for _ in range(slots)]
    for validity in itertools.product((False, True), repeat=slots):
        pv = math.prod((p if v else 1-p for v in validity), start=Fraction(1))
        if not pv:
            continue
        for bank_choices in itertools.product(choices, repeat=slots):
            pb = math.prod((c[2] for c in bank_choices), start=Fraction(1))
            requests = [(v, c[0], c[1]) for v, c in zip(validity, bank_choices)]
            n, decisions = oracle(requests, banks, ports)
            total += pv * pb * n
            for i, x in enumerate(decisions):
                by_slot[i] += pv * pb * x
    return total, by_slot


def sample_oracle(banks, slots, ports, p, rho, samples, seed):
    rng = random.Random(seed)
    sum_accepted = 0
    for _ in range(samples):
        requests = []
        for _ in range(slots):
            a = rng.randrange(banks)
            b = a if rng.random() < rho else rng.randrange(banks)
            requests.append((rng.random() < p, a, b))
        sum_accepted += oracle(requests, banks, ports)[0]
    return sum_accepted / samples


def tile_projection(law, control_path_ns, candidate_path_ns, other_path_ns, bytes_per_op, bandwidth_gbs,
                    control_overhead=0.0, candidate_overhead=0.0):
    values = (control_path_ns, candidate_path_ns, other_path_ns, bytes_per_op, bandwidth_gbs)
    if any(isinstance(x, bool) or not isinstance(x, (float, int)) or not math.isfinite(x) or x <= 0 for x in values):
        raise ValueError('positive finite timing and bandwidth inputs required')
    if any(isinstance(x, bool) or not isinstance(x, (int, float)) or not math.isfinite(x) or x < 0
           for x in (control_overhead, candidate_overhead)):
        raise ValueError('overheads must be finite and nonnegative')
    q = law['expected_admissions_per_cycle']
    if q <= 0:
        raise ValueError('no offered work')
    t0, t1 = max(control_path_ns, other_path_ns), max(candidate_path_ns, other_path_ns)
    r0 = min(q / (t0 * (1 + control_overhead)), bandwidth_gbs / bytes_per_op)
    r1 = min(q / (t1 * (1 + candidate_overhead)), bandwidth_gbs / bytes_per_op)
    return {'control_gops': r0, 'candidate_gops': r1, 'gain_fraction': r1/r0-1,
            'bandwidth_threshold_gbs': bytes_per_op*q/(t0*(1+control_overhead)),
            'candidate_overhead_break_even_if_no_bandwidth_limit':
                t0*(1+control_overhead)/t1-1,
            'same_fixed_clock_gain_fraction': 0.0,
            'evidence_tier': 'CONDITIONAL_PATH_PROXY_NOT_MEASURED_TILE_FMAX'}


def self_test():
    # Independent full enumeration, not a second implementation of the DP.
    for b,s,ports,p,rho in [(2,2,1,'1','0'), (2,3,2,'0.5','0.25'),
                            (3,2,2,'0.75','0.5'), (2,3,3,'0.8','1')]:
        result = exact_law(b,s,ports,p,rho)
        expected, per = exhaustive(b,s,ports,p,rho)
        assert Fraction(result['exact_fraction']) == expected
        for a,x in zip(result['per_slot_admission_probabilities'], per):
            assert abs(a-float(x)) < 1e-14
    # Frozen deterministic, out-of-table Monte Carlo regimes. These are synthetic
    # model checks, not unopened GPU workload holdouts.
    for b,s,ports,p,rho,seed in [(16,4,2,0.75,0.2,481), (8,6,1,0.65,0.6,482),
                                  (12,5,3,0.9,0.35,483)]:
        predicted = exact_law(b,s,ports,p,rho)['expected_admissions_per_cycle']
        n = 40000
        measured = sample_oracle(b,s,ports,p,rho,n,seed)
        # Hoeffding 99.9% bound for observations in [0,slots].
        tolerance = s * math.sqrt(math.log(2000)/(2*n))
        assert abs(measured-predicted) < tolerance, (b,s,ports,p,rho,measured,predicted)
    for bad in [(0,4,2,1,0), (16,4,0,1,0), (16,4,2,1.1,0),
                (16,4,2,1,float('nan')), (16,4,2,True,0)]:
        try: exact_law(*bad)
        except ValueError: pass
        else: raise AssertionError('invalid input accepted')
    baseline = exact_law(16,4,2,'0.8','0.2')
    assert tile_projection(baseline,3.427697,3.101637,3.0,4,0.5)['gain_fraction'] == 0
    assert tile_projection(baseline,3.427697,3.101637,3.5,4,8)['gain_fraction'] == 0
    assert tile_projection(baseline,3.427697,3.101637,3.0,4,8)['gain_fraction'] > 0.10
    assert tile_projection(baseline,3.427697,3.101637,3.0,4,8,candidate_overhead=0.12)['gain_fraction'] < 0
    assert tile_projection(baseline,3.427697,3.101637,3.0,4,8,candidate_overhead=3.0)['gain_fraction'] < 0
    print('V296_EXACT_ADMISSION_LAW_SELFTEST_PASS')


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--self-test', action='store_true')
    p.add_argument('--banks', type=int, default=16)
    p.add_argument('--slots', type=int, default=4)
    p.add_argument('--ports', type=int, default=2)
    p.add_argument('--valid-probability', default='0.8')
    p.add_argument('--same-bank-correlation', default='0.2')
    a = p.parse_args()
    if a.self_test:
        self_test()
        return
    law = exact_law(a.banks,a.slots,a.ports,a.valid_probability,a.same_bank_correlation)
    law['frozen_synthetic_tile_regimes'] = {
        'predicted_win_if_controller_critical_and_bandwidth_spare': tile_projection(law,3.427697,3.101637,3.0,4,8),
        'predicted_no_win_if_bandwidth_saturated': tile_projection(law,3.427697,3.101637,3.0,4,0.5),
        'predicted_no_win_if_other_tile_path_dominates': tile_projection(law,3.427697,3.101637,3.5,4,8),
        'predicted_loss_if_candidate_overhead_exceeds_break_even': tile_projection(law,3.427697,3.101637,3.0,4,8,candidate_overhead=0.12)}
    print(json.dumps(law,indent=2,sort_keys=True))

if __name__ == '__main__':
    main()
