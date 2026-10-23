# V296: prospective two-round cap-margin electrical-closure result (2026-10-23)

## Frozen experiment and evidence identity

- Preregistration: `research/v296/CAP_MARGIN_REPAIR_PREREG_20261023.md` (written before evaluation).
- Complete rerun after a reporting-command compatibility repair: [Actions run 39967273689](https://github.com/sushxnthd/vektor/actions/runs/39967273689), [41-file artifact 12507594243](https://github.com/sushxnthd/vektor/actions/runs/39967273689/artifacts/12507594243), artifact SHA-256 `abafd41930be74be5c103dd7b69c611e604e45127491061a72a12c698930f886`.
- Source head `b40af3ec00fe03fa92ed5e6e78f864cbba589b3b`. The later `dcd1a57649ea68c881f8a364f9da6af6f683a6ff` only added a forensic report.
- All six cases completed placement, two equal electrical-repair rounds, global routing, and the independent audit. OpenROAD 2.0-17598-ga008522d8, Nangate45, identical 3.5 ns clock and 0.005 pF output load. All numbers are **global-route estimated RC**, not detailed-route extraction or signoff.
- The workflow's red status is **a scientific gate failure**, not an interrupted execution: `MARGIN_PHYSICAL_GATE_FAIL`, `all_clean=true`, `all_timed=false`, `candidate_smaller_both_scenarios=true`, `candidate_faster_both_scenarios=true`. Do not suppress this failure.

## Frozen six-case outcomes

All six final routed cases had **zero max-slew and zero max-capacitance violations**. Area is repaired controller standard-cell area in µm²; slack is modeled worst setup slack at the **same** 3.5 ns clock.

| RC | Original area / slack | Optimized area / slack | V296 area / slack | V296 saving vs smallest control | V296 lead vs fastest control |
|---|---|---|---|---:|---:|
| Nominal (1.0×) | see artifact / **−0.039100 ns** | **6250.202** / **+0.375115 ns** | **5375.860** / **+0.762746 ns** | **874.342 µm² (13.989%)** | **+0.387631 ns** |
| High (2.0×) | see artifact / **+0.003946 ns** | **6922.650** / **+0.188226 ns** | **5983.670** / **+0.677119 ns** | **938.980 µm² (13.564%)** | **+0.488893 ns** |

The original controller's nominal-RC setup slack **−39.100 ps** violates the preregistered requirement that **all six** cases meet 3.5 ns. The optimized control and V296 both meet 3.5 ns in both RC cases, and all six cases are electrically clean under the modeled checks. The original control's high-RC slack is only +3.946 ps.

**Decision: MARGIN_PHYSICAL_GATE_FAIL.** The area/timing-erasure retirement condition was **not** triggered, because V296 remains smaller and has more modeled setup margin than both controls. It survives **provisionally**, not as a passed physical gate.

## Prospective prediction assessment

- **Nominal predicted-win:** supported for controller area, modeled setup margin, and max-slew/max-cap checks. Not an all-six-case gate pass.
- **High-RC predicted-no-win/kill:** **falsified** in this modeled experiment. V296 retained a 13.564% area advantage, +0.488893 ns slack lead, and clean electrical checks.
- **Same-clock workload prediction:** unchanged and not independently tested. With functionally equivalent issue decisions at 3.5 ns, the predicted improvement in issue instructions/cycle is **0%**. Neither slack lead nor controller area reduction is evidence of GPU throughput gain.

## Mechanistic and physical limits

The surviving compact *controller-area* boundary is `A_pairwise + A_integration < A_control`, with measured same-run postrepair margins of **874.342 µm² nominal** and **938.980 µm² high-RC**. These are *controller-level* implementation budgets, not tile area, dynamic power or energy. For an unchanged tile with controller-area fraction `a`, the idealized tile-area reduction is `a × 0.139890` at nominal RC, conditional on zero integration overhead. The performance law still predicts `G=1` at a common verified clock, and `G=1` in a bandwidth-limited regime even if a higher candidate frequency is later validated.

The original 2 ns and 3.5 ns failures remain preserved. This six-case run is not CTS, detailed routing, extracted SPEF, hold closure, multi-corner signoff, power measurement, equal-*tile*-resource performance, unseen workload transfer, or an RTX-5090-equivalence result.

## Next falsifiable discriminator

Do **not** relax this preregistered six-case pass criterion after observing the 39.1 ps failure. In a **separately frozen** follow-on experiment, apply identical post-second-route setup repair and electrical repair to **all six** implementations, followed by rerouting and independent checks, without selecting only the failing original. If the repaired strongest control eliminates V296's area/timing advantage, retire V296. Otherwise advance to matched detailed-route parasitics, power proxies, and equal-tile-resource workload integration. Keep prospective workload holdouts sealed until the physical gate is genuinely passed.
