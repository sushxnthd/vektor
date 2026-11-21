# V317: physical dominance gate against the competent compact baseline (2026-11-09 UTC)

Evidence tier: **completed matched RF-proxy OpenROAD routing**, not an SRAM macro or integrated GPU. This is a **negative result**; it does not reopen the killed V317 positive mechanism.

## Source-pinned inputs

- Matched compact-versus-pairwise RF-proxy OpenROAD run [41443576796](https://github.com/sushxnthd/vektor/actions/runs/41443576796): compact area **21,314.6 um²**, pairwise area **21,324.7 um²**. Compact: **6 hold / 14 max-cap** violations; pairwise: **0 hold / 21 max-cap** violations. Both electrically illegal.
- Independently completed matched generic-Yosys [run 42536495043](https://github.com/sushxnthd/vektor/actions/runs/42536495043): source fixed **1321 cells / 49 levels**; pairwise fixed **272 / 22**; source rotating **1614 / 58**; pairwise rotating **558 / 31**. These are **controller-only generic gates**, not placed cell area, setup slack, wire RC or tile throughput.
- The previously executed exact RF-arbiter challenger had **6339 generic cells** versus **1321** for its fixed-priority source, i.e. **4.7986x** the source cell count. This candidate is not a competitive equal-area baseline.

## Reproducible conditional bounds

Let C=21314.6 and P=21324.7 um². For any identical nonnegative added tile hardware H, P+H>C+H, hence for any area budget B>=0, floor(B/(P+H)) <= floor(B/(C+H)). The pairwise implementation **cannot create an extra tile through area reduction** against this compact control. The observed area saving 1-P/C is **-0.047385%**. The strict previously frozen >=2% whole-proxy area-saving gate fails, even before electrical legality.

Under equal work, equal occupancy, equal per-cycle grants, and common bandwidth constraints, clock-adjusted throughput ratio is T_compact/T_pairwise. Thus pairwise must run at **strictly shorter clock period** than compact merely to obtain a positive throughput ratio; generic depth 22 versus 49 does not establish that. An equal-clock model predicts exactly **1.000x** service. A 2% clock-adjusted gain requires T_pairwise <= T_compact/1.02, independently of generic cell counts. This is a *necessary* condition under the stated equal-work assumptions, not evidence that it is met.

**Decision:** no physically credible positive V317 tile-level claim survives. Do not promote generic cell-count or logic-depth improvements to mapped/routed timing, energy, or GPU IPC. The next legitimate positive claim requires new legal, matched routed evidence against the compact control, independently audited offered-workload service, and a frozen predictive boundary tested on unseen regimes. Preserve prior failures and do not change the threshold after seeing results.
