# V296 routed extracted-SPEF worst-path topology (2026-10-27)

**Evidence tier: one worst setup and hold path per implementation, NOT routed signoff.** The decoded density-0.35 V296 repair remains rejected.

Source: [hosted replay #40456767609](https://github.com/sushxnthd/vektor/actions/runs/40456767609), original routed physical run [#40427986118](https://github.com/sushxnthd/vektor/actions/runs/40427986118). The pinned OpenROAD run returned exit code zero for both reconstructed STA invocations, printed the original worst slacks exactly to six decimal places, and printed one complete named setup/hold path each. The hosted *parser* then rejected those logs because it expected `slack (VIOLATED) <value>` while the actual binary prints `<value> slack (VIOLATED)`. Thus **the hosted checker verdict for this run is failure**; this report is an independent read-only audit of the raw path logs, not a claim that the hosted checker passed. A corrected parser has been committed and requeued.

| Extracted metric | V296 pairwise | Optimized serial onehot |
|---|---:|---:|
| Worst setup slack | -220.829 ps | -711.405 ps |
| Worst hold slack | -10.023 ps | -13.032 ps |
| Setup startpoint | `_13159_` | `_13099_` |
| Setup endpoint | `_13098_` | `_13046_` |
| Setup timed cell-pin rows | 80 | 80 |
| Setup buffer-pin rows | 35 | 23 |
| Longest consecutive setup buffer chain | **15** | **2** |
| Incremental delay across that chain | **358.260 ps** | **56.041 ps** |
| Worst hold startpoint | `rf_write_data[3]` | `rf_write_data[3]` |
| Worst hold endpoint | `_13026_` | `_12878_` |

The 15-buffer sequence on V296 runs from `wire299/Z` through `wire275/Z`, and the path time rises from 1.454786 ns immediately before the sequence to 1.813046 ns after it. The 358.260 ps figure is **path incremental time through this chain**, including modeled parasitic effects, not a counterfactual saving if buffers were deleted. Removing the chain would alter loads, slew, placement, and electrical behavior. The optimized serial implementation has a much shorter consecutive buffer chain on its own worst setup path, but its overall setup slack is worse, so the chain alone cannot explain the relative timing advantage.

**Falsification of the previous uncertainty:** The 15-buffer topology observed pre-CTS also appears on V296's *extracted routed worst setup path*, not merely on an early timing estimate. However, the routed DEF's synthesized instance names have not yet been mapped to source-level scheduler/RF registers. Therefore a scheduler-to-operand-capture *source attribution* is still unproven. The single-path diagnostic also does not characterize other near-critical paths.

Independent reproducibility: [SHA-pinned path auditor](https://github.com/sushxnthd/vektor/blob/research/v296-pairwise-bank-conflict/research/v296/v296_postroute_topology_independent.py) accepts the two failed-parser ZIPs (artifact IDs `12713255529`, `12713435714`) and checks SHA-256, completed OpenROAD marker, named path, exact slack against original within 1 ps, buffer chain, and endpoint. The checker was executed locally against both ZIPs; deliberate ZIP corruption was rejected. Machine-readable measurements are in [JSON](https://github.com/sushxnthd/vektor/blob/research/v296-pairwise-bank-conflict/research/v296/V296_EXTRACTED_WORST_PATH_TOPOLOGY_20261027.json). Hosted execution of the independent auditor remains outstanding.

**Next physical intervention gate:** first map `_13159_` and `_13098_` back to the synthesized netlist and verify the fanout/load and logic function of the 15-buffer chain. Freeze a single candidate topology intervention, compare against the strongest equal-resource serial baseline at identical clock/RC and area constraints, and reject any intervention that fails setup +50 ps, hold >=0, capacitance=0, slew=0 and zero DRC. No speedup, power, or RTX-5090-equivalence claim is supported.

## Source-level attribution resolved from original synthesized netlists

An independent [SHA-pinned synthesized-netlist mapper](https://github.com/sushxnthd/vektor/blob/research/v296-pairwise-bank-conflict/research/v296/v296_extracted_path_netlist_map.py) was run against **both original physical-design artifact ZIPs** (pairwise ID `12703514184`, serial ID `12703682763`). Both ZIPs matched their frozen SHA-256 hashes. Each extracted worst-path flop instance occurred exactly once in the original synthesized Verilog, with the following clocked Q-net mapping:

| Extracted setup path | Source flop Q net | Destination flop Q net |
|---|---|---|
| V296 `_13159_ -> _13098_` | `candidate.issue.scheduler.rr1[2]` | `staged_operand_data[1][3]` |
| Serial `_13099_ -> _13046_` | `strongest_serial.issue.scheduler.rr1[2]` | `staged_operand_data[2][3]` |

Both source and destination are positive-edge DFFR cells clocked by `clk`. This **resolves the earlier uncertainty**: the extracted worst setup paths really are scheduler round-robin state to staged operand capture, not an unrelated netlist cone. It does not prove the 15-buffer sequence is removable, nor that its 358.260 ps can be recovered. The serial path has a different operand-data endpoint, so its lower chain count cannot be interpreted as an isolated treatment effect.

**Falsifiable next intervention:** retain the single V296 bank-conflict mechanism, but test a scheduler-to-operand-select critical-cone refactor only after extracting the intervening combinational logic and confirming functional/cycle equivalence. Freeze equal-resource serial, routed 3.5 ns/2x RC, setup +50 ps, nonnegative hold, zero cap/slew/DRC, area, and workload constraints. No physical pass has been established.

## Final hosted reconstruction verification

[Corrected hosted replay #40457095368](https://github.com/sushxnthd/vektor/actions/runs/40457095368) **PASSED both matrix jobs** with the pinned OpenROAD binary. The corrected fail-closed checker reports `POSTROUTE_REPLAY_REPRODUCED` for V296 and serial. Both setup/hold values match the original physical run to six decimal places, and the first named setup/hold path matches each corresponding worst slack.

- V296 success artifact ID `12713390928`, ZIP SHA-256 `a6914eab364dd99d8ec9c210b1062fea87d91ab048c06147d29298e47d37da86`, path-log SHA-256 `b934128e8ce87d8a054cc9cbc17f99c78ec74144bf81388b15619bdf61b021d2`.
- Serial success artifact ID `12712433839`, ZIP SHA-256 `c524929aec08b99e7691a2a3382b9c384b0160d15fc377b7d1aad27faa41ad43`, path-log SHA-256 `63e08dfd142590c8b3e5f068c40e0cb5feba87c1b0748b02cfd2b67e5648a5e3`.

Both successful path-log byte streams were independently compared with the previously downloaded failed-parser ZIPs and found **byte-for-byte identical**. The prior failure was therefore strictly a parser incompatibility, not a changed STA result. The SHA-pinned independent topology auditor's conclusions transfer to the hosted-verified logs without modifying the measured paths. The 15-buffer V296 chain and scheduler-to-staged-operand source mapping are now supported by exact hosted replay, independent log analysis, and SHA-verified original synthesized netlists.

**Physical verdict remains FAIL:** V296 setup -220.829 ps, hold -10.023 ps, three capacitance violations; serial setup -711.405 ps and hold -13.032 ps. This is a reproducible diagnosis, not a recovered GPU architecture win.
