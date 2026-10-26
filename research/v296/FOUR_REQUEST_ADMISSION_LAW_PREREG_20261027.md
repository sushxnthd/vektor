# V296: exact multi-request RF-bank admission law (preregistered 2026-10-27)

## Scope and physical priority
This is a **subordinate, calibration-free, synthetic analytical test** of the existing V296 16-bank/two-read-port resource model. It does **not** change the V296 architecture, the single research branch, the physical constraints, or the decoded post-CTS experiment. V287 remains retired. Strongest serial control and routed physical closure remain mandatory; no GPU speedup or novel architecture claim follows from this law.

## Predictive law, frozen before outcomes
For K=4 simultaneously ready, independent warp requests, each with two bank operands, let the bank distribution be p=(h+(1-h)/16,(1-h)/16 repeated 15 times). Generate first bank a from p, then with probability rho copy a for second operand b; otherwise sample b independently from p. Each bank has exactly two read ports. Admit requests in fixed index order if their two operands fit the remaining read-port capacities. Rejected requests do not consume ports.

Predict **E[A_K]** exactly using a finite-state Markov recurrence over (used read ports on hot bank, number of cold banks with 0/1/2 used ports). Transition probabilities are summed over the complete 16x16 operand-pair distribution; states after rejection are retained. No fitted parameters, random-number calls, or workload outcomes may enter the predictor. This extends the existing exact two-request compatibility law to simultaneous four-request admission, but remains a classical resource law rather than a novel mechanism.

## Independent falsification
Implement an independent event-level simulator that samples bank pairs and greedily admits four requests with an explicit 16-entry read-port array. Compare to exact recurrence for K=1,2,3,4 and require the K=2 identity E[A_2]=1+P(compatible) from the existing pair-law formula. For the 5 frozen regimes below, run 30,000 independent four-request batches on each of three previously unopened seeds 717171, 818181, 919191. Require absolute mean-admission prediction error <=0.025 in every one of the 15 heldout cells, and 0<=E[A_4]<=4. Report any failures without tuning thresholds.

Regimes (hotspot h, within-warp operand copy rho):
- uniform independent (0,0)
- uniform correlated (0,0.7)
- moderate hotspot (0.45,0.2)
- heavy hotspot (0.80,0.2)
- extreme hotspot correlated (0.95,0.7)

Preserve the naive baseline E_naive=1+3*P_pair solely as an intentionally limited comparison (it is **not** asserted to be a valid general bound). Report prediction and actual values, absolute errors, and the baseline's errors. Include source script and machine-readable results.

## No unsupported extrapolation
The K=4 instantaneous admission law excludes warp dependencies, queueing, multi-cycle arbitration, occupancy, clock, area, bandwidth, energy, wire loads, SRAM, and routing. Even exact heldout agreement cannot pass V296's frozen routed feasibility gate. Do not unseal real workload holdouts until physical closure. Do not rewrite prior evidence or PR history.
