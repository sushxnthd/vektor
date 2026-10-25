# V296 extracted critical paths mapped to actual synthesized RTL nets (2026-10-25)

**Evidence tier:** independent SHA-pinned original post-route OpenSTA path endpoints cross-referenced to the **same-run Yosys mapped Verilog**. No physical rerun, no new hardware, no real GPU speedup.

The original matched [physical run 40203738175](https://github.com/sushxnthd/vektor/actions/runs/40203738175) and [independent recovered path report](ORIGINAL_IN_SITU_CRITICAL_ENDPOINT_RECOVERY_20261025.md) identify four critical endpoint flops. The [independent mapping checker](in_situ_endpoint_rtl_mapping.py) opens both original ZIPs, checks the same SHA-256 provenance and original physical evidence, finds each unique mapped flop instance and extracts its Q, D and CK pins. Local self-tests, adversarial missing/duplicate-instance rejection and full original-artifact checks passed.

| Path | V296 pairwise | Serial one-hot |
|---|---|---|
| Worst setup start Q | `candidate.issue.scheduler.rr1[2]` (`_15189_`) | `strongest_serial.issue.scheduler.rr1[1]` (`_15350_`) |
| Worst setup endpoint Q | `executed_data[15]` (`_15164_`) | `executed_data[31]` (`_15342_`) |
| Worst setup slack | **-1.047895 ns** | **-1.859922 ns** |
| Worst hold start | `rf_write_data[5]` input | `rf_write_data[3]` input |
| Worst hold endpoint Q | `rf[12][5]` (`_14914_`) | `rf[13][3]` (`_15082_`) |
| Worst hold slack | **-0.036622 ns** | **-0.019796 ns** |

**Mechanistic implication:** The extracted worst setup path in both implementations connects a **scheduler round-robin state flop** to an **executed-data output register**. It therefore spans a larger scheduling/admission/data-selection cone than an isolated controller-only timing comparison. The worst hold path is a separate **external RF write-data input to a register-file storage flop**. Its repair must be treated independently of setup-path optimization. This is more specific than the previous unnamed-flop attribution, but it does **not** prove which individual logic gate or wire segment dominates the delay. A mapped netlist association is not transistor-level causal attribution, and the post-route flow can resize or buffer cells.

**Reproduce:** Download the two SHA-pinned original ZIPs referenced in the recovered path report, then run:

```bash
python3 research/v296/in_situ_endpoint_rtl_mapping.py --self-test
python3 research/v296/in_situ_endpoint_rtl_mapping.py \
  --pairwise-zip v296-in-situ-path-pairwise.zip \
  --serial-zip v296-in-situ-path-serial_onehot.zip
```

**Next physical falsification:** Before changing hardware, independently inspect the actual worst setup cone's gate and wire contributions, then preregister matched candidate/control optimization of scheduler-to-executed-data paths and RF input hold repair under unchanged constraints. Both original integrated implementations remain infeasible at 3.5 ns, with three capacitance violations each. No equal-consumed-area Pareto superiority, integrated tile speedup, measured power, or RTX-5090 equivalence is established. V296 sole mechanism; V287 retired; Kernellum PR #119 and prospective GPU holdouts untouched.
