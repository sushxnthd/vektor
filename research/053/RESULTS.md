# Vektor-053: RF admission conservation and RTL CI

2026-10-09. DISCRIMINATION / CAPABILITY-BUILDING. This branch is based on 052, not main. No PPA or GPU-level capability claim.

## Preregistered mechanism and prediction

The three 052 policies (clock round-robin, first-grant round-robin, completion-first) greedily grant independent register operand reads with identical per-bank ports and a global credit budget. Prediction: static grant count is invariant under priority order and equals min(slots, sum over banks min(ports, eligible reads targeting bank)). Bijective bank relabeling preserves grants. Different grant identities may change future queue state and multi-cycle IPC.

## Results (software, not RTL)

C++ exhaustive enumeration: 653,184 W=2/O=3/B=2/PORTS=2 configurations x 3 policies = 1,959,552 policy checks, **0** oracle count disagreements, **0** bank-relabel disagreements, **0** count differences. Grant masks differed in 35,928 configurations. Additional 100,000 random configurations (300,000 policy checks) across W/B/O/ports had no count-oracle disagreements. Independent Python brute-force feasible-subset enumeration: 60,000 checks, 0 disagreements. Exact seed values and full source/results are preserved in the Vektor-053 reproducibility package. This branch includes a standalone Python exhaustive regression checker.

## Supported structural law

For bank b, at most min(P,R_b) eligible reads can issue; global slots S give upper bound min(S, sum_b min(P,R_b)). Greedy scans all eligible reads and rejects only when that bank or global slots are full. If it issued fewer than the bound, global slots remain and some bank has unused capacity despite an eligible request, contradiction. Thus all priority orders have the same count **only under independent per-operand admission**. Atomic instructions, variable read costs, and cross-bank coupling invalidate the proof.

## Discovery Protocol V2

KNOWN: the static count law and bank-relabel invariance hold in exhaustive bounded tests and follow from the contract.
BELIEVED: completion-first's Vektor-051 IPC improvement is due to multi-cycle operand-collector state, not higher instantaneous read count.
CONFLICTING: 051 selected +38.9% modeled IPC versus broad +0.41% mean and 103/336 losses.
FALSIFIED: interpreting completion-first as improving the same-cycle independent read count.
ANOMALOUS: queue-credit and scheduler phase transitions despite count conservation.
UNTESTED: RTL differential equivalence, tagged data return, multi-tile effects, physical timing/area/power and all RTX 5090-class gates.

Residual: zero count mismatches. Competing explanation: the simulation contract omits coupled instruction-level admission and physical return paths. Uncertainty: hardware feasibility and general GPU impact unknown.

## CI falsification

The first 052-053 GitHub Actions run failed on the very first vector because the 052 testbench did not explicitly pulse asynchronous reset, leaving the RTL pointer X. The testbench was corrected on this branch; subsequent CI results must be inspected separately. This is a **testbench reset initialization defect**, not yet evidence of a faulty arbiter.

## Next decisive action

Run all 12 RTL differential configurations and six matched Yosys syntheses in GitHub Actions. Then add tagged operand return and scoreboard state and test whether future-state effects survive fair baselines and hardware cost.
