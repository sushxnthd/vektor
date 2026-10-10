"""Vektor-088 compact, deterministic reproduction of the admission fairness result.
For full 168-case search, independent C++ replication, and RTL see research package.
Synthetic reservations, NOT GPU instruction throughput.
"""
from collections import defaultdict

class Calendar:
    def __init__(self, mode="baseline", latencies=4, clients=4, age=16):
        assert mode in ("baseline", "triggered", "static")
        self.mode, self.L, self.N, self.age = mode, latencies, clients, age
        self.t = 0
        self.events = defaultdict(int)
        self.rr = [0] * (latencies + 1)
        self.wait = [0] * (latencies + 1)
        self.owners = {}

    def step(self, valid, latency):
        assert len(valid) == len(latency) == self.N
        t, L = self.t, self.L
        due = self.events.pop(t, 0)
        assert due <= 1
        if self.mode == "triggered":
            pending = {owner for d, owner in self.owners.items()
                       if owner > 0 and d - owner >= t}
            eligible = [l for l in range(1, L + 1)
                        if l not in pending and self.wait[l] >= self.age
                        and any(valid[i] and latency[i] == l for i in range(self.N))]
            self.owners[t + L] = max(eligible, key=lambda l: (self.wait[l], -l)) if eligible else 0
            for d in range(t + 1, t + L):
                self.owners.setdefault(d, 0)
        grant = [0] * self.N
        for l in range(1, L + 1):
            deadline = t + l
            owner = (self.owners[deadline] if self.mode == "triggered"
                     else 1 + deadline % L if self.mode == "static" else 0)
            if owner > 0 and l > owner:
                continue
            for delta in range(self.N):
                i = (self.rr[l] + delta) % self.N
                if valid[i] and latency[i] == l and self.events[deadline] < 1:
                    self.events[deadline] += 1
                    grant[i] = 1
                    self.rr[l] = (i + 1) % self.N
        if self.mode == "triggered":
            for l in range(1, L + 1):
                present = any(valid[i] and latency[i] == l for i in range(self.N))
                served = any(grant[i] and latency[i] == l for i in range(self.N))
                self.wait[l] = self.wait[l] + 1 if present and not served else 0
            self.owners.pop(t, None)
        assert all(v <= 1 for v in self.events.values())
        self.t += 1
        return grant, due

def experiment(latencies, cycles=4096, valid=None, age=16):
    valid = valid or [1] * len(latencies)
    out = {}
    for mode in ("baseline", "static", "triggered"):
        m = Calendar(mode, max(latencies), len(latencies), age)
        count = [0] * len(latencies)
        for _ in range(cycles):
            grants, _ = m.step(valid, latencies)
            count = [x + y for x, y in zip(count, grants)]
        out[mode] = count
    return out

def test():
    mixed = experiment([1, 2, 3, 4])
    assert mixed["baseline"] == [1, 1, 1, 4096], mixed
    assert mixed["triggered"] == [205, 205, 205, 3484], mixed
    assert min(mixed["static"]) >= 1024, mixed
    single = experiment([2, 2, 2, 2], valid=[1, 0, 0, 0])
    assert sum(single["static"]) < sum(single["baseline"]), single
    assert sum(single["triggered"]) == sum(single["baseline"]), single
    for a in (4, 8, 16, 32, 64):
        x = experiment([1, 2, 3, 4], age=a)
        assert all(n > 0 for n in x["triggered"]), x
    print("PASS: compact Vektor-088 deterministic admission tests")
    print("mixed 4096 cycles:", mixed)

if __name__ == "__main__":
    test()
