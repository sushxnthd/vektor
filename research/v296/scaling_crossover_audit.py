#!/usr/bin/env python3
"""Preregistered V296 mapped combinational-area crossover; holdouts are NOT workloads.

Fit two fixed two-parameter models on frozen training configurations ONLY.
Only after fitting are the holdout synthesis logs opened. Fail closed.
"""
import argparse
import json
import math
from pathlib import Path
import re

TRAIN = ((2, 2), (3, 2), (3, 4), (4, 2), (4, 4),
         (5, 4), (5, 8), (6, 2), (6, 4))
HOLDOUT = ((2, 4), (3, 8), (4, 8), (5, 2), (6, 8))
AREA_RE = re.compile(r"Chip area for (?:top )?module[^:\n]*:\s*([0-9.]+)")


def feature(kind, bits, slots):
    if kind == "pairwise":
        return bits * (2 * slots * (slots - 1) + slots)
    if kind == "onehot":
        return (1 << bits) * 2 * slots
    raise ValueError("unknown architecture")


def read_area(root, bits, slots, kind):
    path = root / f"b{bits}_s{slots}_{kind}.synth.log"
    data = path.read_text()
    matches = AREA_RE.findall(data)
    if not matches:
        raise ValueError(f"missing characterized area: {path}")
    area = float(matches[-1])
    if not math.isfinite(area) or area <= 0:
        raise ValueError(f"invalid area: {path}")
    sim = root / f"b{bits}_s{slots}.sim.log"
    if f"V296_SCALING_ORACLE_PASS bits={bits} slots={slots} " not in sim.read_text():
        raise ValueError(f"independent oracle missing/failed: {sim}")
    return area


def fit(points, kind):
    xx = [feature(kind, b, s) for b, s, _ in points]
    yy = [a for _, _, a in points]
    xm, ym = sum(xx) / len(xx), sum(yy) / len(yy)
    denom = sum((x - xm) ** 2 for x in xx)
    if denom <= 0:
        raise ValueError("degenerate feature matrix")
    beta = sum((x - xm) * (y - ym) for x, y in zip(xx, yy)) / denom
    alpha = ym - beta * xm
    if not all(map(math.isfinite, (alpha, beta))):
        raise ValueError("nonfinite coefficients")
    return alpha, beta


def predict(coef, kind, bits, slots):
    return coef[0] + coef[1] * feature(kind, bits, slots)


def evaluate(root):
    # Do not even read held-out synthesis logs until coefficients are fixed.
    training = {
        kind: [(b, s, read_area(root, b, s, kind)) for b, s in TRAIN]
        for kind in ("pairwise", "onehot")
    }
    coefficients = {kind: fit(training[kind], kind) for kind in training}
    frozen_coefficients = json.dumps(coefficients, sort_keys=True)
    if any(c[1] <= 0 for c in coefficients.values()):
        # Preserve holdout predictions for audit but never call this a law pass.
        monotone = False
    else:
        monotone = True

    rows = []
    for b, s in HOLDOUT:
        # Holdout values first become visible here, after the fit is frozen.
        predicted = {kind: predict(coefficients[kind], kind, b, s)
                     for kind in ("pairwise", "onehot")}
        actual = {kind: read_area(root, b, s, kind)
                  for kind in ("pairwise", "onehot")}
        error = {kind: abs(predicted[kind] - actual[kind]) / actual[kind]
                 for kind in ("pairwise", "onehot")}
        rows.append({
            "bank_bits": b, "banks": 1 << b, "slots": s,
            "prediction_um2": predicted, "measured_um2": actual,
            "relative_error": error,
            "predicted_pairwise_wins": predicted["pairwise"] < predicted["onehot"],
            "measured_pairwise_wins": actual["pairwise"] < actual["onehot"],
            "measured_pairwise_area_saving_fraction":
                1.0 - actual["pairwise"] / actual["onehot"],
        })
    mean_error = {
        kind: sum(row["relative_error"][kind] for row in rows) / len(rows)
        for kind in ("pairwise", "onehot")
    }
    max_error = {
        kind: max(row["relative_error"][kind] for row in rows)
        for kind in ("pairwise", "onehot")
    }
    winner_correct = sum(row["predicted_pairwise_wins"] ==
                         row["measured_pairwise_wins"] for row in rows)
    pass_gate = (monotone and winner_correct >= 4 and
                 all(mean_error[k] <= 0.20 and max_error[k] <= 0.30
                     for k in mean_error))
    return {
        "decision": "MAPPED_CROSSOVER_LAW_PROVISIONAL_PASS" if pass_gate
                    else "SIMPLE_MAPPED_CROSSOVER_LAW_FALSIFIED",
        "evidence_tier": "Nangate45 mapped combinational-arbiter area only",
        "fit_only_cases": [list(p) for p in TRAIN],
        "unseen_parameter_cases": [list(p) for p in HOLDOUT],
        "frozen_coefficients_before_holdout_read": json.loads(frozen_coefficients),
        "positive_slopes": monotone,
        "holdout_mean_relative_error": mean_error,
        "holdout_max_relative_error": max_error,
        "holdout_winner_correct": winner_correct,
        "holdout_winner_total": len(rows),
        "holdouts": rows,
        "workload_holdouts": "SEALED",
        "physical_pareto_gate": "INDEPENDENT_AND_NOT_SUPERSEDED",
        "limitations": "No selector/scheduler area, routing, CTS, power, measured throughput or GPU tile consequence",
    }


def self_test():
    # Synthetic fixture verifies the fitter, prospective holdout split,
    # winner scoring, and that negative slopes are rejected.
    assert len(TRAIN) == 9 and len(HOLDOUT) == 5
    assert set(TRAIN).isdisjoint(HOLDOUT)
    pair = [(b, s, 10 + 2 * feature("pairwise", b, s)) for b, s in TRAIN]
    mask = [(b, s, 15 + 3 * feature("onehot", b, s)) for b, s in TRAIN]
    assert all(abs(a - b) < 1e-8 for a, b in zip(fit(pair, "pairwise"), (10, 2)))
    assert all(abs(a - b) < 1e-8 for a, b in zip(fit(mask, "onehot"), (15, 3)))
    assert fit([(b, s, 1000 - feature("pairwise", b, s))
                for b, s in TRAIN], "pairwise")[1] < 0
    assert feature("pairwise", 4, 4) == 4 * (24 + 4)
    assert feature("onehot", 4, 4) == 128
    print("V296_SCALING_BOUNDARY_SELFTEST_PASS")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("root", nargs="?")
    p.add_argument("--cases", action="store_true")
    p.add_argument("--self-test", action="store_true")
    args = p.parse_args()
    if args.cases:
        for tier, cases in (("train", TRAIN), ("holdout", HOLDOUT)):
            for bits, slots in cases:
                print(bits, slots, tier)
        return
    if args.self_test:
        self_test()
        return
    if not args.root:
        p.error("root required")
    root = Path(args.root)
    try:
        result = evaluate(root)
    except (OSError, ValueError, AssertionError) as e:
        result = {"decision": "SCALING_EVIDENCE_INCOMPLETE",
                  "error": str(e), "workload_holdouts": "SEALED"}
    (root / "scaling_crossover_audit.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))
    if result["decision"] != "MAPPED_CROSSOVER_LAW_PROVISIONAL_PASS":
        raise SystemExit(3)


if __name__ == "__main__":
    main()
