"""V303: independent behavioral checks for write-coherent operand caching.

These tests deliberately avoid a value-carrying datapath. They verify the
necessary version-invalidation accounting, not numerical register correctness.
"""
from sim.vektor.pipeline import (
    DependencyTileSimulator, Instruction, TileConfig, Wave,
    dependency_fma_kernel, reuse_fma_kernel,
)


def _run(waves):
    return DependencyTileSimulator(
        TileConfig(operand_cache_entries=64, rf_read_ports_per_bank=16)
    ).run(waves)


def test_read_modify_write_cannot_hit_stale_source_version():
    wave = Wave(
        [Instruction("fp32", src=(0,), dst=0, latency=1) for _ in range(4)],
        wave_id=0,
    )
    result = _run([wave])
    assert result.instructions == 4
    assert result.rf_reads == 4
    assert result.operand_cache_hits == 0


def test_immutable_source_reuse_remains_a_hit():
    wave = Wave(
        [Instruction("fp32", src=(0,), dst=i + 1, latency=1) for i in range(4)],
        wave_id=0,
    )
    result = _run([wave])
    assert result.rf_reads == 1
    assert result.operand_cache_hits == 3


def test_write_invalidation_is_wave_local():
    waves = [
        Wave([
            Instruction("fp32", src=(0,), dst=0, latency=1),
            Instruction("fp32", src=(0,), dst=2, latency=1),
        ], wave_id=0),
        Wave([
            Instruction("fp32", src=(0,), dst=2, latency=1),
            Instruction("fp32", src=(0,), dst=3, latency=1),
        ], wave_id=1),
    ]
    result = _run(waves)
    assert result.rf_reads == 3
    assert result.operand_cache_hits == 1


def test_independent_version_oracle_lower_bound_on_dependency_kernel():
    # Every iteration reads a register written by the previous iteration
    # (except the first, which reads the initial version). Thus each of the
    # 64 dynamic source reads/wave is a new version; reg 1 is immutable.
    waves = dependency_fma_kernel()
    result = _run(waves)
    assert result.rf_reads >= 32 * (64 + 1)
    assert result.instructions == 32 * 64


def test_read_only_reuse_negative_control():
    # Destination registers 2..31 never alias immutable sources 0 and 1.
    # The 64-entry cache can retain the two sources for all 32 waves.
    result = _run(reuse_fma_kernel())
    assert result.rf_reads == 64
    assert result.operand_cache_hits == 32 * 64 * 2 - 64
