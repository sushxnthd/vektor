# V317: exact dependence falsification of workload-share confidence gate (2026-11-03)

## Scope and decision

The prior `workload_share_sampling_gate.py` correctly states an iid-batch assumption but gives a nominal 95% decision rule that cannot be applied to temporally correlated GPU traces without independent sampling or a justified dependence bound. This note gives an exact counterexample; it does not alter the underlying two-regime synthetic oracle threshold or rescue the physically falsified V317 controller.

## Frozen mathematical countermodel

Take n=10,000 batch indicators X_i=Z for all i, with one latent Z~Bernoulli(p). Every batch has the correct marginal favorable-regime probability p, but the entire sequence contains only one independent random draw. Apply the existing two-sided Hoeffding radius sqrt(log(40)/(2n)) and threshold 4182118219409/29448873950865 (approximately 0.142013). The sample share is either zero or one.

For p=1/10, the true share is below threshold, but the nominal 95% gate announces `possible-oracle-win` whenever Z=1, probability exactly 1/10. For p=1/5, the true share exceeds threshold, but it announces `oracle-no-win` whenever Z=0, probability exactly 4/5. The nominal confidence interval misses the true p with probability one in both cases, so coverage is zero, not 95%.

## Implications and kill criteria

The prior 18,445/4,612/738 batch sample-size figures are **iid-only**. Raw batch count alone cannot establish a confidence certificate. Before real-kernel transfer, preregister the sampling unit, kernel provenance, workload segmentation, and a defensible independence/mixing assumption; otherwise return **indeterminate**, regardless of batch count. Independent launches do not automatically imply independence if workload conditions or physical mapping are shared. No effective-sample-size shortcut should be labeled a rigorous confidence guarantee without a proven dependence model.

## Reproduction

Run `python3 research/v317/correlated_sampling_exact_falsification.py`. All probabilities are exact rational sums over the two possible sequences; only the nominal Hoeffding radius uses floating point. No new RTL, physical result, bank mapping, GPU IPC, or RTX-5090 comparison is claimed. Existing V317 electrical/area failures remain binding.
