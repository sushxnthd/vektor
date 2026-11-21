# V317 dual-write-port completeness: RTL falsification and matched generic cost (2026-11-01)

**Decision: integration correctness PASS under a complete two-port write stream; architecture-performance claim remains NO-GO.** This is a bounded extension of the V317 evidence instrument on draft PR #34, not a newly promoted GPU mechanism.

## Prospective evidence chain

1. Frozen protocol: [FROZEN_DUAL_WRITE_PORT_COMPLETENESS_20261101.md](FROZEN_DUAL_WRITE_PORT_COMPLETENESS_20261101.md) committed at `0d908c4`, **before** dual-port RTL, the exhaustive checker, or the physical-width sweep.
2. New synthesizable RTL: [dual_write_forwarding.sv](rtl/dual_write_forwarding.sv), with independent per-port identity comparisons, live same-cycle union hazards, sticky per-lane dirty state, and coverage-fault poisoning.
3. Independent two-lane semantic checker: [dual_write_audit.py](dual_write_audit.py) and [test_dual_write_audit.py](test_dual_write_audit.py). **1,024** exhaustive captured/requested/write-mask/namespace worlds; **63** unsafe admissions when a one-port observer is incorrectly attached to a two-port RF, **zero** with both ports completely observed. This is an integration counterexample; the original one-port RTL never claimed two-port completeness.
4. Independent RTL simulation: [tb_dual_write_forwarding.sv](rtl/tb_dual_write_forwarding.sv), **393,225** Icarus checks, including all **65,536** four-lane capture/request/write0/write1 mask combinations, same-cycle and sticky hazards, namespace isolation, concurrent capture/write, fail-closed coverage and an explicit stale-grant witness against the incomplete one-port integration.
5. Hosted source-pinned RTL/synthesis run [#41261239144](https://github.com/sushxnthd/vektor/actions/runs/41261239144) **PASSED** on `094815f`. [Independent netlist parser](rtl/parse_dual_write_scale.py) verified log-to-netlist cell counts, storage, generic logic depth and fanout. Raw Yosys JSON/logs and machine-readable summary are archived in the run artifact.

## Matched generic-Yosys implementation sensitivity

Same tool version, lane widths, identity widths, snapshot storage and `synth -flatten` settings. **The one-port design is an intentionally incomplete integration control for a two-port RF, not a functionally equivalent strong baseline.** The comparison measures the added cost of observing a second physical write source, not an architecture area win.

| Lanes x bits | One-port cells | Complete two-port cells | Additional cells | Flops (both) | Generic depth one/two | Max generic fanout one/two |
|---|---:|---:|---:|---:|---:|---:|
| 4 x 8 | 219 | 278 | +59 (+26.94%) | 50 | 12 / 12 | 53 / 52 |
| 8 x 16 | 591 | 694 | +103 (+17.43%) | 158 | 13 / 14 | 161 / 160 |
| 32 x 32 | 3,650 | **3,909** | **+259 (+7.10%)** | 1,107 | **14 / 17** | **1,110 / 1,109** |

The 32-lane dual-port implementation adds **three generic logic levels** and still has a **1,109-sink maximum generic-net fanout proxy**. Neither generic depth nor fanout is a routed delay, cap/slew violation, extracted RC, silicon area, power or measured clock-frequency penalty. The writeback-source wiring, multiport event delivery, coherent capture interface, CDC, timing constraints and physical routing are not integrated. Fanout can change after buffering/placement.

## Exact scope and negative result

A complete observer of both physical write ports can prevent stale forwarding caused by either visible port under the frozen coherence/capture assumptions. If either write event is dropped while `coverage_ok` incorrectly stays high, **no local logic can infer the missing write**; the prior information-theoretic no-go still applies. A trusted coverage source and its physical distribution are not implemented.

The strongest equally informed reuse-aware baseline receives the same two write streams, snapshot and coverage authority and can make the same safe forwarding decisions. **Incremental modeled register-read saving = 0**. There is therefore no positive GPU throughput law, no validated candidate speedup, and no reason to promote V317 forwarding as a novel architecture. A naive one-port control is not a legitimate speedup baseline.

V296's prior routed physical no-go and V287's historical retirement are unchanged. Kernellum PR #119 and its holdouts were not modified. No RTX-5090 equivalence is claimed.

## Reproduction

```bash
python -m unittest research.v317.test_dual_write_audit -v
python -m research.v317.dual_write_audit
iverilog -g2012 -s tb_v317_dual_write_forwarding -o /tmp/v317_dual \
  research/v317/rtl/forwarding_gate.sv \
  research/v317/rtl/stateful_forwarding.sv \
  research/v317/rtl/coverage_forwarding.sv \
  research/v317/rtl/dual_write_forwarding.sv \
  research/v317/rtl/tb_dual_write_forwarding.sv
vvp /tmp/v317_dual
# The source-controlled workflow also runs matched Yosys width sweeps.
```

**Next hard gate:** do not invest further in V317 forwarding without an *incremental* physically implementable benefit against an equally informed, multiport reuse-aware control. Dynamic register-bank and write-event traces, matched standard-cell timing, routed wire/load sensitivity, occupancy/bandwidth and actual workload throughput are still missing. Preserve the negative result.
