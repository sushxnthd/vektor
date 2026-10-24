# V296 preregistration: matched I/O-boundary geometry sensitivity (2026-10-25)

## Distinct physical intervention and prior failure
The preceding **placement-seed** experiment was blocked by the pinned OpenROAD binary: `global_placement -random_seed` is unsupported. Its two failures and independent archives are preserved in `CTS45_SEED_REPLICATION_TOOL_INCOMPATIBILITY_20261025.md`; no physical replication claim follows. This is a **new, separate I/O-geometry sensitivity experiment**, not a relabeling or rescue of the seed protocol.

Freeze exactly two boundary perturbations **before any new physical results**: `place_pins -hor_layers metal5 -ver_layers metal6 -exclude top:*` and the same command with `-exclude bottom:*`. These redistribute physical pin locations while keeping pin count, RTL, ports, controller resources, die/core area, timing constraints, 3.5 ns clock, 45% density, 2x extracted RC, 5 fF output loading, fanout-16 policy, 250 ps post-CTS setup-repair margin, and the serial control's extra optimization round identical. No variant-specific placement constraints. The original unmodified geometry is a historical reference, not a third prospective case. This intervention probes physical wire/topology sensitivity, **not** standard-cell placement seed variation.

Generate each Tcl/shell chain from the immutable setup250 source with exact-anchor checks and SHA-256 manifests. Do not change any original frozen experiment. If the pinned OpenROAD binary rejects `-exclude`, record tool incompatibility rather than silently changing the physical intervention.

## Frozen success/falsification gate
For **both** I/O geometries, require both contestants to finish routed CTS with propagated clocks and extracted OpenRCX parasitics, <=7400 um² controller area, >=50 ps setup slack, nonnegative hold, zero max-slew/max-cap/DRC violations. V296 must retain >=10% lower controller cell area and >=200 ps extracted setup advantage **in each** geometry. All four implementations count; no best-case selection. The independent checker returns `BOTH_PIN_GEOMETRIES_FEASIBLE_PARETO_SUPPORTED`, `PIN_GEOMETRY_ROBUSTNESS_FALSIFIED`, or `INCOMPLETE_NO_PIN_SENSITIVITY_CLAIM`. Report failures and per-case evidence without tuning thresholds.

A pass supports only robustness to these two pin-boundary changes. It does **not** prove arbitrary wire/load tolerance, independent placement-seed replication, strict equal-consumed-area, integrated GPU-tile timing, measured power, signoff, or unseen-workload speedup.

## Workload law and isolation
V296's arbitration semantics are unchanged, so at fixed tile clock and matched resources/ports the throughput improvement is zero. The necessary positive law remains `T=min(I*occupancy/((1+overhead)*max(controller_period,other_tile_period)), bandwidth_GBps/bytes_per_op)`. Freeze and preserve existing win/no-win holdouts until measured tile clocks and traffic exist. V296 is the sole active mechanism; V287 stays retired. Kernellum PR #119 is separate and unchanged.

Reproduce: `python3 research/v296/pin_geometry.py --self-test`; `python3 research/v296/pin_geometry.py --edge top`; `python3 research/v296/pin_geometry.py --edge bottom`; `python3 research/v296/pin_geometry.py --aggregate build/v296/cts45_pin_stress`.
