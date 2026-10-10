# Vektor-085: coherent RF bank sharing and writeback reservation

**2026-10-10 · SIMULATED only.** A separate value-aware V-Tile pipeline model accounts for RAW/WAW, staged operand collection, finite per-bank RF read/write grants, finite issue, execution latency, coherent cache invalidation and future writeback-slot reservation. No RTX 5090-class claim.

## Key measurements (synthetic instruction tokens, not FP32 GPU throughput)

| 8 waves ×128 instructions, spread, latency 3, no cache | Simulated cycles |
|---|---:|
| Shared 3 read/write ports, no reservation | 490 |
| Fixed 2 read + 1 write port, no reservation | 401 |
| Shared 3 ports with read cap 2 | 401 |
| Shared 3 ports, future writeback-slot reservation | **395** |
| Fixed 2 read + 1 write, reservation | 397 |

Reservation reduces the worst-case selected trace by 19.4%, but **is not a universal speedup**. Frozen 96-case holdout: 47 wins, 17 losses, 32 ties versus unreserved shared3; worst regression +113 cycles. A four-cycle lookahead read throttle **failed** (17 wins, 31 losses, 48 ties). Among 120 boundary cases, shared3/split2+1 reversals depend on occupancy, latency and operand-cache capacity.

At 1,024 cold, single-bank, 2-source/1-destination tokens: shared2 = 0.6654, split1-read+1-write = 0.4988, split2-read+1-write = 0.9942 tokens/cycle. This matches a conservation bound: shared p ports <= p/3 tokens/cycle, ignoring latency and fill/drain.

**Verification:** 75 Python tests passed. All simulation cases were checked against a sequential integer interpreter and Python event auditor. Independent C++17 trace auditor verified 2,560 commits across three fixed traces. No independent cycle-level replication, RTL simulation, synthesis or physical PPA has been performed.

**Reproducibility:** Full executable research package `vektor_085_shared_rf_writeback.zip`, SHA-256 `8991fbe156316e4fe8199edc5d411da632a2c9804d77be9c14fae5b647cbeb8f`, attached to the corresponding research run. The package is not yet mirrored into GitHub: **this branch contains the compact findings and experimental RTL only**, not the full simulation code.

**Limitations:** integer-valued instruction tokens, not IEEE FP32 or tensor operations; logical ports not equal-area silicon ports; cache fill/invalidation are uncosted; no NoC, GDDR7 controller, graphics, ray tracing or KPX runtime. No hardware equivalence or novelty claim.

Prior art: https://gpgpu-sim.org/manual/index.php/Main_Page documents operand collectors, RAW/WAW scoreboard and writeback-priority bank arbitration.

**Next decisive action:** integrate coherent writeback with canonical `sim/vektor/pipeline.py`; simulate and formally check the experimental grant RTL; test reservation on compiler-generated kernels under logical-port and area/timing controls. All 5090-class gates remain INCONCLUSIVE.
