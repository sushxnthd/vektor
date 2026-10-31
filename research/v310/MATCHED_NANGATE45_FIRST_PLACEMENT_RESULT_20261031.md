# V310 first matched standard-cell placement result (2026-10-31)

**Status: prospective early physicality prefilter PASSED; GPU architecture claim NOT established.** The first independent hosted [V310 physical run #41166647289](https://github.com/sushxnthd/vektor/actions/runs/41166647289) executed matched Yosys/OpenROAD Nangate45 synthesis, same-netlist zero-wire timing, and two placement-estimated-RC geometries. [Immutable 32-file evidence artifact #13029104535](https://github.com/sushxnthd/vektor/actions/runs/41166647289/artifacts/13029104535). Independent adversarial audit completed successfully.

| Controller metric | Matched compact greedy | V310 verified-read coalescer | Candidate/base |
|---|---:|---:|---:|
| Nangate45 mapped area | 251.370 | 266.266 | **1.05926x** |
| Same mapped netlist, zero wire | 0.39 ns | 0.42 ns | **1.07692x** |
| Dense 30x30 um placed estimated-RC | 0.41 ns | 0.43 ns | **1.04878x** |
| Relaxed 45x45 um placed estimated-RC | 0.41 ns | 0.43 ns | **1.04878x** |

Both area and clock-limited optimistic timing screens pass the *frozen* gates of 1.50x mapped area and 1.5625x delay ratio for the q=.75 two-request hot-bank motif. The synthetic issue ratio is 1.5625x, giving **1.48983x optimistic issue-times-frequency** under the explicitly assumed controller-clock-limited and issue-bound model. This is an **upper-bound model output**, NOT an observed GPU throughput improvement. The matched controller adds 5.93% mapped area and 4.88% placed controller delay.

The earlier [V310 independent RTL/law CI #41166575481](https://github.com/sushxnthd/vektor/actions/runs/41166575481) passed 109,076 RTL oracle cases and four frozen 100k-opportunity synthetic regimes: observed admission ratios 1.56117 (q=.75), 1.00000 (q=0), 1.16012 (q=.4) and 1.81150 (q=.9). Generic synthesis reported 228 cells baseline and 239 candidate. A separate preregistered occupancy/overlap law extension is committed but is not considered accepted until its own hosted run passes.

## Why this is NOT a positive hardware result yet

1. The controller receives a **trusted verified-equality flag**; its mapped area/timing exclude the complete physical-register equality comparator, operand fanout, forwarding mux, read-enable control, register identity transport and their electrical loads. Equal top-level 40-bit input and four-bit output port counts do not make the full tile equal-resource.
2. The historical Vektor compact greedy control **does not already reuse identical physical-register operands**. A practical modern GPU may do so. Against an already reuse-capable baseline, the incremental gain could be exactly zero. Strong-baseline and prior-art audits are mandatory before claiming novelty.
3. These are **placement-estimated metal3 parasitics**, not detailed routing, extracted RC, signoff slew/capacitance, actual tile clock, RF access timing, measured power, occupancy or bandwidth.
4. The q=.75 hot-bank motif is synthetic and may be rare in real execution traces. Its 1.48983x number is an optimistic model upper bound for a narrow regime, not a general GPU benchmark.
5. In the separately preregistered two-request overlap/occupancy model, G(o,h,q)=1+o*h*q^2/(2-o*h). For h=0, q=0, or o=0 the issue gain vanishes. A bandwidth-limited service ceiling can erase any remaining issue improvement.

## Next decisive gate

Implement and physically cost the full register-ID comparator and operand fanout datapath; compare against a **strong reuse-capable equal-resource alternative**. Measure actual identical-register operand frequencies and correlated bank conflicts from real execution traces before selecting a workload win/no-win split. Freeze a tile-level boundary, then run matched extracted-RC/electrical/area and workload throughput checks. **Kill V310 immediately** if the full-system strong control or timing/area/bandwidth constraints erase its benefit.

V309's physically failed exact-max candidate remains retired in [draft PR #26](https://github.com/sushxnthd/vektor/pull/26). This is the single active V310 mechanism on its separate persistent branch and draft PR #27. No RTX 5090 equivalence or finished architecture claim.

## Conditional positive boundary from the measured *controller-only* delay

Let x=o*h and q be verified duplicate-source probability in the separately frozen two-slot model. With measured placed controller delay ratio D=0.43/0.41=1.0487804878, the idealized **clock-limited, issue-bound** inequality G(x,q)>D is equivalent to

    x > 2*(D-1)/(q*q + D-1),  provided q*q + D-1 > 0.

For q=0.60, the necessary offered-load times bank-overlap threshold is **x>0.23866**. The frozen medium-overlap regime has x=0.75*0.50=0.375 and thus predicts an optimistic 1.08308/1.04878=**1.0327x** issue-times-frequency, while the frozen h=0 no-win regime predicts **0.95349x** under that clock-limited assumption. With a bandwidth ceiling beta=0.9 of baseline issue capacity, the same simplified roofline predicts **1.0x** for both, regardless of the issue-stage opportunity. These are *derived conditional predictions* using a measured local controller ratio, not held-out measured GPU throughput. They can be falsified by stronger controls, comparator/fanout cost, tile slack and real workload effects.
