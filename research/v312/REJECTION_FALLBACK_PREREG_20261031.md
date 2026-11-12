# V312 prospective protocol: rejection-aware bank-conflict fallback (2026-10-31)

## Mechanism, not a claim of novelty
V312 is **late substitution after a register-bank rejection**: each of four scheduler partitions supplies a primary and an independently ready backup; after earlier slots consume read ports, a rejected primary may be replaced by its backup without increasing the four-wide issue width or 16-bank, two-read-port-per-bank budget. Physical register IDs are distinct unless explicitly verified equal; this first model conservatively charges both source reads, even for same-bank operands.

The current V-Tile `steal_warp_scheduler` only donates backup waves to *empty* issue slots. It does not substitute a backup when a populated slot's primary is rejected by `rf_bank_arbiter`. This protocol tests that narrower missed opportunity. V287, V296, V309, V310 and V311 remain retired.

## Fair comparators
1. Existing greedy head-only bank arbiter with the same four primaries and identical bank-port limits.
2. **Strong two-choice optimal oracle**: maximize accepted slots over all 3^4 choices {none,primary,backup} with one issue per partition, two reads per instruction, no additional ports, and tie-break toward primaries. This is an upper bound, not a hardware-feasible matched-timing baseline.
3. A future physically implemented strong equal-resource bank-aware selector is required before any architectural superiority claim. A comparison against head-only alone is insufficient.

## Frozen test cases and kill rules
- Hardware model: 4 partitions, up to 2 eligible waves each; 16 banks, 2 reads/bank/cycle; four output slots; no operand reuse or cache/scoreboard effects. The model is synthetic issue admission, **not GPU throughput**.
- Hotspot predicted-win: all four primaries request banks (0,1); backups request distinct pairs (2,3), (4,5), (6,7), (8,9), each independently ready with probability 0.95. Predict >1.50x candidate/head admissions, and candidate >=0.90x of optimal oracle. No tuning on holdout.
- Disjoint predicted-no-win: primaries request disjoint bank pairs (0,1),(2,3),(4,5),(6,7); backups request pairs (8,9),(10,11),(12,13),(14,15). Predict exactly 1.000x candidate/head, 1.000x candidate/oracle.
- Perturbed unseen transfer: heads each use hot pair (0,1) with probability 0.75, otherwise distinct partition-specific pairs (2,3),(4,5),(6,7),(8,9); backups independently ready with probability 0.75 and use pair (10,11),(12,13),(14,15),(2,3). **No point estimate frozen**; test whether a boundary based on conditional rejection/backup compatibility predicts direction on an independently seeded holdout.
- Holdout sizes: 100,000 opportunities each; deterministic seeds 312031, 312032, 312033. Fixed seed is for reproducibility, not a guarantee of independence from model selection.
- Kill if hotspot gain <=1.10x; if no-win gain differs from 1.0; if candidate violates bank ports; or if it fails to improve over a **strong, physically matched** two-choice controller when one becomes available. Do not claim novelty or physicality from this model.
- Physical gates, if synthetic screening survives: synthesizable RTL + independent iverilog oracle; Nangate45 matched area <=1.50x, placement-estimated-RC delay ratio <= (hotspot admission ratio / 1.10); max-cap/slew, routed wire/load sensitivity, full operand mux/forwarding, real traces, occupancy, traffic, power proxies. Kill if realistic frequency, resource or bandwidth costs erase gain.

## Analytical boundary (pre-outcome)
For a **single late slot with a fixed prefix** and primary rejection probability r, let a=P(backup ready | primary rejected), c=P(backup bank-compatible | primary rejected, backup ready). Then
P(candidate admits)=1-r+rac, P(primary admits)=1-r, and G=1+rac/(1-r).
For four slots, earlier substitutions alter later port occupancy, so this formula is **not** an exact global law. Report measured conditional rates and compare the formula only on a controlled final-slot experiment. For the full scheduler, report oracle regret and measured admission gain, then derive a predictive global law before opening new regimes.

## Prior art and scientific honesty
Multi-candidate warp scheduling, operand collectors, and bank-aware arbitration are established areas. The only claim presently under test is a concrete V-Tile integration gap and its quantitative operating boundary. The strongest equal-capability selector may eliminate any incremental novelty. All negative results remain committed; no RTX-5090 equivalence claim.
