from sim.vektor.cycle import KernelWork, TileSimulator
from sim.vektor.model import VektorConfig


def config() -> VektorConfig:
    return VektorConfig.from_json("specs/vektor_1a.json")


def test_peak_targets_are_derived_from_topology():
    c = config()
    assert abs(c.fp32_tflops - 104.8576) < 1e-9
    assert abs(c.fp4_dense_tops - 1677.7216) < 1e-9
    assert abs(c.fp4_sparse_tops - 3355.4432) < 1e-9
    assert abs(c.texture_gtex_s - 1638.4) < 1e-9
    assert abs(c.pixel_gpix_s - 450.56) < 1e-9
    assert abs(c.memory_bandwidth_gb_s - 1792.0) < 1e-9


def test_single_tile_peak_resource_accounting():
    sim = TileSimulator()
    result = sim.run(
        KernelWork(
            fp32_ops=256 * 100,
            fp4_matrix_ops=4096 * 100,
            memory_bytes=256 * 100,
        )
    )
    assert result.cycles == 100
    assert result.fp32_utilization == 1.0
    assert result.matrix_utilization == 1.0
    assert result.memory_utilization == 1.0


def test_bottleneck_is_visible_in_utilization():
    sim = TileSimulator()
    result = sim.run(
        KernelWork(
            fp32_ops=256 * 100,
            fp4_matrix_ops=4096 * 25,
            memory_bytes=256 * 50,
        )
    )
    assert result.cycles == 100
    assert result.fp32_utilization == 1.0
    assert result.matrix_utilization == 0.25
    assert result.memory_utilization == 0.5
