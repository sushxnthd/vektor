#!/usr/bin/env python3
"""Independent, read-only falsifier of V296's opened mapped-area holdouts.

Input is scaling_crossover_audit.json from the frozen GitHub Actions artifact.
Does not refit models, change the frozen gate, or read workload holdouts.
"""
import argparse
import json
import math
from pathlib import Path
import re

AREA_RE = re.compile(r"Chip area for (?:top )?module[^:\\n]*:\\s*([0-9.]+)")

EXPECTED = {(2, 4), (3, 8), (4, 8), (5, 2), (6, 8)}


def evaluate(payload, logs_dir=None):
    assert payload["decision"] == "SIMPLE_MAPPED_CROSSOVER_LAW_FALSIFIED"
    rows = payload["holdouts"]
    assert len(rows) == 5
    assert {(r["bank_bits"], r["slots"]) for r in rows} == EXPECTED
    errors = {"pairwise": [], "onehot": []}
    records = []
    correct = 0
    for r in rows:
        b, s = r["bank_bits"], r["slots"]
        p = r["measured_um2"]["pairwise"]
        h = r["measured_um2"]["onehot"]
        assert math.isfinite(p) and math.isfinite(h) and min(p, h) > 0
        if logs_dir is not None:
            sim = (logs_dir / f"b{b}_s{s}.sim.log").read_text()
            assert f"V296_SCALING_ORACLE_PASS bits={b} slots={s} " in sim
            for kind, reported in (("pairwise", p), ("onehot", h)):
                log = (logs_dir / f"b{b}_s{s}_{kind}.synth.log").read_text()
                matched = AREA_RE.findall(log)
                assert matched, f"missing raw area {b} {s} {kind}"
                assert math.isclose(float(matched[-1]), reported, abs_tol=1e-8)
        actual_win = p < h
        assert actual_win == r["measured_pairwise_wins"]
        assert math.isclose(1 - p / h, r["measured_pairwise_area_saving_fraction"],
                            abs_tol=1e-10)
        correct += (actual_win == r["predicted_pairwise_wins"])
        for kind, actual in (("pairwise", p), ("onehot", h)):
            pred = r["prediction_um2"][kind]
            error = abs(pred - actual) / actual
            assert math.isclose(error, r["relative_error"][kind], abs_tol=1e-10)
            errors[kind].append(error)
        xp = b * (2 * s * (s - 1) + s)
        xh = (1 << b) * 2 * s
        records.append({"bits": b, "slots": s, "feature_ratio_mask_to_pair": xh / xp,
                        "pairwise_wins": actual_win, "area_saving": 1 - p / h})
    assert correct == payload["holdout_winner_correct"]
    assert correct == 5
    for kind in errors:
        assert math.isclose(sum(errors[kind]) / 5,
                            payload["holdout_mean_relative_error"][kind], abs_tol=1e-10)
        assert math.isclose(max(errors[kind]),
                            payload["holdout_max_relative_error"][kind], abs_tol=1e-10)
    gate = (all(sum(v) / 5 <= .20 and max(v) <= .30 for v in errors.values())
            and correct >= 4 and payload["positive_slopes"])
    assert not gate, "Frozen law unexpectedly passes"
    wins = [r for r in records if r["pairwise_wins"]]
    losses = [r for r in records if not r["pairwise_wins"]]
    # Both orientations of a single monotone ratio threshold are contradicted.
    increasing = [(w, l) for w in wins for l in losses
                  if w["feature_ratio_mask_to_pair"] < l["feature_ratio_mask_to_pair"]]
    decreasing = [(w, l) for w in wins for l in losses
                  if w["feature_ratio_mask_to_pair"] > l["feature_ratio_mask_to_pair"]]
    assert increasing and decreasing
    return {"decision": "FROZEN_AREA_LAW_FALSIFIED_AND_SINGLE_RATIO_THRESHOLD_FALSIFIED",
            "holdout_winner_correct": correct, "holdout_total": len(rows),
            "mean_error": {k: sum(v) / 5 for k, v in errors.items()},
            "max_error": {k: max(v) for k, v in errors.items()},
            "witness_increasing_threshold_fails": list(increasing[0]),
            "witness_decreasing_threshold_fails": list(decreasing[0]),
            "rows": records,
            "scope": "Nangate45 mapped combinational area; no new prospective test"}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("audit_json", type=Path)
    p.add_argument("--logs-dir", type=Path, default=None)
    args = p.parse_args()
    print(json.dumps(evaluate(json.loads(args.audit_json.read_text()), args.logs_dir),
                     indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
