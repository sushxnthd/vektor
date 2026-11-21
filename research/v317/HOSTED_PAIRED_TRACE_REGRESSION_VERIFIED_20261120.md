# Hosted paired-trace regression: verified execution (2026-11-20 UTC)

## Immutable evidence
- Existing research branch: `research/v317-sass-provenance-gate`; existing draft PR #34.
- GitHub Actions run: https://github.com/sushxnthd/vektor/actions/runs/44688889518
- Job ID: `136129675151`; status completed, conclusion success.
- Pull-request merge checkout commit: `9a8efd813f0c039a760d5339bc4bfdb8221f4b13`, incorporating research commit `412682925a4edee88f69a827e6c18ed0021e7df6`.
- Runtime: CPython 3.13.18.
- `independent_periodic_conservation_audit_20261120.py`: PASS, 12 full-window periodic comparisons; SHA256 `878cf4e997e623d9feeba7398ca758b06ed3248fce0d04ab98e3c785a5a6befe`.
- `paired_trace_conservation_regression_20261120.py`: PASS, 8 paired-trace reference checks, full-window FIFO conservation, bank legality and warmup accounting; SHA256 `01172527a33544ab60d59954d03165c3efe2292763dd1b85071750ea694b22e8`.
- `finite_queue_prospective_20261120.py` SHA256 `c54ca8dcd779ee0de63f0c223cf11aa19f56c60af4dd390634a062bb19398a4e`.

## Interpretation and decision
This verifies reproducible hosted execution of the committed regression against the existing prospective simulator, not an independent physical implementation, statistically independent workload holdout, or GPU throughput measurement. A passing self-consistency regression cannot establish a throughput advantage. Prior finite-FIFO oracle comparisons remain below the frozen 1.02x materiality gate. Compact greedy remains the strongest equal-resource baseline; the earlier routed electrical violations and area dominance remain binding. **No-go** for promoting the protected combinational oracle to hardware. V287 is historical only.

## Next gate
Do not add a second active mechanism. If pursuing stateful scheduling, first freeze a realizable state machine and a genuinely unseen finite-FIFO workload protocol with compact greedy as the control, then require >=1.02x paired throughput under finite buffers before matched RTL, synthesis, electrically legal route, wire/load sensitivity and power/area/occupancy accounting. Preserve negative evidence. No RTX-5090 equivalence claim.
