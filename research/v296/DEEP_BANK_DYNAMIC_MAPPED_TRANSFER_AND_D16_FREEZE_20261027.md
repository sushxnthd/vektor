# V296 dynamic deep-bank mapped transfer: SHA-pinned outcome and D16 prospective gate (2026-10-27)

## Evidence boundary
This report uses **original immutable artifacts** from [GitHub Actions #40527760514](https://github.com/sushxnthd/vektor/actions/runs/40527760514), head `41b3a4d2c922aea43336aa571a60d5b3d88dbcb5`. All five original ZIP SHA-256 digests were checked independently. This is **RTL plus Yosys/Nangate45 mapped synthesis only**, not routed timing, physical feasibility, energy, GPU IPC, or an RTX 5090 comparison.

The 2048-cycle independent direct-index RTL oracle passed at D=4, 8, 16, reporting 6608 accepted waves per run and all D word addresses visited. Both implementations use the same 16-bank, two dynamic read ports/bank, 8-bit word RF and one global write port. Source RTL, issue cores, Yosys version, and Nangate45 library SHA are identical between D4/D8 mapped experiments. Yosys `check -assert` reported **zero problems** for all four mapped configurations.

| Bank depth D | V296 mapped cell area (µm²) | V295 serial mapped cell area (µm²) | V296 area saving | LTP -noff nodes, V296/serial |
|---|---:|---:|---:|---|
| 4 | 12,960.584 | 13,835.990 | 875.406 (6.3270%) | 252 / 270 |
| 8 | 17,552.542 | 18,782.260 | 1,229.718 (6.5472%) | 267 / 282 |

**Critical interpretation:** `ltp -noff` emitted many detected-loop warnings because it does not respect flip-flop timing boundaries; its node counts are **not clock period or STA timing measurements**. The serial control uses `v295_issue_core(PREDECODE=0)`, which is an equal-RF resource comparison but is **not proven to be the strongest independently feasible fifth-stage serial physical control**. The mapped RF is a flop array, not a real production register-file macro. Thus the observed area ordering is a narrow mapped proxy result, not a physically credible GPU advantage.

## Frozen *before* D16 mapped evaluation
Fit only the two available depths, D4 and D8, using the transparent two-point linear extrapolation
`A_x(D)=A_x(8)+[(A_x(8)-A_x(4))/4]*(D-8)`, where x is pairwise or serial.

At D16, **prospective predictions, not observations**:
- V296 mapped cell area **26,736.458 µm²**.
- V295 serial mapped cell area **28,674.800 µm²**.
- Pairwise area saving **1,938.342 µm²** (6.7597% relative to serial).
- Preregistered model survival gate: **each** D16 mapped area must be within **15% relative error** of its prediction **and** V296 mapped area must remain lower than serial. If either fails, reject the *linear mapped-area transfer model*. Do not infer architecture failure from this proxy alone.
- If D16 synthesis times out or fails, classify as **censored**, not a pass or numerical falsification.

This two-point extrapolation is not a physical area law, not evidence of realistic wire/load scaling, and not a positive workload throughput law. Any V296-only physical area overhead exceeding the measured serial-minus-pairwise margin erases the mapped area advantage: **875.406 µm² at D4; 1,229.718 µm² at D8**. These are necessary area break-even boundaries only. At a purely illustrative 30,000 µm² packing budget, both D4 implementations fit 2 mapped copies and both D8 implementations fit 1; **there is no extra integer slice in either case**.

## Falsification decision
**Retain V296 pairwise bank admission as the sole provisional mechanism; retire fixed-word static readout for D>2.** D4/D8 dynamic readout passes RTL and mapped synthesis, but cannot advance to a production-depth GPU claim. Next: D16 blinded-to-outcome mapped check; independent routed extracted-RC gates at realistic depths for both contestants; strongest feasible serial alternative; bandwidth/port/occupancy and unseen workload validation. Preserve sealed workload holdouts and all earlier negative results. V287 remains retired; Kernellum PR #119 unchanged.

### Artifact digests
- D4 mapped, ID 12745855863: `fe59053e653148616c35b2e1304d34ff9e200fe0ddd02b443ba6b8c2bcf68b20`
- D8 mapped, ID 12744174948: `add9c2dcf6a85e6fd6bd5eaf63bee86c78bbc34e205c0b8d51378c612d9df8fb`
- D4 RTL, ID 12745770168: `41bb2b30d57f0dbea2212243b0896c521f908c60538cf518c1c1e58f961b4d21`
- D8 RTL, ID 12743389008: `69d662753c42526a3b63dde5a3f0bd0cb9c2df61a5ee4a5e6fadae60acd29c1b`
- D16 RTL, ID 12744113447: `cc9cfc0c456fdd5e9781f32e684319cae6c7935676fe3c3c1f0d8b22d0dbce6f`
