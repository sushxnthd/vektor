# V317: exact workload-share reversal boundary (2026-11-03)

**Evidence tier:** restricted synthetic two-cycle oracle model, exact rational arithmetic. Not GPU IPC, routed timing, or a new architecture mechanism.

## Question
A four-bank regime can individually win while a 64-bank regime individually loses under the same illustrative 0.5% clock-period penalty. How much of the workload must occupy the favorable regime before the *aggregate* improvement is positive?

For batch share w of regime A, baseline completions G_A, oracle opportunities P_A, and regime B analogues, the net ratio is
R(w)=[w(G_A+P_A)+(1-w)(G_B+P_B)]/[(1+d)(wG_A+(1-w)G_B)].
Define per-batch net margins M_i=P_i-dG_i. If M_A>0>M_B, the unique break-even share is **w*=-M_B/(M_A-M_B)**. R>1 iff w>w*. This is a strict, prospective workload-composition requirement, not an average of individual speedups.

Using exact polynomial coefficients previously audited in `robust_clock_impossibility.py`, with q=1, B_A=4, B_B=64, and d=1/200, the certificate is:

- M_A = 0.11489990234375 additional-equivalent completions per batch.
- M_B = -0.01901807181370259.
- **w* = 4182118219409/29448873950865 = 0.14201283982493867**, or **14.2013% of batches**.
- At w* the net aggregate ratio is exactly 1. Below w* the aggregate loses, above it the aggregate wins.

`workload_share_reversal_certificate.py` independently recomputes aggregate baseline and opportunity sums at five shares, including the exact equality and near-boundary perturbations. It checks the sign against the closed-form certificate using rational arithmetic.

## Limits and architectural decision
This is an oracle ceiling for a synthetic four-request, two-cycle workload with uniform bank mapping, no sustained queues, no routing, no power, and an **assumed** clock penalty. A real controller can do worse. The 14.2% share is **not** a measured workload distribution and cannot rescue V317's electrically illegal and area-dominated implementation. No new mechanism is promoted. The necessary next evidence is compiled-kernel register-bank traces and electrically clean matched-resource RTL.

Prior negative results and the V317 single-branch/draft-PR workflow remain binding.
