# V270 — sole active kernel: asymmetric dual-warp lane packing
Status: E1 hypothesis, no breakthrough. V269 retired. FP32 V153/V156 electrically disqualified.
Bottleneck law: for two compatible precollected warps, 8 physical lanes can retire 2 warp-instructions per issue cycle if active-lane counts fit a supported partition. T=r*(1+p_pair), with clock retention r. This is not GPU throughput.
Mechanism: support 4+4 and 6+2/2+6 partitions in one eight-lane execution datapath, preserving source-warp and lane-index tags. No extra register ports or execution lanes assumed.
Controls: fixed 4+4 and fully flexible 0..8 lane compaction, same two input collectors and 8 physical lanes. Strongest flexible control matches V270's positive throughput; a real win requires physical PPA superiority at equal throughput and matched resources.
Win boundary: compatible 6+2: fixed=1, adaptive=2, flexible=2; 5+3: fixed=adaptive=1, flexible=2; 4+4: all=2. Adaptive wins vs control c only if r_a/r_c > (1+p_c)/(1+p_a), or energy/area Pareto dominates at matched throughput.
Smallest RTL: combinational 8-lane compactor with three parameter modes. Test all lane payloads and tags with random masks. Synthesis and Nangate45 mapping are proxies, not signoff.
Metrics: useful lane ops/cycle, warp-instructions/cycle, collector traffic, mapped area, delay, switching, max-cap/slew, 0.5x/1x/2x wire assumptions.
Falsification: corrupt lane identity, equal-budget flexible control dominates, or no physical advantage after wire/load and collector-stall sensitivity. One repair then pivot.
Frozen unopened holdouts: positive seed 270101 (6+2), no-win seed 270102 (5+3), divergent seed 270103 (mixed opcode); generator SHA256 9a02c887f3f3616097377c3229daf159fae9c97963f138b8bff1be988b114217. Lock PPA prediction before opening.
Consequence: no integrated tile change unless physical PPA and unseen directions pass. Prior art: Fung et al. MICRO 2007 dynamic warp formation; Wald HPG 2011 active thread compaction; Lashgar et al. arXiv:1208.2374 dynamic warp resizing. Novelty unestablished.
