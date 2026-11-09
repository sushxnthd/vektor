#!/usr/bin/env python3
"""V317 prospective matched-repair sensitivity: no physical claims.

Only accepts *same-run, electrically legal* paired observations. Computes
required service gain rather than assuming the candidate wins on clock alone.
The frozen illustrative sweep is a sensitivity test, NOT measured routing.
"""
import argparse
import json
import math
from dataclasses import dataclass

@dataclass(frozen=True)
class Route:
    area: float
    period_ns: float
    setup: int
    hold: int
    cap: int
    slew: int
    fanout: int
    drc_verified: bool
    drc_violations: int
    experiment_id: str = ""

    def legal(self):
        return (math.isfinite(self.area) and math.isfinite(self.period_ns)
                and self.area > 0 and self.period_ns > 0
                and all(isinstance(x, int) and not isinstance(x, bool) and x == 0 for x in (self.setup, self.hold, self.cap,
                                          self.slew, self.fanout, self.drc_violations))
                and self.drc_verified)

def required_service(candidate, baseline, target=1.02):
    # Falsification: earlier gate silently accepted cross-run timing/area inputs.
    # A shared nonempty provenance identifier is mandatory, not documentation.
    if not (isinstance(target, (int, float)) and not isinstance(target, bool)
            and math.isfinite(target) and target > 0):
        return None
    if not (isinstance(candidate.experiment_id, str) and candidate.experiment_id
            and candidate.experiment_id == baseline.experiment_id):
        return None
    if not (candidate.legal() and baseline.legal()):
        return None
    return target * candidate.area * candidate.period_ns / (baseline.area * baseline.period_ns)

def decision(candidate, baseline, measured_service, target=1.02, service_experiment_id=None):
    req = required_service(candidate, baseline, target)
    if req is None:
        return {"accept": False, "reason": "electrical_or_DRC_failure", "required_service": None}
    if service_experiment_id != candidate.experiment_id:
        return {"accept": False, "reason": "workload_provenance_mismatch", "required_service": req}
    if (measured_service is None or not isinstance(measured_service, (int, float))
            or not math.isfinite(measured_service) or measured_service <= 0):
        return {"accept": False, "reason": "missing_matched_workload_service", "required_service": req}
    return {"accept": measured_service >= req, "reason": "tested", "required_service": req}

def synthetic_sweep():
    # Prior reported areas and periods originate in DIFFERENT experiments.
    # All rows are counterfactual; not eligible for physical acceptance.
    a_c, a_p = 21314.6, 21324.7
    for compact_repair in (0, 0.02, 0.05, 0.10):
        for pair_repair in (0, 0.02, 0.05, 0.10):
            tc, tp = 2.24 + compact_repair, 2.20 + pair_repair
            yield {"compact_repair_ns": compact_repair,
                   "pairwise_repair_ns": pair_repair,
                   "required_service_for_2pct": 1.02 * a_p * tp / (a_c * tc),
                   "required_service_for_break_even": a_p * tp / (a_c * tc),
                   "evidence": "counterfactual_cross_run_only"}

def selftest():
    ok = Route(100, 2, 0, 0, 0, 0, 0, True, 0, "paired-run-001")
    illegal = Route(100, 2, 0, 1, 0, 0, 0, True, 0, "paired-run-001")
    unverified = Route(100, 2, 0, 0, 0, 0, 0, False, 0, "paired-run-001")
    assert required_service(ok, ok) == 1.02
    assert required_service(illegal, ok) is None
    assert required_service(ok, unverified) is None
    assert not decision(ok, ok, None, service_experiment_id="paired-run-001")["accept"]
    assert decision(ok, ok, 1.03, service_experiment_id="paired-run-001")["accept"]
    assert not decision(ok, ok, 1.01, service_experiment_id="paired-run-001")["accept"]
    assert not decision(illegal, ok, 100, service_experiment_id="paired-run-001")["accept"]
    # Falsification: the previous gate accepted +infinity as a workload win.
    # It also accepted negative-infinity periods as invalid but positive-infinity
    # area/period could contaminate required_service. Fail closed on all nonfinite.
    for nonfinite in (float('nan'), float('inf'), -float('inf')):
        assert not Route(nonfinite, 2, 0, 0, 0, 0, 0, True, 0).legal()
        assert not Route(100, nonfinite, 0, 0, 0, 0, 0, True, 0).legal()
        assert not decision(ok, ok, nonfinite, service_experiment_id="paired-run-001")["accept"]
    assert not Route(100, 2, -1, 0, 0, 0, 0, True, 0).legal()
    assert not Route(100, 2, False, 0, 0, 0, 0, True, 0).legal()
    # Cross-run legal measurements cannot be combined into a false positive.\n    other = Route(100, 1, 0, 0, 0, 0, 0, True, 0, "other-run")\n    assert required_service(other, ok) is None\n    assert required_service(ok, ok, target=float("nan")) is None\n    assert required_service(ok, ok, target=-1) is None\n    assert not decision(ok, ok, 999, service_experiment_id="other-run")["accept"]\n    assert not decision(ok, ok, 999)["accept"]\n    assert required_service(Route(100, 2, 0, 0, 0, 0, 0, True, 0), ok) is None\n    rows = list(synthetic_sweep())
    assert len(rows) == 16
    # Candidate timing deterioration makes the required service monotonically worse.
    assert rows[0]["required_service_for_2pct"] < rows[3]["required_service_for_2pct"]
    # Baseline deterioration improves candidate's relative position.
    assert rows[0]["required_service_for_2pct"] > rows[12]["required_service_for_2pct"]

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--selftest", action="store_true")
    args = p.parse_args()
    selftest()
    print(json.dumps({"selftest": "pass", "sweep": list(synthetic_sweep()),
                      "physical_acceptance": "blocked_until_same_run_legal_routes_and_measured_service"}, indent=2))
