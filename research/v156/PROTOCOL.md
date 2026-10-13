# Frozen V156 protocol

1. Base ref: V155 commit cfd1083072765057a3a5cc929653755c421fce9b.
2. Two sequential implementations: `vektor_wave32_buffered_baseline` and `vektor_wave32_cutset_pipe`; `LANES=1`, `TAG_BITS=8`, same 2-stage ready/valid capacity.
3. First rerun `research/v155/CI.sh` (24,220 vector oracle and pinned Nangate45 area mapping).
4. Map both with the same Yosys script; pin Nangate45 Liberty by Git blob SHA `90e4afb274cfc6514c587c434c77903d554117d1`.
5. OpenSTA constraints: 10 ns core clock, 0.05 ns input/output delays, 0.02 ns input slew, output load 0.01 library units; false path only asynchronous reset input.
6. Capture raw mapped netlists, synth logs, STA logs, tool versions and machine-readable summary. Upload on failure too.
7. Compare critical path and constrained period minus slack. This proxy is not routed Fmax, not silicon PPA.
8. Do not gate CI on the hypothesis being true. Gate on correctness and a parsable timing report; preserve negative science.
9. Follow with equal-resource external baseline, tagged scoreboard/writeback, holdout workload tests and placement-aware timing before architectural adoption.
