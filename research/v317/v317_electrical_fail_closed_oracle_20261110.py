"""Fail-closed matched physical acceptance gate for V317.

Evidence: values transcribed from completed matched OpenROAD run 42656831972,
as audited in research commit 2d0fc047. This is a deterministic independent
acceptance/falsification checker, NOT a new route, STA extraction, or DRC signoff.
Never treat a successful routing process as electrical closure.
"""
from dataclasses import dataclass
import json

@dataclass(frozen=True)
class Physical:
    name: str
    area_um2: float
    period_ns: float
    setup: int
    hold: int
    max_cap: int
    max_slew: int
    max_fanout: int
    drc_verified: bool
    workload_ratio: float | None = None

    def legal(self):
        return (self.drc_verified and self.period_ns > 0 and self.area_um2 > 0
                and all(x == 0 for x in (self.setup, self.hold,
                                         self.max_cap, self.max_slew,
                                         self.max_fanout)))

# Same source provenance as physical audit; reported area is earlier matched
# measurement, not independently established as the routed cell area.
COMPACT = Physical("compact", 21314.6, 2.24, 0, 0, 10, 0, 0, False)
PAIRWISE = Physical("pairwise", 21324.7, 2.20, 0, 12, 13, 0, 0, False)

def assess(base, candidate, service_ratio=None):
    """Service ratio is completed useful work under IDENTICAL demand/resources."""
    violations = {
        p.name: {
            "setup": p.setup, "hold": p.hold, "max_cap": p.max_cap,
            "max_slew": p.max_slew, "max_fanout": p.max_fanout,
            "drc_unverified": not p.drc_verified,
        } for p in (base, candidate)
    }
    legal = base.legal() and candidate.legal()
    # Area and period inequality is necessary, not sufficient; bandwidth,
    # power and occupancy remain separate acceptance gates.
    area_ratio = base.area_um2 / candidate.area_um2
    period_ratio = base.period_ns / candidate.period_ns
    physical_factor = area_ratio * period_ratio
    required_service = 1 / physical_factor
    throughput_per_area = (service_ratio * physical_factor
                           if service_ratio is not None else None)
    return {
        "status": ("ELIGIBLE_FOR_FURTHER_WORKLOAD_AND_POWER_AUDIT"
                   if legal and throughput_per_area is not None
                   and throughput_per_area > 1
                   else "REJECT_UNPROVEN"),
        "both_electrically_legal": legal,
        "violations": violations,
        "area_ratio_baseline_over_candidate": area_ratio,
        "period_ratio_baseline_over_candidate": period_ratio,
        "required_service_ratio_for_area_normalized_win": required_service,
        "conditional_area_normalized_gain": throughput_per_area,
        "warning": "mixed-provenance area and routed period; conditional only",
    }

def self_test():
    r = assess(COMPACT, PAIRWISE)
    assert r["status"] == "REJECT_UNPROVEN"
    assert not r["both_electrically_legal"]
    assert r["violations"]["pairwise"]["hold"] == 12
    assert r["violations"]["compact"]["max_cap"] == 10
    assert r["conditional_area_normalized_gain"] is None
    # Even a fabricated 2x service ratio cannot bypass electrical legality.
    assert assess(COMPACT, PAIRWISE, 2.0)["status"] == "REJECT_UNPROVEN"
    # DRC unknown is not DRC clean, even if all numerical violations are zero.
    clean_but_unsigned = Physical("unsigned", 100, 1, 0, 0, 0, 0, 0, False)
    assert not clean_but_unsigned.legal()
    # Both legally signed off: only a measured service gain above the
    # matched period/area boundary can proceed to further scrutiny.
    legal_base = Physical("b", 100, 1, 0, 0, 0, 0, 0, True)
    legal_candidate = Physical("c", 110, 1.1, 0, 0, 0, 0, 0, True)
    assert assess(legal_base, legal_candidate, 1.0)["status"] == "REJECT_UNPROVEN"
    assert assess(legal_base, legal_candidate, 1.3)["status"].startswith("ELIGIBLE")
    return r

if __name__ == "__main__":
    print(json.dumps(self_test(), indent=2, sort_keys=True))
