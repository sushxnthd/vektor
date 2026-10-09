# Vektor-057: return-lane phase and bounded-age arbitration

**Evidence level: synthetic software model.** No silicon, mapped area, timing, power, compiled dynamic GPU trace, or RTX 5090 equivalence.

A two-slot, three-cycle-latency, one-return-lane collector shows a repeatable BACB phase effect: 12,000-cycle FIFO completions drop from 5,332 (no dedup) to 4,798 (dedup), despite RF reads falling from 12,000 to 9,600. A completion-aware return selector recovers 5,332 completions. Pure completion priority can starve a three-source instruction; a four-cycle age override restores bounded ready-response service in the tested model.

The standalone `tests/phase_model_057.py` reproduces the selected case, long-horizon control, starvation counterexample, and 96-pattern holdout. The `rtl/` prototype is a combinational response selector only, with external age tracking and queue state. `run_rtl_057.sh` invokes 12,288 independent Python-oracle differential vectors and Yosys generic synthesis through GitHub Actions. Do not claim RTL tests or PPA passed until CI evidence is inspected.

Full staged preregistration, independent heap-based event replay, 512-case stress results, negative results, and raw CSVs are in the accompanying reproducibility archive. No architectural novelty claim is made.
