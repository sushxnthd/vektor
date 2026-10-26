# V296 two-request bank-compatibility diagnostic: prospective holdout protocol (2026-10-26)

**Evidence boundary.** V296 remains the sole provisional mechanism; V287 is retired. This is an exact resource-compatibility sub-law for the *existing* 16-bank, two-read-port RF, not a new architecture, a V296-versus-serial speedup, or a physical-timing result. The matched post-CTS experiment 40359299905 remains the primary physical gate and its constraints are unchanged.

## Mechanistic law, fixed before the heldout seeds

Each independent warp request reads two operands. The first bank is sampled from p[0..15], with p[0]=h+(1-h)/16 and p[k>0]=(1-h)/16. The second bank copies the first with probability rho, otherwise is independently drawn from p. Requests are independent of each other. Let q_ab=p_a*(rho*[a=b]+(1-rho)*p_b), and d_a=q_aa.

For two requests, two ports/bank, the exact compatible probability is

P2 = sum_a d_a*(1-p_a)*(rho+(1-rho)*(1-p_a))
   + sum_(a!=b) q_ab*(1-d_a-d_b).

Explanation: a same-bank first request consumes both ports of a, so the second must avoid a; a distinct-bank first request is blocked only if the second reads twice from a or twice from b. No parameters are fitted.

The independent reference enumerates all 16^4 operand quadruples and counts bank demands. The predictive test samples fresh pairs with separate RNG seeds. Two ready requests have conditional expected issue count 1+P2 when the first always issues and the second issues iff compatible. This is not a model of the 4-slot scheduler, dependency cooldown, shared bandwidth, or routed GPU performance.

## Frozen experiment

Pilot seeds 271828, 314159, 161803 were inspected before this protocol and are **excluded** from prospective validation. The following are unopened heldout seeds: **424243, 515151, 616161**. Each has 50,000 independent request-pair samples in each of five frozen regimes: (h,rho)=(0,0),(0,0.7),(0.45,0.2),(0.8,0.2),(0.95,0.7). The prediction and independent exhaustive enumeration must agree to <1e-10; empirical holdout probability must agree within max(0.005,5*sqrt(P2*(1-P2)/50000)) in **all 15 cells**. Failures are preserved and not silently excluded. Record all raw predictions, observations, errors, and thresholds in JSON.

The frozen predicted high-compatibility regime is h=0,rho=0; the predicted low-compatibility regime is h=0.95,rho=0.7. These are *compatibility*, not GPU throughput, win/no-win predictions. No causal performance or novelty claim follows from this known combinatorial occupancy calculation without independent workload transfer.

## Relationship to decisive architecture gate

A surviving V296 result still requires both physical contestants to close +50 ps setup, nonnegative hold, zero cap/slew/DRC, matched strongest fifth-stage serial control, physically replicable equal-resource tile, measured-feasible-clock throughput, power proxies, and independent unseen workload predictions. If the routed decoder fails, reject it regardless of this law. Do not unseal existing GPU-workload holdouts before physical closure. Kernellum PR #119 remains untouched.
