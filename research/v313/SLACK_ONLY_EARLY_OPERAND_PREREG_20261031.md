# V313 prospective screen: version-safe, slack-only early operand staging

Date: 2026-10-31. **Frozen before running the held-out seeds below.**

## Single mechanism
Use existing operand-collector entries to read a source of a *dependency-blocked* warp instruction before its other source is ready. Issue remains forbidden until both sources are ready and their values have been read. A prefetch may use **only read-bank ports left idle after fully-ready instruction service**. No extra bank ports, issue slots, or collector entries. Every early read must be protected by an immutable source-version guarantee or a version-tag validation/replay path. A source overwrite without validation invalidates the mechanism.

## Strong alternative and resource matching
The comparator is a bank-aware, buffered **fully-ready-only operand collector** with the same four warp slots, four-entry FIFO per slot, sixteen banks, two reads per bank per cycle, two operands per instruction, bank-aware arbitration, ready-first service, and identical queue admission, age rotation, and output issue capacity. Both policies operate on the same offered trace. The candidate differs only in whether it uses residual bank-port slack to read an available operand of a blocked instruction. The strongest same-information early-prefetch collector may implement the same policy; incremental novelty is NOT established by beating ready-only.

## Locked tests
- Synthetic win: arrival probability 0.90 per slot/cycle; first source ready at arrival; second ready after a uniformly selected 3, 4, 5 or 6 cycles; first bank=0 with probability 0.80 (else uniform 16-bank); second bank=1+slot with probability 0.80 (else uniform 16-bank). Holdout seed **313701**, 20,000 measured cycles, 2,000 warmup. Predict candidate/ready-only completed instructions **1.02 to 1.06**, without extra ports. The 1.02 minimum is the promotion gate.
- Synthetic no-win: both sources ready immediately, both banks uniform over sixteen. Holdout seed **313702**, same length. Predict **exactly 1.000000** issue ratio and identical queue/dropped counts.
- Perturbed transfer: arrival 0.90; second source delay uniformly 2,3,4,5; first-bank hotspot probability 0.65; second-bank slot affinity probability 0.65. Holdout seed **313703**, same length. No minimum gain is asserted: this is a falsification/sensitivity test, not a free positive result.

## Invariants and kill gates
1. Never read an operand before its ready timestamp; never issue before both are ready and captured.
2. Per-bank service <=2 reads/cycle; four issue slots and four-entry FIFO per slot.
3. Early reads cannot displace any fully-ready reads in the same cycle.
4. If version stability cannot be established or version checking exceeds the physical budget, kill.
5. No throughput claim from immediate admission alone. Record sustained completed instructions/cycle, offered/dropped work, mean and p99 latency, and prefetch traffic.
6. Kill if win ratio <1.02, no-win deviates from 1.0, a same-information competent baseline erases the gain, or matched full RTL/area/timing/electrical/bandwidth constraints erase it.
7. A positive synthetic screen only authorizes RTL/physical and trace work. It does not establish GPU speedup or novelty.

## Prior-art challenge
GPU operand collectors and operand prefetch/reuse are established architectural concepts. Search specifically for early/partial operand collection and scoreboard-safe speculative RF reads before any novelty claim. Compare against an equally provisioned collector that is allowed to prefetch partial operands; if identical, reframe as implementation research or retire.

## Evidence tiers
An exploratory pilot used seed 123 and 10,000 cycles to choose this *candidate* and is not a holdout. Holdout seeds and boundaries above are prospective. No RTL, synthesis, placement, extracted RC, power, real GPU trace, or novelty evidence exists at freeze time.
