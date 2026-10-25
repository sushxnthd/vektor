# V296: hosted mapped-synthesis falsification of the parallel-threshold timing-repair hypothesis

**2026-10-26. Mechanism: V296 only. V287 remains retired. Evidence tier: hosted Icarus RTL + Yosys/ABC Nangate45 combinational mapping, not extracted STA, routed timing, GPU throughput or power.**

## Frozen trial and provenance

The previously committed PARALLEL_THRESHOLD_TOPOLOGY_PREREG_20261026.md hypothesized that replacing procedural hit-count additions with explicit pairwise equalities and parallel two-hit detection could improve the V296 priority-greedy arbiter topology without changing its four-slot, two-operand, two-read-ports-per-bank semantics. The unchanged V296 arbiter, rewritten variant, and serial one-hot comparator were mapped using the same library and synthesis script.

Hosted [workflow 40224543790](https://github.com/sushxnthd/vektor/actions/runs/40224543790) **completed successfully** on source commit a9904d3a75ba0b8d3acad5d009cfa2f35ffa644f. Download the original [artifact 12612060538](https://github.com/sushxnthd/vektor/actions/runs/40224543790/artifacts), whose ZIP SHA-256 is 1a2782cd35befa806fb49179d83b289473ada29a21ae693796bae97f3b35e861. Its Nangate45 typical Liberty SHA-256 is 8d540a4d4cf6d09d27c87ad067857a9c0c2eeb023ab7a56e058cd3113db4e9b1; Yosys reports version 0.9 (1979e0b). The hosted suite passed 164,976 RTL comparisons and 164,976 independent oracle cases. These are finite tests, **not universal formal equivalence**.

## Matched mapped combinational measurements

| Top-level implementation | Nangate45 mapped area (µm²) | Mapped cells | Yosys LTP edges |
|---|---:|---:|---:|
| Original V296 pairwise arbiter | 278.236 | 204 | 11 |
| V296 parallel-threshold rewrite | **257.754** | **201** | **13** |
| Serial one-hot control | 727.244 | 677 | 20 |

The rewrite saves **20.482 µm² (7.3614%)** of *arbiter-only* mapped area and three cells (1.4706%) relative to original V296, but its longest mapped graph path grows by **two edges (18.1818%)**. These graph edges are not nanoseconds. This is an equal-I/O-width and equal-bank-port comparison, **not an equal-consumed-area tile-level physical comparison**. In particular, serial one-hot remains an independently optimizable control, not a demonstrated physical Pareto optimum.

**Falsification:** reject the specific hypothesis that this rewrite improves mapped combinational **logic-depth proxy**. It retains an area-proxy benefit, but there is **no demonstrated STA or physical timing advantage**. The RTL variant must not be promoted to the integrated physical repair merely because the hosted CI succeeded. Nor can this evidence prove the variant's routed delay is worse: cell types, fanout, drive strengths, placement and RC could reverse a topological ordering.

## Independent reproduction and corruption test

The committed independent [checksum-locked checker](v296_parallel_threshold_mapped_audit.py) reads the original hosted ZIP and verifies the pinned library, finite RTL/oracle PASS markers, all three mapped areas, mapped cell counts and path-edge lengths. The accompanying [machine-readable results](V296_PARALLEL_THRESHOLD_HOSTED_SYNTH_AUDIT_20261026.json) preserve the exact observations. Locally, deliberately changing the RTL PASS marker to FAIL caused the checker to exit 2; the original unmodified archive passed. Reproduce using:

    python3 research/v296/v296_parallel_threshold_mapped_audit.py v296-parallel-threshold-rtl-synthesis.zip --expected-zip-sha256 1a2782cd35befa806fb49179d83b289473ada29a21ae693796bae97f3b35e861

GitHub artifacts may expire. The SHA-pinned original is the evidence; do not silently substitute a fresh synthesis run.

## Decision

**Keep V296 as the sole active architecture mechanism; do not advance the parallel-threshold RTL topology as a proven timing repair.** Preserve this mixed/negative result. The earlier *integrated* matched physical results still fail frozen 3.5 ns setup, hold and capacitance requirements. Next discriminating gate: freeze one equal-resource integrated scheduler-to-executed-data cone repair and independently optimized serial control; require extracted post-route setup, hold, capacitance/slew, wire/load sensitivity and feasible-clock workload evaluation. Kill the implementation variant if matched physical closure or bandwidth eliminates the gain. No GPU speedup, measured power reduction or RTX-5090 equivalence is established. Kernellum PR #119 and its holdouts are untouched.
