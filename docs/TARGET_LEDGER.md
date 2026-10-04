# Target and evidence ledger

## Reference envelope

RTX 5090 is an **external comparison envelope**, not an implementation template. Authoritative NVIDIA product specifications were re-verified on 2026-10-04 and currently list:

| Quantity | RTX 5090 public specification | Vektor-1A hypothesis / target | Evidence status |
|---|---:|---:|---|
| CUDA cores / Vektor FP32 lanes | 21,760 CUDA cores | 160 tiles x 128 lanes = 20,480 lanes | architectural quantities are not directly equivalent |
| Boost clock | 2.41 GHz | 2.56 GHz | Vektor target only; no timing closure |
| Conventional peak FP32 FMA estimate | 104.8832 TFLOP/s* | 104.8576 TFLOP/s* | analytic projections only |
| AI throughput | 3,352 AI TOPS | 3,355.4432 sparse FP4 TOPS target | **not datatype-equivalent evidence**; NVIDIA product page does not define the displayed AI-TOPS datatype/sparsity basis sufficiently for a direct gate |
| RT throughput | 318 RT TFLOPS | no validated equivalent | Vektor FAIL/INCONCLUSIVE capability gap |
| Memory capacity | 32 GB GDDR7 | 32 GB GDDR7 target | target only |
| Memory interface | 512-bit | 512-bit | target only |
| External bandwidth | not stated on cited NVIDIA product page | 1,792 GB/s from 28 Gb/s-pin x 512-bit / 8 | Vektor projection; comparison requires separately sourced RTX bandwidth |
| Total graphics power | 575 W | <=575 W | Vektor target only; no power evidence |
| PCIe | Gen 5 | Gen 5 target | target only |

*The FP32 figures are derived arithmetic, not vendor claims: RTX estimate = 21,760 x 2 FLOP/FMA x 2.41 GHz = 104.8832 TFLOP/s; Vektor = 20,480 x 2 x 2.56 GHz = 104.8576 TFLOP/s. This near equality is useful only as a peak arithmetic target and is **not** evidence of architectural equivalence.

Authoritative source: NVIDIA GeForce RTX 5090 product specification page, checked 2026-10-04: https://www.nvidia.com/en-in/geforce/graphics-cards/50-series/rtx-5090/

### Target-ledger rule

Every external target must record (1) source, (2) verification date, (3) whether the number is vendor-stated or derived, and (4) semantic comparability. Numbers with ambiguous datatype, sparsity, boost residency, or workload meaning cannot be used as PASS evidence.

## 5090-class gate state

| Gate | State | Evidence / blocker |
|---|---|---|
| FP32 functional arithmetic | **PASS (reference only)** | exact fused binary32 oracle passed >=10,000 generated fmaf vectors plus directed IEEE-754 cases on research/fp32-fma-001 |
| FP32 synthesizable throughput | **INCONCLUSIVE** | exact 556-bit oracle is intentionally correctness-first and timed out in generic synthesis; bounded pipelined lane required |
| Matrix/tensor | **INCONCLUSIVE** | issue-resource model only; no standards-checked matrix RTL or datatype-specific PPA |
| Memory behavior | **INCONCLUSIVE** | executable non-blocking L1/L2/DRAM model exists; no controller/PHY implementation or broad workload validation |
| Graphics/raster | **INCONCLUSIVE** | not implemented |
| Ray traversal | **INCONCLUSIVE** | not implemented |
| Software execution | **INCONCLUSIVE** | KPX compiler/ISA execution path not yet end-to-end |
| Frequency | **INCONCLUSIVE** | 2.56 GHz architectural target only; no technology-mapped timing closure |
| Area | **INCONCLUSIVE** | no whole-tile / whole-GPU physical estimate |
| Power | **INCONCLUSIVE** | <=575 W target only; no credible whole-chip power model |
| Reproducibility | **PARTIAL** | deterministic simulation/RTL CI artifacts exist; full gate suite does not |
| Overall RTX 5090-class | **INCONCLUSIVE** | broad evidence gate intentionally unmet |

## Discovery Protocol V2 world model — target/FP32 slice

### KNOWN
- The exact fused FP32 reference provides a working correctness oracle for the current RNE/flag contract.
- A 556-bit shared-lattice implementation is expensive enough that the current generic Yosys flow did not complete within the imposed 180 s synthesis budget.
- Peak-FP32 arithmetic targets can be matched analytically by trading lane count against clock; this says nothing about realizable timing, area, power, utilization, or non-FP32 capability.

### BELIEVED
- A bounded-width, staged FMA can preserve bit-exact binary32 behavior while making synthesis tractable.
- The 2.56 GHz target will require explicit pipeline boundaries and technology-aware mapping; generic cell count alone cannot validate it.

### CONFLICTING
- Vektor-1A uses fewer nominal FP32 lanes than the RTX 5090 public CUDA-core count but a higher target clock. The analytic products nearly coincide, while physical feasibility is untested.

### FALSIFIED
- Treating the exact 556-bit correctness oracle as the production 128-lane/tile datapath is not a credible implementation path under the current synthesis budget.

### ANOMALOUS
- The near-exact peak-FP32 equality (104.8576 vs 104.8832 TFLOP/s) is an arithmetic consequence of chosen Vektor parameters, not an observed foothold. It must not bias architecture search toward preserving 160x128x2.56 if PPA evidence favors another point.

### UNTESTED
- Bit-exact bounded FMA equivalence over the existing oracle vectors.
- Initiation interval 1 after pipelining.
- Technology-mapped Fmax, area, and power proxy for one lane and replicated lane groups.
- Whether 128 lanes/tile remains Pareto-efficient once RF ports, bypass, operand distribution and scheduler wiring are included.

## Next decisive experiment

**FP32-PIPE-001 — DISCRIMINATION / CAPABILITY-BUILDING.** Implement a bounded-width staged FP32 FMA (classify/unpack -> 24x24 multiply -> exponent-difference shift-with-jam -> signed accumulate -> normalize -> RNE/pack), with ready/valid backpressure. Reuse the frozen exact-oracle vectors and add cycle-aware scoreboard tests.

Preregistered prediction: the bounded implementation will match all finite/special-case oracle results while allowing generic synthesis to complete inside the same 180 s budget. A mismatch falsifies the arithmetic transformation; a synthesis timeout after equivalence indicates that width reduction alone is insufficient and pipeline/resource decomposition becomes the next discriminator.

Cheapest next measurement after PASS: synthesize one lane and 4/8/16-lane replicated wrappers, record cell growth and critical structural operators, then decide whether the 128-lane/tile hypothesis deserves further investment.
