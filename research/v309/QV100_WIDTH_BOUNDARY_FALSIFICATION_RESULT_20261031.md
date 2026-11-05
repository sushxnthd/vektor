# V309: independently accepted two-workload width transfer and conditional boundary falsification (2026-10-31)

## Evidence and frozen decision

The prospectively frozen LUD bus-width transfer from `QV100_LUD_BUSWIDTH_TRANSFER_PREREG_20261031.md` **passed** the source-pinned hosted workflow [#41138030921](https://github.com/sushxnthd/vektor/actions/runs/41138030921) at `2f94a6ca110848426f907a8a9d2d83f2de63c3c5`. The independent transfer audit passed all three frozen predictions. The run retained raw logs, two repeats per configuration, original launches and memory-copy commands, exact single-parameter mutations, and per-kernel conservation checks. [Artifact #13017776096](https://github.com/sushxnthd/vektor/actions/runs/41138030921/artifacts/13017776096).

| Original workload | 8-byte bus | 16-byte baseline | 32-byte bus | 16-to-32 gain |
|---|---:|---:|---:|---:|
| Pathfinder, four launches | 28,729 | 28,717 | 28,717 | 0.0000% |
| LUD-64, ten launches | 127,309 | 127,309 | 127,309 | 0.0000% |

All values are **simulated QV100-SASS cycles**, not physical GPU measurements. Both workloads retained their independently accepted instruction and cache counter totals. The second workload has more reported global writes per simulated instruction, yet this did not create width sensitivity in the tested range.

## Mechanistic conditional-law kill test

Consider the **strong but falsifiable** smooth, non-saturated inverse-width service law
`T(w)=T_fixed + K/w`, with unchanged work and all other parameters fixed. Its exact three-point implication is

`T(8)-T(16) = 2*[T(16)-T(32)]`.

- Pathfinder: observed left side **12 cycles**; observed right side **0 cycles**. The exact law is **falsified** on this deterministic simulator response, including with a one-cycle residual tolerance. Width-limited fraction inferred from halving is `12/28717 = 0.000417871`; inferred from doubling is `0`. They disagree.
- LUD-64: both sides **0 cycles**, consistent with `K=0`, but this does not identify whether width is intrinsically non-binding or hidden by another service floor.
- Under this particular smooth law, a hypothetical >=2% width-limited time fraction at the 16-byte baseline would predict >=1% cycle improvement on doubling. The observed improvement is 0% on both workloads. **Reject that conditional hypothesis**, not all bandwidth optimizations.

A threshold/floor model such as `T(w)=T_fixed+max(T_floor,K/w)` can explain a plateau after 16 bytes. The three widths do **not** uniquely identify its parameters or establish the cause. A positive general law requires new workload regimes that cross a predicted threshold, with independently checked traffic and occupancy/port pressure. Do not retrofit the current null results into a claimed physical mechanism.

The executable independent model falsification is `qv100_width_boundary_falsification.py`, with forged-evidence rejection controls. It is integrated after the already accepted two-workload audit in the existing workflow. **The new law-checker CI run must pass before its own output is promoted as independently verified.** The underlying two-workload simulation results above are already accepted.

## Architecture decision

**Kill the modeled 16-to-32-byte DRAM bus-widening direction for these two workloads.** Do not claim the same no-win across all workloads. The test changes a simulator configuration, not actual pins, PHY, wiring, area, clock, energy or silicon. No equal-resource architecture comparison exists, and the current V309 branch/PR is **qualification only**, not a newly promoted architecture mechanism.

Next substantive gate: identify one implementable RTL architecture mechanism from preserved physical evidence; compare against a strongest equal-resource alternative, with matched synthesis, timing and electrical constraints, and then run prospectively frozen predicted-win and predicted-no-win workloads. No RTX 5090 equivalence claim.
