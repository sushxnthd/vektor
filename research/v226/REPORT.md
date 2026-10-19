# V226 — same-key instruction-fetch multicast (research only)
Date: 2026-10-19. Isolated branch. **Evidence class: analytic + independent Python cycle model; RTL and physical gates pending.**
## Ten mandatory fields
1. **Bottleneck law.** For four wave fetch requesters, two physical instruction-cache read ports F=2 and C=4 per-wave completion slots, with groups of equal (ASID,PC) keys of size g_j, same-cycle eligible fetches are at most min(C,sum_{j<=F} g_j). Unmerged upper bound is min(C,F,ready_waves). Actual throughput benefit requires fetch admission to be the limiting stage; it cannot be inferred from this bound alone.
2. **Mechanism.** Admit first two unique (ASID,PC) requests and broadcast each selected instruction-cache read to every requester with an identical key. Do not merge across address spaces.
3. **Strongest controls.** (A) Same two physical read ports, same four completion slots, conventional oldest-first wave admission. (B) An equal-area PC-aware instruction buffer or existing I-cache broadcast/deduplication, NOT YET IMPLEMENTED. B is required before claiming a new architecture law.
4. **Win/loss boundary.** Win only with >2 ready waves/cycle, substantial identical-key occupancy, and fetch port saturation; no benefit if all keys distinct or dependent-memory/compute/issue limits dominate.
5. **Smallest RTL.** 4 requesters, 2 fetch read ports, combinational key comparisons, wave-to-port map. No added storage; comparator/fanout area and delay must be charged.
6. **Physical proxy.** Generic synthesis cell count and path-depth only until mapped Liberty and electrical STA run; no power inference from reduced reads alone.
7. **Workload metric.** Total wave-fetch admissions/cycle, unique I-cache reads, and total modeled cycles; NOT GPU IPC.
8. **Falsification.** If RTL differs from exhaustive oracle, if max-cap/slew fails, if matched area/timing loses, or if same-budget PC-aware buffering/broadcast matches performance, retire mechanism.
9. **Unseen predictions.** Frozen n=173 coherent (>=90% admission-speedup); n=157 staggered memory, n=149 divergent, n=151 distinct ASID (<=0.1%); n=167 two-PC groups (>=90%). These holdouts were frozen after exploratory n=128 cases; not independent workload families.
10. **Tile consequence.** No integration without proof that Vektor instruction fetch is throughput-limiting, real cache response fanout supports 4 wave deliveries, and area/timing is matched.

## Observed Python-only model (not RTL/STA)
- coherent 173: 346 -> 173 cycles; +100.0% modeled fetch admissions; 692 -> 173 I-cache reads.
- two groups 167: 334 -> 167; +100.0%; 668 -> 334 reads.
- staggered memory 157: 1255 -> 1255; 0.0%.
- divergent 149: 298 -> 298; 0.0%.
- ASID distinct 151: 302 -> 302; 0.0%.
- 768 exhaustive mode-key oracle checks (256 configurations x 3 selectors), 768 RTL vectors prepared but RTL not yet executed.

## Prior-art/novelty
SIMT instruction broadcast, warp fetch buffers and I-cache line sharing are established. AMD's documentation describes shared L1 instruction caches. The proposed same-PC sharing is NOT presented as novel. References:
- https://rocmdocs.amd.com/projects/HIP/en/latest/understand/hardware_implementation.html
- https://www.cse.iitk.ac.in/users/biswap/CASS18/CASS-GPU-CUDA.pdf
- https://arxiv.org/abs/1208.2374
- https://pmc.ncbi.nlm.nih.gov/articles/PMC8537857/

## Invalid shortcuts
No claims about RTX 5090 equivalence, energy, timing closure, complete cache correctness, GPU IPC, or novelty. V153/V156 FP32 remains retired pending electrical repair. Do not merge this branch to main.
