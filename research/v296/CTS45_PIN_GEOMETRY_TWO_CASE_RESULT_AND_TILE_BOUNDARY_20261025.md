# V296 two-geometry post-CTS physical replication and conditional tile boundary (2026-10-25)

## Preregistered result and provenance
Source: GitHub Actions run [40134996756](https://github.com/sushxnthd/vektor/actions/runs/40134996756), completed 2026-10-24 22:04 UTC. Independent aggregate job 121000329634 returned **BOTH_PIN_GEOMETRIES_FEASIBLE_PARETO_SUPPORTED** for both preregistered I/O-edge exclusions. Original raw artifacts: top 12577525943 (SHA256 41dc47bc835995cfceafc27abb2d595567b83c442ca5ca9a6d53d9e7968ecd21); bottom 12577345409 (SHA256 d6c1a90d0691577d345e1dbf729e3ba6e170399a900c949f98d673367a641fea); independent aggregate 12578170086 (SHA256 5a07382cc04095e9be515a72c95104e1d925c41bdceb4a5805b6cd05311ea90f). The independent checker passed its adversarial self-tests and preserved extracted clock and parasitic evidence. **These results were obtained from completed hosted logs; this report does not claim a second independent download or rerun.**

| Excluded pin edge | Architecture | Final area (um²) | Extracted setup (ps) | Extracted hold (ps) | Slew / cap / DRC | Feasible |
|---|---|---:|---:|---:|---|---|
| Top | V296 pairwise | 6240.094 | +398.363 | +252.838 | 0 / 0 / 0 | Yes |
| Top | Serial one-hot | 7315.532 | +72.303 | +250.092 | 0 / 0 / 0 | Yes |
| Bottom | V296 pairwise | 6239.828 | +430.410 | +284.848 | 0 / 0 / 0 | Yes |
| Bottom | Serial one-hot | 7284.942 | +104.791 | +249.547 | 0 / 0 / 0 | Yes |

Matched clock 3.5 ns, Nangate45, 45% density, 2x extracted RC, fanout 16, 250 ps setup-repair target, 5 fF outputs and matched pin exclusions. The serial control retains its additional optimization round. Both cases meet the frozen 50 ps minimum setup, nonnegative hold, zero electrical/DRC, <=7400 um² ceiling, >=10% area saving and >=200 ps setup-lead gates.

**Top:** V296 area saving 14.70075%, setup lead 326.060 ps. **Bottom:** 14.34622%, setup lead 325.619 ps. Across the tested pin geometries, candidate area shifts by only 0.266 um², while candidate setup slack shifts 32.047 ps; control area shifts 30.590 um² and setup slack shifts 32.488 ps. The pairwise setup lead changes by 0.441 ps. The worst tested area-saving margin above the 10% requirement corresponds to **316.620 um²** additional candidate area at fixed bottom-control area; this is algebraic headroom, not a measured repair.

This supports two-point **I/O boundary sensitivity**, not independent placement-seed replication (the separate seed experiment was blocked by unsupported OpenROAD syntax). It is neither strict equal-consumed-area comparison nor signoff.

## Mechanistic, conditional performance law
At identical IPC/occupancy and effective instruction count, the two controllers implement the same issue semantics. Thus **same-clock GPU issue throughput improvement is zero**. The physically observed area/slack result can matter only if it changes a real tile clock or allows another measured area/occupancy consequence.

For a tile with controller critical period P, other critical period O, instruction service factor I/(1+h), and traffic-limited throughput B/q:

T(P,O,B,q,h) = min( I / ((1+h) max(P,O)), B/q ).

For matched IPC, occupancy, overhead and traffic, a **necessary** condition for a clock-driven win is O < P_control, P_candidate < P_control, and the bandwidth roof must exceed baseline throughput. If O >= P_control or B/q <= baseline throughput, the gain is exactly zero. Increased candidate overhead or reduced occupancy can erase the benefit even when its controller path is faster.

For a *conditional illustration only*, hold clock-tree/path constraints fixed and convert reported setup slack s to a path-period proxy P*=3.5 ns - s. This is **not measured Fmax** and may not remain valid under clock retiming, different CTS or integrated tile loads. Top: P*_candidate=3.101637 ns, P*_control=3.427697 ns; bottom: 3.069590 ns versus 3.395209 ns. The controller-only optimistic proxy gains are 10.5125% top and 10.6079% bottom. The proxy does not imply these gains exist on any GPU.

## Prospective analytical boundary regimes (not opened workload holdouts)
Using I=1 op/cycle and h=0, freeze the following **illustrative tile-model inputs**, before any tile implementation: predicted-win O=3.0 ns and B/q=0.5 op/ns, giving approximately +10.51% top / +10.61% bottom from the proxy; predicted-no-win O=3.5 ns and B/q=0.5 op/ns, giving 0%; second predicted-no-win O=3.0 ns and B/q=0.1 op/ns, giving 0%. These are model probes, **not real workload selections or observations**, and they do not replace or unseal the pre-existing prospective workload holdouts.

Reproduce the analytical calculation and adversarial input checks:
`python3 research/v296/pin_geometry_physical_boundary.py --self-test`

The independent physical aggregate remains the authority for actual timing, electrical and routing closure; the script transcribes reported measurements and checks the derived boundary. A new equal-consumed-area GPU-tile experiment must independently measure clock, occupancy, issue IPC, traffic and power, and compare against a fully feasible equally resourced control. Kill any GPU throughput claim if the other critical path or bandwidth roof dominates.

## Research decision
V296 remains the sole provisional mechanism. V287 remains retired. Kernellum PR #119, its frozen holdouts and all previous negative evidence remain untouched. No RTX-5090-equivalence, measured power, GPU IPC or signoff claim is supported. World-class completion gate remains **NOT REACHED**.
