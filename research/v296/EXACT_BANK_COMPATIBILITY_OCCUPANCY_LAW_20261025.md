# V296 exact compatibility–occupancy law and conditional tile boundary (2026-10-25)

**Status: independently checked mathematical model; NOT GPU workload measurements, physical tile timing, or a novel architecture claim.** V296 remains the sole active mechanism; V287 is retired. No existing holdout, physical protocol, or Kernellum branch was opened or modified.

## Why this experiment matters

The matched post-CTS physical result already establishes lower V296 *controller* area and better timing slack against a feasible serial one-hot controller under the tested Nangate45 conditions. It does **not** establish better same-clock issue throughput. V296 and serial one-hot implement identical greedy admission decisions, so they have identical issue traces for identical requests. The missing workload-level variable in the conditional tile law was admitted useful work per cycle, previously represented by an unspecified `q`.

This experiment derives `q` **exactly** for an explicit, limited stochastic traffic family, rather than assuming a made-up constant IPC. It also supplies a direct falsifier for controller overhead and bandwidth.

## Frozen request family and exact boundary

For each of `S` ordered request slots, independently mark it valid with probability `p` (an offered-work/occupancy proxy). A valid request chooses first operand bank uniformly from `B` banks. With probability `rho`, the second operand uses the same bank; otherwise it independently chooses a uniform bank. Thus the actual same-bank probability is `rho + (1-rho)/B`. Each bank has `P` physical read ports. An accepted request consumes two read ports, including two on one bank if both operands match. Admission is greedy in slot priority order.

**`rho` is intra-request *bank overlap*, not V287's retired dual-warp execution-mask overlap.** Real GPU request correlations, register mapping, scheduling feedback, memory stalls, instruction mix, and bank skew are NOT represented by this uniform independent-request family.

Let `h_l` be the number of banks already holding `l` read reservations, `l=0..P`; `sum_l h_l=B`. Let `U=sum_(l<P) h_l` and `D=sum_(l<P-1) h_l`. The **exact** probability that the next valid request is compatible with the current bank occupancy histogram is

```
C(h; B,P,rho) = rho * D/B + (1-rho) * (U*U - h_(P-1))/(B*B)
Pr[admit next slot | h] = p * C(h; B,P,rho)
q(B,S,P,p,rho) = sum_(t=0 to S-1) p * E[C(h_t; B,P,rho)]
```

The expectation is evaluated with a finite-state rational dynamic program over histogram transitions. Same-bank pairs move a bank from load `l` to `l+2`; distinct-bank pairs each increase one bank's load by one; incompatible and invalid requests leave the histogram unchanged. Probability mass conservation and the closed-form compatibility identity are checked at every step. The DP uses exact `fractions.Fraction` arithmetic and exports both an exact fraction and decimal estimate.

This is a predictive law for **shared** issue admissions, not a mechanism-specific V296 IPC advantage. V296's positive tile consequence can only arise from independently validated clock, area-reinvestment, or power changes.

## Exact synthetic results, not GPU measurements

At the V296 nominal resource point `B=16, S=4, P=2, p=0.8, rho=0.2`:

- Expected accepted waves/cycle `q = 957548877/320000000 = 2.992340240625`.
- Per-slot acceptance probabilities `[0.8, 0.7675, 0.73148375, 0.693356490625]`.
- The model has 15 reachable terminal bank-load histogram states.

The model predicts a **non-monotonic** bank-overlap response at `B=16,S=4,P=2,p=0.8`: `q(rho=0)=3.097039`, `q(0.5)=2.905812`, `q(0.75)=2.903125`, `q(1)=2.967900`. Intermediate overlap is more harmful than completely correlated same-bank operands under these assumptions because two reads concentrated on one two-port bank can leave other banks free. This is a model-specific occupancy effect, **not** an established new GPU effect or novelty claim. It must be checked on independent real bank traces before being generalized.

## Independent falsification performed before commit

The checker uses a separate per-bank reservation-array oracle and exhaustively enumerates all validity, operand-bank and correlation outcomes for four small resource configurations: `(B,S,P,p,rho)=(2,2,1,1,0), (2,3,2,0.5,0.25), (3,2,2,0.75,0.5), (2,3,3,0.8,1)`. Exact fractions and each slot's acceptance probability match the DP.

Additional **synthetic out-of-table** Monte Carlo tests (40,000 independently sampled cycles each) produced:

| B | S | P | p | rho | Exact predicted q | Independent sample q | Absolute error |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 16 | 4 | 2 | 0.75 | 0.20 | 2.818110 | 2.820225 | 0.002115 |
| 8 | 6 | 1 | 0.65 | 0.60 | 1.065143 | 1.062450 | 0.002693 |
| 12 | 5 | 3 | 0.90 | 0.35 | 4.312759 | 4.314300 | 0.001541 |

The tests check the sample discrepancy against a preregistered 99.9%-confidence Hoeffding bound for bounded admissions. They are checks of the stochastic mathematical model, **not** prospective GPU workload holdouts or validation of measured clocks. Invalid-resource and NaN input rejection also passed.

Reproduce with `python3 research/v296/exact_bank_admission_law.py --self-test` and `python3 research/v296/exact_bank_admission_law.py`. The hosted workflow is `.github/workflows/v296-exact-bank-admission-law.yml`.

## Conditional positive/no-win boundary, frozen before future GPU measurement

For a measured tile, let `T_j=max(T_other,T_controller,j)`, `h_j` be additional control cycles per useful issue (normalized), `b` bytes/useful wave and `W` sustained GB/s. With equal bank resources and matched request streams,

```
R_j = min( q / (T_j * (1+h_j)), W/b )  [G admitted waves/s]
G = R_V296/R_serial - 1
W_critical,serial = b*q/(T_serial*(1+h_serial))
h_V296,break-even = T_serial*(1+h_serial)/T_V296 - 1
```

This law explicitly includes bank compatibility, intra-request bank overlap, read-port pressure, offered occupancy, bandwidth and control overhead. It predicts zero gain at equal clock and overhead. It does **not** claim any independent performance effect from V287 execution-mask overlap.

The **illustrative** top-pin-geometry post-CTS controller-path period proxies `3.427697 ns` (serial) and `3.101637 ns` (V296) are derived from the frozen 3.5 ns clock minus extracted setup slack in physical run [40134996756](https://github.com/sushxnthd/vektor/actions/runs/40134996756). **They are not measured integrated-tile Fmax** and are not used to claim an achieved GPU speedup.

Freeze `q=2.992340240625`, `b=4 B/op`, `h_serial=h_V296=0` for these synthetic boundary probes:

| Preregistered synthetic regime | Other tile path | Bandwidth | Predicted gain |
|---|---:|---:|---:|
| Win *if* controller really limits integrated clock | 3.0 ns | 8 GB/s | +10.5125% |
| No-win if memory saturated | 3.0 ns | 0.5 GB/s | 0% |
| No-win if another tile path dominates | 3.5 ns | 8 GB/s | 0% |
| Regression if V296 adds 12% issue overhead | 3.0 ns | 8 GB/s | -1.3281% |

For the first scenario, the control bandwidth saturation boundary is `W_critical = 3.491954 GB/s` and V296's overhead break-even is `10.5125%`. These are mathematical consequences of the assumed input values, not physical measurements. The actual tile may have entirely different path, occupancy, bandwidth, overhead and power constraints.

## Decision and next falsification

**V296 remains provisional.** The exact workload compatibility law is supported *for the stated i.i.d model* by independent exhaustive and synthetic Monte Carlo tests. This does not satisfy the world-class completion gate. The next decisive experiment must use unseen measured bank-request traces, derive empirical `q` and `b` independently, compare V296/serial RTL cycle by cycle, measure integrated tile critical path and power, and test the frozen win/no-win boundary without retuning. Realistic nonuniform bank hotspots, temporal correlations and scheduler feedback are primary potential falsifiers. Equal-consumed-area control reinvestment is also unresolved. If the measured tile clock or bandwidth erases the projected gain, report **zero GPU speedup** and do not inflate controller-level results into an architecture claim.

Prior art: occupancy models, greedy bank arbitration and hazard comparison are classical; no claim of original mathematics or RTX-5090 equivalence is made. The existing prospective workload holdouts remain sealed; Kernellum PR #119 remains separate.
