# V317: frozen competent same-policy RF-proxy baseline challenge (2026-11-02)

## Lineage and non-retroactivity
This is a **new prospective challenger** to the sole V317 pairwise bank-credit implementation on `research/v317-sass-provenance-gate` / draft PR #34. V317's original RF-proxy physical gate (0.825521% saving, electrically illegal) and its 0.15/0.35 density-repair failures remain **failed**. This experiment cannot amend, rescue, or erase those outcomes. V287 and V296 remain historical, not revived.

## Why this control is required
The existing comparison uses `rtl/vtile/rf_bank_arbiter.sv`, whose serial 16-bit occupancy masks are a poor implementation-quality control. A previously verified, *exactly grant-equivalent*, compact fixed-priority greedy implementation exists in V309 at `rtl/vtile/compact_greedy_arbiter.sv` (Git blob `38a1423b3a5de1086438784e8627dfca976c4804`), with 260 generic cells versus 1,321 for the original under V309's matched Yosys mapping. That prior **isolated** result is motivation, not evidence of the new integrated route.

## Frozen experiment, before RTL and routing
- Copy the exact V309 compact greedy RTL into V317 as an independent, third **baseline**, without altering the existing source/pairwise modules or their RTL, RF storage, issue policy or timing constraints.
- Test three variants: historical source, active pairwise, and **compact same-policy greedy**. All must produce cycle-exact identical grant masks, issued wave IDs, RF operand data, and bank-port overflow status on at least 4,096 deterministic directed/random cycles, with no bank oversubscription.
- Route all three with the *same* pinned `openroad/orfs@sha256:9bd99a4657f491615a5a516a8de3352f8b82013a7d0788e0b244c233efd9f5b8`, Nangate45, ABC_AREA=1, 3.000-ns clock, 0.100-ns uncertainty, 10-fF output load, 240x240-um die / 8..232-um core, placement density add-on **0.35**, same flop-mapped 16-bank 2R proxy, and identical sinks. No selective tuning or variant-specific constraints.
- Preserve all routes, mapped cells, logs, extracted RC, wire, power proxies, violation counts and failures. A route exit code of zero is **not** electrical signoff.
- Do not substitute the source/compact 2026-10-31 isolated mapping numbers for new integrated physical measurements.

## Prospectively locked predictions and falsifiers
1. **Functional equivalence/no service gain:** all three are same-policy and must issue identical grants and operand data; intrinsic equal-clock issue throughput ratio **1.000000x**. Any mismatch is a correctness failure, not a speedup.
2. **Predicted raw area no-win:** pairwise will save **less than 2.0%** total routed RF-proxy standard-cell area against compact greedy, including the possibility compact is smaller. This is falsified if the pairwise route saves >=2.0% relative to compact, irrespective of electrical legality; record the raw comparison separately.
3. **Legal material-win gate:** pairwise can be retained as a material RF-proxy implementation optimization **only if both compact and pairwise** meet zero setup/hold/capacitance/slew/fanout/DRC violations, nonnegative setup/hold slack, and pairwise routed area <=0.98 times compact routed area. Otherwise no legal material win. If any required report is absent, report **UNKNOWN/FAIL**, never pass.
4. **Strong-baseline decision:** if compact is no larger than pairwise, pairwise is **dominated on raw area**; if compact is electrically legal and pairwise is not, pairwise is **dominated on legal implementation**. A raw area win with electrical failure is not a physical win.
5. **Positive-law boundary:** identical grants, read ports, bank traffic, occupancy and bandwidth impose `G_service=1` at fixed frequency. A hypothetical area-reinvestment gain requires a discrete additional tile *and* nonlimiting bandwidth/occupancy; no such tile is implemented here. If compact eliminates the area saving, reject even that hypothetical interpretation.

## Evidence tiers and next gate
This is a **flop-mapped tiny RF proxy**, not SRAM macro, GPU tile, measured GPU IPC or RTX 5090 equivalence. Regardless of outcome, physical multi-corner, real RF SRAM, datapath and workload validation remain missing. Keep negative evidence. The only purpose is to challenge V317 against the strongest already-known same-resource/same-policy implementation rather than an unoptimized source.
