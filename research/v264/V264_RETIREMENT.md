# V264 retirement — 2026-10-21
E1 software-model evidence only. No RTL simulation, synthesis, Liberty electrical checks, or STA.
Bottleneck law: D_eff=D(1-p/2), ideal RF-service gain 1/(1-p/2), with clock retention r requiring r>1-p/2.
Mechanism: 1R bank, two collectors, identical (warp,register,epoch,address) read fusion, one physical read and two destinations.
Strongest equal-resource control: conventional bank-output broadcast with the SAME comparator, two outputs, read port, fanout, flops and wire load. RTL instantiates the same module for both.
Frozen seeds, 8192 operands each:
positive 264101: 2252 reads saved, 5940 physical reads, 27.49% reduction, 1.379x RF-service gain vs oldest, 1.000x vs matched;
negative 264102: 42 reads saved, 8150 reads, 0.51% reduction, 1.005x vs oldest, 1.000x vs matched;
divergent 264103: 653 intervening writes, 658 reads saved, 7534 reads, 8.03% reduction, 1.087x vs oldest, 1.000x vs matched.
Independent grouping oracle and value comparisons passed; exhaustive control truth table 16384/16384 passed.
Wire proxy C=0.2+load multiplier gives 0.7/1.2/2.2 at 0.5/1/2x, same for candidate and matched; hypothetical cap 1.5 would fail at 2x, NOT an electrical check.
Physicality: software model PASS; RTL authored but not simulated; synthesis/STA/real power NOT RUN. Area/timing/energy deltas vs matched are zero by construction, not measured silicon PPA.
Prior art: CORF (ASPLOS 2019, doi:10.1145/3297858.3304026); BOW (MICRO 2020, doi:10.1109/MICRO50266.2020.00084).
Decisive falsification: same hardware and same grants as matched broadcast. Retire V264. No V-Tile changes; V153/V156 remain electrically disqualified.
Frozen generator SHA256 94c8ba2d7d1b06b522c6af96f9a1c2aa13f92f0f1cf6a23d84955cf14f42f049; full run source, logs and hashes in conversation archive vektor264_retirement_v265_frozen_2026-10-21.zip.
