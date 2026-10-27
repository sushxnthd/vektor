# V296 fixed-word: matched extracted-RC falsification and prospective hold-path boundary (2026-10-27)

**Research decision: REJECT the fixed-word two-word-RF implementation.** V296 pairwise bank admission remains the sole provisional architecture mechanism; V287 stays retired. This report does not claim a physically feasible GPU advantage.

## Independently verified original physical evidence

Both contestants finished detailed routing and extracted-RC analysis in [Actions #40469489684](https://github.com/sushxnthd/vektor/actions/runs/40469489684). The new independent checker opens the original SHA-256-pinned ZIPs, verifies archived physical Tcl/runner/source-RTL hashes, the unchanged 3.5 ns clock, 2x RC, 0.45 density, fifth-stage extra serial repair, routed DEF/SPEF, empty DRC reports, and agreement between extracted logs and physical audit JSON.

- Pairwise [artifact #12721519936](https://github.com/sushxnthd/vektor/actions/runs/40469489684/artifacts/12721519936), ZIP SHA-256: 7342c8e1b16b5193279c6d2ad5d15ddb6cb849c9fc0aa06a984297efeef6404b.
- Optimized serial [artifact #12724948549](https://github.com/sushxnthd/vektor/actions/runs/40469489684/artifacts/12724948549), ZIP SHA-256: 56781fca03ab151661e2c3c393639caa5e71862358fbbe50e0be1dfc278d6050.

| Extracted physical metric | V296 pairwise | Fifth-stage serial |
| --- | ---: | ---: |
| Cell area (µm²) | **13,379.001906** | 15,779.651363 |
| Setup slack (ps) | **+74.236** | −751.540 |
| Hold slack (ps) | **−12.622** | −9.430 |
| Capacitance violations | 0 | 1 |
| Slew violations | 0 | 0 |
| DRC violations | 0 | 0 |
| Frozen physical gate | **FAIL** | **FAIL** |

The candidate saves **15.21358% cell area** and has an **825.776 ps relative setup lead**. These are measured proxy-level differences, not a feasible matched Pareto advantage: both contestants violate the frozen physical gates. The independent aggregate job correctly returned a failure verdict. The fifth-stage optimized serial control is preserved, not substituted with a weaker baseline.

## Quantitative boundary frozen before new path attribution

The candidate needs **at least 12.622 ps** improvement to its extracted worst hold slack, while having only **24.236 ps** remaining setup deterioration tolerance before violating the existing +50 ps setup guard. These are necessary, not sufficient, constraints: repairing a path can move the critical endpoint, alter clock skew, introduce cap/slew/DRC violations, or consume more area. No timing threshold is relaxed.

The conditional area-only 18-candidate versus 16-serial packing law is

\[
18(A_p+\Delta A_p)\le16A_s,\qquad
\Delta A_p\le\frac{16A_s}{18}-A_p=647.354861\;\mu\mathrm{m}^2
\]

per candidate slice, or **4.83859%** of current candidate area. This is not a feasible tile result: neither architecture closes timing, integration and memory overhead are omitted, and the two-word-per-bank RF proxy does not transfer to deeper production banks.

## Prospective read-only hold-path experiment

The existing extracted logs report only worst hold slack, not the hold startpoint, endpoint, or gate path. Changing RTL or inserting hold buffers now would be speculative. A separate SHA-pinned workflow will load both original routed DEFs and extracted SPEFs into the original OpenROAD version with the identical clock, IO, false-path, fanout, library and 2x-scaled parasitics. **No reroute, repair, re-extraction, new constraints or additional RC scaling** is permitted.

The checker requires each reconstructed setup and hold worst slack to reproduce the original result **within 1 ps** before accepting named path attribution. Failure means NO_EXTRACTED_PATH_ATTRIBUTION, not an invitation to change the acceptance threshold. Only after reproducing the actual hold path may a symmetric, cycle-equivalent physical intervention be preregistered and compared with the strongest reoptimized serial control, with full routed setup, hold, cap, slew, DRC, area and workload gates unchanged.

Reproduce the independent paired audit with the following commands:

    python3 research/v296/fixed_word_matched_extracted_boundary.py --self-test
    python3 research/v296/fixed_word_matched_extracted_boundary.py --pairwise-zip pairwise.zip --serial-zip serial_onehot.zip --output matched.json

Local original-ZIP replay and corrupt-ZIP rejection passed. Workload holdouts remain sealed. No production signoff, measured GPU throughput/power, or RTX-5090 equivalence is established. Kernellum PR #119 and its holdouts were not modified.
