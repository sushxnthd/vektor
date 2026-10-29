# V308: frozen two-bank operand-collector falsification protocol (2026-10-29)

## Status and objective
**Provisional mechanism, not accepted architecture.** Test whether completion-aware per-bank partial operand admission beats a strong shortest-remaining-operands (SRPT) control under identical resources. This is a *synthetic feasibility screen*, NOT a reproduced real GPU workload bottleneck. Do not promote to RTL or claim novelty from a weak FIFO comparison.

Prior work V296 and V307 is retired by its existing no-go reports. V287 is historical. The goal here is to reject unsupported bank-scheduling mechanisms early and establish a conservation boundary for a physically plausible two-bank independent scheduler domain.

## Fixed model
- Two independent RF banks, one read per bank per cycle, four finite operand-collector slots.
- Two source reads per instruction, including same-bank sources; operands may be read on different cycles.
- One instruction admitted per cycle when a collector slot is free; no issue-stage overlap beyond these explicit capacities.
- Identical trace and capacity for all three policies: OLDEST, SRPT (strong simple control), COMPLETION (candidate).
- No writeback, cache, scoreboard dependencies, bypass, execution, memory system, power, wires, or timing. These omissions prohibit any GPU IPC claim.
- Exhaustive legal per-bank grant enumeration with deterministic tie-break; every read is accounted for.
- The model intentionally grants no unpriced extra bank ports or collector entries.

## Frozen prospective regimes
Pilot seeds 31–34 are OPENED; 1,200 instructions per trace. Observed pilot candidate throughput gain vs SRPT: IID +0.2689%, SKEW 0%, ALTERNATING 0%, MIXED 0%, ALL_CROSS 0%. These observations are disclosed **before** any prospective seeds are opened.

**Predicted-win W1:** IID two-source bank mapping, seed set 1001–1008. Candidate must improve mean per-seed throughput by **at least 5% versus SRPT**; also report versus OLDEST. A result below 5% kills the candidate without RTL investment.

**Predicted-no-win N1:** ALL_CROSS, same prospective seeds, expected <=1% absolute throughput change versus SRPT. A no-win result does not rescue W1 failure.

Additional fixed sensitivity: SKEW, ALTERNATING, MIXED with the same prospective seeds. Report all, including negative results. No seed or threshold changes after opening.

## Conservation and law
Every instruction requires two RF reads. For B banks with p reads per bank per cycle, total throughput T obeys **T <= Bp/2** instructions/cycle (ignoring any additional bottlenecks). For a given fixed trace with D_b reads to bank b, total cycles C >= max_b D_b/p, and also C >= 2N/(Bp). With B=2, p=1, T <= 1. These are classical resource bounds, not an architectural discovery. Collector blocking and arrivals can only reduce T. Validate empirical completion cycles against both bounds.

## Verification and stopping
- Exhaustive grant legality/argmax check on 2,340 small states, conservation of 2N reads, capacity and low-load no-win checks.
- Pilot is already opened; prospective results must be committed after this protocol commit.
- If W1 <5% vs SRPT, retire immediately and leave prospective data as a negative result. Do not tune on opened results.
- No RTL/synthesis/physical or RTX-5090 claims are justified by this screen.
- Reproduce: `cd research/v308 && python3 -m unittest -v test_collector.py && python3 collector.py --pilot && python3 collector.py`.

**Prior-art boundary:** operand collectors and bank-aware scheduling are established; see Barnes, Shen and Rogers, HPCA 2023, https://engineering.purdue.edu/tgrogers/publication/barnes-hpca-2023/barnes-hpca-2023.pdf . The two-bank model is an illustrative Volta/Ampere-like domain, NOT a confirmed Blackwell configuration.
