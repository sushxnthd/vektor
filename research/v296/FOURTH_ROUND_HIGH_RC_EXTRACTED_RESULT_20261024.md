# V296 fourth-round high-RC extracted physical result (2026-10-24)

**Evidence tier:** completed pinned OpenROAD detailed-route + OpenRCX SPEF, independently parsed by `research/v296/audit_fourth_high_rc.py`; **pre-CTS and high-RC only**. This is a **new targeted provisional pass**, not a retroactive pass of the frozen six-case experiment. Only active mechanism: V296 pairwise bank-conflict admission. V287 retired.

## Immutable evidence and frozen protocol

- Prospective protocol (committed before execution): [FOURTH_ROUND_HIGH_RC_PREREG_20261024.md](FOURTH_ROUND_HIGH_RC_PREREG_20261024.md).
- Completed [GitHub Actions run 40027903793](https://github.com/sushxnthd/vektor/actions/runs/40027903793), head `31f59821c2c1dd4f9d6edff3c6035e11f6316d19`, job `120668600404`, successful on 2026-10-23 UTC (2026-10-24 India).
- Raw [artifact 12534554683](https://github.com/sushxnthd/vektor/actions/runs/40027903793/artifacts/12534554683), 7,949,518 bytes, GitHub SHA256 `819473d4257f513678f1de206b2605382bedbde80aee1dee757d08f2e80de460`; includes all three logs, detailed-route DEF/SPEF, reports and independent `fourth_audit.json`.
- Shared constraints: 3.5 ns clock, 0.25 ns max transition, 0.005 pF output load, high-RC scale 2.0, cap margin 20%, fourth-round slew margin 25%, identical repair and extraction procedure for all three architectures.

## Measured three-way result

| Post-fourth-round extracted high-RC metric | Original | Optimized one-hot | V296 pairwise |
|---|---:|---:|---:|
| Standard-cell area (um²) | 7196.363949 | 6949.250064 | **5987.926155** |
| Setup slack (ns) | **-0.113988** | -0.168119 | **+0.418903** |
| Hold slack (ns) | +0.249579 | +0.270420 | +0.282110 |
| Max-slew violations | 0 | **15** | **0** |
| Max-cap violations | 0 | 0 | 0 |
| Detailed-route DRC violations | 0 | 0 | 0 |

The independent checker returned **`TARGETED_HIGH_RC_PROVISIONAL_PASS`**. V296 meets P1 (zero extracted electrical/DRC violations; nonnegative setup/hold) and P2 (13.833491% area saving against the smaller optimized control and +0.532891 ns setup-slack lead against the faster original control). The observed fourth repair reduces the candidate's previously recorded 33 high-RC slew violations to zero; this is an outcome comparison across distinct runs, not a claim of identical placed nets. Candidate area increased by ~2.660 um² versus the preceding high-RC third-round measurement, under differing repair protocols.

**Critical qualification:** the optimized one-hot control still has 15 slew violations and both controls miss 3.5 ns setup. A control failing closure is not a physically viable Pareto comparator at the frozen operating point. A new equal-resource, *electrically clean* control optimization is required. The original frozen six-case extracted-RC gate remains **`DETAILED_PHYSICAL_GATE_FAIL`** and must not be overwritten.

## Prospective predictive boundary for the *next* equal-resource control experiment

Let `A_v=5987.926155`, `A_o=6949.250064`, `A_r=7196.363949` (um²) and `s_v=+0.418903`, `s_o=-0.168119`, `s_r=-0.113988` (ns) be the *observed* post-route reference point. Let `dA_i` be a future change in cell area from that point and `p_i` a future **loss** in setup slack (negative if timing improves). With new same-run, fully closed physical controls, V296 retains >=10% area saving and >=0.20 ns setup-slack lead **if and only if**, for *each* control `j in {o,r}`:

```
dA_v - 0.90*dA_j <= 0.90*A_j - A_v
p_v - p_j <= s_v - s_j - 0.20 ns
```

Numerical thresholds (valid for the above fixed reference point; not physical guarantees):

| Comparator | Differential area budget `dA_v-0.9*dA_j` (um²) | Differential slack-loss budget `p_v-p_j` (ns) |
|---|---:|---:|
| Optimized one-hot | <= **266.398903** | <= **0.387022** |
| Original | <= **488.801399** | <= **0.332891** |

**Pre-frozen counterexamples for the next experiment:** if the optimized control becomes clean and its area falls by >=295.998781 um² with V296 area unchanged, the >=10% saving disappears. If the original control becomes clean and improves setup slack by >=0.332891 ns with V296 slack unchanged, the >=0.20 ns timing lead disappears. These are *conditional thresholds*, not evidence those control improvements are feasible. Do not tune after seeing the next sweep. Use the independently routed post-repair measurements, not these reference estimates, for the final decision.

## Scientific interpretation and next kill gate

V296 remains a **controller implementation-topology** candidate, not a demonstrated GPU throughput mechanism. Same-clock issue throughput improvement is **0%** by functional equivalence. A tile-level gain requires verified controller criticality, CTS and clock-tree loading, post-CTS electrical/hold closure, area/power integration, matched-resource controls, and bandwidth/occupancy limits. There is no measured GPU energy or frequency gain.

Next experiment: preregister a matched **control Pareto sweep** with identical technology, voltage, RC, floorplan and tool settings; independently close max slew/cap, DRC, setup and hold for each variant. Optimize the strongest one-hot control within the same resource envelope before comparing Pareto fronts. **Kill V296** if its advantage vanishes against an equal-resource clean control or if the resulting tile-level frequency/area consequence is null. Preserve the frozen workload predicted-win/no-win holdouts. No unsupported RTX-5090-equivalence claim.

**Status:** targeted high-RC provisional pass; frozen six-case failure preserved; world-class completion gate **NOT REACHED**.
