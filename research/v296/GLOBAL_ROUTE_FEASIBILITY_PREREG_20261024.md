# V296 high-RC global-route feasibility discriminator — preregistration (2026-10-24)

## Motivation and frozen negative evidence

The control-advantaged four-way 65%-density detailed-route experiment [run 40058628923](https://github.com/sushxnthd/vektor/actions/runs/40058628923) was **cancelled after the 150-minute job budget**, not physically validated. The job log shows the candidate-first pairwise contestant started at 03:32:24 UTC and remained inside OpenROAD until cancellation at 06:01:41 UTC; it did not reach the next contestant. Its [14-file partial artifact](https://github.com/sushxnthd/vektor/actions/runs/40058628923/artifacts/12550720536) must be retained. **Do not count the absence of a completed detailed route as an electrical violation or as a pass.** Earlier 65%-density original-control fifth repair failed global routing with GRT-0116; fourth-repair area 9,796.248 um2 and fifth-repair area 10,208.814 um2 exceeded the fixed 7,400 um2 ceiling. The previously proposed simple mapped area-scaling law is separately falsified.

## One-mechanism continuation

Sole candidate V296 pairwise RF-bank admission; V287 retired. Same persistent branch/PR. This is a **lower evidence tier** to isolate capacity, area growth, global-route congestion and preliminary electrical/timing feasibility before spending another 150 minutes on detailed routing. It does NOT supersede any failed full physical gate.

Four independently mapped contestants: pairwise V296, serial one-hot, parallel one-hot, original. Preserve the original 3.5 ns ideal clock, 140x140 um die, 120x120 um core, 65% initial placement-density target, Nangate45 library and pinned OpenROAD, 2.0x wire RC, 20% capacitance repair margin, and 4 rounds for all variants plus a 5th 35%-slew-margin repair for controls only. No parameter retuning after seeing results. Run variants as independent matrix jobs to prevent a slow candidate from concealing control outcomes. The Tcl modification is gated by V296_GLOBAL_GATE_ONLY=1; its default path retains the original detailed route and extracted SPEF.

## Prospective hypotheses and kill criteria

H1: V296 completes its fourth global-route repair under the same high-RC 65%-density constraints; this may fail because congestion or tool runtime dominates. H2: original control's extra fifth repair repeats GRT-0116 or otherwise fails. H3: parallel one-hot's large mapped area may remain above the 7,400 um2 ceiling after repair. None of these is an asserted result.

For any candidate/control at the final completed global-route stage, record A, setup slack, slew violations, cap violations. Necessary area condition: A <= 7400 um2. Area-repair budget is 7400 - A, with negative values constituting an area-ceiling failure. The gate can *reject* a contestant on an explicit area violation; a nonnegative budget is **not** sufficient for timing, electrical, DRC or CTS closure. Likewise global-route zero violations and nonnegative ideal-clock slack cannot certify post-detailed-route physicality. A missing or timed-out result is INCOMPLETE, never a pass. Require independently parsed log markers, exact variant and fifth-repair identity, plus nonempty DEF for a complete global-route-only record.

Freeze this experiment before outcomes. If V296 cannot complete even global routing or exceeds the area ceiling, prioritize falsification of V296's target-configuration feasibility; do not promote its prior successful 45%-density run into a 65%-density comparison. A future lower-density/larger-core experiment requires a separate preregistered common floorplan for every contestant. Workload holdouts stay sealed. No RTX 5090, throughput, energy, CTS, detailed-route, or equal-area superiority claim.

## Output

Per-variant logs, netlists, DEF, guide, technology checksums, independent machine-readable audit. All negative and incomplete results retained. Cross-variant comparison only after all four variant artifacts are available; no cherry-picked partial winner.
