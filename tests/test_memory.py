from sim.vektor.memory import CacheConfig, MemoryHierarchy, MemoryHierarchyConfig
from sim.vektor.pipeline import DependencyTileSimulator, addressed_load_use_kernel


def small_memory_config(**overrides):
    values = {
        "l1": CacheConfig(256, 64, 1, 4, 4),
        "l2": CacheConfig(4096, 64, 4, 20, 4),
        "dram_latency": 50,
        "dram_requests_per_cycle": 2,
        "mshrs": 8,
    }
    values.update(overrides)
    return MemoryHierarchyConfig(**values)


def test_dram_fill_becomes_l1_hit():
    memory = MemoryHierarchy(small_memory_config())
    cold = memory.issue(1, 0)
    assert cold is not None and cold.level == "dram"
    memory.advance(cold.completion_cycle)
    hot = memory.issue(cold.completion_cycle + 1, 0)
    assert hot is not None and hot.level == "l1"
    assert memory.stats.dram_misses == 1
    assert memory.stats.l1_hits == 1


def test_same_line_miss_merges():
    memory = MemoryHierarchy(small_memory_config())
    first = memory.issue(1, 0)
    second = memory.issue(2, 32)
    assert first is not None and first.level == "dram"
    assert second is not None and second.level == "merged"
    assert second.completion_cycle == first.completion_cycle
    assert memory.stats.merged_misses == 1
    assert memory.stats.dram_misses == 1


def test_mshr_limit_backpressures_new_line():
    memory = MemoryHierarchy(small_memory_config(mshrs=1))
    assert memory.issue(1, 0) is not None
    assert memory.issue(2, 64) is None
    assert memory.stats.mshr_stalls == 1


def test_l1_eviction_can_reveal_l2_hit():
    memory = MemoryHierarchy(small_memory_config())
    a = memory.issue(1, 0)
    assert a is not None
    memory.advance(a.completion_cycle)

    # 256B is the next line mapping to the same direct-mapped L1 set.
    b = memory.issue(a.completion_cycle + 1, 256)
    assert b is not None and b.level == "dram"
    memory.advance(b.completion_cycle)

    again = memory.issue(b.completion_cycle + 1, 0)
    assert again is not None and again.level == "l2"
    assert memory.stats.l2_hits == 1


def test_pipeline_cold_unique_loads_reach_dram():
    memory = MemoryHierarchy(small_memory_config(dram_latency=30, mshrs=8))
    result = DependencyTileSimulator().run(
        addressed_load_use_kernel(wave_count=4, iterations=1, line_bytes=64),
        memory=memory,
    )
    assert memory.stats.dram_misses == 4
    assert result.dependency_stalls > 0
    assert result.cycles >= 30


def test_pipeline_shared_line_merges_outstanding_misses():
    memory = MemoryHierarchy(small_memory_config(dram_latency=30, mshrs=8))
    result = DependencyTileSimulator().run(
        addressed_load_use_kernel(
            wave_count=8,
            iterations=1,
            working_set_lines=1,
            line_bytes=64,
        ),
        memory=memory,
    )
    assert memory.stats.dram_misses == 1
    assert memory.stats.merged_misses >= 1
    assert result.instructions == 16
