"""Conservative tile-level matched-route gate. Run: python research/v317/legal_tile_decision.py.
Never infer GPU gains from electrically illegal routed proxies or isolated controller area.
"""
from dataclasses import dataclass, replace
from math import floor

@dataclass(frozen=True)
class Route:
    area: float
    mhz: float
    service: float
    setup_wns: float
    hold_wns: float
    hold_count: int
    cap_count: int
    slew_count: int
    routed: bool

    def legal(self):
        return (self.routed and self.setup_wns >= 0 and self.hold_wns >= 0
                and self.hold_count == self.cap_count == self.slew_count == 0)

def evaluate(base, candidate, common_area, budget, threshold=1.02):
    assert common_area >= 0 and budget > 0 and threshold > 0
    for r in (base, candidate):
        assert r.area > 0 and r.mhz > 0 and r.service > 0
    if not (base.legal() and candidate.legal()):
        return {"verdict": "NO_PHYSICAL_CLAIM", "base_legal": base.legal(),
                "candidate_legal": candidate.legal()}
    nb = floor(budget / (common_area + base.area))
    nc = floor(budget / (common_area + candidate.area))
    if nb == 0:
        return {"verdict": "NO_BASELINE_TILE"}
    per_tile = candidate.mhz * candidate.service / (base.mhz * base.service)
    total = per_tile * nc / nb
    return {"verdict": "PASS" if total >= threshold else "FAIL",
            "per_tile_ratio": per_tile, "tile_ratio": total,
            "base_tiles": nb, "candidate_tiles": nc}

def test():
    b = Route(21314.6, 455.75, 1, 0.1, 0, 6, 14, 0, True)
    c = Route(21324.7, 444.709, 1, 0.1, 0, 0, 21, 0, True)
    assert evaluate(b, c, 0, 1000000)["verdict"] == "NO_PHYSICAL_CLAIM"
    b = replace(b, hold_count=0, cap_count=0)
    c = replace(c, cap_count=0)
    assert evaluate(b, c, 0, 1000000)["verdict"] == "FAIL"
    b = replace(b, area=100, mhz=100)
    c = replace(c, area=110, mhz=110)
    r = evaluate(b, c, 0, 1000)
    assert r["per_tile_ratio"] > 1 and r["tile_ratio"] < 1
    assert evaluate(b, c, 10000, 20200)["verdict"] == "FAIL"
    c = replace(c, area=100, mhz=105)
    assert evaluate(b, c, 0, 1000)["verdict"] == "PASS"
    print("PASS: illegal-route refusal, clock normalization, tile-floor reversal, common-area and positive controls")

if __name__ == "__main__":
    test()
