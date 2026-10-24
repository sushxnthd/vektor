# V295 retirement — characterized equal-resource area failure (2026-10-23)

**Decision: RETIRE.** Active kernel passes to V296 only after this retirement is persisted. V287 remains retired.

## Hardware evidence

Public GitHub Actions run: https://github.com/sushxnthd/vektor/actions/runs/39891526821
Artifact with full raw synthesis logs and RTL output: https://github.com/sushxnthd/vektor/actions/runs/39891526821/artifacts/12474609537

- Icarus: 2,048 randomized input cycles with pre/post-clock three-way output comparison **PASS**.
- Independent Python arbiter oracle: 65,536 exhaustive two-slot cases plus 100,000 randomized four-slot cases, **zero mismatches** (E0).
- Original integrated V-Tile issue control: **4,046.126 µm²** Nangate45 mapped cell area.
- Stronger optimized decode-after-select control: **3,780.126 µm²**.
- V295 parallel bank predecode: **7,462.098 µm²**.
- V295 / best equal-resource control: **1.974034× area** (+97.4034%).

Same scheduler, issue slots, RF banks, ports and storage; candidate only changes bank-decode ordering. Candidate has a large all-wave one-hot decoder and selection fabric. The experiment **falsifies the equal-area gate**, so predicted frequency headroom is not sufficient to keep the mechanism alive.

**Not measured:** electrical STA, max-cap/slew, wire parasitics, placed timing, power, workload performance. This is characterized mapped-cell **area** falsification, not measured timing or power.

Frozen compute-bound and memory-bound holdouts were **not opened** because the area gate failed. No V-Tile integration or GPU-class capability claim is justified.

## Next kernel policy

The next mechanism must deliberately seek a positive architecture law using a boundary sweep and equal-resource controls, not another optimization of V295's decoder.
