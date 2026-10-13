# V153 SCIENCE

Active question: Can a registered signed-accumulation cutset improve area-normalized FMA clock rate without loss of bit-exactness or throughput?

Frontier: V151 24,220 RTL oracle passes, 14,459 generic cells and 383 generic logic levels; V152 balanced LOD 19,981 cells and 439 levels, rejected. These are not mapped PPA.

Objective: minimize max mapped stage delay times mapped area at one result/cycle, subject to bit-exact RNE and flags, with workload throughput and latency measured.

Equal-resource baseline: V151 plus matched two-entry elastic buffering, same lane count, library and clock constraints. External CVFPU/HardFloat matching FMA precision and pipeline depth required for competitive claims.

Mechanism: split after signed alignment/accumulation, before leading-one detection and rounding. Prediction: max generic stage depth below 383; steady-state one result/cycle; +1 latency cycle and 138 bits/lane intermediate state. Dependent chains may lose.

Falsification: any numerical/tag mismatch or no mapped area-normalized throughput gain. Publishable threshold: genuinely novel mechanism, >=5% improvement versus strong open matched baseline with independent reproduction, holdouts and uncertainty. Architecture threshold: >=10% mapped Fmax at <=10% mapped area cost, <=5% dependency-heavy end-to-end slowdown.

Kill: three substantive runs without mapped improvement or new regime boundary. Wildcard: ~10% of probes vary dependency length and stall bursts. Evidence class: RTL candidate; mapped timing and novelty not established.

Build progress is separate from scientific evidence.
