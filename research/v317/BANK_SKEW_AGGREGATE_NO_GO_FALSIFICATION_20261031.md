# V317: aggregate RF no-win inference falsified by bank skew (2026-10-31)

**Decision:** the earlier V317 pooled-register-file no-win condition is **not** a valid general certificate for independently ported RF banks. This is an exact, synthetic *model-identifiability falsification*, not measured GPU IPC or a new hardware mechanism.

## Provenance and prospective scope

The frozen [protocol](FROZEN_BANK_SKEW_IDENTIFIABILITY_PROTOCOL_20261031.md) was committed first at `a374c63`, before the implementation at `073c9d4` and independent tests at `0b6c24a`. The two cases were chosen analytically in advance; this is a prospective **code check of known synthetic counterfactuals**, not an unseen real workload or independently measured experiment.

Independent hosted Python 3.11 audit: [GitHub Actions #41218576015](https://github.com/sushxnthd/vektor/actions/runs/41218576015), passed at `0b6c24aa8d00067299dbb8e57864e512b23a7920`. The suite includes 8 new tests and 1,000 seeded independent three-bank stress cases, in addition to existing V317 tests. The same-commit simulator push workflow also passed: [#41218571992](https://github.com/sushxnthd/vektor/actions/runs/41218571992).

## Counterexample under identical aggregate observations

Two RF banks, each with two ideal read units/cycle, issue and ALU ceilings both 5/4 instructions/cycle. Both worlds have total physical demand 3 reads/instruction. The candidate removes precisely 1/2 read/instruction from bank 0, using **the same physical ports**, and pays no assumed overhead.

| Exact synthetic world | Baseline bank demand | Candidate bank demand | Banked-envelope gain | Pooled-envelope gain |
| --- | --- | --- | --- | --- |
| Frozen predicted no-win | (3/2,3/2) | (1,3/2) | **1.000x** | 1.000x |
| Frozen predicted win | (5/2,1/2) | (2,1/2) | **1.250x** | 1.000x |

The aggregate model predicts *no win in both worlds*, because total capacity / demand = 4/3 exceeds issue/ALU capacity 5/4, before and after demand reduction. But in the skewed world bank 0 alone limits the baseline rate to 2/(5/2)=4/5. Removing 1/2 bank-0 read increases the ideal rate to 2/2=1, giving 5/4 gain. In the balanced world, issue/ALU capacity already binds, so the candidate cannot improve throughput.

**The same total demand, total ports, and demand-reduction budget do not identify the speedup sign relative to a 1.02x materiality gate.** These are *ideal upper-envelope rates*, not evidence that such an implementation exists or can reach them.

## Exact predictive law and bounded sensitivity

For independent bank capacities P_b, physical reads d_b per instruction, savings k_b with 0 <= k_b <= d_b, and nonnegative issue, ALU and clock overheads c,a,t:

    lambda0 = min(W, A, min_b P_b/d_b)
    lambda1 = min(W/(1+c), A/(1+a), min_b P_b/(d_b-k_b))/(1+t)
    G = lambda1/lambda0

Zero-demand bank terms are omitted. A sufficient no-win certificate for read-elimination-only mechanisms is **every bank** P_b/d_b >= min(W,A). The weaker pooled condition sum(P_b)/sum(d_b) >= min(W,A) is insufficient.

The frozen exact six-point allocation sweep holds D=3, K=1/2, P=(2,2), W=A=5/4, and changes bank-0 demand from 1/2 to 3 in increments of 1/2. The resulting gains are:

    d0:     1/2    1      3/2    2      5/2    3
    G:      1      1      1      5/4    5/4    6/5

Exact min/max = **[1, 5/4]**. An independent Fraction-based oracle recomputes all cases and 1,000 additional seeded configurations with nonnegative control/clock overheads. This establishes a model-internal bound over the *enumerated six-world domain*, not a distribution-free bound over arbitrary GPU workloads.

## Correction to previous V317 claims

The prior [aggregate capacity no-go](CONDITIONAL_RF_CAPACITY_NO_GO_20261031.md) remains mathematically correct **only** if P is a genuinely pooled RF resource, or if a separately established bank-balance condition makes that approximation valid. It cannot be applied to NVIDIA's banked RF from SASS lexical counts, aggregate reuse hints, or an aggregate hit-rate estimate. In particular, an apparently cache-saturated aggregate regime does **not** rule out a hot-bank bottleneck without per-bank physical demand evidence.

This result is a *falsification of the inference pipeline*, not a proposed architectural speedup. The strong modern RF-cache-aware comparator remains mandatory; the candidate's assumed bank-0 read elimination has not been implemented, simulated as RTL, synthesized, or electrically validated.

## Next hard gate

Obtain real binary/disassembler provenance and independently grounded **dynamic per-bank** read pressure and RF-cache behavior, or publish a justified conservative uncertainty envelope. Only then select one mechanism and preregister a matched-resource win/no-win and unseen workload evaluation. No physical timing, routing, energy, tile throughput, or RTX-5090-equivalence result is claimed. Kernellum PR #119 was not modified.
