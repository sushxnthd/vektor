# V296 mapped-STA gate: failure and controlled repair (2026-10-23)

Run: https://github.com/sushxnthd/vektor/actions/runs/39907831159
Artifact: 12482200204 (v296-matched-sta-rc).
Commit tested: ee40687465cb356b94310903c5d86b06eb0864fb.

## Observed evidence

* OpenSTA and CUDD compiled successfully, and the three-way RTL test passed 2,048 randomized cycles.
* Synthesis stopped on the **first control**, `vektor_issue_control`, before a mapped Verilog netlist or any STA report could be generated.
* `synth -top vektor_issue_control -flatten` had already reported zero Yosys structural problems.
* After `dfflibmap`, `abc -liberty`, and `clean`, `check -assert` reported 24 output bits with no known driver: `issue_valid[3:0]` and `issue_wave0..3[4:0]`.
* The synthesis command had not imported Nangate standard-cell module/port definitions with `read_liberty -lib`; this is a **probable cell-model visibility issue**, not proof that RTL outputs are electrically undriven. The strict mapped check must stay enabled.

## Repair hypothesis and falsifier

Import the exact same Nangate45 Liberty as Yosys blackbox modules **before** RTL synthesis, using `read_liberty -lib -ignore_miss_func -ignore_miss_dir`. This supplies mapped cell pin directions to `check -assert` without changing the RTL, cell library, clock constraints or ABC optimization script.

If mapped-driver checks still fail, stop and inspect mapped netlists; **do not suppress the checks**. If the check passes, require complete mapped netlists and all nine STA cases. No timing or electrical gain is established by this repair alone.

The earlier 18.04% mapped area difference remains a preliminary report, not a validated mapped-netlist timing result. This run does not unseal the positive/no-win workload holdouts, does not integrate the V-Tile and does not support an RTX 5090 claim.
