# V296 unrestricted 2-state combinational admission equivalence: hosted result (2026-10-26)

**Result: PASS for the frozen 36-input-bit combinational grant-equivalence claim.** Evidence tier: hosted Yosys SAT proof, not an integrated timing, electrical, sequential correctness, or GPU throughput result. V296 is the sole active architecture mechanism; V287 remains retired.

## Prospective test and repair of evidence harness

The previously committed [prospective protocol](FORMAL_ALL_INPUT_ADMISSION_EQUIVALENCE_PREREG_20261026.md) fixes a 4-bit request-valid vector plus eight unrestricted 4-bit operand-bank IDs, i.e. **36 input bits** and **2^36 possible assignments**. The unchanged pairwise, serial one-hot, and rejected parallel-threshold RTL arbiters are compared in [one miter](v296_formal_admission_miter.sv) whose `bad` output is asserted on any grant-vector difference.

The first hosted [run 40233313969](https://github.com/sushxnthd/vektor/actions/runs/40233313969) was **inconclusive due to the negative-control harness**. Yosys 0.9 exits on a failed `sat -verify -prove bad 0` with `ERROR: Called with -verify and proof did fail!` but without the required model-found marker; the job therefore stopped before attempting the positive equivalence proof. That run is NOT a failed equivalence proof and NOT a pass.

Commit `9287e4f9c489f8408482a3a3c2f0fc4ffb6637d7` repairs only the *negative-control invocation*: it removes `-verify` for the deliberately faulty same-bank implementation and requires an explicit SAT counterexample marker. The **positive proof** remains `sat -verify -prove bad 0 -show-inputs -show-outputs -timeout 300`. No RTL module, miter, input domain, environmental assumption, or expected result was changed.

## Hosted outcome and provenance

[Hosted run 40238720024](https://github.com/sushxnthd/vektor/actions/runs/40238720024) completed successfully with Yosys **0.9 (1979e0b)** on Ubuntu 22.04. The job reports both:

- `V296_MUTATION_CONTROL_SAT_COUNTEREXAMPLE_PASS` — deliberately denying a valid same-bank request is detectable by SAT.
- `V296_FORMAL_ALL_INPUT_ADMISSION_EQUIVALENCE_PASS` — unrestricted `bad = 0` proof succeeds for all 36 two-state inputs across the three unchanged RTL modules.

The hosted run uploaded [artifact 12615749011](https://github.com/sushxnthd/vektor/actions/runs/40238720024/artifacts/12615749011), named `v296-unrestricted-sat-admission-evidence`, with workflow-reported ZIP SHA-256 `5a62e77851a596ea28c3c9c2143e8929f874a07460904f922be9685cdd3541fa`. It includes Yosys version, source hashes, mutation and positive proof logs. The CI job and step conclusions were checked separately from the initial queued status; this report does **not** claim an independent offline re-execution of the downloaded ZIP.

## Scientific interpretation and hard limits

The three combinational implementations produce identical grant vectors for all unrestricted **2-state** bank IDs and request-valid masks at these exact widths. This closes the finite-testing gap left by the previous 164,976 RTL examples. It does **not** prove X-state behavior, sequential fairness/liveness, scheduler correctness, physical implementation equivalence, feasible frequency, energy savings, or any architecture-specific workload throughput improvement. The already falsified clock-label placebo still applies: an arbiter-equivalent model cannot infer a V296 throughput gain merely by assigning V296 a faster hypothetical clock.

**Original matched integrated physical gate remains failed** at 3.5 ns: V296 setup slack -1.047895 ns, hold -0.036622 ns and three capacitance violations; serial one-hot setup slack -1.859922 ns, hold -0.019796 ns and three capacitance violations. An independently optimized, equal-resource serial control and repaired detailed-route STA/hold/cap/slew remain mandatory. Preserve prospective workload holdouts. No measured GPU speedup, measured power advantage or RTX-5090-equivalence claim follows.

**Next substantive experiment:** preregister and implement matched scheduler-to-executed-data critical-cone topology changes (not the already falsified parallel-threshold depth rewrite), with independent serial optimization, then run detailed route, extracted STA, hold and capacitance/slew and bandwidth-limited workloads at feasible clocks. Kill the V296 performance claim if the matched physical/electrical comparison erases it. Kernellum PR #119 and its holdouts remain untouched.
