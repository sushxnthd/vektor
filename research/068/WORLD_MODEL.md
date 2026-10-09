# Vektor-068: ACK producer closure and late-delivery correctness

**Evidence date:** 2026-10-10. **Class:** DISCRIMINATION / CAPABILITY-BUILDING.
**Baseline:** Vektor-067 local package; GitHub branch research/dual-fence-lease-067 contains only the earlier 066 base, not the 067 RTL. Main is unchanged.

## Decisive counterexample

Vektor-067's experimental guard contains `if (ack_valid && ack_closed) protocol_error <= 1;`.
That assertion confuses *producer closure* (no new ACKs will be emitted) with
*transport extinction* (all previously emitted ACK copies are terminal).
A legal ACK may be delivered after the producer closes while `ack_pending > 0`.
Finite state exploration (maximum 2 DATA, 2 ACK physical copies, 2 queued ACKs)
enumerated **114 reachable states**, **6,064 legal transitions**, including
**16 legal post-closure ACK-delivery transitions**. An independent C++ implementation
exactly reproduced all four aggregate counts, including one retirable state.
These are finite software-model observations, NOT RTL simulation or a proof of an
unbounded fabric.

A minimal witness: DATA sender closed; DATA physical count 0; ACK queue empty;
ACK producer closed; one ACK copy in flight; that copy is delivered and terminal.
This is legal and allows retirement, but the 067 guard flags a protocol error.

## Mechanism and implementation

`ack_closure_068.sv` is a synthesizable single-transaction control prototype:
- DATA sends and router clones each reserve a physical DATA copy; terminal events release one.
- DATA deliveries queue ACK obligations, which obey ACK output backpressure.
- ACK admissions and router clones each reserve a physical ACK copy; terminal events release one.
- Sender closure prohibits new sends but permits already-in-flight DATA clones.
- ACK producer closure requires sender closure, DATA extinction, and an empty ACK queue.
- Late ACK deliveries and ACK router clones remain legal after ACK producer closure.
- Retirement requires an accepted ACK, producer closure, and zero DATA, queued ACK, and physical ACK copies.
- A trusted external full-fabric quiescence signal is required to allocate after reset.

**Not implemented:** real network routers, generation of trustworthy terminal indications,
finite-ID wrap management across multiple concurrent transactions, end-to-end formal
assume/guarantee closure, physical timing/area, and software/GPU integration.

## Discovery Protocol V2 world model

- **KNOWN (finite model):** 114 states, 6,064 transitions, 16 legal post-closure ACK delivery transitions, exact C++ agreement.
- **KNOWN (RTL source inspection):** 067 would flag a legal late ACK after closure.
- **BELIEVED:** split producer closure from physical-copy extinction avoids the false-error condition.
- **CONFLICTING:** ACK closure can be early for throughput, but safe retirement must wait for every physical copy.
- **FALSIFIED:** 'ACK producer closed' implies 'no further ACK can arrive.'
- **ANOMALOUS:** post-closure replay is legal even when producer has stopped emitting; a single closure bit cannot encode both states.
- **UNTESTED:** 068 RTL simulation/synthesis, asynchronous reset with outstanding copies, false external quiescence, arbitrarily many clones, multi-tag scaling, 5090-class gate.

## Hypothesis, prediction, outcome, residual, alternatives

| Mechanism / type | Prediction before enumeration | Outcome | Residual / assumption | Competing explanation / uncertainty / cheapest next test |
|---|---|---|---|---|
| DISCRIMINATION: separate ACK producer closure and ACK transport extinction | At least one legal post-closure ACK delivery exists | 16 transitions among 6,064 | Qualitative prediction confirmed; finite bound 2 | Model could permit invalid clone transitions; independently enumerate and test directed RTL |
| CAPABILITY: bounded physical-copy and ACK queue counters | Reachable legal states maintain conservation | 114 states, no invariant failure | Does not verify RTL, no realistic router | Icarus directed test, then random differential RTL |
| DISCRIMINATION: reset fencing | No allocation before trusted fabric-quiescent indication | RTL source explicitly gates start_ready; no RTL run | External signal can lie | Reset mid-flight test with physical router model |
| SURPRISE: post-closure replay | An in-flight ACK can clone after producer closure | Present in finite state graph and directed test stimulus | No cost/latency model | Sweep bounded ACK copy count and backpressure |
| EXPLOITATION: fix 067 false error | A late ACK is accepted without protocol_error | Proposed RTL and testbench written; simulation pending | No confirmed HDL execution | Run free Icarus + Yosys CI |

**Roles:** Explorer separates closure and extinction; Skeptic challenges the external terminal/quiescence contract; Experimentalist constructs late ACK witness; Analyst restricts claims to finite models; Anomaly Hunter inspects replay after closure; Prior-Art Auditor finds producer/consumer credit accounting established (not novel); Replicator independently implements C++ graph; Theorist states: *no further creation* is weaker than *no remaining physical copies*.

**Prior art:** OpenTitan TileLink-UL protocol checker
https://opentitan.org/book/hw/ip/tlul/doc/TlulProtocolChecker.html ;
gem5 Garnet https://www.gem5.org/documentation/general_docs/ruby/garnet-2/ ;
Vortex GPU https://github.com/vortexgpgpu/vortex .

## External target ledger (not validation)

NVIDIA GeForce RTX 5090 official 2026-10-10 check:
https://www.nvidia.com/en-in/geforce/graphics-cards/50-series/rtx-5090/
21,760 CUDA cores, 2.41 GHz boost, 32 GB GDDR7, 512-bit interface,
575 W TGP, fifth-generation tensor, fourth-generation RT, marketed 3352 AI TOPS
and 318 RT TFLOPS. AI TOPS and RT TFLOPS are NOT comparable to FP32 FLOPS
without datatype, sparsity and workload definitions. RTX 5090 cache size,
effective memory bandwidth, raster/texture benchmarks and datatype-specific
tensor throughput require separate sourced entries; currently INCONCLUSIVE.

Vektor-1A arithmetic peak: 160*128*2*2.56 GHz = **104.8576 TFLOPS projected**
assuming sustained FMA issue, 2 operations/FMA, 100% utilization.
Frequency, memory bandwidth, area, power, software and graphics gates are
**INCONCLUSIVE**. This milestone changes none of those gates.

## Next decisive action

Run Icarus/Yosys on the RTL with the directed late-delivery witness. Then add
cycle-accurate randomized differential tests with a bounded router that
generates the terminal indications and external reset quiescence; run formal
checks for conservation, producer closure, and no unsafe retirement.
