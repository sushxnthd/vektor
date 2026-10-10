"""Bounded invariants for Vektor-083; stdlib-only."""
from decoupled import simulate, simulate_jobs, make_jobs

def main():
    checks = 0
    for c in (1, 4, 16, 24):
        for q in (0, 1, 2, 4):
            for pattern in ("spread", "hot", "skew", "random", "intra_bank"):
                for k in (1, 2, 4):
                    jobs = make_jobs(60, k, 16, pattern, 43)
                    r = simulate_jobs(jobs, collectors=c, fifo=q, banks=16, ports=2, issue_width=4)
                    assert r["completed"] == 60
                    assert r["requests"] == 60 * k
                    assert r["max_fifo"] <= q
                    assert r["throughput"] <= 4
                    if q > 0:
                        assert r["throughput"] <= q
                    checks += 1
    # With one hot bank, k operands per instruction require at least k/p cycles.
    for k in (1, 2, 4):
        r = simulate(collectors=20, fifo=4, src_count=k, ports=1,
                     pattern="hot", instructions=1000)
        assert r["throughput"] <= 1/k
    print(f"PASS {checks + 3} deterministic tests")

if __name__ == "__main__":
    main()
