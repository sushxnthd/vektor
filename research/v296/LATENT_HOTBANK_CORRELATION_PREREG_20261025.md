# V296: latent-hot-bank correlation falsifier — prospective protocol (2026-10-25)

## Scope and preservation
One active mechanism: V296 pairwise bank-conflict admission; V287 remains retired. This is a **shared arbitration workload-model stress test**, not a new hardware mechanism or a claim of V296-specific IPC. Do not open existing GPU holdouts or modify prior physical artifacts. No additional branches or PRs.

## Frozen hypothesis and traffic family
The existing exact bank law assumes requests independent across issue slots. Test whether its scalar inputs `(B,S,P,p,rho)` predict issue admissions when **cross-slot bank correlation** changes while all one-request marginals remain exactly identical.

For each issue cycle draw one latent hotspot bank H uniformly from B banks. Each slot independently:
1. valid with probability p;
2. first operand bank A=H with probability lambda, otherwise A uniform on B;
3. second operand bank C=A with probability rho, otherwise C uniform on B.

H is resampled every cycle. The marginal distribution of A remains uniform for every lambda; the marginal same-bank probability remains `rho+(1-rho)/B`; p and port resources remain unchanged. Lambda changes only cross-slot dependence, not single-slot bank skew. Greedy slot-order admission consumes two physical read ports, including two if A=C.

## Preregistered test and decision
Freeze `B=16,S=4,P=2,p=0.8,rho=0.2`, and lambda in `{0,0.25,0.5,1}`. Before running the exact checker, predict:
- lambda=0 reproduces the existing i.i.d exact law `q=2.992340240625` exactly;
- `q(0)>q(0.25)>q(0.5)>q(1)` for this **particular** parameter point;
- `q(0)-q(1)>1.0` admitted waves/cycle and `2.5<q(0.5)<2.8`;
- V296 and serial one-hot have exactly the same `q(lambda)` under the same bank requests and resources, hence zero same-clock architectural IPC gain.

Independent checks: a separate full enumeration of latent hotspot, valid bits and ordered operand pairs for `B=2,S=3,P=2,p=0.75,rho=0.3,lambda=0.65`, plus `B=3,S=2,P=2,p=0.5,rho=0.25,lambda=0.4`; exact fractions must match the histogram DP. Check probability mass conservation, endpoint lambda=0 identity and invalid input rejection. Monte Carlo is optional and cannot replace exact cross-checks.

## Consequence and falsification
If accepted work changes at fixed `(B,S,P,p,rho)`, the previous five-variable compatibility law is not sufficient beyond its i.i.d family. Add a cross-slot dependence parameter to its predictive boundary and explicitly bound applicability. If it does not, preserve the negative result. This test is synthetic and cannot validate actual GPU traces, integrated timing, power, or novelty. Both integrated physical implementations remain infeasible at the original 3.5 ns gate; controller-level closure is a distinct evidence tier. Do not open GPU holdouts, infer GPU speedup or use unsupported RTX-5090 comparisons.
