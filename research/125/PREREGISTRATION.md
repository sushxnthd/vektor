# Vektor-125 preregistration — 2026-10-12

## Research class
CAPABILITY-BUILDING + DISCRIMINATION. No claim of GPU throughput or novelty.

## Hypothesis
An original one-issue/cycle Wave32 integer/predication RTL slice with 16 architectural registers/lane and 8 mask frames can reproduce the KPX-0 arithmetic and nested mask semantics from V124, including read-before-write for aliased destination/source registers. This is a **functional** claim, not a clock/area/power claim.

## Predeclared tests and acceptance
- 224 deterministic programs, seeds 125000..125223; 28 (12.5%) minimally guided surprise programs.
- Full-state equality at program end and mask/depth equality after **every** instruction, with intermediate register probes. Approximately 139k checks.
- Three independent software paths: V124 Python reference, V124 C++ reference, new per-step Python model; then RTL in Icarus.
- Compare `laneid`, `imm`, `add`, `mul`, `xor`, `iflt`, `else`, `endif`, `ballot`, `reduce_add`. Check unsigned less-than, wraparound, nested/empty masks, in-place destination aliases.
- Test invalid ELSE/ENDIF/opcode with no state mutation; stack overflow directed test is next if initial random traces do not reach depth 8.
- RTL PASS requires an actual Icarus compile and execution. Python/C++ agreement alone cannot pass RTL.
- PPA/area/frequency require independent synthesis and STA. No PPA conclusions from source code.

## Mechanism, predictions and discrimination
Prediction P1: 224/224 final states match independent models; residual 0. Prediction P2: every mask/depth transition and all checked registers match Icarus. P3: invalid operations assert fault and leave state unchanged. If P2 fails, minimize by opcode, alias class, active-mask structure, and stack depth before modifying RTL. Compare the full combinational 32-lane reduction against a balanced tree in a subsequent equal-budget synthesis experiment.

## Competing explanations and limitations
Agreement can be due to shared specification mistakes, because the three software implementations implement the same defined contract. The V124 C++ interpreter is independently coded, but it is not independent from the published semantics. The RTL has a behavioral register array, combinational integer multiplication, and a serial reduction expression; no memory operations, pipelines, physical register banking, or graphics/tensor/ray execution. Icarus passing would not demonstrate timing closure or hardware manufacturability.

## Adversarial roles
Explorer: integer/mask slice. Skeptic: 32-wide multiplication and serial reduction could violate 2.56GHz. Experimentalist: adversarial masks, aliasing, stack depth, invalid opcodes. Analyst: separate software agreement from RTL validation. Anomaly Hunter: cluster any mismatches by op, depth, alias and mask population. Prior-art Auditor: predicated SIMD/SIMT integer ALUs are established; Vortex and other open GPUs provide stronger baseline context. Replicator: V124 C++ + separate new per-step Python. Theorist: read-before-write is required for same-cycle register alias semantics; no new architectural law claimed.
