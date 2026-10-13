# V143 SCIENCE — 2026-10-13

**Active kernel:** Can operand-source reuse and writeback multicast yield a robust GPU throughput/traffic/PPA improvement against a coalescing-aware strongest baseline?

**Frontier:** V142 producer multicast had no consistent gain over no-forward. V143 corrects the RF duplicate-read baseline and measures its hardware implementation cost.

**Objective:** cycles, RF reads, physical broadcast traffic, generic logic cost, response bandwidth, ultimately mapped PPA and unseen kernel performance.

**Strongest baseline:** best grouped/interleaved nonforwarding with identical RF banks, physical ports, issue, collectors, latency AND duplicate-read coalescing. Additional forwarding buses not area-equalized.

**Mechanism:** FMA(x,x,c) needs two physical RF reads, FMA(x,x,x) one; one producer writeback can satisfy all listening source slots. However naive three-input Wave32 response crossbar has large data-plane mux cost; replacing it with a single vector bus trades area proxy for response serialization.

**Decisive falsification:** bit-exact final-state mismatch, independent cycle-model mismatch, no surviving equal-budget speedup, or physical PPA dominated by response steering/serialization.

**Publishable threshold:** novel mechanism beyond known reuse/bypass, multiple unseen realistic kernels, independent checking, mapped PPA and matched area/energy. NOT MET.

**Architecture threshold:** >=5% completion improvement across two unseen workload classes with no increased RF traffic, plus acceptable mapped timing/area. NOT MET.

**Kill/reformulate:** three runs without a new discriminating boundary or equal-budget improvement.

## Frozen cycle-model experiment
216 configurations x 12 arms = 2592 runs, 96 discovery + 96 holdout + 24 wildcard. Independent C++/Python timing/traffic **480/480** matches, final FP32 states match sequential glibc fmaf on one representative lane per wave.

- P1 PASS: no-forward physical RF reads 3/2/1 per FMA for 1/2/3 distinct source registers.
- P2 PASS: all completed final states agree.
- P3 PASS: 48/96 holdout apparent forwarding wins vs unfair uncoalesced no-forward baseline disappear when baseline coalesces.
- P4 PASS: best-policy coalesced forwarding wins 36/96 holdout (34 >=5%); by source multiplicity 1x 20/32, 2x 0/32, 3x 16/32. Wildcard wins 9/24 (5 >=5%). Selection is oracle best-policy, not hardware-realizable policy without predictor cost.

## Hardware/response-bus discriminator
First V143 CI PASS run 38381018667: 3456 abstract cases and 800 full-Wave32 RTL vectors; 9286 generic cells/6144 muxes for 3-vector coalescer vs 6 for passthrough (not same physical read traffic). Second CI PASS run 38381219776: 800 more RTL vectors for 1-vector valid-only response topology, **81 generic cells**. Exploratory 432-run cycle model shows one response bus slows by 1.49–3.58x on average across source multiplicities vs unlimited response bandwidth; worst 5.53x. See `evidence/response_bus_tradeoff.md`. This is an architectural tradeoff, NOT a new law or measured GPU PPA.

## Evolving world model
- KNOWN (simulation): duplicate-read coalescing materially changes forwarding comparisons; response bandwidth throttles the synthetic FMA throughput.
- KNOWN (RTL/generic synth): both isolated RTL topologies pass their tests; 3-response mux implementation has 9286 generic cells vs 81 for a 1-response valid-only implementation.
- BELIEVED: bank-local RF response multicast is a promising intermediate topology; not validated.
- CONFLICTING: source multiplicity 2x eliminates forwarding wins, while 1x/3x sometimes retain wins; cause may depend on synthetic chain topology.
- FALSIFIED: charging a separate RF read for identical source tags as a fair baseline; assuming single-response bus is a cost-free replacement for 3-response datapath.
- ANOMALOUS: nonmonotonic 1x/2x/3x performance response.
- UNTESTED: real FMA tile, realistic kernels, physical PPA, energy, software/ISA, scalability.

## Prior art
Operand bypass, RF reuse, and multicast are established concepts (BOW, Triple-A, Malekeh). No V143 novelty claim.

**Next decisive action:** integrate bank-local response multicast and a real FP32 FMA execution slice, compare equal-resource throughput and mapped PPA on GEMM/reduction/stream kernels. Preserve negative 1-bus result.
