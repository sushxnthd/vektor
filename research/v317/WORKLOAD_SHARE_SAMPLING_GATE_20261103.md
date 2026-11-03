# V317: prospective workload-share measurement gate (2026-11-03)

**Evidence tier:** analytical sampling design for the existing synthetic two-cycle oracle ceiling. No compiled GPU trace, physical speedup, RTL result or timing signoff.

## Falsifiable transfer question

The previous exact workload-share threshold of 14.2012839825% (four-bank favorable batches versus 64-bank unfavorable batches, assumed 0.5% clock overhead) is not evidence that any real workload crosses it. We now specify *before* obtaining a workload trace how a measured share would be classified.

For N independent Bernoulli batch classifications, observed favorable fraction w_hat and two-sided error alpha, Hoeffding's inequality gives radius r=sqrt(log(2/alpha)/(2N)). An oracle-level win remains possible only when w_hat-r>w*. If w_hat+r<w*, even the synthetic oracle cannot win under the fixed two-regime assumptions. Otherwise classify indeterminate. This is a confidence rule, not a physical win certificate.

At alpha=0.05, resolving a share separated from the threshold by 1, 2, or 5 percentage points requires respectively at least 18,445; 4,612; or 738 independent batches by this conservative bound. These are *design calculations*, not observed samples.

## Strong failure conditions

1. Actual GPU bank mapping and scheduling demand may not correspond to either artificial bank regime. In that case the binary classifier and its threshold are invalid, not merely uncertain.
2. Temporal correlation and kernel-phase clustering violate iid Hoeffding assumptions. Use independent kernel/launch blocks and a prespecified block-level procedure instead; never treat correlated instructions as independent batches.
3. This classifier ignores oracle attainability, resource-matched implementation, wire loading, controller area and power. Passing it does not promote V317.
4. Never select the favorable regime definition after viewing performance outcomes. Freeze the extraction and mapping procedure before holdouts.

The companion script checks the exact rational threshold and all three decision states. No new mechanism is promoted. Existing electrical/area falsifications remain binding.
