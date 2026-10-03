# FP32-PIPE-002 bounded fused lane

Class: DISCRIMINATION and CAPABILITY-BUILDING.

Parent evidence: research/fp32-fma-001 commit 9c79edc93304422e4ac77558e6fd426570c39753.

Question: can the bit-exact FP32 fused semantics already established by the wide simulation oracle be reproduced by a hardware-shaped bounded-width pipeline without the synthesis blow-up of the oracle?

Mechanism: classify/unpack; 24x24 significand multiply; exponent compare and right-shift-with-jam alignment; bounded signed accumulation with guard/round/sticky state; leading-zero normalization; one round-to-nearest-even decision after fused accumulation; pack result and exception flags. The exact reference lane remains the semantic oracle, not a PPA candidate.

Preregistered predictions:
- P1: bounded datapath matches all 10,008 existing fmaf vectors bit-for-bit.
- P2: generic Yosys synthesis completes under the same 180 second budget that timed out on the wide reference. This is not evidence for 2.56 GHz.
- P3: mismatches, if present, cluster around cancellation, subnormal output, exponent-difference truncation, and halfway rounding.
- P4: internal precision increases only when residuals demonstrate lost information.

Equal-budget controls: same vector corpus and flag checks; same generic synthesis flow and wall-clock cap. No frequency, area, power, or throughput claim follows from generic cell counts.

World model:
KNOWN: exact fused reference matches the current 10,008-vector software oracle; its generic synthesis exceeds the imposed budget; FMA requires one rounding after accumulation.
BELIEVED: a bounded fused datapath with shift-jam and explicit rounding state can preserve correctness while synthesizing tractably.
CONFLICTING: none yet. Synthesis timeout does not establish excessive silicon area.
FALSIFIED: the wide exact lattice can serve directly as the production FP32 lane in the current flow.
ANOMALOUS: pending bounded-candidate residual mining.
UNTESTED: bounded-lane exactness and synthesis complexity; mapped critical path; replication cost; 2.56 GHz feasibility; physical area and power.

Adversarial roles: Explorer proposes the compact shift-jam datapath. Skeptic attacks cancellation and underflow. Experimentalist reuses the frozen oracle corpus. Analyst classifies residuals. Anomaly Hunter searches precision boundaries. Prior-Art Auditor treats standard FMA structure as prior art. Replicator independently derives an integer model. Theorist seeks the minimum retained-bit law for correctly rounded binary32 FMA.

Foothold criterion: bounded candidate passes the frozen corpus, synthesizes within the fixed budget, and exposes a reproducible internal-width/complexity boundary.

Next decisive action: implement an independent bounded integer model, sweep retained precision against the frozen corpus, then translate the smallest passing mechanism to staged RTL.