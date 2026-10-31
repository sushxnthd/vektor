# V310 prospective extension: occupancy / overlap / bandwidth boundary (2026-10-31)

**Freeze point:** This extension is committed before running the occupancy/overlap holdouts. It does not change the original q-only holdouts, already independently accepted in CI #41166575481. It remains a *synthetic two-slot model*, not an integrated GPU claim.

Two request slots have independent validity Bernoulli(o). Each valid request's two source operands map to a single bank; conditional on both valid, their banks coincide with probability h. For each valid request, the full physical register identities match independently with probability q, in which case the two reads can be coalesced into one. A baseline consumes two ports for each request, a candidate consumes one only on verified equality, and each bank has two ports.

Exact expected admissions:

    A_base = 2 o - o^2 h
    A_new  = 2 o - o^2 h + o^2 h q^2
    G(o,h,q) = A_new/A_base = 1 + o h q^2/(2 - o h), o > 0.

This predicts *zero gain* when any of o, h, or q is zero. It is not a law for four-way correlated queues or actual register-operand statistics; those require an independent joint-distribution model.

**Frozen new holdouts**, each 200,000 seeded opportunities, ratio tolerance 0.015 and independent port-counting oracle:
- overlap_medium: seed 31035, o=0.75, h=0.50, q=0.60; predicted 1 + 0.135/1.625 = **1.083076923076923**.
- overlap_zero_no_win: seed 31036, o=0.75, h=0, q=0.80; predicted **1.000000000000000**.
- overlap_hot: seed 31037, o=0.60, h=0.90, q=0.70; predicted 1 + 0.2646/1.46 = **1.181232876712329**.

A separate *explicitly assumed* bottleneck model uses D = candidate/base clock period ratio and beta = bandwidth service ceiling / baseline issue-limited throughput:

    S = min(G/D, beta) / min(1, beta).

For beta=0.9 and D=1, all three synthetic regimes predict **S=1** despite any admission gain, because the modeled system is already bandwidth-limited. This is an illustrative roofline-style counterexample, not a measured GPU bottleneck.

Reject if an independent checker disagrees with the frozen admission law beyond the tolerance. The physical/electrical and stronger real-hardware reuse-baseline gates from the parent preregistration remain unchanged.
