#!/usr/bin/env python3
"""Prospectively frozen V296 latent-hotspot test. Synthetic traffic, NOT GPU data.

One cycle: a hidden bank H is uniform; each valid slot uses H with probability h
or another bank uniformly. Each request uses two reads of its chosen bank.
All per-slot bank marginals are uniform; cross-slot dependence varies with h.
"""
import argparse
import itertools
import json
import math
import random
from fractions import Fraction


B, S, PORTS, P = 16, 4, 2, Fraction(4, 5)
SPLITS = {
    "h_3_8": {"h": Fraction(3, 8), "calibration_seed": 296375,
              "evaluation_seed": 297375},
    "h_5_8": {"h": Fraction(5, 8), "calibration_seed": 296625,
              "evaluation_seed": 297625},
}
CAL_CYCLES = 40000
EVAL_CYCLES = 80000
FROZEN_TOLERANCE = 0.05


def exact_q(b, slots, p, h):
    """Exact expected admissions: each distinct used bank consumes both ports."""
    if not isinstance(b, int) or b < 2 or not isinstance(slots, int) or slots < 1:
        raise ValueError("invalid dimensions")
    p, h = Fraction(p), Fraction(h)
    if not 0 <= p <= 1 or not Fraction(1, b) <= h <= 1:
        raise ValueError("invalid probabilities")
    return 1 - (1-p*h)**slots + (b-1)*(1-(1-p*(1-h)/(b-1))**slots)


def uniform_q(b, slots, p):
    return b*(1-(1-Fraction(p)/b)**slots)


def concrete_greedy(requests, banks, ports=2):
    """Independent indexed-bank admission oracle, not histogram DP."""
    used = [0]*banks
    admitted = 0
    for valid, bank in requests:
        if valid and used[bank]+2 <= ports:
            used[bank] += 2
            admitted += 1
    return admitted


def exhaustive_small(b, slots, p, h):
    """Enumerate latent H and concrete valid/invalid slot outcomes exactly."""
    p, h = Fraction(p), Fraction(h)
    total = Fraction(0)
    for hidden in range(b):
        choices = [(False, 0, 1-p)]
        choices.extend((True, bank, p*(h if bank == hidden else (1-h)/(b-1)))
                       for bank in range(b))
        for outcome in itertools.product(choices, repeat=slots):
            weight = Fraction(1, b)
            for _, _, probability in outcome:
                weight *= probability
            if weight:
                total += weight*concrete_greedy(
                    [(valid, bank) for valid, bank, _ in outcome], b)
    return total


def generate(b, slots, p, h, cycles, seed, with_admissions):
    rng = random.Random(seed)
    pair_equal = pair_total = 0
    bank_hist = [0]*b
    admitted = 0
    for _ in range(cycles):
        hidden = rng.randrange(b)
        requests = []
        valid_banks = []
        for _ in range(slots):
            valid = rng.random() < float(p)
            if rng.random() < float(h):
                bank = hidden
            else:
                bank = rng.randrange(b-1)
                if bank >= hidden:
                    bank += 1
            requests.append((valid, bank))
            if valid:
                valid_banks.append(bank)
                bank_hist[bank] += 1
        for i in range(len(valid_banks)):
            for j in range(i+1, len(valid_banks)):
                pair_total += 1
                pair_equal += valid_banks[i] == valid_banks[j]
        if with_admissions:
            admitted += concrete_greedy(requests, b)
    return {"c": pair_equal/pair_total if pair_total else None,
            "pairs": pair_total, "bank_hist": bank_hist,
            "q": admitted/cycles if with_admissions else None}


def invert_pair_collision(b, c):
    """Invert within-cycle valid-slot pair collision; h >= 1/B branch."""
    if c is None or not math.isfinite(c):
        raise ValueError("no finite collision statistic")
    clipped = min(1., max(1./b, c))
    return (1+math.sqrt((b-1)*(b*clipped-1)))/b


def self_test():
    for b, slots, p, h in [
        (2, 3, Fraction(3, 4), Fraction(1, 2)),
        (2, 3, Fraction(3, 4), Fraction(3, 4)),
        (3, 2, Fraction(1, 2), Fraction(2, 3)),
        (3, 3, Fraction(1, 2), Fraction(1, 1)),
    ]:
        assert exact_q(b, slots, p, h) == exhaustive_small(b, slots, p, h)
    for h in [Fraction(1, B), Fraction(1, 4), Fraction(1, 2), Fraction(3, 4), Fraction(1)]:
        c = float(h*h+(1-h)*(1-h)/(B-1))
        assert abs(invert_pair_collision(B, c)-float(h)) < 1e-12
    assert exact_q(B, S, P, Fraction(1, B)) == uniform_q(B, S, P)
    assert exact_q(B, S, P, Fraction(1)) == 1-(1-P)**S
    for bad in [-0.1, float("nan"), 1.1]:
        try:
            invert_pair_collision(B, bad) if bad != 1.1 else exact_q(B,S,P,Fraction(11,10))
        except ValueError:
            pass
        else:
            if bad != -0.1:  # noisy negative c is deliberately clipped
                raise AssertionError("invalid input accepted")
    print("V296_LATENT_HOTSPOT_SELFTEST_PASS")


def experiment():
    baseline = uniform_q(B, S, P)
    development = {}
    for h in [Fraction(1, B), Fraction(1, 4), Fraction(1, 2), Fraction(3, 4), Fraction(1)]:
        development[str(h)] = {"q": float(exact_q(B,S,P,h)),
                               "baseline_overprediction_fraction": float(baseline/exact_q(B,S,P,h)-1),
                               "cross_slot_pair_collision": float(h*h+(1-h)*(1-h)/(B-1))}
    unseen = {}
    for label, split in SPLITS.items():
        h = split["h"]
        cal = generate(B,S,P,h,CAL_CYCLES,split["calibration_seed"],False)
        estimated_h = invert_pair_collision(B,cal["c"])
        # Frozen prospective prediction from REQUESTS ONLY; no evaluation outcome read.
        predicted = float(exact_q(B,S,P,Fraction(str(estimated_h))))
        ev = generate(B,S,P,h,EVAL_CYCLES,split["evaluation_seed"],True)
        true_q = float(exact_q(B,S,P,h))
        observed = ev["q"]
        err = abs(predicted-observed)
        if err > FROZEN_TOLERANCE:
            raise AssertionError((label,"prospective law falsified",err))
        unseen[label] = {
            "calibration_seed": split["calibration_seed"], "evaluation_seed": split["evaluation_seed"],
            "calibration_cycles": CAL_CYCLES, "evaluation_cycles": EVAL_CYCLES,
            "calibration_valid_slot_pairs": cal["pairs"], "calibration_pair_collision": cal["c"],
            "estimated_h_from_requests_only": estimated_h,
            "known_h_exact_q": true_q, "prospective_predicted_q": predicted,
            "independent_concrete_oracle_q": observed, "abs_error": err,
            "uniform_marginal_baseline_q": float(baseline),
            "baseline_abs_error": abs(float(baseline)-observed),
            "frozen_tolerance": FROZEN_TOLERANCE, "pass": True,
            "evaluation_bank_marginal_max_abs_deviation": max(
                abs(x/sum(ev["bank_hist"])-1/B) for x in ev["bank_hist"]),
        }
    return {"evidence": "PROSPECTIVE_SYNTHETIC_ONLY_NOT_GPU_TRACE",
            "assumptions": {"banks": B,"slots":S,"ports":PORTS,"valid_probability":str(P),
                            "same_bank_operand_probability":1,
                            "all_unconditional_slot_bank_marginals":"1/16"},
            "development":development,"unseen":unseen,
            "architecture_gain_at_equal_clock":0,
            "claim_limit":"No real traces, measured tile power/fmax, or V296 speedup."}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test",action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
    print(json.dumps(experiment(),indent=2,sort_keys=True))
