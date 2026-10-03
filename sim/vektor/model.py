from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path


@dataclass(frozen=True)
class VektorConfig:
    active_tiles: int
    fp32_lanes_per_tile: int
    clock_target_ghz: float
    fp4_dense_ops_per_tile_cycle: int
    structured_sparsity_multiplier: int
    texture_samples_per_tile_cycle: int
    rops_total: int
    memory_bus_bits: int
    gddr7_pin_rate_gbps: float

    @classmethod
    def from_json(cls, path: str | Path) -> "VektorConfig":
        raw = json.loads(Path(path).read_text())
        d = raw["design"]
        return cls(
            active_tiles=d["active_tiles"],
            fp32_lanes_per_tile=d["fp32_lanes_per_tile"],
            clock_target_ghz=d["clock_target_ghz"],
            fp4_dense_ops_per_tile_cycle=d["fp4_dense_ops_per_tile_cycle"],
            structured_sparsity_multiplier=d["structured_sparsity_multiplier"],
            texture_samples_per_tile_cycle=d["texture_samples_per_tile_cycle"],
            rops_total=d["rops_total"],
            memory_bus_bits=d["memory_bus_bits"],
            gddr7_pin_rate_gbps=d["gddr7_pin_rate_gbps"],
        )

    @property
    def fp32_tflops(self) -> float:
        # One FMA = two floating-point operations.
        return (
            self.active_tiles
            * self.fp32_lanes_per_tile
            * 2
            * self.clock_target_ghz
            / 1000
        )

    @property
    def fp4_dense_tops(self) -> float:
        return (
            self.active_tiles
            * self.fp4_dense_ops_per_tile_cycle
            * self.clock_target_ghz
            / 1000
        )

    @property
    def fp4_sparse_tops(self) -> float:
        return self.fp4_dense_tops * self.structured_sparsity_multiplier

    @property
    def texture_gtex_s(self) -> float:
        return (
            self.active_tiles
            * self.texture_samples_per_tile_cycle
            * self.clock_target_ghz
        )

    @property
    def pixel_gpix_s(self) -> float:
        return self.rops_total * self.clock_target_ghz

    @property
    def memory_bandwidth_gb_s(self) -> float:
        return self.memory_bus_bits * self.gddr7_pin_rate_gbps / 8

    def report(self) -> dict[str, float]:
        return {
            "fp32_tflops_target": self.fp32_tflops,
            "fp4_dense_tops_target": self.fp4_dense_tops,
            "fp4_sparse_tops_target": self.fp4_sparse_tops,
            "texture_gtex_s_target": self.texture_gtex_s,
            "pixel_gpix_s_target": self.pixel_gpix_s,
            "memory_bandwidth_gb_s_target": self.memory_bandwidth_gb_s,
        }
