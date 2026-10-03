# ISSUE-CONTROL-001 — Backpressured scheduler to RF admission

## Question

Can the current V-Tile scheduler and RF bank arbiter be composed without silently losing waves when register-bank conflicts reduce issue width?

## Design change

The limited work-stealing scheduler now has an explicit `issue_accept` interface. Scheduler round-robin state advances only for proposals actually accepted by downstream admission. The integrated `vektor_issue_control` block:

1. selects up to four candidate Wave32 IDs;
2. selects each candidate's two source-bank identifiers;
3. runs the four candidates through the two-read-per-bank RF arbiter;
4. feeds the grant mask back as scheduler acceptance;
5. exposes only accepted work as final `issue_valid`.

Blocked candidates remain eligible and are retried as long as their wave remains valid/ready.

## Verification

Deterministic RTL tests cover:

- four non-conflicting waves: all four admitted;
- severe same-bank conflict: one admitted, rejected waves remain pending;
- external retirement of only the accepted wave: a previously rejected wave is proposed again;
- partial conflict: the conflicting slot is rejected while independent slots still issue;
- direct scheduler backpressure: zero acceptance leaves proposals unchanged; partial acceptance advances only the accepted partition.

An initial CI run `37131661907` failed before integrated simulation because the scheduler testbench deasserted reset in the same simulation time slot as a rising edge. That testbench race was fixed rather than ignored. No result from that failed run is promoted.

Clean evidence head: `b30d6aaf55898845dec44fcba36b470263a236c5`

- RTL Actions run: `37131853863` — success
- simulator Actions run: `37131853865` — success
- RTL artifact digest: `sha256:7a7b8c5c543a9539e24abfe18a4926537e73c4cdd186d4840879e37fa31e5c9c`

## Generic synthesis

Yosys 0.33 generic mapping on the clean run:

- backpressure-aware limited-steal scheduler: **1,310 cells**
- RF bank arbiter: **1,321 cells**
- integrated issue-control hierarchy: **3,627 cells**

The integrated hierarchy includes about 998 top-level cells, dominated by per-wave source-bank selection/control muxing in this provisional interface. That overhead is now explicit and is a candidate for later instruction-buffer/scoreboard co-design.

These are generic synthesis proxies, not transistor counts, mm², frequency, energy, or power.

## Supported claim

Vektor now has a synthesizable issue-control path in which RF bank conflicts reduce admitted issue width without advancing rejected waves out of the scheduler. The property is covered by deterministic RTL tests and the combined block synthesizes in the open Yosys flow.

## Not established

- instruction fetch/decode or scoreboard correctness;
- physical register-file implementation;
- operand-cache integration;
- IEEE-754 arithmetic correctness;
- timing closure or 2.56 GHz feasibility;
- real-workload throughput;
- process area, power, or energy;
- RTX 5090 equivalence.

## Next gate

Attach real operand/register state and an IEEE-754 FP32 FMA backend. Arithmetic throughput is not counted toward Vektor's validated capability until bit-exact correctness, exceptional values, rounding behavior, pipeline protocol, and synthesis evidence are present.
