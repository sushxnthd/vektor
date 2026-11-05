# V309 external GV100 profiler-counter audit: naive miss-to-DRAM proxy falsified (2026-10-30)

**Status:** HOSTED PASS, exploratory public counter evidence, **not matched** to V309's historical Rodinia 2.0-ft SASS traces. No hardware mechanism promoted.

## Evidence and provenance

- [Exploratory protocol](EXTERNAL_PROFILER_COUNTER_AUDIT_PROTOCOL_20261030.md), committed before implementation at `e1b611c`. The public CSV was already inspected during hypothesis formation, so this is **not** a prospective unseen-data validation.
- [Executable Python auditor](external_profiler_counter_audit.py), Python 3.11 standard library, independently cross-checked Decimal arithmetic, malformed-input rejection, fail-closed Git blob identity.
- [Hosted audit #41025536955](https://github.com/sushxnthd/vektor/actions/runs/41025536955) **PASS**: parser mutation tests, independent arithmetic oracle, immutable upstream download and complete sample audit. Artifact: `v309-external-profiler-counter-audit`.
- Source: [Accel-Sim sample GV100 hardware-profiler counters](https://github.com/accel-sim/accel-sim-framework/blob/7ba54ded60c4ba0083410c37d22d719166acd6dc/util/accelwattch/accelwattch_hw_profiler/hw_perf.csv), commit `7ba54ded60c4ba0083410c37d22d719166acd6dc`, Git blob `aa88bb2566ff3b3e012442cd20bc753127732cac`. These are **published sample counters**, not independently remeasured or independently authenticated hardware logs. Counter units and aggregation conventions are not established by this audit.

## Observations

| Audited quantity | Result |
|---|---:|
| Published kernel rows | 25 |
| Distinct benchmark families | 19 |
| Rows with `L1_RM=0` but `DRAM_Rd>0` | **5** |
| Rows with `L2_RM=0` but `DRAM_Rd>0` | **3** |
| Rows with positive L1 read misses and DRAM reads | 20 |
| Minimum `DRAM_Rd/L1_RM` | **0.01266574931** (sobolQRNG) |
| Maximum `DRAM_Rd/L1_RM` | **1.032155649** (backprop-rodinia-3.1, adjust weights) |
| Spread among positive-denominator ratios | **81.49187413×** |
| Rows with >1% relative difference `abs(DRAM_Rd-L2_RM)/DRAM_Rd` | **4** |

The five L1-zero counterexamples occur in `kmeans-rodinia-3.1`, `dct8x8`, `binomialOptions`, and two `quasirandomGenerator` kernels. Three of these (`binomialOptions` and two `quasirandomGenerator` kernels) also have zero reported L2 read misses but positive reported DRAM reads. **A universal zero-intercept multiplicative mapping from either L1_RM or L2_RM alone to DRAM_Rd cannot reproduce this published sample.**

This does **not** prove that L1 or L2 miss counters are intrinsically invalid. The columns can count different operations or address spaces; aggregation, bypass paths, profiler definitions, and sample normalization may explain discrepancies. Their exact semantics require verification before quantitative interpretation. The 81.49× spread is **not** a cache-hit-rate or byte-traffic multiplier.

## Hardware-research consequence

The preceding V309 synthetic sector-to-line-fill falsification had no external profiler evidence. This run adds an independent, publicly sourced **counter-domain mismatch falsification**, not a hardware speedup. It prevents treating SASS sector counts, L1 misses, L2 misses, and DRAM reads as interchangeable without a calibrated translation.

**Critical provenance failure:** V309's 210 historical traces were drawn from `rodinia_2.0-ft`, while the sample contains `rodinia-3.1` and other benchmark families. Kernel names, problem sizes, hardware config, trace producer and profiling run identity are not matched. Thus no sector-count-to-DRAM regression, latency model, causal hardware claim, or unseen-workload prediction is permitted from joining these sources.

**Kill:** universal zero-intercept L1_RM-only and L2_RM-only DRAM_Rd proxy claims for this published sample. **Keep:** the external data as a counter-semantics caution and reproducible negative result. No new architecture candidate is promoted; V287/V296 are not revived.

**Next decisive gate:** obtain a *matched* source-authenticated trace, per-kernel profiler counters (including read/write sectors, L1/L2 hit/miss, DRAM transactions, stalls and occupancy where available), and a cycle-model calibration with explicit hardware and workload identifiers. Only then qualify one physical mechanism and proceed through equal-resource RTL/synthesis/timing/electrical gates. Existing source-conditional sector interval and all earlier falsifications remain unchanged.

No RTX-5090-equivalence claim. Kernellum PR #119 remains independent and untouched.
