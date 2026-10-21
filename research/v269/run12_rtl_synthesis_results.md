# V269 run 12 — first reproducible RTL/synthesis discriminator (not physical closure)

CI: https://github.com/sushxnthd/vektor/actions/runs/39629958849
Commit: 98dca9fdbd333e36c48813c999e9debb5711f5d2
Artifact: v269-generic-rtl-evidence (GitHub Actions ID 12358656734).

## Functional RTL gate
Icarus Verilog 2012: all three configurations PASS deterministic per-class exactly-once/in-order scoreboard over 9,000 active cycles plus drain.
Offered traffic: 7,544 response attempts per implementation; class blocking and output-ready signals are identical, accepted traffic varies with backpressure.
- 4+4 split V269: 6,656 accepted and delivered (slow 2,029; fast 4,627).
- 8-slot two-head bypass: 5,453 accepted and delivered (slow 2,031; fast 3,422).
- 8-slot fully associative ready-select: 6,449 accepted and delivered (slow 2,382; fast 4,067).
These are workload-level RTL event counts, NOT physical throughput. Split improvement: 22.06% vs two-head and 3.21% vs associative under this offered sequence. Distinct admission policies and backpressure make this a system-level comparison, not a same-accepted-stream latency comparison.

## Generic Yosys synthesis (unmapped logic proxies)
- V269 split: 569 generic cells; 11 longest topological logic edges.
- Two-head control: 754 generic cells; 15 edges.
- Fully associative control: 1,240 generic cells; 45 edges.
Cell counts and logic-edge counts are not area, delay, power or STA. Shared 8-entry payload budget and one ingress/egress per cycle; implementation overhead and mux topology differ.

## Decisive remaining gate
No characterized Liberty mapping, placement, extracted RC, max-cap/slew, power, matched STA or 0.5x/1x/2x wire sensitivity. The identical conventional 4+4 virtual-output queue is a prior-art equal-resource control; it reproduces V269 exactly, so the mechanism is NOT novel or a breakthrough even if it is an efficient implementation choice. Freeze V269 holdouts unopened. At most one further substantive run may address electrical physicality; then retire/pivot rather than add evidence wrappers.

FP32 V153/V156 remain electrically disqualified. Integrated Vektor tile unchanged.
