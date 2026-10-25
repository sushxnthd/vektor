# V296 original extracted STA: critical endpoints recovered from immutable routed artifacts (2026-10-25)

**New evidence:** The matched integrated physical run [40203738175](https://github.com/sushxnthd/vektor/actions/runs/40203738175) completed RTL equivalence and **both** routed physical contestants. Its original aggregate job failed closed with `INCOMPLETE_NO_PATH_CLAIM`, not because the extracted paths were missing, but because the checker assumed the wrong OpenSTA slack-line orientation. The original failure is preserved. This report independently reanalyzes the original artifacts **without rerunning or changing any physical implementation**.

## Artifact provenance and independent recovery

Original downloaded artifact SHA-256 values:
- `v296-in-situ-path-pairwise`: `239a648829c41f5cd0229ec1ca6663463ca2a253d9186321bb476869223e640e`
- `v296-in-situ-path-serial_onehot`: `d755641eba65a4b89c36f1226ae23e55ce647b390dc910e649d157360d538815`

Both ZIPs match their hosted upload digests. Both share exactly the same original Tcl SHA-256 `30b0a072ec197a47c5e2264567fee50f908b85a8d946e607765083221c0fcf3d` and read-only instrumented Tcl SHA-256 `3f54505d286268eb0d526e5a3076d5be0a91f4b9d827239c1d2a283f140b4451`. The independent checker verifies that **only** the specified timing reports were inserted, that original constraints remain unchanged, and that each recovered path slack matches the original `report_worst_slack` and physical audit within 5 ps (in fact exactly to six decimals).

**Why the old aggregate failed:** The pinned OpenSTA report writes `-1.047895   slack (VIOLATED)` (numeric first). The old audit parser recognized only `slack (VIOLATED) -1.047895` (label first). No physical evidence was invalidated; only endpoint extraction failed. New independent checker: [`in_situ_path_artifact_recovery.py`](in_situ_path_artifact_recovery.py). Its adversarial self-tests reject missing endpoints, tampered slack and unknown report labels. Both original ZIPs were analyzed locally; the checker returned `EXTRACTED_CRITICAL_PATHS_IDENTIFIED_BOTH_INFEASIBLE`.

## Measured extracted critical paths

| Metric | V296 pairwise | Serial one-hot |
|---|---|---|
| Setup startpoint | `_15189_` (coreclk flop) | `_15350_` (coreclk flop) |
| Setup endpoint | `_15164_` (coreclk flop) | `_15342_` (coreclk flop) |
| Worst extracted setup slack | **-1.047895 ns** | **-1.859922 ns** |
| Hold startpoint | `rf_write_data[5]` (input port) | `rf_write_data[3]` (input port) |
| Hold endpoint | `_14914_` (coreclk flop) | `_15082_` (coreclk flop) |
| Worst extracted hold slack | **-0.036622 ns** | **-0.019796 ns** |
| Final cell area | 17,857.644252 µm² | 18,953.830505 µm² |
| Capacitance violations | 3 | 3 |
| Slew violations | 0 | 0 |
| Feasible at frozen 3.5 ns | **NO** | **NO** |

V296's measured setup-slack lead is **812.027 ps**, but neither contestant passes timing/electrical closure. To reach +50 ps setup guardband, candidate requires at least **1.097895 ns** improvement and serial at least **1.909922 ns**. Both also require hold repair and elimination of all three cap violations. This is a necessary-margin calculation, **not a demonstrated repair or achievable timing result**.

The worst setup paths are **register-to-register** in both contestants. The worst hold paths are **register-file write-data input-to-register** in both. This is a meaningful root-cause localization: the worst hold failure is not the same endpoint class as the worst setup failure. The synthesized instance identifiers are not yet reliably mapped back to architectural RTL source signals. Do **not** claim that bank arbitration itself is the cause of the worst setup path, or that changing fanout alone will repair it.

## Reproduction

Download the two immutable artifact ZIPs from [physical run 40203738175](https://github.com/sushxnthd/vektor/actions/runs/40203738175), then execute:

```bash
python3 research/v296/in_situ_path_artifact_recovery.py --self-test
python3 research/v296/in_situ_path_artifact_recovery.py \
  --pairwise-zip v296-in-situ-path-pairwise.zip \
  --serial-zip v296-in-situ-path-serial_onehot.zip
```

The original SHA-pinned artifacts, matched Tcl hashes, original extracted slack and endpoint slacks must all agree. Local self-tests and independent original-artifact verification passed. **Hosted execution of this new recovery checker has not yet been established.**

## Decision and next physical experiment

V296 remains the sole provisional mechanism. V287 stays retired. This closes the *endpoint identification* blocker, not the *physical feasibility* blocker. Next: trace the four synthesized endpoint cells through original mapped netlist/DEF, identify actual setup logic cones and short hold paths, and preregister a **matched**, independently optimized electrical repair for both candidate and serial. The original failed gate must not be rewritten. Require zero cap/slew/DRC, setup >= +50 ps, hold >=0, matched consumed area and bandwidth-aware workload evaluation before any integrated advantage claim.

No GPU speedup, measured power reduction, or RTX-5090 equivalence is established. Existing workload holdouts and Kernellum PR #119 remain unchanged.
