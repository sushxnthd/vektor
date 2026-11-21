"""Independent V317 mapped-arbiter budget frontier.

Reads source-pinned mapped-cell summary, not raw RTL or routed timing.
Reports conditional scheduler-only boundaries, never GPU IPC or clock signoff.
"""
import argparse
import json
from pathlib import Path


def audit(data):
    c = data["configurations"]
    sf, pf = c["source_fixed"], c["pairwise_fixed"]
    sr, pr = c["source_rotating"], c["pairwise_rotating"]
    area = lambda x: float(x["mapped_cell_area_um2"])
    if not all(area(x) > 0 for x in (sf, pf, sr, pr)):
        raise ValueError("Nonpositive mapped area")
    if not (area(pf) < area(sf) and area(pr) < area(sr)):
        raise AssertionError("Frozen mapped-area predictions failed")
    if (pf["flop_count"], pr["flop_count"]) != (0, 2):
        raise AssertionError("Unexpected sequential state")
    w = data["workload"]
    if w["regime"] != "stressed_synthetic_p060":
        raise AssertionError("Unrecognized frozen workload")
    f, r, oldest = (int(w[k]) for k in ("fixed_completions", "rotating_completions", "oldest_first_completions"))
    if min(f, r, oldest) <= 0:
        raise ValueError("Nonpositive service completions")
    service_ratio = r / f
    area_ratio = area(pr) / area(pf)
    # Hypothetical arbiter share of a larger tile; no measured tile area.
    tile = []
    for a in (0.0, 0.001, 0.01, 0.05, 0.10):
        tile_area_ratio = 1 + a * (area_ratio - 1)
        tile.append({
            "assumed_fixed_arbiter_tile_area_fraction": a,
            "tile_area_ratio": round(tile_area_ratio, 8),
            "max_clock_slowdown_fraction_for_service_per_tile_area_win": round(1 - tile_area_ratio / service_ratio, 8),
            "assumption_not_measured": True,
        })
    alphas = sorted(set(pf["fanout_weighted_logic_depth_proxy"]) & set(pr["fanout_weighted_logic_depth_proxy"]), key=float)
    stress = []
    for alpha in alphas:
        fixed_depth = float(pf["fanout_weighted_logic_depth_proxy"][alpha])
        rotating_depth = float(pr["fanout_weighted_logic_depth_proxy"][alpha])
        if min(fixed_depth, rotating_depth) <= 0:
            raise ValueError("Nonpositive dimensionless stress")
        depth_ratio = rotating_depth / fixed_depth
        stress.append({
            "alpha": float(alpha),
            "dimensionless_rotating_to_fixed_depth_ratio": round(depth_ratio, 6),
            "hypothetical_inverse_depth_service_ratio": round(service_ratio / depth_ratio, 6),
            "is_sta": False,
        })
    return {
        "source_run": data["provenance"]["workflow_run"],
        "source_sha": data["provenance"]["source_sha"],
        "evidence_tier": "mapped_cell_area_plus_synthetic_service_conditional_boundary",
        "fixed_area_reduction_fraction": round(1 - area(pf) / area(sf), 8),
        "rotating_area_reduction_fraction": round(1 - area(pr) / area(sr), 8),
        "optimized_rotating_to_fixed_area_ratio": round(area_ratio, 8),
        "synthetic_rotating_to_fixed_service_ratio": round(service_ratio, 8),
        "max_clock_slowdown_fraction_for_rotating_service_win": round(1 - 1 / service_ratio, 8),
        "scheduler_only_service_per_mapped_area_ratio": round(service_ratio / area_ratio, 8),
        "oldest_first_to_rotating_service_ratio": round(oldest / r, 8),
        "dimensionless_stress": stress,
        "conditional_tile_area_sweep": tile,
        "max_fixed_arbiter_tile_fraction_at_equal_clock": round((service_ratio - 1) / (area_ratio - 1), 8),
        "timing_signoff": False,
        "routed_rc": False,
        "power_measured": False,
        "gpu_ipc_measured": False,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("snapshot", type=Path)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    data = json.loads(args.snapshot.read_text())
    result = audit(data)
    if args.check:
        assert data["provenance"]["source_sha"] == "0d62a15fd0c1046374f287a6c683333297e6139d"
        assert data["provenance"]["workflow_run"] == 41296883857
        assert abs(result["optimized_rotating_to_fixed_area_ratio"] - 1.71413934) < 1e-7
        assert abs(result["max_clock_slowdown_fraction_for_rotating_service_win"] - 0.05996851) < 1e-7
        assert result["scheduler_only_service_per_mapped_area_ratio"] < 1
        assert all(x["hypothetical_inverse_depth_service_ratio"] < 1 for x in result["dimensionless_stress"])
        assert result["conditional_tile_area_sweep"][-1]["max_clock_slowdown_fraction_for_service_per_tile_area_win"] < 0
    print(json.dumps(result, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
