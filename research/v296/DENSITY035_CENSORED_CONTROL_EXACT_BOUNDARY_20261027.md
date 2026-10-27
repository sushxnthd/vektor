# V296 density-0.35 serial-control identifiability and physical sensitivity (2026-10-27)

**Evidence tier:** exact-integer sensitivity computed from the existing SHA-pinned, right-censored experiment `DENSITY035_FROZEN_ROUTE_FORENSICS_20261027.json`. No new routed control result, GPU measurement, or calibrated physical prediction is claimed. Reproduce with `python3 research/v296/density035_control_censoring_sensitivity.py --self-test --report`.

## What the original diagnostic can and cannot establish

At completed DRT iteration 3, density-0.35 V296 had 3,632 violations, compared with 12,020 at density 0.45, a 69.7837% candidate-only reduction. Its density-0.35 fifth-stage serial control did not reach detailed routing in 75 minutes. The frozen relative gate is

```text
( V296_DRC035 / serial_DRC035 ) / (12020 / 5281) <= 3/4
```

For any nonnegative integer candidate DRC `c`, the **necessary-and-sufficient missing serial boundary** (when serial DRC > 0) is

```text
serial_DRC035 >= ceil(4 * c * 5281 / (3 * 12020)).
```

No regression, stochastic model, or inferred missing serial observation is involved.

## Sensitivity to candidate iteration-3 variability

The table changes the observed candidate DRC hypothetically by the indicated percentage, rounded to an integer. These are **counterfactuals, not additional runs**.

| Hypothetical candidate change | Candidate DRC | Minimum serial DRC for ratio gate | Serial DRC=2,000 | Serial DRC=2,500 |
|---:|---:|---:|---|---|
| -10% | 3,269 | 1,915 | passes | passes |
| -5% | 3,450 | 2,022 | fails | passes |
| 0% (observed) | 3,632 | **2,128** | fails | passes |
| +5% | 3,814 | 2,235 | fails | passes |
| +10% | 3,995 | 2,341 | fails | passes |

All these candidate values independently pass the <=8,414 candidate-only threshold, yet their *comparative* verdict changes with the unmeasured serial outcome. Therefore, candidate DRC improvement alone **cannot** support a relative routing advantage.

The candidate's density-0.35 global-route estimated setup slack was +55.559 ps, just **5.559 ps above** the +50 ps requirement *before* extracted detailed-route RC. This is not a setup-signoff margin; routing, clock, capacitance, hold, and full DRC closure remain unresolved.

## Prospective resolution

The separately preregistered [210-minute-per-contestant matched experiment](DENSITY035_EXTENDED_MATCHED_ROUTE_PREREG_20261027.md) is intended to reveal both completed iteration-3 DRC counts without deleting the serial control's independently optimized fifth-stage timing repair. The unchanged integer gates will be applied before interpreting later routing or workload evidence. A timeout or missing checkpoint is explicitly **INCOMPLETE**, not a pass or a zero.

A successful early-routing diagnostic does not rescue a candidate that fails full DRC=0, extracted setup >=+50 ps, hold >=0, zero capacitance/slew violations, area matching, or bandwidth-constrained throughput. If physical closure fails, retire this decoded density-0.35 repair rather than presenting synthetic bank-admission gains as GPU performance.

V296 remains the only provisional mechanism; V287 is retired. No sealed workload holdouts or Kernellum research artifacts were opened.
