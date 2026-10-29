from sim.vektor.pipeline import (
    DependencyTileSimulator,
    TileConfig,
    dependency_fma_kernel,
    load_use_kernel,
    reuse_fma_kernel,
)


def test_empty_simulation_is_zero():
    result = DependencyTileSimulator().run([])
    assert result.cycles == 0
    assert result.instructions == 0
    assert result.issue_utilization == 0.0


def test_operand_cache_reduces_rf_reads_on_reuse_kernel():
    no_cache = DependencyTileSimulator(
        TileConfig(operand_cache_entries=0)
    ).run(reuse_fma_kernel())
    cached = DependencyTileSimulator(
        TileConfig(operand_cache_entries=64)
    ).run(reuse_fma_kernel())

    assert cached.rf_reads < no_cache.rf_reads
    assert cached.cycles < no_cache.cycles
    assert cached.issue_utilization > 0.95


def test_dependency_latency_and_operand_cache_write_policy_are_distinct():
    # The former >95% result implicitly assumed coherent free cache updates
    # after every destination overwrite. Preserve that as an ideal upper bound.
    ideal = DependencyTileSimulator(
        TileConfig(operand_cache_entries=64, operand_cache_write_policy="ideal_update")
    ).run(dependency_fma_kernel())
    conservative = DependencyTileSimulator(
        TileConfig(operand_cache_entries=64, operand_cache_write_policy="invalidate")
    ).run(dependency_fma_kernel())

    assert ideal.instructions == conservative.instructions == 32 * 64
    assert ideal.dependency_stalls > 0
    assert ideal.issue_utilization > 0.95
    assert conservative.rf_reads >= ideal.rf_reads
    assert conservative.cycles >= ideal.cycles


def test_load_use_kernel_exposes_memory_latency():
    result = DependencyTileSimulator(
        TileConfig(operand_cache_entries=64, memory_latency=120)
    ).run(load_use_kernel())

    assert result.memory_bytes == 32 * 8 * 128
    assert result.dependency_stalls > 0
    assert result.idle_cycles > 0
    assert result.issue_utilization < 0.5
