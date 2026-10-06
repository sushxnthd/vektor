#!/usr/bin/env python3
"""Vektor compute/memory roofline phase-boundary experiment.

This is an analytic model, not silicon evidence. It makes the Vektor-1A peak
targets executable and identifies the arithmetic-intensity boundary at which
the configured external-memory interface stops being the first-order roof.
"""
from dataclasses import dataclass
import json

@dataclass(frozen=True)
class Config:
    tiles: int = 160
    fp32_lanes_per_tile: int = 128
    clock_ghz: float = 2.56
    fp32_flop_per_lane_cycle: int = 2
    mem_bus_bits: int = 512
    mem_pin_gbps: float = 28.0

def evaluate(c: Config):
    fp32_tflops = c.tiles*c.fp32_lanes_per_tile*c.clock_ghz*c.fp32_flop_per_lane_cycle
    bandwidth_gbs = c.mem_bus_bits/8*c.mem_pin_gbps
    ridge = fp32_tflops*1000/bandwidth_gbs
    probes=[]
    for intensity in [1,2,4,8,16,32,48,56,58,59,64,96,128]:
        memory_roof_tflops = intensity*bandwidth_gbs/1000
        attainable=min(fp32_tflops,memory_roof_tflops)
        probes.append({"flop_per_byte":intensity,
                       "roof_tflops":round(attainable,6),
                       "limiter":"memory" if memory_roof_tflops < fp32_tflops else "compute",
                       "peak_fraction":round(attainable/fp32_tflops,6)})
    return {"evidence_type":"analytic_model",
            "fp32_peak_target_tflops":fp32_tflops,
            "external_bandwidth_target_gbs":bandwidth_gbs,
            "fp32_ridge_flop_per_byte":ridge,
            "probes":probes}

if __name__ == "__main__":
    print(json.dumps(evaluate(Config()),indent=2,sort_keys=True))
