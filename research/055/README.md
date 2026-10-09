# Vektor-055: masked RF source collection and PTX realism audit

This research branch extends the 054 fixed-three-source tagged operand collector with explicit source-valid masks, valid-only root selection, masked completion, and tagged response fanout. The new RTL is **experimental**, with a two-slot one-read-port interface, not a full RF or GPU.

The static PTX audit checks pinned public hand-written BPF PTX and compiler-produced vector-add PTX. It finds 10 duplicate virtual-register source uses among 577 eligible static uses (1.733%). These counts are not dynamic physical-register measurements.

Software reference plus independent trace checker: 40 traces, 60,000 cycles. In 64 exploratory PTX-static-uniform holdout seeds, dedup improves modeled completions by 0.703% in aggregate, with 19 negative cases. High synthetic alias injection produces much larger gains and must not be mistaken for typical workloads.

Files: `rtl/` masked collector and Icarus bench; `tests/` Python reference, checker, PTX parser, frozen source counts; `RESULTS_055.md` bounded evidence; `WORLD_MODEL_055.md` Discovery Protocol V2; `PREREGISTERED_055.md` predictions frozen before RTL CI; `CORPUS_055.md` source provenance.

Run `python3 research/055/tests/run_055.py`, then `bash research/055/run_055.sh` with free Icarus Verilog and Yosys installed. CI should perform these steps automatically. **No RTX 5090-class capability claim; all gates INCONCLUSIVE.**
