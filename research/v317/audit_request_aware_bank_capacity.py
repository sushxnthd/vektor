"""Independent request-aware capacity bound; synthetic counterexample only."""
from itertools import product, combinations

def aggregate(requests, bank_ports, output_slots):
    return min(len(requests), sum(bank_ports), output_slots)

def exact(requests, bank_ports, output_slots):
    best = 0
    for k in range(min(len(requests), output_slots) + 1):
        for subset in combinations(requests, k):
            demand = [0] * len(bank_ports)
            for req in subset:
                for bank in req:
                    demand[bank] += 1
            if all(a <= b for a, b in zip(demand, bank_ports)):
                best = max(best, k)
    return best

def audit():
    ports = (1, 1, 1)
    total = loose = max_gap = 0
    choices = [(0,), (1,), (2,), (0, 1), (0, 2), (1, 2)]
    for n in range(1, 5):
        for ids in product(range(len(choices)), repeat=n):
            reqs = tuple(choices[i] for i in ids)
            a = aggregate(reqs, ports, 3)
            e = exact(reqs, ports, 3)
            assert e <= a, (reqs, e, a)
            total += 1
            loose += a > e
            max_gap = max(max_gap, a - e)
    example = ((0,), (0,), (0,))
    assert aggregate(example, ports, 3) == 3
    assert exact(example, ports, 3) == 1
    print(f"PASS cases={total} loose={loose} max_gap={max_gap}; example aggregate=3 exact=1")

if __name__ == "__main__":
    audit()
