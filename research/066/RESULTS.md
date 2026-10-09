# Vektor-066 verified results — 2026-10-09

GitHub Actions (passing): https://github.com/sushxnthd/vektor/actions/runs/37969170192
Commit tested: f1e02565f323250aa0850dbc8546172d79b756df

## Evidence classes

**SIMULATED (synthetic, not GPU throughput):** 288 structured and 36 exploratory Python runs, zero full-UID false ACK credits. 16 tag-only ablations produced **43,964** false ACK credits. All-ACK-loss directed case completed zero transactions (no unconditional liveness). Results reproduce deterministically on free GitHub Actions.

**INDEPENDENT MODEL:** C++ finite-domain identity oracle evaluated 1,044,480 distinct-UID/tag combinations: 261,120 tag-only aliases and zero full-UID aliases. After 8-bit wrap, 256/256 old/new UID comparisons alias. This proves only the predicate, not network correctness.

**RTL SIMULATED:** Icarus directed test passed after fixing a testbench delta-cycle sampling race. Tests old ACK replay rejection after tag reuse, matching ACK acceptance, quiescence gating and stable retirement under backpressure.

**GENERIC SYNTHESIS:** Yosys default TAG_W=4, UID_W=16 generated **89 generic cells**, including 23 flip-flop-type cells (22 enabled and one plain). No technology mapping, physical area, critical path, power, clock or P&R evidence.

**UNVERIFIED:** Full end-to-end RTL DATA/ACK producer, finite receiver dedup storage, wrap-safe UID allocation, reset, congestion, formal temporal proof, silicon, graphics, tensor and memory performance.

## Failure and next action

The initial CI testbench falsely reported rejected ACK because it sampled a combinational output in the same simulation delta as driving the input. The DUT was not proven faulty; a #1 delta-settle delay fixed the test. The negative result is preserved in Actions run https://github.com/sushxnthd/vektor/actions/runs/37969046437 .

Next decisive experiment: finite UID tombstones and ACK-side quiescence fence under explicit bounded replay horizon; test ID wrap, packet loss, and reset against an equal-storage baseline.
