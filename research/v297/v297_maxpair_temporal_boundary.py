#!/usr/bin/env python3
"""Independent fixed-request temporal kill test for V297 vs unrestricted max-pair.

Synthetic admission model, not a GPU, RTL or physically matched comparison.
Protocol: V297_MAXPAIR_TEMPORAL_BOUNDARY_PREREG_20261029.md.
"""
import json
from statistics import mean

SEEDS = (101, 103, 107, 109)
WARMUP = 10_000
MEASURE = 200_000
REGIMES = ((0.4, 0.9), (0.4, 0.2), (0.25, 0.85), (0.7, 0.8), (0.0, 0.0), (1.0, 1.0))

class XorShift32:
    def __init__(self, seed):
        assert 0 < seed < (1 << 32)
        self.x = seed
    def draw(self):
        x = self.x
        x ^= (x << 13) & 0xffffffff
        x ^= x >> 17
        x ^= (x << 5) & 0xffffffff
        self.x = x & 0xffffffff
        return self.x / 4294967296.0


def predict(p, a):
    rescue = p / (1 + a)
    return {"rescue_per_cycle": rescue, "maxpair_advantage_over_v297": p - rescue,
            "v297_over_maxpair": (1 + rescue) / (1 + p)}


def simulate(p, a, seed):
    assert 0 <= p <= 1 and 0 <= a <= 1
    b = p * (1 - a) / (1 - p) if p < 1 else 1
    assert 0 <= b <= 1
    rng = XorShift32(seed)
    motif = rng.draw() < p
    cooldown = False
    n_motif = n_rescue = n_max = n_v297 = n_serial = n_port_errors = 0
    for t in range(WARMUP + MEASURE):
        # Motif: bank pairs 00,01,02; nonmotif: 00,00,00.
        jobs = ((0, 0), (0, 1), (0, 2)) if motif else ((0, 0),) * 3
        max_grant = (False, True, True) if motif else (True, False, False)
        rescue = motif and not cooldown
        v297_grant = max_grant if rescue else (True, False, False)
        serial_grant = (True, False, False)
        for grant in (max_grant, v297_grant, serial_grant):
            counts = [0] * 3
            for i, active in enumerate(grant):
                if active:
                    for bank in jobs[i]:
                        counts[bank] += 1
            if sum(grant) > 2 or max(counts) > 2:
                n_port_errors += 1
        if t >= WARMUP:
            n_motif += int(motif)
            n_rescue += int(rescue)
            n_max += sum(max_grant)
            n_v297 += sum(v297_grant)
            n_serial += sum(serial_grant)
        cooldown = rescue
        motif = rng.draw() < (a if motif else b)
    return {"seed": seed, "observed_motif_p": n_motif / MEASURE,
            "observed_rescue_rate": n_rescue / MEASURE,
            "serial_admissions_per_cycle": n_serial / MEASURE,
            "v297_admissions_per_cycle": n_v297 / MEASURE,
            "maxpair_admissions_per_cycle": n_max / MEASURE,
            "v297_over_maxpair": n_v297 / n_max,
            "maxpair_advantage_over_v297": (n_max - n_v297) / MEASURE,
            "port_violations": n_port_errors}


def periodic_negative():
    cooldown = False
    motif_count = rescue_count = 0
    n = 300_000
    for t in range(n):
        motif = t % 3 != 2
        rescue = motif and not cooldown
        motif_count += motif
        rescue_count += rescue
        cooldown = rescue
    p = motif_count / n
    a = 0.5
    return {"pattern": "110_repeating", "cycles": n, "p": p,
            "lag1_conditional_a": a, "observed_rescue": rescue_count / n,
            "markov_prediction": predict(p, a)["rescue_per_cycle"],
            "absolute_error": abs(rescue_count / n - predict(p, a)["rescue_per_cycle"])}


def main():
    rows = []
    for p, a in REGIMES:
        samples = [simulate(p, a, s) for s in SEEDS]
        pred = predict(p, a)
        ratio = mean(s["v297_over_maxpair"] for s in samples)
        assert all(s["port_violations"] == 0 for s in samples)
        assert all(s["maxpair_admissions_per_cycle"] >= s["v297_admissions_per_cycle"] for s in samples)
        assert abs(ratio - pred["v297_over_maxpair"]) < 0.003, (p, a, ratio, pred)
        if p == 0:
            assert all(s["v297_over_maxpair"] == 1 for s in samples)
        if p == 1:
            assert all(s["v297_over_maxpair"] == 0.75 for s in samples)
        rows.append({"p": p, "a": a, "prediction": pred, "mean_observed_ratio": ratio,
                     "absolute_ratio_error": abs(ratio - pred["v297_over_maxpair"]), "seeds": samples})
    negative = periodic_negative()
    assert negative["absolute_error"] > 0.05
    return {"evidence_tier": "INDEPENDENT_SYNTHETIC_FIXED_REQUEST_TEMPORAL_FALSIFICATION",
            "prereg": "V297_MAXPAIR_TEMPORAL_BOUNDARY_PREREG_20261029.md",
            "seeds": SEEDS, "burnin": WARMUP, "measured_cycles_per_seed": MEASURE,
            "rows": rows, "non_markov_negative_control": negative,
            "claim": "On fixed bank patterns with first-order Markov motif arrivals, V297 is strictly dominated in mean admissions by unrestricted maxpair when p*a>0. Does not imply dynamic-queue or physical dominance."}


if __name__ == "__main__":
    print(json.dumps(main(), indent=2))
