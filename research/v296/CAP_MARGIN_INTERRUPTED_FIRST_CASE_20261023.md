# V296 cap-margin prospective experiment: interrupted first case (2026-10-23)

## Evidence identity and decision

- Source workflow: https://github.com/sushxnthd/vektor/actions/runs/39961546771
- Preserved artifact: https://github.com/sushxnthd/vektor/actions/runs/39961546771/artifacts/12505702141
- Head at failed execution: `0cd54bd7fc0f5de9c76d0430d0576d1af7194ae0`.
- **Decision: INCOMPLETE_EVIDENCE; neither V296 win nor loss established.** No candidate or optimized-control physical case ran. The preregistered all-six-case gate was not evaluated; workload holdouts remain sealed.

## First observed case: original control, nominal RC, 3.5 ns

| Stage | Area (um^2) | Max-slew violations | Max-cap violations | Setup slack (ns) |
|---|---:|---:|---:|---:|
| Placed | 3856.734043 | 1413 | 62 | -3.070271 |
| After first matched margin repair | 6280.791887 | 0 | 0 | -0.024833 |
| After first global route | 6280.791887 | 0 | 0 | +0.002116 |

The first repair increased standard-cell area by **2424.057843 um^2 (62.85%)**. The routed slack is only **2.116 ps**, an extremely small modeled setup margin. The two-round protocol and V296-versus-control comparisons did not complete. This is *global-route-estimated* RC, not detailed-route/SPEF, CTS, hold closure, or signoff.

## Failure and correction

After `V296_FIRST_CAP_VIOLATORS_BEGIN`, pinned OpenSTA rejected `report_check_types -max_count 50` with `STA-0562`. This is an instrumentation incompatibility, not an electrical or architectural failure. The first case stopped before its DEF and before the second repair. The raw artifact and failure remain intact.

The follow-up commit removes only the unsupported `-max_count 50` option from both first and final capacitance-violator reports. The reports still request `-max_capacitance -violators -format end -digits 6`; no electrical, timing, area, resource, RC, clock, or kill threshold was changed. The CI rerun must be independently checked; this report does not claim the repair succeeded.

## Frozen interpretation

A passing result would require **all three** architectures (original, optimized one-hot, V296) to finish **both** nominal and high RC at 3.5 ns with zero max-slew/max-cap violations, nonnegative setup slack, and V296 lower area and better slack than **both** controls. A lost relative advantage means retire V296; incomplete evidence means continue repair without opening holdouts. Same-clock issue-throughput advantage is predicted to be 0%.
