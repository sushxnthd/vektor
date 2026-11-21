# V317: forwarding freshness and generic RTL gate (2026-11-01)

**Decision: do not promote same-register forwarding as a novel GPU architecture mechanism.** The prior name-only sharing oracle is unsafe under warp aliasing and intervening writes. The new conservative admission RTL is synthesizable and passes hosted tests, but an equally informed reuse-aware baseline can instantiate the same forwarding path. This is a correctness/physical-feasibility gate, **not** a measured GPU speedup or a positive architecture result.

## Prospective provenance

The [frozen protocol](FROZEN_FORWARDING_FRESHNESS_RTL_GATE_20261101.md) was committed at `a01694f` before checker implementation or RTL evaluation. The checker, RTL, testbench and dedicated CI workflow were committed at `5b1835a`; a SystemVerilog directive typo was corrected at `1034ff8` before the successful final-commit CI. This report distinguishes independent value semantics from RTL simulation and generic synthesis.

## Exact semantic audit

Exhaustive 2-lane worlds vary producer/consumer warp, register, bank, captured mask, requested mask, intervening dirty mask, captured 1-bit lane values, and current values. Worlds with identical physical location constrain unwritten lanes to retain their values. Results:

| Metric | Count |
|---|---:|
| Legal worlds enumerated | 46,464 |
| Conservative provenance/freshness gate admissions | 416 |
| Unsafe admissions by conservative gate | **0** |
| Naive textual-register identity admissions | 21,888 |
| Naive admissions lacking provenance or captured-lane proof | **20,992** |
| Naive admissions returning incorrect requested values | **12,160** |

The 20,992 number is **unjustified admissions**, not necessarily 20,992 observed wrong outputs; 12,160 is the distinct observed wrong-value count. The conservative rule requires a live buffered value, matching warp/register/bank, captured requested lanes and zero writes to requested lanes since capture. A masked write to a disjoint lane does not invalidate clean requested lanes. These results rely on complete write monitoring, which is **not yet implemented or verified at tile level**.

For 1-, 2-, 3- and 4-bit version tags, a cache entry can be stale after 2, 4, 8 and 16 writes respectively even when the tag wraps back to its original value. Sticky dirty bits reject these cases. This is a finite-tag alias counterexample, not an empirical GPU register-cache characterization.

## Hosted RTL and generic synthesis

[GitHub Actions run #41248754956](https://github.com/sushxnthd/vektor/actions/runs/41248754956) passed on commit `1034ff8`. Independent Python tests passed; Icarus Verilog simulated **4,102** cases (4,096 exhaustive 4-lane mask combinations and six directed provenance controls). Yosys 0.33 synthesized the parameter-default combinational forwarding admission/data mux:

- **72 generic logic cells**: 43 ANDNOT, 4 AND, 4 NAND, 1 NOR, 12 OR, 8 XOR;
- **10 logic levels** along the reported longest topological path from requested-warp bit to forwarded-data bit;
- no state elements or actual buffered-value storage included in this block.

These are **generic logic counts and a topology proxy only**. No standard-cell library, floorplan, wire parasitics, register-file macros, clock constraints, placed/routed timing, electrical signoff, energy or equal-area performance comparison is claimed. The dirty-mask tracking, source buffer, invalidation broadcast, and forwarding wiring are external and uncosted. Thus 72 cells is **not** the full physical cost of a correct forwarding mechanism.

## Matched-resource comparator and research decision

A reuse-aware compiler/collector baseline with the same physical metadata, write visibility, buffer and forwarding resources can apply the identical rule. On the explicitly modeled legal cases, the candidate has **zero incremental transaction advantage** over that comparator. A weaker name-only baseline would be unsafe and cannot establish novelty. The forwarding gate is useful as a reusable correctness primitive, but not a promoted hardware architecture result.

**Next decisive experiment:** source a provenance-pinned dynamic GPU operand trace, build complete lane-version/write monitoring and a matched collector/RF-cache baseline, then measure physical RTL PPA and workload traffic. Do not reanimate V287 or V296 based on this evidence. No RTX 5090 equivalence is claimed.
