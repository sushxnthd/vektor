# V296 all-input combinational equivalence: prospective proof gate (2026-10-26)

**Sole active mechanism: V296 pairwise bank-conflict admission. V287 retired.** This is a verification experiment on the unchanged arbiter, **not** a timing repair, an added mechanism, or a physical GPU result.

## Frozen question and decisive gates

The earlier 164,976 finite RTL comparisons cannot establish equivalence over all 2^36 combinations of four request-valid bits and eight four-bit bank IDs. Prove or refute, with an independent bit-vector SAT backend, that the existing V296 priority-greedy pairwise arbiter, the serial one-hot control, and the previously rejected parallel-threshold topology produce identical four-bit grants for **every** input assignment. There are no environmental assumptions on bank IDs, valid masks, bank equality, or contention. Both same-bank operands must count as two port demands.

1. Build one synthesizable combinational miter from **unchanged** modules. Its `bad` output is the OR of original-vs-serial and original-vs-parallel-threshold grant differences. No input assumptions.
2. Run Yosys `read_verilog -formal -sv`, flatten hierarchy, then `sat -verify -prove bad 0` with a bounded 300-second solver timeout. A tool timeout, unsupported syntax, or missing PASS marker is **INCONCLUSIVE**, never a proof.
3. Independently verify the miter is not vacuous by substituting a deliberately wrong `grant` implementation in a separate negative-control miter and requiring SAT to find a counterexample. The negative control must never be accepted as a proof.
4. Preserve tool version, full solver log, source hashes and both positive and negative controls as a hosted artifact. A successful run proves only 2-state combinational equivalence for these exact RTL modules, not sequential scheduler correctness, X-state equivalence, STA, power, or physically feasible throughput.
5. If any valid counterexample appears, **falsify V296 admission equivalence** and do not proceed to new physical claims until understood. If proof passes, return to the original matched integrated post-route failure: V296 -1.047895 ns setup, -0.036622 ns hold, three cap violations; serial -1.859922 ns setup, -0.019796 ns hold, three cap violations. Both fail 3.5 ns. An optimized equal-resource serial baseline remains mandatory.

**Interpretation:** This closes a finite-testing gap without treating a formal proof as an architecture speedup. Do not open frozen workload holdouts, merge the draft PR, modify Kernellum PR #119, or infer RTX-5090 equivalence.
