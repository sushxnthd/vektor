# V309 pre-registered opcode-aware Volta register-bank falsification (2026-10-30)

## Scope and evidence boundary
This is a **qualification/falsification experiment**, not a new architecture mechanism. V309 remains the only active Vektor research branch and draft PR #26. Retired V287/V296/V297-V308 must not be reopened. The original Purdue V100 Rodinia SASS archive is fixed by SHA-256 `aeb7de478785856e4ac834d12be0e71ab0df297f43fc02650e2ca90dea66d8b1`. Prior full-corpus bank totals and application identities have already been inspected; **no application in this archive is an unseen holdout**.

## External mechanism calibration
Jia et al., *Dissecting the NVIDIA Volta GPU Architecture via Microbenchmarking* (2018), section 3.5, report two 64-bit register banks, register index modulo-two assignment, and a bank-conflict signature for FFMA when three 32-bit source operands map to one bank. Reference: https://arxiv.org/abs/1804.06826 . This motivates a **conditional** 2 x 32-bit-read/bank idealization for FFMA; it does not establish arbitrary two-port RF hardware, nor per-opcode timing.

## Frozen analysis (before new opcode-conditioned corpus run)
For every active dynamic instruction row, count each distinct source register once (free intra-instruction broadcast), assume R255 is bypassed, and map remaining registers to bank `r % 2`. Let `d_b` be distinct source demand in bank `b`. Define `e_P=max(0,max_b(ceil(d_b/P))-1)`. Count `e_1` and `e_2` for P=1 and P=2. Independently classify **FFMA-family only** using exact base opcode `FFMA` (before the first period). Do not silently include DFMA, HFMA, IMAD, or unknown variants.

Primary outcome: `E_FFMA_P2 = sum(e_2 for active FFMA rows)` and `f=E_FFMA_P2/N_active`. Strong control: two-bank, P=2, free broadcast, R255 bypass, versus the older one-port all-opcode upper screen. Report `E_nonFFMA_P2`, per-family `E_FFMA_P2`, opcode base contributions, distinct-register counts, zero-mask exclusions, and count of FFMA rows with 3 distinct same-parity sources. The last count should equal `E_FFMA_P2` **only if** the corpus contains no FFMA instruction with >3 distinct non-R255 sources; otherwise report and investigate.

Predicted **win opportunity** at the isolated RF-service level: FFMA rows with 3 distinct non-R255 sources on one parity bank require 2 rather than 1 idealized service cycles for P=2; removing that conflict would save 1 idealized read-service cycle. Predicted **no-win**: FFMA rows with at most 2 distinct non-R255 sources, or with at most 2 on either bank, require <=1 idealized cycle. These are *row regimes*, not unobserved workload holdouts. Do not relabel them as prospective application-family validation.

### Pre-registered kill/advance decision
- If `f < 0.01`, **retire the FFMA-only bank-conflict hardware avenue as too small in this deliberately optimistic serialized-instruction proxy**, regardless of any per-application hotspot. This 1% cutoff is a resource-allocation screen, not a theorem about measured GPU speedup.
- If `f >= 0.01`, **do not promote hardware**: first reproduce the published FFMA microbenchmark and obtain paired V100 hardware counters or validated cycle simulation; then freeze new, disjoint workload families and compare matched-resource RTL/area/timing. The 1% threshold alone cannot justify hardware.
- If independent row parsing, archive hash, opcode semantics, or conservation checks fail, **fail closed** and publish the failure rather than a positive result.

The isolated serialized proxy `T_ideal=N+E_FFMA_P2` versus conflict-free `T'_ideal=N` implies a conditional throughput uplift of `E_FFMA_P2/N`; it is **not a universal GPU speedup upper bound**, because occupancy, collectors, overlap, scheduling and memory stalls are absent. An all-opcode `E_P2/N` screen is also reported as an intentionally overinclusive sensitivity bound. No Blackwell or RTX 5090 equivalence is inferred.

## Reproducibility
Use only pinned, no-cost public traces and GitHub Actions. Run an independent second parser that does not import the primary parser, plus adversarial mutation tests for FFMA classification, free broadcast, R255 bypass, zero-mask filtering, bank parity, and conservation. Preserve raw JSON and audit artifact. Never rewrite prior reports or prospective holdouts.
