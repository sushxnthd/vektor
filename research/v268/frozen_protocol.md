# V268 frozen protocol — live-lane sector-isolated RF read
E0 hypothesis. Sole active kernel after V267 retirement. No measured energy, timing or throughput advantage.

1. Bottleneck law: 32-lane RF word split into S=4 independently read-enabled 8-lane sectors. For active mask m, a(m)=number of sectors with >=1 active lane. Delta read energy=(4-a)*E_sector - E_decode - E_wire - E_enable. Fractional saving=1-(a+h)/4 where h=overhead/E_sector.
2. Mechanism: use existing SIMT lane mask to disable physically separate RF sector read wordlines, zero-fill inactive outputs. Same 1R1W, storage capacity, bank count, no new buffers.
3. Equal-resource controls: full-width RF with post-read masking; independently sector-clock-gated RF with same enables, area and ports. If second control matches physically, retire as non-novel.
4. Boundary: illustrative h=0.4: a<=3 yields positive read dynamic energy, a=4 loses. Require retained clock >=0.98, no area/throughput regression for Pareto. No assumed h or r may support a claim.
5. Smallest RTL: 16 words x 32 lanes x 32 bits, four 8-lane read-enabled arrays vs full-width baseline; verify simultaneous read/write, masks, version semantics. Generic RTL enable is NOT SRAM bitline proof.
6. Physical gate: independent functional checker, RTL simulation, synthesis, characterized macro or explicit flop-array implementation, clean max-cap/slew, matched STA/area/toggle under 0.5x/1x/2x wire/load, workload traffic. Kill/pivot after at most two substantive physical-repair runs.
7. Workloads: compute-bound full masks; RF-bound clustered live lanes; memory-bound stalls; divergent sparse masks with four-sector coverage. Metrics: active sector fraction, toggles, energy, IPC, bank stalls, area and Fmax.
8. Falsify if equal-budget sector gating matches, power saving disappears, no physical isolation, wire/timing/area loss, or unseen directions fail.
9. Unseen frozen seeds: 268101 clustered 1..8 live lanes in one sector predicts energy win; 268102 full masks predicts no win/loss; 268103 one lane in each sector predicts no win/loss. Generator SHA256 5b4f07c8d246a7156ad4293c5e0d71f815006edd4659d395aa7da25b0e7fcd5a. Seeds NOT evaluated.
10. Architecture consequence: integrate only after physically credible matched-resource improvement, independent checker, novelty audit and sensitivity. Otherwise retain conventional RF. Prior art: Warped-Compression ISCA 2015; compressed GPU execution TC 2017; SIMT lane clock gating.

V153/V156 FP32 cutset electrically disqualified. RTX 5090-class capability is only a long-range reference.