# V293 characterized status addendum (2026-10-23)

CI run: https://github.com/sushxnthd/vektor/actions/runs/39885772280
Head: 9d70c1ebd1edae2a8a0fb9bd2696684f68c3697d
Result: SUCCESS (directed Icarus smoke, independent Python holdouts, generic Yosys synthesis).

- Icarus testbench: PASS, 4096 deterministic read cycles. **Does not cover randomized writes**, electrical validity, or all state invariants.
- Generic Yosys mapped cell count, LOCAL=1: **481** cells.
- Generic Yosys mapped cell count, LOCAL=0 (global four-entry RR): **538** cells.
- Local/global generic cell-count ratio: **0.894**. This is not area in square microns, not a matched STA comparison, and does not compare the strongest global LRU control.
- Exact same-capacity banked control is identical to LOCAL=1, so any physical benefit also belongs to the equal-budget control.
- No characterized Liberty mapping, clean max-cap/slew, wire-load sensitivity, switching energy, or integrated 1024-bit operand evidence.

Retirement stands. The generic cell-count difference is a control-topology comparison, not a breakthrough.
