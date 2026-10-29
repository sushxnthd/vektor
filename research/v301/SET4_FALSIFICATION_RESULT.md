# V301 prospective four-way set-associative falsification (2026-10-29)

**Verdict: eight-way CAM is not justified by the synthetic controls. Physical comparison is still unperformed.**

The prospective protocol was frozen in commit `27c5e27`, before the N1-N4 seeds 201-220 were evaluated. All cases use 5000 offered cycles, four return lanes, eight queue entries, one scoreboard write port (except two-bank, which has two), and identical input streams. The N1 and N3 precommitted rule was that set4 at >=95% of full CAM means the eight-way CAM lacks a sufficiently large strong-control advantage.

| Frozen regime | V301 full CAM (events/cycle) | set4 (events/cycle) | set4/V301 | two-bank (events/cycle) |
| --- | ---: | ---: | ---: | ---: |
| N1 medium skew, short epoch | 1.830553 | 1.745257 | **95.340%** | 1.381506 |
| N2 uniform high | 1.066369 | 1.053549 | 98.798% | **1.878912** |
| N3 hot, short epoch | 3.195944 | **3.195944** | **100.000%** | 1.112241 |
| N4 short-epoch diagnostic | 1.478044 | 1.436464 | 97.187% | **1.478531** |

**Both preregistered falsification conditions were met.** In N1, the eight-way CAM's residual gain over set4 is only 4.887% (=1/0.953405-1); N3 ties exactly. In N2 the two-bank control wins decisively; N4 two-bank slightly exceeds full CAM.

Independent exhaustive conservation: **3072 policy/trace configurations passed**; 192 selftests passed. Hosted execution: [GitHub Actions #40821886147](https://github.com/sushxnthd/vektor/actions/runs/40821886147), full raw JSON in the artifact and job log. Source: `research/v301/set4_holdout.py`.

**Severe workload-model confounder:** N1's upstream queue peaked at a mean of 3852.5 pending events for full CAM and 4288.45 for set4, from 5000 offered cycles. N2 peaked at >11000 pending events for both. These are overdriven producer-backlog drain tests, not steady-state GPU throughput. N3 is approximately stable for full CAM but set4's peak pending is 10.3. N4 two-bank is marginally ahead.

## Physicality decision

The originally claimed H1 +16.866% gain over set2 was not robust to a stronger same-capacity, one-write-port set4 controller. **Do not claim a world-class architecture result or use the opened H1 threshold to override this prospective failure.** The eight-way CAM requires eight-way tag comparison and multi-way update logic; the set4 alternative has only four ways per set. It is plausible, but not yet proven, that set4 is physically cheaper and faster.

The only defensible reason to continue V301 is a strictly bounded **matched RTL physical falsification** against set4 and two-bank, with no change to the synthetic thresholds or workloads. If set4 is physically no worse in area/timing/power and sustains >=95% of full CAM's frozen N1 rate, retire V301 immediately. Without such a test, label the mechanism *unjustified*, not physically validated or novel.

No real GPU scoreboard port-count, energy, integrated tile throughput, or RTX 5090 equivalence is established.
