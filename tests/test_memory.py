from sim.vektor.memory import MemoryConfig, MemoryHierarchy


def test_cold_then_l1_hit():
    m = MemoryHierarchy()
    first = m.access(0x1000)
    second = m.access(0x1000)
    assert first.level == "dram"
    assert second.level == "l1"
    assert second.latency < first.latency


def test_l1_eviction_can_reveal_l2_hit():
    c = MemoryConfig(l1_sets=1, l1_ways=1, l2_sets=8, l2_ways=4)
    m = MemoryHierarchy(c)
    m.access(0)
    m.access(128)
    again = m.access(0)
    assert again.level == "l2"
    assert again.latency == c.l2_hit_latency


def test_l2_eviction_returns_to_dram():
    c = MemoryConfig(l1_sets=1, l1_ways=1, l2_sets=1, l2_ways=1)
    m = MemoryHierarchy(c)
    m.access(0)
    m.access(128)
    assert m.access(0).level == "dram"


def test_same_cache_line_hits():
    m = MemoryHierarchy()
    assert m.access(0).level == "dram"
    assert m.access(64).level == "l1"
