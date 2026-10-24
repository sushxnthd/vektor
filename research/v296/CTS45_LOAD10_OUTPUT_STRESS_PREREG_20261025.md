# V296: frozen 10 fF output-load stress (2026-10-25)

**Status: PREREGISTERED BEFORE OUTCOMES.** Sole active architecture mechanism V296; V287 remains retired. Previous 5 fF feasible-control result is not modified. Workload holdouts remain sealed.

## Physical hypothesis and comparison

The completed 5 fF, 45%-density, 3.5 ns, high-RC, fanout-16, setup250 experiment established V296 6239.828210 um² / +430.410 ps setup / +284.848 ps hold versus feasible serial one-hot 7284.941983 um² / +104.791 ps setup / +249.547 ps hold. Both had zero electrical and DRC violations. Source run: https://github.com/sushxnthd/vektor/actions/runs/40113773976 .

**New, independent stress:** replace the external load on *all* output ports from 0.005 pF to **0.010 pF**, identically for both designs, after the unchanged third placement stage and before the shared fourth repair, clock-tree construction, post-CTS fanout-16 repair, setup250 optimization, detailed route and fresh extracted parasitics. Preserve pinned OpenROAD/Nangate45, 2x RC, 0.45 density, 3.5 ns clock, 250 ps max transition, area ceiling 7400 um² and 50 ps minimum setup margin. The serial one-hot control retains its extra pre-CTS repair. Do not selectively tune or re-run one contestant. This is an external-output-load stress, **not** a random placement-seed replication, full-tile timing, signoff or a PVT distribution.

## Frozen signed predictions and gates

**Predicted-win physical regime:** at 10 fF, if both implementations route with zero slew/cap/DRC violations and meet >=50 ps extracted setup, >=0 ps hold, <=7400 um² area, V296 will retain >=10% lower controller cell area and >=200 ps more setup slack. This is a falsifiable *hypothesis*, not a fact.

**Predicted-no-win regime:** at unchanged tile clock and resources, functional equivalence predicts exactly zero extra admitted operations per cycle regardless of the output-load result. Likewise, a bandwidth-saturated or other-path-limited tile gets no throughput improvement from faster controller logic. The positive tile throughput law is conditional on actual tile critical-path reduction and unsaturated bandwidth; do not use controller slack as a measured GPU frequency.

**Kill condition:** if V296 violates electrical/route/setup/hold/area feasibility at 10 fF, record `CANDIDATE_LOAD_STRESS_FAIL` and do not claim robust physicality. If the control fails, record `CONTROL_LOAD_STRESS_FAIL_NO_PARETO_CLAIM`, even if V296 passes. If both pass but the preregistered 10% area / 200 ps timing gates fail, record `LOAD_STRESS_PARETO_FALSIFIED`. No winner selection based on incomplete runs.

## Reproducibility and independent audit

- Runner: `research/v296/run_cts45_load10.sh`
- Physical Tcl: `research/v296/cts45_load10.tcl`
- Independent audit: `research/v296/audit_cts45_load10.py`
- Hosted workflow: `.github/workflows/v296-cts45-load10.yml`

The checker requires a unique 10 fF load marker between the completed third stage and CTS, verifies the original setup250 physical evidence gates, and reports failures separately. Negative results and artifacts must be preserved. This stress does not satisfy equal-consumed-area, power, full-tile, unseen-workload, or novelty gates.
