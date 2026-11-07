# V317 stateful write-observation gate: hosted RTL and generic PPA sensitivity (2026-11-01)

**Decision: retain only as a correctness/evidence instrument. Do not promote as a novel GPU mechanism.** The frozen [stateful protocol](FROZEN_STATEFUL_WRITE_MONITOR_GATE_20261101.md) was committed at `f361eea` before implementation. Final validated code head: `d11395f168474aff57766375c12ae94025b46f9f`.

## Functional and independent semantic verification

The [hosted stateful forwarding workflow #41251667478](https://github.com/sushxnthd/vektor/actions/runs/41251667478) **passed** on `d11395f`. It simulated **12,300** Icarus checks: 4,096 exhaustive 4-lane captured/requested/write-mask combinations, each checked before a live write, during the same-cycle write hazard, and after sticky invalidation; plus directed namespace, reset, capture/write collision and re-capture cases. The independent software value-history checker passed four tests, enumerating **768** two-lane snapshot/value/write/request worlds, with **144** safe admissions, **176** overlapping-write hazard blocks and **zero** unsafe admitted values under the stated complete-write-monitoring assumption.

A same-cycle capture/write collision dirties overlapping captured lanes even if captured data happens to equal the new value. A concurrent request is blocked from the old entry while a new snapshot is being captured. Dirty bits remain sticky across value ABA. Writes to a different warp, register or bank do not invalidate the cached entry. This module assumes a coherent source snapshot and **all** physical writes are observable; no tile-level proof of these assumptions exists.

## Generic synthesis: missing source storage is expensive

Yosys 0.33 synthesized the complete snapshot, sticky mask, identity comparators, forwarding gate and same-cycle hazard rejection, with flattened hierarchy. The earlier combinational-only gate is included for comparison, **not** as an equal-functionality performance baseline.

| Lanes x bits | Combinational-only generic cells | Full stateful generic cells | State bits / flop cells | Stateful generic logic-depth proxy |
|---|---:|---:|---:|---:|
| 4 x 8 | 72 | **214** | 49 | 11 |
| 8 x 16 | 200 | **586** | 157 | 12 |
| 32 x 32 | 1,250 | **3,645** | 1,106 | 13 |

At 32 x 32, the fully stateful model uses **2.916x** as many generic cells as the combinational gate alone, including 1,024 data snapshot bits and 82 additional metadata/dirty bits. This is an **implementation accounting correction**, not a technology-mapped area ratio. The source-pinned Yosys JSON, cell/fanout summaries, logs and simulation trace are archived in [the hosted artifact](https://github.com/sushxnthd/vektor/actions/runs/41251667478/artifacts/13061442472). The reported logic depth is generic and unplaced; it is **not** clock frequency or routed delay.

The first hosted run [#41251580028](https://github.com/sushxnthd/vektor/actions/runs/41251580028) failed only at netlist accounting because the parser expected flattened hierarchy; all new semantic and RTL simulations passed. The Yosys command was corrected to `synth -flatten` at `d11395f`, and the complete subsequent workflow passed. Preserve this failure as provenance rather than hiding it.

## Strongest same-information control and boundary

An equal-resource collector with the same coherent snapshot, per-lane write visibility and conservative admission predicate can perform every transfer admitted by this candidate. Therefore the incremental modeled read-transaction saving is **exactly zero** against that control. No positive GPU throughput law can be claimed for this implementation. Prior 1.5x/2x synthetic improvements depended on weaker or non-equivalent baselines and remain invalid as evidence of a novel architecture.

The physical costs are still incomplete: the write-event distribution network, actual register-file bank organization, collector capacity, placement/wire length, clock-tree loading, standard-cell timing, dynamic power and actual GPU trace demand are unmeasured. In particular, the 1,106 state bits are a concrete register-count proxy, **not** RF-cache SRAM macro area or energy. Generic fanout is available in the archived JSON but cannot substitute for electrical checks.

## Next research gate

Do **not** invest in another variant of forwarding without a new independently predicted resource advantage over the strongest equal-information collector. The next viable architecture candidate must establish an equivalent operand-supply path, frozen predicted-win/no-win workloads, matched-resource RTL, physical timing and electrical evidence, and a positive law that survives unseen dynamic workload traces. Do not resurrect V287 or displace the existing primary V296 direction based on this falsification. Kernellum PR #119 remains untouched.
