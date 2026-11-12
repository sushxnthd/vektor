# V309: matched Nangate45 standard-cell synthesis and load-proxy gate (2026-10-31)

**Prospective, conditional protocol.** Run only after the stronger compact-greedy RTL equivalence and unchanged generic 2.0x cell gate pass. This tests the same one active exact-max admission mechanism. Do not resurrect V287 or V296.

## Frozen library, tool and resource contract

Use the publicly distributed NangateOpenCellLibrary typical corner from OpenROAD-flow-scripts, path `flow/platforms/nangate45/lib/NangateOpenCellLibrary_typical.lib`, **Git blob SHA `90e4afb274cfc6514c587c434c77903d554117d1`**. Fetch from the public upstream path and verify with `git hash-object` before using it; reject source drift. Preserve SHA-256, Yosys version, complete logs and mapped JSON. This is a public educational 45-nm library, **not** a modern GPU foundry node.

Synthesize the same 36-bit input / 4-bit output combinational contract for (1) original greedy, (2) compact priority-greedy, and (3) factored exact-max. Use the same Yosys command sequence: `read_liberty -lib`, `read_verilog -sv`, `synth -noabc -top`, `abc -liberty`, `clean`, `stat -liberty`, `write_json`. Do not alter port counts, allow extra pipeline stages or exclude cells from the comparison.

## Frozen pass/fail and report

An independent Python checker parses each mapped netlist JSON and standard-cell area report, rejects unmapped internal cells, verifies identical primary input/output widths, computes cell count, mapped area, maximum net fanout, and area ratios. The candidate must be **<=2.0x compact greedy's mapped standard-cell area**. If it exceeds that ceiling, **kill the current factored RTL implementation**, even if the earlier generic gate passed. The old brute-force rejection remains preserved.

This is **pre-place-and-route standard-cell synthesis**, not extracted-RC timing. Fanout is only an electrical-load proxy. No frequency or power claim may be made without actual input slews, output loads, wire parasitics, setup/hold, capacitance/slew checks and a matched timing budget. If any required metric cannot be parsed, fail the experiment rather than silently pass.

## Physical and workload kill rules still outstanding

Next, apply equal input slew/output load, realistic register-file wire lengths and capacitive load corners; compare worst delay and area at identical resources. If frequency retention multiplied by the prospectively predicted admission ratio cannot exceed unity (or if downstream acceptance, queue occupancy, scoreboard and bandwidth erase the gain), kill the architecture mechanism. The exact IID bank-equality law is only a workload-conditional **issue-admission** prediction, not a GPU speedup.

Preserve all negative results, tool versions, provenance and independent checks. No RTX 5090 equivalence claim.
