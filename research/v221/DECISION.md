# V221 decisive gate: retire fixed hashed MSHR partition

Evidence class: Python admission model, independent oracle, RTL simulation, Liberty-mapped combinational lookup area. No valid STA or power data.

Mechanism: 16 MSHRs partitioned into four 4-entry banks by tag[1:0]. Matched control: fully associative 16-entry CAM, same tag width, one lookup port, response path, and capacity. Derived law: 16 versus 4 comparator lanes; target-bank-full probability for n uniform live tags is sum from j=4 to n of binom(n,j)(1/4)^j(3/4)^(n-j). It is 0.00390625 at n=4 and 0.351221 at n=12.

Frozen unseen holdouts: seed 22117 uniform latency 4: throughput ratio 1.0000 (positive low-occupancy prediction passed); seed 22129 90% bank-zero latency 12: ratio 0.358835 (-64.12%, negative prediction passed); seed 22131 uniform latency 12: ratio 0.744602 (-25.54%, negative sensitivity passed). Compute-only unchanged. Independent oracle: 218450 checks, zero mismatches. RTL: 5000 differential lookups passed.

Mapped lookup-only Nangate45 area, Ubuntu 22.04 Yosys: full CAM 791.882, banked 665.266, -15.99%. Ubuntu 24.04: full 783.370, banked 596.638, -23.84%. Storage excluded. No valid STA: OpenSTA 2.0.17 rejected report_checks -group_path_count, report_worst_slack -max, and report_check_types -max_slew; process still exited 0. CI success is a false-green electrical gate. No max-cap, slew, delay, wire-load, or power claim.

Prior art: banked associative structures and hierarchical GPU MSHRs already exist; see Karimi et al. 2020 arXiv:2007.16175. The candidate is not novel as stated. High-occupancy modeled throughput losses prevent a Pareto claim. RETIRE V221; no integrated tile change. V153/V156 FP32 cutset remains electrically unqualified and retired. No 5090-class equivalence claim.

CI runs: 39197375693 (RTL syntax failure), 39197482834 (RTL and synthesis pass), 39197629551 (mapped synthesis pass, STA Tcl failed). Two repair passes exhausted; next run must pivot to a distinct mechanism rather than repair V221.
