"""Vektor-105 controlled group-sector incidence microbenchmark (stdlib only).
NOT a GPU timing model. Full cycle experiments are separately archived.
"""
from collections import Counter, defaultdict
from dataclasses import dataclass

@dataclass(frozen=True)
class Lane:
    warp: int
    lane: int
    path: int
    address: int

def workload(layout):
    lanes = []
    for w in range(8):
        for l in range(32):
            p = l % 2
            if layout == "shared_sector":
                a = (p * 16 + l // 8) * 128 + (l % 8) * 4
            elif layout == "warp_contiguous":
                a = (w * 32 + l) * 4
            else:
                raise ValueError(layout)
            lanes.append(Lane(w, l, p, a))
    return lanes

def group(lanes, policy):
    bins = defaultdict(list)
    for l in lanes:
        key = (l.warp, l.path) if policy == "masked" else (0, l.path)
        bins[key].append(l)
    groups = []
    for key in sorted(bins):
        values = bins[key]
        if policy == "local":
            values = sorted(values, key=lambda l: (l.address // 128, l.warp, l.lane))
        groups.extend(values[i:i + 32] for i in range(0, len(values), 32))
    assert all(0 < len(g) <= 32 and len({l.path for l in g}) == 1 for g in groups)
    assert Counter(lanes) == Counter(l for g in groups for l in g)
    return groups

def sector_incidence(groups):
    return sum(len({l.address // 128 for l in g}) for g in groups)

def lower_bound(lanes):
    return sum((n + 31) // 32 for n in
               Counter((l.path, l.address // 128) for l in lanes).values())

def main():
    for layout, expected in [
        ("shared_sector", (64, 32, 8)),
        ("warp_contiguous", (16, 16, 16)),
    ]:
        lanes = workload(layout)
        counts = tuple(sector_incidence(group(lanes, p))
                       for p in ("masked", "dwf", "local"))
        assert counts == expected, (layout, counts)
        assert counts[-1] >= lower_bound(lanes)
        if layout == "shared_sector":
            assert counts[-1] == lower_bound(lanes)
        print(layout, "groups", [len(group(lanes, p)) for p in
              ("masked", "dwf", "local")], "sectors/instruction", counts,
              "lower_bound", lower_bound(lanes))
    print("PASS: structural conservation and controlled sector tests")

if __name__ == "__main__":
    main()
