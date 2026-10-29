from sim.vektor.pipeline import (
    DependencyTileSimulator, TileConfig, Instruction, Wave
)
from research.v303.coherence_oracle import run as independent_oracle


def test_v303_overwritten_cached_source_must_be_refetched():
    wave = [Wave([
        Instruction("fp32", (0,), dst=0, latency=1),
        Instruction("fp32", (0,), dst=1, latency=1),
    ], 0)]
    conservative = DependencyTileSimulator(
        TileConfig(operand_cache_entries=2, operand_cache_write_policy="invalidate")
    ).run(wave)
    ideal = DependencyTileSimulator(
        TileConfig(operand_cache_entries=2, operand_cache_write_policy="ideal_update")
    ).run(wave)
    assert conservative.instructions == ideal.instructions == 2
    assert conservative.rf_reads == 2
    assert ideal.rf_reads == 1
    assert conservative.operand_cache_hits == 0
    assert ideal.operand_cache_hits == 1


def test_v303_default_is_conservative():
    assert TileConfig().operand_cache_write_policy == "invalidate"


def test_v303_invalid_policy_fails_closed():
    try:
        DependencyTileSimulator(TileConfig(operand_cache_write_policy="preserve")).run(
            [Wave([Instruction("fp32", (0,))], 0)]
        )
    except ValueError:
        return
    assert False, "unsupported policy must be rejected"


def test_v303_independent_value_oracle():
    summary = independent_oracle()
    assert summary["violations_by_policy"]["invalidate"] == 0
    assert summary["violations_by_policy"]["ideal_update"] == 0
    assert summary["violations_by_policy"]["implicit_preserve"] > 0


def test_v303_independent_scheduler_replay_matches_main_model():
    from research.v303.independent_replay import run as independent_run
    from sim.vektor.pipeline import (
        dependency_fma_kernel, load_use_kernel, reuse_fma_kernel
    )
    factories = {
        "H1": reuse_fma_kernel,
        "H2": dependency_fma_kernel,
        "H3": load_use_kernel,
    }
    for name, factory in factories.items():
        for capacity in (0, 8, 64):
            for policy in ("invalidate", "ideal_update"):
                expected = independent_run(name, capacity, policy)
                actual = DependencyTileSimulator(
                    TileConfig(operand_cache_entries=capacity,
                               operand_cache_write_policy=policy)
                ).run(factory())
                for key in ("cycles", "rf_reads", "operand_cache_hits",
                            "bank_stalls"):
                    assert getattr(actual, key) == expected[key], (name, capacity, policy, key)
                assert abs(actual.issue_utilization - expected["issue_utilization"]) < 1e-12
