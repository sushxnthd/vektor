# V309 prospective falsification: sector counts do not identify line-fill traffic (2026-10-30)

**Branch/PR:** continue the single existing V309 qualification branch and draft PR #26. No hardware mechanism is promoted. This protocol is committed *before* the executable experiment and its results.

## Fixed hypothesis and counterexample construction

The existing V309 conditional sector roofline uses the audited number of 32-byte sectors as if each sector were 32 bytes of bottleneck service. Its arithmetic is internally correct **under that explicit assumption**. Test the stronger, potentially invalid inference that the same (I, S_baseline, S_candidate) determines memory traffic or the sign of a speedup.

Construct two deterministic 64-instruction synthetic trace families, each with exactly four unique 32-byte sectors per instruction before a hypothetical address/layout change and three after it. Both have I=64, S_base=256, S_changed=192, and the same r_sector=25%.

- **Same-line/reuse:** baseline sector addresses [0,32,64,96], candidate [0,32,64], repeated each instruction. All sectors belong to the same 128-byte aligned cache line.
- **Distinct-line/stream:** instruction i uses four sectors [512i,512i+128,512i+256,512i+384], candidate retains the first three. Each sector is in a different, never-reused 128-byte line.
- Use a *hypothetical* fully associative, write-allocate-free, demand-only LRU cache of 4 lines, initially empty, with 128-byte line-fill transfers. Count line fills (not V100 hardware transactions). Simulate baseline and changed traces independently with cold caches.
- Fix conditional issue ceiling P=1 instruction/cycle, hypothetical line-fill service B=8 bytes/cycle, and candidate issue-time penalty h=5%. Define throughput I/max(I/P, 128*line_fills/B), and candidate issue time I*(1+h)/P.

## Preregistered predictions

Both families must have identical (I,S_base,S_changed), yet:
1. Same-line/reuse: baseline and changed both generate exactly one 128-byte line fill; conditional gain = -1/21 (-4.7619%) because issue time dominates.
2. Distinct-line/stream: baseline generates 256 line fills, changed 192; conditional gain = +1/3 (+33.3333%) because fill service dominates.
3. The prior sector-only model at B=8, P=1, r=25%, h=5% predicts +1/3 for *both* families, and therefore cannot determine the sign of the hypothetical cache-line throughput change.
4. Equal-resource unchanged-address ideal coalescer (candidate identical to baseline) cannot reduce line fills in either family.
5. Independent reference oracle must reproduce all line-fill counts on a finite grid of tiny synthetic traces, and the experiment must reject malformed addresses/parameters.

## Interpretation and kill criterion

This is an *identifiability falsification*, not a measured cache result, new GPU architecture, or real layout transformation. 128-byte fills are an explicit counterfactual assumption; actual GPU caches may use sector fills, writeback, replay, reuse, and different hierarchy policies. If the counterexample passes, **kill any inference from V309 aggregate sector counts alone to actual memory traffic or achieved throughput**. Require independently validated cache/traffic behavior, per-workload/phase inputs, occupancy/MLP, and matched hardware counters before promoting a new architecture. The synthetic families are not unseen application holdouts. Retain all prior negative evidence.
