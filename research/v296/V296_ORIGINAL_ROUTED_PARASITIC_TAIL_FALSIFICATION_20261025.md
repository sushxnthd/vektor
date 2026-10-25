# V296: original routed parasitic tails falsify uniform-load scaling (2026-10-25)

**Evidence tier:** SHA-256 verified, original routed GitHub Actions artifacts, with independent SPEF parsing. This is a physical load-distribution sensitivity and falsification result, **not** timing closure, switched power, or GPU speedup.

## Original matched artifacts
Run [40173311725](https://github.com/sushxnthd/vektor/actions/runs/40173311725), pairwise ZIP artifact 12592692428 (SHA-256 `9ce2ede807ba5858efcd113b3cd4c2f9e8e5d4a6d97a7b04eb663dd354786259`), serial ZIP artifact 12594851895 (SHA-256 `5c0f7ef91a2151ac2069553cd93a34b97d38c939d6f1106ea95ef4cc8b85706e`). Both use original physical Tcl SHA-256 `30b0a072ec197a47c5e2264567fee50f908b85a8d946e607765083221c0fcf3d`. Nangate45, common 260 µm die / 240 µm core, frozen 3.5 ns timing constraint. The in-situ STA report command failed **after** route and SPEF extraction, leaving valid original physical artifacts.

| Original routed metric | V296 | Serial one-hot | V296 change |
|---|---:|---:|---:|
| Cell area (µm²) | 17,857.644 | 18,953.831 | −5.78% |
| Routed wire (µm) | 205,993 | 230,023 | **−10.45%** |
| Routed vias | 84,490 | 94,181 | **−10.29%** |
| SPEF D_NET count | 9,123 | 9,450 | −3.46% |
| Sum of reported net cap (pF) | 51.5463 | 59.0860 | **−12.76%** |
| Mean reported net cap (fF) | 5.6502 | 6.2525 | −9.63% |
| 99th-percentile net cap (fF) | **51.4120** | **49.2905** | **+4.30%** |
| Maximum net cap (fF) | **117.442** | **113.710** | **+3.28%** |
| Nets above 50 fF | **96** | **91** | **+5.49%** |

The uniform-capacitance-scaling null predicts V296 p99 = 49.2905 × (51.5463/59.0860) = **43.0008 fF**, but the original SPEF yields **51.4120 fF** (**19.56% above the null prediction**). The maximum is 117.442 fF versus 99.200 fF under that null (**18.39% higher**). Therefore **global interconnect reductions do not imply proportional improvement in high-load tails**. The 50 fF threshold is descriptive and post hoc, not a frozen holdout.

### Bounded activity/load sensitivity
For a deliberately simplified aggregate-capacitance activity proxy, under common voltage and coupling treatment,

`Q_pairwise/Q_serial = 0.872395 × (alpha_pairwise/alpha_serial)`.

The proxy advantage disappears if the candidate's mean activity factor is **14.627% higher**. This is **not measured power**: SPEF coupling entries can be counted on multiple nets, effective Miller capacitance depends on simultaneous switching, and internal-cell energy, glitches, clock-tree activity, and workload-dependent transitions are excluded. No causal attribution to the extracted critical path is possible without the actual STA endpoints.

### Reproduction
Download the original artifact ZIPs from run 40173311725 and run:

```bash
python3 research/v296/v296_original_parasitic_audit.py \
  --pairwise /path/to/v296_pairwise_in_situ.zip \
  --serial /path/to/v296_serial_in_situ.zip \
  --output /tmp/v296_original_parasitic_audit_result.json
```

The script checks exact ZIP SHA-256, SPEF units, matched physical Tcl hash, detailed routing, setup/hold markers, original failed electrical gate, net-cap distribution, wire/via counts and the uniform-scaling falsification. It passed locally on both original downloaded artifacts. An independently implemented second parser of the same original SPEF `*D_NET` headers reproduced the net-cap totals, p99 and maxima.

### Decision
Both implementations still fail the original gate: V296 setup **−1.047895 ns**, hold **−0.036622 ns**, three cap violations; serial setup **−1.859922 ns**, hold **−0.019796 ns**, three cap violations. Zero detailed-route DRC violations does not imply electrical closure. Same-clock admission gain is zero. V296 remains the sole mechanism under falsification, V287 remains retired, and Kernellum PR #119 is untouched. Next: extract pinned-compatible STA endpoints; run separately preregistered symmetric physical repair with a strongest equal-consumed-area control and activity-aware power before any GPU claim. Preserve original failures and sealed holdouts.
