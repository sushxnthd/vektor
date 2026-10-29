# V309: external H200 SASS trace acquisition is over the no-cost CI byte budget

Date: 2026-10-29. **Evidence tier: verified GitHub release asset metadata only. No SASS trace, Nsight Compute data, simulator result, GPU timing, or physical result was downloaded or measured.**

## External provenance and preregistered acquisition constraint

Source: Accel-Sim 2.0.1 release, https://github.com/accel-sim/accel-sim-framework/releases/tag/v2.0.1
- GitHub release ID: `418693044`
- Published: 2026-10-20T17:47:59Z
- Release assets contain per-part byte sizes and SHA-256 digests.
- Analysis is pinned to release ID and tag and fails closed on missing parts, malformed digests, duplicate parts, or unrecognized assets.
- **Conservative automated acquisition cap: 512 MiB of downloaded trace bytes per research run.** This is an internal no-cost resource discipline, not a measured GitHub Actions bandwidth limit. We do not claim GitHub Actions cannot download larger files.
- Target: three distinct workload families with real SASS traces and paired hardware statistics before hardware-candidate promotion. This is a minimum *evidence diversity* requirement, not evidence that those families represent all GPUs.

## Independently auditable release-metadata results

| Metric | Result |
|---|---:|
| Trace configurations | 20 |
| Trace tar parts | 116 |
| Aggregate compressed trace bytes | 208,293,038,080 (208.293 GB decimal) |
| Smallest complete configuration | DLRMv2 inference, 256: 802,283,520 bytes |
| Second cheapest distinct family | Mixtral 8x7B inference, 256_255_1: 878,080,000 bytes |
| Third cheapest distinct family | Llama 3.1 8B inference, 256_255_1: 1,074,974,720 bytes |
| Exact minimum for three distinct families | **2,755,338,240 bytes = 2,627.695 MiB** |
| Configurations within 512 MiB | **0** |
| Three-family acquisition within 512 MiB | **NO** |
| Three-family acquisition within 3,072 MiB | **SIZE-ONLY ELIGIBLE**, not validated |

The three-family minimum is exact for this release's part sizes: each workload family must contribute one complete configuration; selecting the cheapest configuration per family, then the three cheapest families, minimizes the sum. The independent self-test compares that selection against exhaustive combination enumeration and rejects six deliberately corrupted inputs.

## Scientific falsification and implications

The previous proposed next step, to fetch a small complete H200 trace set during a lightweight CI research run, is **not viable under the explicitly frozen 512 MiB transfer cap**: even the smallest complete configuration requires 802 MB. The prior V309 static PTX results cannot be promoted to a measured GPU bottleneck in lieu of traces. A one-part archive is still an entire configuration; downloading only part of a multi-part archive is not valid SASS evidence.

This is an **acquisition-feasibility negative result**, not a negative result about GPU architecture, scheduling, register banks, or the quality of Accel-Sim. Release asset size alone does not establish extracted size, simulator runtime, RAM requirement, or actual kernel coverage. SHA-256 digests were checked for *presence and format*, not recomputed over trace bytes. The release metadata is a mutable external source, not cryptographically frozen evidence by itself. Real H200 behavior must not be presented as RTX 5090 behavior.

## Decision and next physicality gate

Do not download the 208 GB release or silently exceed the no-cost transfer budget. Keep V309's one existing research branch and draft PR as a qualification workstream, with **no promoted hardware mechanism**. To proceed, first locate a separately published genuinely small, authentic SASS trace plus paired hardware counters, or arrange a bounded one-time verified acquisition of the 802 MB DLRMv2 set using already available free resources. Do not fabricate a reduced trace by truncating a multipart archive. Freeze predicted-win and predicted-no-win workload regimes *before* hardware-candidate evaluation.

When genuine dynamic evidence is obtained: quantify measured bottlenecks; compare strongest equal-resource controls; select only one hardware mechanism; then require RTL, synthesis, electrical checks, matched timing/area, traffic and occupancy sensitivity, independent checker, and prospective predictive law. Otherwise do not promote V310.

## Reproduction

```sh
curl -fsSL https://api.github.com/repos/accel-sim/accel-sim-framework/releases/tags/v2.0.1 > release.json
python3 research/v309/release_budget_gate.py --selftest
python3 research/v309/release_budget_gate.py release.json --budget-mib 512
python3 research/v309/release_budget_gate.py release.json --budget-mib 3072
```

No user laptop was accessed. Kernellum PR #119 was not modified. No auto-merge or force-push.
