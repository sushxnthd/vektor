# V296 extracted-RC partial falsification: 45-minute runner cutoff (2026-10-23)

## Evidence provenance and scope

GitHub Actions [run 39982695395](https://github.com/sushxnthd/vektor/actions/runs/39982695395) was **cancelled by its job's frozen 45-minute execution limit**, not by an OpenROAD design error. Artifact [12516218110](https://github.com/sushxnthd/vektor/actions/runs/39982695395/artifacts/12516218110) contains 45 files, including complete original/nominal, original/high and optimized/nominal detailed-route/OpenRCX logs and nonempty SPEF/DEF for those three cases. Optimized/high was interrupted after `V296_DETAIL_BEGIN`; pairwise/nominal and pairwise/high were **not executed**. This is incomplete six-case evidence; the all-case detailed gate **cannot pass**.

The numbers below are independently transcribed from the archived `detail/<variant>.<scenario>.log` stage markers, with no changes to physical constraints or clock. They are **research OpenROAD/Nangate45 extracted-RC estimates**, not signoff.

| Completed case | Global-route third-round setup slack (ns) | Extracted detailed-route setup slack (ns) | Change (ns) | Extracted pre-CTS min slack (ns) | Cell area (µm²) | Max-slew / max-cap | Detailed-router DRC |
|---|---:|---:|---:|---:|---:|---|---:|
| Original / nominal | +0.004180 | **−0.051866** | −0.056046 | +0.242990 | 6400.758 | 0 / 0 | 0 |
| Original / high RC | +0.113725 | **−0.159637** | −0.273362 | +0.251041 | 7175.616 | 0 / 0 | 0 |
| Optimized / nominal | +0.360324 | **+0.284155** | −0.076169 | +0.246046 | 6249.936 | 0 / 0 | 0 |

The original controller's extracted setup failures are **51.866 ps nominal and 159.637 ps high-RC**, at the frozen **3.5 ns** clock. Thus the preregistered requirement that **all six cases close at 3.5 ns is already falsified**, regardless of V296's pending measurements. An extrapolated 3.551866 ns / 3.659637 ns clock period would be required to remove these *specific* deficits under the measured fixed implementations if slack changed one-for-one with period; this is **not** a new validated clock closure and must not be used to reclassify the 3.5 ns failure.

### Scientific consequences

1. Global-route closure is **not a reliable substitute** for extracted detailed-route setup closure in this experiment. The original/high-RC estimate loses 273.362 ps after detailed route and extracted RC.
2. The three completed cases have clean reported detailed-router DRC and zero reported slew/cap violations; nevertheless, clean electrical checks **do not imply setup closure**.
3. The V296 area and timing dominance predictions are **not evaluated** by this partial artifact because the V296 detailed-route cases are missing. Do not infer either survival or retirement from controls alone.
4. Same-clock issue-throughput gain remains **0%** by functional equivalence. The sealed workload holdouts remain unopened.

### Exact next action and immutable acceptance criteria

The workflow's `timeout-minutes: 45` cut off a serial six-case experiment after roughly four case starts. Increase **only the job execution budget to 120 minutes**, leaving all six RTL sources, pinned tools, physical constraints, RC multipliers, clock, checker and frozen predictions unchanged. Re-execute all six cases rather than selectively resuming successful ones. This is a compute-budget compatibility amendment, **not** an alteration of the preregistered scientific test.

The original/high and original/nominal failures already make the all-six 3.5 ns gate fail. Even if V296 retains positive area/timing dominance, report `DETAILED_PHYSICAL_GATE_FAIL` for the original frozen gate. If V296 loses area or setup-slack dominance against the strongest control in either regime, recommend retirement under the existing rule. Do not rewrite the prior global-route pass or open workload holdouts.
