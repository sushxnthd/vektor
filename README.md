# Vektor

Vektor is Kernellum's open research program for contemporary massively parallel GPU architecture.

The long-term engineering target is a fully specified, independently designed GPU architecture whose measured, simulated, synthesized, and projected evidence can be compared rigorously with current high-end GPUs, with RTX 5090-class capability as the initial reference envelope.

## Status

**Research / pre-silicon.** Vektor does not currently claim RTX 5090 equivalence. Peak-throughput arithmetic, simulation results, synthesis results, power/area estimates, and silicon measurements are tracked separately.

The initial architecture hypothesis is **Vektor-1A**. Work proceeds through executable simulation, RTL, verification, synthesis, benchmarks, and architecture search.

## Research rule

Every headline claim must follow:

`claim -> implementation -> experiment -> measurement`

Negative results and failed hypotheses are preserved.

## Repository layout

- `docs/` architecture specifications and research ledger
- `specs/` machine-readable architecture configurations
- `sim/` executable architectural models
- `rtl/` synthesizable hardware
- `compiler/` KPX ISA/compiler work
- `benchmarks/` compute, graphics, tensor, and ray workloads
- `experiments/` architecture-search experiments
- `verification/` formal and simulation verification
- `ppa/` timing/area/power evidence
- `evidence/` frozen experiment artifacts and claim boundaries

Vektor is developed as a Kernellum research program.
