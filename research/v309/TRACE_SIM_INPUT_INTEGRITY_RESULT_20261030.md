# V309: authenticated legacy trace-to-simulator input integrity (2026-10-30)

**HOSTED PASS:** [GitHub Actions #41071848717](https://github.com/sushxnthd/vektor/actions/runs/41071848717), commit `895f0c6`. Frozen protocol `04ec3cc` preceded executable auditor `2321a4e`. Full JSON and selftest artifacts are preserved by the hosted workflow.

## Decisive corpus observation

The 2020-03-18 Purdue Tesla V100 Rodinia 2.0-ft archive, verified against SHA-256 `aeb7de478785856e4ac834d12be0e71ab0df297f43fc02650e2ca90dea66d8b1`, contains **11 `kernelslist.g` command lists and 210 `.traceg` files**. Parsing the original command lists without extracting or dereferencing tar links establishes:

| Source-attested property | Result |
|---|---:|
| Command lists | **11** |
| Kernel launch references | **210** |
| Exact same-directory launch-to-trace matches | **210/210** |
| Missing or ambiguous references | **0** |
| Weak basename-only fallback matches | **0** |
| Unreferenced trace files | **0** |
| Duplicate launch targets | **0** |
| Host-to-device memcpy commands | **351** |
| Trace prefixes with recognizable legacy NVBit rows | **210/210** |
| Historical tar link entries skipped | **11** |
| Unknown command lines | **0** |

The strict local-linkage gate **passes**. This is a meaningful advance from isolated trace analysis: all 210 SASS trace files have a corresponding, locally resolved launch in the original simulator input command lists. The 351 memory-copy commands are preserved in those lists and must not be dropped in a future simulator invocation. The hosted Python tests passed **one valid fixture and eleven negative controls** (missing, duplicate, ambiguous, unreferenced, weak fallback, traversal, malformed and non-UTF8 records).

## Inference boundary and next physicality gate

This establishes a **necessary input-identity condition only**. It does not establish that any particular version of `accel-sim.out` can parse these historical traces, that the simulated GPU configuration is calibrated, or that any cycles/counters correspond to hardware. The source producer's exact revision remains unverified. No hardware mechanism or speedup is promoted.

**Next decisive run:** Pin the historical simulator and GPGPU-Sim revisions and run **one bounded, low-cost, complete original `kernelslist.g` workload** under a pinned QV100-SASS configuration. Preserve every memcpy command; verify full trace parser completion; record simulator cycles, cache/DRAM counters, configuration SHAs, trace SHA and repeatability. If the binary cannot be built or the trace parser fails, preserve the negative evidence and do not infer performance. A passing simulation still requires matched hardware calibration and equal-resource architecture/RTL evidence before promotion.

V309 remains the sole qualification branch and draft PR #26. V287/V296 remain retired. Kernellum PR #119 untouched. No RTX-5090-equivalence claim.
