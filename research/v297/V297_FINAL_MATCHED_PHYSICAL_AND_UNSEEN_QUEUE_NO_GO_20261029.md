# V297 final matched physical and prospective queue no-go (2026-10-29)

## Verdict
**Retire V297 as a positive GPU scheduling mechanism.** Its bounded cooldown cannot beat the simpler, physically implemented unrestricted maximum-compatible-pair selector under the preregistered three-request/two-issue-slot/two-bank-port resource model. V287 and V296 remain retired. Do not turn the max-pair comparator into a new "novel" V297 claim; maximum-cardinality bank-aware scheduling has relevant prior art.

## Evidence tier A: matched routed arbiter macro (not a GPU tile)
[Three-way OpenROAD workflow #40775325841](https://github.com/sushxnthd/vektor/actions/runs/40775325841), SHA `41a9291b5d4fa3d2fd6f54c38b84b81ad0840c96`. All contestants used identical registered input/output boundaries, 3.5 ns clock, 100 ps setup/50 ps hold uncertainty, Nangate45, 0.45 placement density, 2x wire/RC extraction, CTS, global and detailed routing, and independent fail-closed audit. The initial run #40775116430 failed because the runner incorrectly demanded a pre-existing output-prefix file; this was repaired at SHA `41a9291` and is **not** counted as physical evidence.

| Extracted-RC measurement | Compact V297 | Unrestricted max-pair | Optimized rotating |
|---|---:|---:|---:|
| Routed cell area (um2) | 358.035990 | **340.480005** | 376.123993 |
| Setup slack (ns) | 2.911081 | **2.944061** | 2.855263 |
| Hold slack (ns) | 0.005009 | 0.002424 | 0.002795 |
| DRC violations | 0 | 0 | 0 |
| Max capacitance violations | 0 | 0 | 0 |
| Max slew violations | 0 | 0 | 0 |
| Complete DEF + SPEF | Yes | Yes | Yes |
| Frozen +50 ps setup, >=0 hold gate | Pass | Pass | Pass |

Max-pair is **4.903% smaller** than compact V297 in the same registered macro and has **32.980 ps more setup slack**. Its hold margin is 2.585 ps smaller, but both pass the frozen zero-hold-violation gate. All hold margins are narrow, so do not extrapolate robustness. The shell is a small arbitration macro; neither tile-level occupancy nor physical energy was measured. No power win, GPU speedup or RTX-5090 equivalence is claimed.

Fixed-route setup-clock extrapolation (not reimplemented physical timing): minimum clock to retain the +50 ps guard is `3.5 - setup_slack + 0.05` ns: compact 0.638919 ns, max-pair 0.605939 ns, rotating 0.694737 ns. This is not a validated tighter-clock design.

## Evidence tier B: prospective unseen finite-queue transfer
[Independent SHA-locked queue workflow #40775655569](https://github.com/sushxnthd/vektor/actions/runs/40775655569). The five unseen rate/regime combinations and four fresh seeds were committed in `V297_UNSEEN_QUEUE_TRANSFER_KILL_PREREG_20261029.md` **before** the evaluator or results. The original queue generator was verified unchanged at Git blob `7e85e328c6d6d1b79ab7082a8ab0171cdb442657`.

| Frozen transfer regime | Arrivals/cycle | Max-pair minus V297 throughput (waves/cycle) | Max-pair minus V297 drops |
|---|---:|---:|---:|
| 37-cycle burst motif | 3 | 0 | 0 |
| Uniform 16 banks | 3 | +0.000025 | -0.5 |
| Single hot bank | 1 | 0 | 0 |
| 37-cycle burst motif | 1 | 0 | 0 |
| Single hot bank | 3 | 0 | 0 |

All **5/5 preregistered** comparisons met the frozen max-pair non-inferiority boundary, with zero bank-port violations. The earlier persistent-queue experiments likewise showed max-pair equal or marginally better in all seven measured regimes, including V297's strongest blocker-motif case. This is a finite synthetic queue, not application IPC, and cannot establish dominance for all possible dynamic arrival processes.

## Evidence tier C: exact scheduler semantics and boundary law
Existing 11,664-case exhaustive canonical test: compact V297 matches the cooldown policy on all cases; unrestricted max-pair is never worse in immediate admissions and strictly better in 60 cooldown-active cases. For the frozen independent Markov blocker motif with probability `p` and persistence `a`, the candidate's rescue rate is `p/(1+a)`, while unrestricted max-pair's is `p`. The admission deficit is `p*a/(1+a)`. The law transferred on four unseen first-order Markov regimes within 0.000405 absolute ratio error but **failed** on the preserved periodic negative control. It is not a general dynamic GPU throughput law.

## Hard kill gate
The preregistered matched physical comparison and prospective queue transfer are both satisfied by the stronger max-pair control, with lower routed cell area and no worse setup timing. **Stop V297**, preserve this PR unmerged as a negative result, and select a genuinely different mechanism only after a prior-art audit and prospective resource-matched positive boundary law. Do not reopen V287/V296 or continue optimizing cooldown parameters.

## Reproduction
- Physical runner: `research/v297/run_v297_matched_physical.sh`
- OpenROAD Tcl: `research/v297/v297_matched_physical.tcl`
- Registered RTL: `research/v297/rtl/v297_matched_shell.v`
- Independent electrical/physical checker: `research/v297/audit_v297_matched_physical.py`
- Queue transfer: `research/v297/v297_unseen_queue_transfer.js`
- Frozen protocols: `research/v297/V297_MATCHED_PHYSICAL_KILL_PREREG_20261029.md`, `research/v297/V297_UNSEEN_QUEUE_TRANSFER_KILL_PREREG_20261029.md`
- GitHub Actions immutable raw artifacts and independent JSON audit at the two workflow links above.

**World-class completion gate:** not reached. No integrated GPU tile, physical power proxy, new physically positive architecture, or independent novelty claim.
