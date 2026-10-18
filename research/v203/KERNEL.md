# V203 — same-register RF read-port compaction (active)

## 1. Bottleneck law
For four simultaneously ready, same-bank, two-source instructions with independently certified source alias probability p, fixed-priority arbitration with two RF reads/bank/cycle has E[grants]=1+p[1-(1-p)^3] when an aliased pair consumes one read; the existing two-read baseline issues exactly one. This is a conditional combinatorial law, not a measured GPU speedup.

## 2. Exact mechanism
Decoder asserts src_alias[i] ONLY if source0 and source1 are the identical physical register in the same wave. Arbiter reserves one read instead of two for that instruction; operand data must be broadcast to both execution latches. No new RF ports or queues. The current issue_control ties alias low until decode/collector integration, so integrated tile gains are NOT demonstrated.

## 3. Strongest equal-resource baseline
Vektor original four-slot fixed-priority arbiter, same 16 banks and two read ports/bank. Its frozen RTL is research/v203/rtl/baseline.sv. Candidate adds alias metadata and gates, so equal-*area* and equal-timing gates are still OPEN; same port budget is not equal silicon area.

## 4. Predicted boundary
Win: p>0 and alias-tagged reads contend for saturated bank ports. No win: p=0 (exact) or RF banks not a bottleneck. All-four-hot formula above is frozen before physical assessment; it must not be extrapolated to general GPU workloads.

## 5. Smallest RTL
rtl/vtile/rf_bank_arbiter.sv; verification/rtl/tb_rf_bank_arbiter.sv (20,002 directed/random cases). Original issue_control supplies src_alias=0 conservatively. Data broadcast and decoder proof are not yet implemented.

## 6. Physical gate
Inherited rtl workflow synthesizes candidate with Yosys generic cells; baseline and candidate need matched Nangate45 mapped area, max-cap/slew and fresh STA under matched input/output loads. Workflow modification to execute this extra gate was rejected by repository safety checks. This is an infrastructure blocker, NOT a physical pass or falsification. Do not extend beyond two plumbing runs.

## 7. Workload metric
4096-cycle, four-lane deterministic synthetic instruction queues. Metrics: issued instructions/cycle, RF reads per issued instruction, absolute RF reads. Compute-hot, compute-distributed, memory-sparse and divergent variants. See results.csv.

## 8. Decisive falsification
Kill if source alias cannot be proven in decoder, alias broadcast adds an unacceptable critical path/area under equal budget, max-cap/slew fails after one repair, or gains vanish after area-equalized baseline and real RF timing. The 20,002-case RTL test does not prove architectural data correctness.

## 9. Unseen prediction
Frozen negative: no_alias and memory_no_alias must match baseline exactly. Frozen positive: hot bank, alias p=.85 should improve modeled issue count. These are synthetic, not external held-out application workloads.

## 10. Architecture consequence
Potentially reduce RF bank reads and issue stalls without additional ports, but requires decoder same-physical-register equality, one-to-two operand fanout and RF-to-execution timing. If timing or area costs dominate, do not integrate; retain baseline.

## Evidence and novelty
Local Python model + independent 2,048-case checker; five tests passed. GitHub inherited RTL/simulator workflows are relevant only after checking the exact SHA and log. Prior art includes BOW (MICRO 2020), Memento/Malekeh (ISCA 2024), Triple-A (2024): register bypass and caching are NOT new. This is a Vektor engineering mechanism under test, NOT a publishable discovery yet.

## Decision
V153/V156 cutset retired pending physically repaired evidence. V200/V202 exchange retired. One active kernel: V203 source-alias port compaction. Kill after two physical-plumbing attempts without a physical discriminator.
