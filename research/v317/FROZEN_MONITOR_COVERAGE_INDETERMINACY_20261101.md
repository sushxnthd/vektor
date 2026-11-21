# V317 frozen monitor-coverage indistinguishability gate (2026-11-01)

**Status: precommitted falsification protocol.** This extends the existing V317 evidence gate on draft PR #34; it does not promote a new architecture mechanism. Prior stateful RTL assumes every intervening physical write is delivered to its local monitor. This experiment tests that assumption as an explicit interface contract.

## Frozen hypotheses and outcomes

1. **Indistinguishable histories.** If a write to a cached physical lane can be lost without a trusted independent coverage-fault signal, there exist two execution histories with identical local monitor inputs but different correct operand values. No deterministic local grant predicate can safely distinguish them. Enumerate a two-lane value-history witness with a hidden write changing one requested lane, and test all nonempty masks.
2. **Fail-closed wrapper.** Add one sticky coverage-fault bit around the existing stateful forwarding gate. coverage_ok=0 must suppress grants *combinationally*, poison the entry on the next clock, and keep it poisoned even after coverage_ok returns to 1. Only a new capture under coverage_ok=1 may clear the poison. Reset, concurrent capture/fault, namespace, masked writes and zero-output-on-reject must be tested. A fresh capture while coverage is absent must not clear the poison.
3. **Same-information baseline.** A baseline with the same snapshots, complete write stream and coverage signal can make exactly the same safe grants. Therefore predicted *incremental* transaction saving is **zero**. No throughput gain is predicted. Compare a weak unguarded model solely to expose unsoundness, never as a performance baseline.
4. **Physical proxy.** Synthesize baseline and coverage-wrapped RTL at 4x8, 8x16 and 32x32 using the same Yosys version and synth -flatten. Report generic cells, flop count, depth proxy and fanout, not placed area or routed timing. The wrapper's trusted coverage_ok distribution and detector are **not** implemented and remain uncosted.
5. **Independent checker.** Python enumerates hidden-write histories and proves that no unchanged monitor observation can certify a stale forwarded value. Test counterexamples, sticky fault transitions and matching grants for equally informed controls. The RTL testbench checks behavior independently of the Python checker.

## Precommitted kill and evidence rules

Any grant after a known coverage gap, before a clean recapture, is a correctness failure. A coverage_ok signal incorrectly remaining high during a missed write is **not** covered by this RTL guarantee and must be documented as a decisive unsolved integration assumption. Passing this experiment is **not** a GPU performance result. Do not promote V317 forwarding, resurrect V287, or displace V296. Preserve all negative evidence, do not modify Kernellum PR #119, and keep one draft PR and one research branch.
