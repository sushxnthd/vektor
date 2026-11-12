#!/usr/bin/env python3
"""Independent V315 capacity-law checker; never uses candidate's f_star."""
import json
import subprocess
import sys

from remat_capacity_screen import REGIMES, W, P, A, N

def envelope(d, f, q, c):
    # Independent per-instruction bottleneck calculation.
    reads = d - d*q*f
    compute = 1 + c*d*q*f
    return max(1/W, reads/P, compute/A)

def main():
    output = subprocess.check_output([sys.executable, "research/v315/remat_capacity_screen.py"], text=True)
    result = json.loads(output)
    for name, (seed, ds, q, cost) in REGIMES.items():
        row = result["regimes"][name]
        assert row["seed"] == seed
        for d, f in zip(ds, row["frozen_f_star"]):
            # A fully independent numerical grid must agree with the derived
            # crossover to within a 0.001 discretization interval.
            fgrid = min((i/1000 for i in range(1001)),
                        key=lambda x: envelope(d, x, q, cost))
            assert abs(fgrid - f) < 0.002, (name, d, fgrid, f)
        for d, sampled in zip(ds, row["sampled_hot_reads"]):
            assert abs(sampled/(N*d)-1) < 0.02, (name, d, sampled)
        assert row["measured_resource_cycles_phase_oracle"] <= row["measured_resource_cycles_dynamic"]+1e-8
        assert row["measured_resource_cycles_hindsight_static"] <= row["measured_resource_cycles_static"]+1e-8
        assert row["incremental_gain_vs_equal_information_phase_aware"] == 1.0
        assert not row["novelty_gate_pass"]
    print("PASS: independent resource-law grid, sampled demand, matched controls, novelty no-go")

if __name__ == "__main__":
    main()
