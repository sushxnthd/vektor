# V307 frozen pilot: conditional synthetic survival, not physical validation

2026-10-29. Frozen protocol committed **before** formal pilot at `1c20c686a91b4c7bc7c629ec00ff5caaac130994`. Executable simulator SHA-256: `868db459b4db9ac23ae4004b8eaa78359891cec5e4e8f7437a0098dd264e0d7a`. Pilot seeds 31–34 only. Prospective holdout seeds 2001–2020 remain **unopened**. Unit tests passed locally: four tests, including 1,296 independent legal-subset enumerations. Independent structural counterexample audit passed.

## 240 synthetic warp instructions, cycles to drain

| Regime | Seed | MAX-NOW | V307 PRESSURE | FUTURE-TIE |
|---|---:|---:|---:|---:|
| W1 random bank pairs | 31 | 120 | 107 | 100 |
| W1 | 32 | 112 | 103 | 103 |
| W1 | 33 | 115 | 102 | 98 |
| W1 | 34 | 122 | 101 | 110 |
| N1 95% rotating pairs | 31 | 104 | 96 | 97 |
| N1 | 32 | 102 | 108 | 100 |
| N1 | 33 | 101 | 90 | 100 |
| N1 | 34 | 97 | 90 | 93 |
| N2 fixed pair per warp | 31–34 | 96 | 96 | 96 |

W1 mean cycles: MAX-NOW 117.25, PRESSURE 103.25, FUTURE-TIE 102.75. **Mean of per-seed throughput gains:** V307 vs MAX-NOW **+13.6061%**; V307 vs FUTURE-TIE **-0.3882%**. N1 mean cycles: 101, 96, 97.5 respectively; mean per-seed V307 vs FUTURE-TIE **+2.0197%**. N2 is an exact tie.

The predeclared gates are W1 >=10% over MAX-NOW, W1 >=-5% versus FUTURE-TIE and N1 >=-2% versus FUTURE-TIE. **All three pilot gates pass.** This is permission for physical testing, not a demonstrated architectural gain over the strongest control.

## Material negative evidence

Individual-seed fragility: W1 seed 31 V307 is **6.5421% slower** than FUTURE-TIE; N1 seed 32 is **7.4074% slower**. A mean-only gate conceals these tails. No parameter tuning is permitted using opened pilot seeds.

More importantly, **bank-pressure P is not a sufficient statistic for conflict-free issue capacity**. Independent counterexample:
- bank-pair masks (3,3,3,192): P=4, maximum independent issued set=2.
- bank-pair masks (3,3,5,9): P=4, maximum independent issued set=1.

Thus no claim of an exact pressure-to-throughput law is justified. An exact instantaneous capacity law is min(issue_slots, maximum independent set of the conflict graph), but it is a classical graph-theoretic statement and not V307 novelty. A surviving V307 must establish a new predictive *end-to-end* boundary law under realistic collector, port, occupancy, and timing constraints.

## Mandatory next gate and no-go rule

Implement clocked matched-interface RTL for PRESSURE, MAX-NOW and the strongest feasible FUTURE-TIE implementation; include real operand-collector staging, within-instruction same-bank operands, finite collector occupancy, scoreboard dependencies and RF port contention. Run synthesis and matched electrical/timing/wire/load sensitivity; evaluate area/energy proxies and unseen workloads **only after** physical feasibility is established. A pressure implementation that fails matched timing/area or has no robust throughput advantage over a simpler equal-resource alternative must be retired. A design that merely matches FUTURE-TIE but is smaller may be an engineering tradeoff, **not** a novel GPU breakthrough.

Reproduce from repo root: `cd research/v307 && python3 -m unittest -v test_simulator.py && python3 simulator.py --pilot && python3 audit_pressure_boundary.py`.

**Evidence tier:** local synthetic simulator, no clocked RTL, mapped synthesis, routed timing, GPU IPC, measured energy or RTX 5090 equivalence. Prior art: Barnes et al. HPCA 2023, GPGPU-Sim, LTRF. Preserve all negative evidence.
