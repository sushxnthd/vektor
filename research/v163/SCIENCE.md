# V163 SCIENCE — RTL-informed response-capacity kernel (2026-10-16)

**Question:** Does mask-aware Wave32 response compaction improve throughput when the actual Vektor FP32 stage storage and packer costs are used rather than the hypothetical V162 FIFO?

**Frontier:** V162 modeled a 4,900-bit, four-dense-response FIFO and reported 3x for k=8. Actual V155/V153 RTL contains one output register of 1,225 logical bits, plus one upstream stage (V155: 3,401 bits; V153: 4,457 bits). V156 OpenSTA parsing is still blocked.

**Objective:** Ordered Wave32 completions per cycle at equal 1,225-bit response storage; ultimately equal mapped area, timing, energy and held-out workload throughput.

**Strongest baseline:** Dense V155 one-response register, identical source/sink pattern and one upstream stage; future matched synthesis must also test optimized dense FIFO/credit allocation.

**Hypothesis:** With ideal one-cycle packing, response bits = 41 + 37k for k active lanes. Under 20 producer / 20 consumer antiphase cycles and U=1, responses per period = min(20,1+floor(B/packet_bits)). For B=1225, k=8: dense 2 vs sparse 4 (2x), not 3x; gain disappears at k>=16. B=4900 reproduces V162's 3x at k=8 but is hypothetical hardware.

**Falsification:** Packer initiation interval >1, metadata, scatter/writeback or area overhead erases gain; dense matched-area baseline matches candidate; realistic masks rarely have <=15 active lanes.

**Publishable threshold:** Novel mechanism beyond known warp compaction; frozen protocol, matched mapped area/timing/energy, >10% replicated Pareto benefit, held-out realistic workloads and independent checker. NOT MET.

**Architecture threshold:** >10% actual divergent-kernel throughput/area or energy improvement without >5% full-mask regression, integrated into tile. NOT MET.

**Kill condition:** Three substantive hardware tests fail to improve claim or expose a new boundary; or matched baseline erases benefit. Pivot kernel, never stop automation.

**Evidence:** Exact 33-density storage boundary asserted in check_widths.py; separate V163 local 9/9 simulation tests and 66 exact cases are in the archived evidence package, not yet pushed to this branch. Logical register bits are not silicon cell area. Novelty: NOT ESTABLISHED.