# Vektor-065: counted replica quiescence and variance-sensitive tag pressure

**Scope:** component-level software correctness and a small experimental synthesizable per-slot tracker. Not GPU equivalence or physical PPA.

Run from repo root:
```sh
python3 research/065/tests/quiescence_065.py
python3 research/065/tests/check_replica_065.py
python3 research/065/tests/capacity_law_065.py
python3 research/065/tests/variance_cliff_065.py
```

The four scripts run 288 structured + 36 exploratory policy simulations, 1,698 exhaustive finite states, 72 independent differential comparisons, 216 occupancy-law tests, and 15 equal-mean variance comparisons. They write JSON into `research/065/results/`. The CI workflow `.github/workflows/vektor-065.yml` additionally installs free Icarus Verilog and Yosys to simulate `rtl/tb_quiescence_tracker_065.sv` and run generic synthesis of `rtl/quiescence_tracker_065.sv`.

**Assumptions:** all physical replicas are registered before close; every replica produces one terminal event; at least one primary delivery is guaranteed in throughput tests; the ACK path cannot replay; reset is externally fenced. These are assumptions, **not** verified features of a complete fabric. The weak first-delivery comparator is intentionally unsafe.

Read `WORLD_MODEL.md` for preregistered predictions, negative results, residuals, adversarial roles, and next decisive action. Read `TARGET_LEDGER.md` for external RTX 5090 targets and unresolved gates.
