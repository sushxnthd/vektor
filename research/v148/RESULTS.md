# V148 first GitHub Actions execution (2026-10-13)

Commit b29f2ffef181e94a4c910bd4dcc70892b8ef09bd
Workflow: https://github.com/sushxnthd/vektor/actions/runs/38420068445
Result: SUCCESS; Ubuntu runner, Icarus Verilog, Yosys 0.33.

**Full Wave32 RTL:** 2 tagged collector->multiplication transactions passed with three RF source responses, two parallel response paths, backpressure holds and output retirement. This is a directed test, not full arithmetic coverage.

**Generic Yosys synthesis, unmapped to process:** 1-lane multiplication slice 3,981 cells; 4-lane slice 15,888 cells; 1-lane collector+multiplier front end 4,780 cells. Counts include registers and generic gates; interfaces differ, no mm^2 or frequency inference.

**Limitations:** no IEEE-754 FMA output; no final writeback or scoreboard; no timing/area/power measurement; no 32-lane full generic synthesis; no silicon. One-stage throughput is a ready/valid interface property, not demonstrated GPU instruction throughput.

**Follow-up:** independent randomized/special-case integer oracle with 512 stage vectors, pending CI confirmation.
