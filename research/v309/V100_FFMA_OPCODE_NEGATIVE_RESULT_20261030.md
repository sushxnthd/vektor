# V309: opcode-aware FFMA bank-conflict avenue RETIRED (2026-10-30)

**Decision: RETIRE FFMA-only register-bank-conflict hardware in the examined V100 Rodinia corpus under the frozen 1% conditional-service screen.** No hardware mechanism promoted. V309 remains a qualification workstream, not a GPU IPC claim.

## Prospective-protocol status and provenance

- [Frozen protocol](FFMA_OPCODE_GATE_PROTOCOL_20261030.md) committed as `19c4f17` **before** the new opcode-conditioned full-corpus experiment. This is a frozen *analysis*, not a previously unopened workload-family holdout: the 11 application families and prior aggregate bank results had already been inspected.
- Source: original Purdue 2020 Tesla V100 Rodinia SASS archive, SHA-256 `aeb7de478785856e4ac834d12be0e71ab0df297f43fc02650e2ca90dea66d8b1` (21,011,152 compressed bytes). [Source archive](https://engineering.purdue.edu/tgrogers/accel-sim/traces/tesla-v100/2020.03.18/rodinia_2.0-ft.tgz).
- [Hosted independent CI #40961786911](https://github.com/sushxnthd/vektor/actions/runs/40961786911) **PASSED**, including full-corpus primary decoder, independent redecoder, SHA check and eight adversarial mutation fixtures.
- [Raw primary JSON and independent audit artifact #12936132622](https://github.com/sushxnthd/vektor/actions/runs/40961786911/artifacts/12936132622).
- Earlier CI #40961138370 and #40961512509 **failed closed** because the independent auditor initially attributed tar paths with a leading `./` to the wrong application. The primary profile itself was not altered. The independent auditor's path normalization was repaired in `25a2c91`; the final hosted audit passed. Both failures remain visible.

## Physically informed opcode-specific result

Reference: Jia, Maggioni, Staiger and Scarpazza, *Dissecting the NVIDIA Volta GPU Architecture via Microbenchmarking* (2018), section 3.5, https://arxiv.org/abs/1804.06826. They report two 64-bit banks, index-modulo-two assignment and an FFMA conflict signature when three 32-bit source operands map to one bank.

We count each distinct source register once (free duplicate-source broadcast), assume R255 bypass, and use the **idealized** ability to serve two 32-bit FFMA reads per bank per cycle. No actual collector, bypass, stall or throughput measurement is inferred.

| Authenticated dynamic SASS descriptor | Count |
|---|---:|
| Active instruction rows, 11 applications | 3,937,565 |
| Active FFMA-family rows | 252,336 |
| FFMA rows with 3 distinct non-R255 sources | 68,788 |
| FFMA rows with all 3 sources on one modulo-two bank | **84** |
| FFMA rows with >3 distinct non-R255 sources | 0 |
| FFMA isolated extra bank-service cycles, P=2 | **84** |
| All-opcode P=2 isolated extra cycles (overinclusive sensitivity) | 39,413 |
| Non-FFMA P=2 isolated extra cycles | 39,329 |

All **84** FFMA conflict opportunities occur in LUD (84/30,528 active LUD rows); the other ten application families have zero. The independently checked identity `FFMA_P2_extra = FFMA_three_same_bank = 84` holds because no FFMA row has more than three distinct non-R255 sources.

### Compact opportunity law, not a new architecture law

For this corpus and idealized isolated FFMA service:

```
f = Pr(FFMA) * Pr(three same-bank distinct sources | FFMA)
  = (252336 / 3937565) * (84 / 252336)
  = 84 / 3937565
  = 0.00002133298117 = 0.0021333%.
```

Thus the unrealistic fully serialized instruction-service proxy `T=N+84` versus conflict-free `T'=N` has only **0.0021333%** modeled throughput headroom. This is **not a bound on real GPU speedup**: actual stall exposure, occupancy, collector overlap, memory latency, instruction weighting and scheduling are absent.

The frozen retirement threshold was **1%** in this proxy, so the FFMA-only hardware avenue fails by roughly 469x. Do not advance it to RTL or reinterpret an application-specific post-hoc hotspot as a prospective win.

### Why the earlier all-opcode residual was misleading

The earlier 39,413 P=2 residual was treated as an all-opcode conditional sensitivity. The new opcode split shows **36,779 (93.3169%) arise from DFMA** and another 2,550 from LEA, versus only 84 from FFMA. **DFMA has 64-bit operands, so a two-32-bit-read/bank FFMA idealization is not a validated physical DFMA service model.** The all-opcode residual must not be used as a calibrated stall estimate or a hardware-opportunity claim.

## What remains unproven

No matched V100 hardware counters, validated cycle simulation, actual RF/collector timing, occupancy model, workload-level speedup, RTL/synthesis, area/power, electrical signoff, prospective independent workload-family transfer or RTX 5090 equivalence. The result is a reproducible **negative architecture qualification**, not a world-class finished GPU.

**Next gate:** retire FFMA-only bank hardware; use authenticated traces and opcode-width-aware resource accounting to identify a distinct measured bottleneck. Before introducing another hardware mechanism, freeze new independent workload families and predictions, calibrate against real counters or a validated simulator, and require matched-resource physical evaluation. Retired V287/V296/V297–V308 remain retired. Kernellum PR #119 unchanged.
