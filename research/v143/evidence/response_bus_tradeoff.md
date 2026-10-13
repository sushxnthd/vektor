# V143 exploratory response-bus tradeoff — 2026-10-13

This experiment was designed **after** observing the first Yosys coalescer synthesis result. It is an exploratory architecture discriminator, not preregistered confirmation or a novel architectural law.

## RTL and generic synthesis
- Commit f36ac1b3985ff3816955d87e6f9f50a5500eec36
- GitHub Actions run: https://github.com/sushxnthd/vektor/actions/runs/38381219776 — PASS
- CI artifact: https://github.com/sushxnthd/vektor/actions/runs/38381219776/artifacts/11802898884
- Independent abstract checker: 3456 PASS.
- 3-response 32-lane coalescer: 800 RTL vectors PASS; **9286 Yosys generic cells, 6144 muxes, 12-cell topological path**.
- 3-response passthrough: **6 generic cells, 1-cell path** (not equal RF traffic/functionality).
- 1-response tagged-bus, valid-only multicast: 800 RTL vectors PASS; **81 generic cells, 7-cell path**.
- Cell counts are generic synthesized logic, not mapped area; path lengths are logic-depth proxies, not frequency. Single-bus design has 1/3 of the response-vector bandwidth of 3-input design, before considering arbitration.

## Cycle-model response-serialization probe
Synthetic one-lane-representative FP32 FMA cycle model with 16 RF banks, 4 waves, 8 collectors, issue width 4, two FMA cycles. 3 workload shapes k/n=(6/48,9/56,13/80), source multiplicity 1/2/3, ports/bank 1/2, RF latency 1/3, response bus widths 1/2/3/4/8/unlimited, interleaved/grouped schedules. **432 modeled runs** (36 resource/workload configs x 6 widths x 2 schedules). Best schedule chosen independently for each width. **72/72** unlimited-width metamorphic comparisons match the original model's cycles, RF reads and final registers. All configurations complete with final FP32 register-state checks.

Mean modeled slowdown of 1-response bus vs unlimited response bandwidth:
- all-distinct FMA sources: **3.5836x**, max 5.5287x; 3-response bus mean 1.2362x.
- two equal sources: **2.9544x**, max 3.963x; 3-response bus mean 1.2201x.
- three equal sources: **1.4856x**, max 1.9877x; 3-response bus mean 1.0x.

Representative k=9,n=56,ports/bank=2,RF latency=1,4 waves,8 collectors, no forwarding, coalescing enabled:
| Source multiplicity | One bus cycles | Three bus cycles | Unlimited cycles |
| --- | ---: | ---: | ---: |
| 1x | 674 | 226 | 126 |
| 2x | 450 | 164 | 114 |
| 3x | 226 | 114 | 114 |

**Consequence:** replacing the 3-vector response network with a single ungated tagged vector eliminates thousands of generic muxes but induces substantial modeled response serialization for broad source patterns. Neither topology dominates in a proven physical PPA/throughput Pareto sense. The 1-bus variant is rejected as an unconditional replacement, retained as a workload-specific hypothesis.

**Limitations:** one representative FP32 lane per wave, synthetic dependency chains, not real kernel suite; generic gates omit RF SRAM, physical wiring and dynamic power; no mapped standard-cell area or critical-path timing; independent C++ checker applies to prior no-response-cap model, while this new response-cap model has metamorphic cross-checks only. Full executable models and raw tables are in the V143 local evidence package.

**Next discriminating test:** bank-local multicast with limited (e.g. 2-4) physically independent response vectors and registered capture, benchmark GEMM/reduction/stream traces, synthesize the integrated collector+FP32 datapath.
