"""V303 finite-port cache coherence and independent control checks."""
from research.v303.port_budget import Config, simulate, run, write_heavy_kernel
from sim.vektor.pipeline import dependency_fma_kernel, reuse_fma_kernel


def test_v303_port_budget_frozen_regression_and_no_go():
    evidence = run()
    assert evidence["survival_gate_passed"] is False
    h2 = next(r for r in evidence["rows"]
              if r["regime"] == "H2_dependent_overwrite" and r["capacity"] == 64)
    assert h2["one_port_rf_read_reduction_pct"] < 5.0
    assert h2["one_port_cycle_change_pct"] > 1.0
    for row in evidence["rows"]:
        for p in row["policies"].values():
            assert p["stale_reads"] == 0
            assert p["resident_write_demand"] == p["updates"] + p["forced_invalidations"]
        assert row["policies"]["limited_update_p1"]["max_cycle_updates"] <= 1
        assert row["policies"]["limited_update_p4"]["max_cycle_updates"] <= 4
        if row["capacity"] == 0:
            assert len({str(v) for v in row["policies"].values()}) == 1


def test_v303_port_budget_matches_existing_control_replay():
    # Previously frozen V303 independent replay (H1/H2, invalidate/ideal).
    expected = {
        ("H1", 0): ((1024, 4096), (1024, 4096)),
        ("H1", 8): ((513, 2048), (513, 2048)),
        ("H1", 64): ((513, 64), (513, 64)),
        ("H2", 0): ((1024, 4096), (1024, 4096)),
        ("H2", 8): ((1024, 4096), (1024, 4096)),
        ("H2", 64): ((516, 2080), (521, 2322)),
    }
    for name, factory in (("H1", reuse_fma_kernel), ("H2", dependency_fma_kernel)):
        for capacity in (0, 8, 64):
            invalid = simulate(factory(), Config(capacity, 0, "invalidate"))
            ideal = simulate(factory(), Config(capacity, 0, "ideal_update"))
            assert ((invalid.cycles, invalid.rf_reads), (ideal.cycles, ideal.rf_reads)) == expected[(name, capacity)]


def test_v303_port_budget_high_contention_rejects_free_update():
    waves = write_heavy_kernel(wave_count=32, instructions=64)
    one = simulate(waves, Config(capacity=64, update_ports=1))
    four = simulate(waves, Config(capacity=64, update_ports=4))
    assert one.forced_invalidations > 0
    assert four.forced_invalidations == 0
    assert one.max_cycle_updates == 1
    assert four.max_cycle_updates <= 4
    assert one.rf_reads > four.rf_reads
