# V317: prospective 4/8/32-lane forwarding RTL synthesis sensitivity (2026-11-01)

**Decision: no architecture promotion.** This run adds real synthesizable RTL and source-pinned generic logic scaling, but it does not establish a novel equal-resource GPU improvement. The proposed forwarding predicate is a correctness primitive available to a strong reuse-aware baseline.

## Preregistration and reproducibility

The [frozen width-sensitivity protocol](FROZEN_FORWARDING_WIDTH_SENSITIVITY_20261101.md) was committed at `8326fe5` before the 8x16 and 32x32 synthesis outcomes. The implementation, reproducible Yosys sweep, JSON fanout parser and workflow were committed at `7fe7249`.

**Source-pinned evidence:** [push-triggered CI #41248977891](https://github.com/sushxnthd/vektor/actions/runs/41248977891) passed. Its archived `commit.txt` contains exactly `7fe72493c34111b102317903001900c3f81edd62`. The corresponding [PR CI #41248980996](https://github.com/sushxnthd/vektor/actions/runs/41248980996) also passed but checked out a synthetic merge commit, so the push artifact is the canonical branch-head evidence. Independent simulator, RTL regression and V317 lexical/semantic workflows also passed at the same source head.

Reproduce with GitHub-hosted `iverilog` and Yosys 0.33:
- `python -m unittest research.v317.test_freshness_gate -v`
- `python -m research.v317.freshness_gate`
- `iverilog -g2012 -s tb_v317_forwarding_gate -o /tmp/v317_tb research/v317/rtl/forwarding_gate.sv research/v317/rtl/tb_forwarding_gate.sv && vvp /tmp/v317_tb`
- `bash research/v317/rtl/synth_scale.sh`
- `python research/v317/rtl/parse_scale.py build/v317`

## Frozen synthesis results

| Lanes x data bits | Output data bits | Generic cells | Longest logic path (levels) | Maximum generic net fanout | Forward-grant net fanout |
|---|---:|---:|---:|---:|---:|
| 4 x 8 | 32 | **72** | 10 | 8 | 4 |
| 8 x 16 | 128 | **200** | 11 | 16 | 8 |
| 32 x 32 | 1,024 | **1,250** | 12 | 32 | 32 |

The preregistered directional prediction that generic cells increase with data width survived. No exact count or fanout was used to tune the design before the sweep. Yosys `synth; stat; ltp -noff; write_json` produced the data; the independent parser counts input loads of generic mapped gates. No source buffers, pipeline registers, tag arrays, dirty-bit state or invalidation broadcast are synthesized in this isolated module.

**Physical consequence:** the width-scaled masked data path is not free. The 32-lane/32-bit instantiation has 1,250 generic cells and a 32-load grant net *before* placement, buffering or wire extraction. This is not a standard-cell area estimate, actual capacitance, routed delay, switching energy or electrical signoff. The true cost can be higher after complete buffer and hazard-monitor integration. The gate is combinational; the synthesis result is not a complete GPU collector.

## Functional and strong-baseline gates

[Prior frozen freshness result](FORWARDING_FRESHNESS_RTL_RESULT_20261101.md) found 12,160 wrong-value admissions by name-only forwarding among 46,464 legal small-domain worlds; conservative admission had zero unsafe admissions under the complete-write-monitor assumption. Hosted Icarus simulation passed 4,102 cases, including all 4,096 four-lane mask triples and directed identity controls.

The same warp/register/bank, lane coverage and freshness predicate can be implemented by an equally informed reuse-aware baseline. **The incremental modeled transaction advantage is exactly zero**; generic synthesis does not rescue architectural novelty. No realistic dynamic RF-bank traffic, matched full-collector RTL, PDK timing, wire parasitics, power, workload-level speedup or RTX 5090 equivalence is claimed.

## Next decisive gate

Stop further abstract forwarding-speedup claims. Obtain provenance-verified dynamic instruction/register demand, implement the complete write-observing collector path, and compare it against the strongest same-information baseline with matched storage, ports, wiring and clock. If the gain disappears at any of those gates, preserve the negative result and retire the candidate.
