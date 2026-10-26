# V296 decoded post-CTS: bounded detailed-route nonconvergence (2026-10-27)

**Negative physical evidence, not a GPU speedup.** Matched GitHub Actions [run #40359299905](https://github.com/sushxnthd/vektor/actions/runs/40359299905) completed. The V296 pairwise contestant **timed out** at the preregistered 160-minute inner execution bound (exit code 124). The independently optimized fifth-stage serial control completed detailed routing and extracted RC but failed setup, hold and capacitance. The original independent aggregate returned `INCOMPLETE_NO_GPU_CLAIM`. The candidate's route is **right-censored**, not a completed STA failure or proof that V296 can never route.

## Original artifacts and provenance

- Candidate: `v296-decoded-postcts-pairwise`, artifact **12683960271**, ZIP SHA-256 `34fc90009fdb35954e66b8e87065404721fa3679adc834a22c24b69fc095a295`.
- Strong serial: `v296-decoded-postcts-serial_onehot`, artifact **12681568761**, ZIP SHA-256 `36c9ce00caadf2416082510a6b9a84cbbd5c8a4b26dce646b7ecb19ed7682713`.
- Both ZIPs contain the identical frozen manifest and decoded RTL source digest `c6de9c9afe5da5ac6197d2917656d091427608ef4c0dd74d6ba2cc733ae6dbcd`. Constraints: **3.5 ns**, **2× RC**, same generated physical Tcl and floorplan. The serial contestant retains the explicitly frozen extra fifth-stage repair. The independent checker validates original ZIP digests, embedded Tcl/runner hashes, RTL source provenance, CTS marker, and complete routing iterations.

## Fixed-iteration, matched DRC falsification

The checker compares **completed** detailed-route optimization iterations 0–8 from both original logs. Candidate iteration 9 started but never produced a completed violation report, and is excluded.

| Completed iteration | V296 candidate DRC | Strong serial DRC |
|---:|---:|---:|
| 0 | 22,343 | 21,145 |
| 1 | 20,278 | 16,581 |
| 2 | 17,245 | 14,993 |
| 3 | 12,020 | 5,281 |
| 4 | 10,441 | 3,083 |
| 5 | 9,305 | 2,071 |
| 6 | 8,865 | 1,219 |
| 7 | 8,445 | 689 |
| **8** | **7,930** | **361** |

At the same eighth completed iteration, candidate DRC is **21.9668×** serial. V296's violations decreased **64.51%** from iteration zero; serial decreased **98.29%**. Candidate metal2/metal3 shorts total **6,581** of 7,930 (82.99%), versus serial **295** of 361 (81.72%). These are *intermediate router* counts, not final DRC signoff.

The candidate has **216,566 µm** wire length at iteration 8 versus serial **229,944 µm** (**5.82% less**). Its post-CTS/global-route cell area is **16,857.484 µm²** versus serial **17,917.229 µm²** (**5.91% less**). **Lower cell area and total wire length did not predict better detailed-route convergence.** Pin access, local congestion, topology and the serial fifth-stage optimization are possible contributors, but no unique cause is established.

The serial control reached **zero detailed-route violations** at iteration 18 and completed extracted RC, yet its extracted setup slack was **−1.328847 ns**, hold slack **−0.013450 ns**, and maximum-capacitance violations **4**. Candidate final route, extracted STA and feasible clock are unavailable.

## Architectural decision and falsification boundary

1. **The decoded repair has not passed the physicality ladder.** Do not promote pre-CTS timing, area, intermediate wire length, or the synthetic admission law into GPU speedup.
2. **V296 remains the sole provisional mechanism; V287 stays retired.** This bounded route nonconvergence rejects the present repair as *physically validated*, not all possible V296 implementations. Do not merely extend router time and call it a breakthrough.
3. Next test must prospectively preregister a symmetric routability intervention or bounded pin-access/congestion ablation, then demonstrate fewer early metal2/metal3 shorts, complete extracted RC and the original +50 ps setup, nonnegative hold, zero cap/slew/DRC and matched-resource workload gates. If repairs continue to fail, retire the repair and reassess V296 itself.
4. **Evidence limits:** No extracted candidate setup/hold, candidate final routed area, feasible Fmax, SRAM tile integration, power measurement, GPU throughput gain or RTX-5090 equivalence. Real workload holdouts remain sealed. Kernellum PR #119 and its holdouts were not modified.

## Reproduction

Download both original artifact ZIPs from run #40359299905. Do not modify or repackage them.

```bash
python3 research/v296/v296_decoded_route_convergence_audit.py --self-test
python3 research/v296/v296_decoded_route_convergence_audit.py \
  --pairwise /path/to/v296-decoded-postcts-pairwise.zip \
  --serial /path/to/v296-decoded-postcts-serial_onehot.zip \
  --output /tmp/v296_decoded_route_convergence.json
```

The SHA-pinned checker rejects substituted ZIPs, altered physical Tcl/runner, mismatched RTL and absent completed iterations. No additional architecture branch, PR, or mechanism was created.
