# ARCHITECTURE — V198

Decision: V151 remains the FP32 integration baseline. Do not adopt V153 from the unplaced V156 slack numbers. The V196 one-level buffering repair has only direct-pin max-cap qualification; it does not include wire parasitics, slew, placement or a full timing sweep.

New quantified robustness boundary: at 0% buffer headroom, an additional uniform 0.01073 fF per load pin is enough to reintroduce a cutset max-cap violation, versus 0.01223 fF/pin for control. At 30% headroom, the corresponding symbolic limits are 0.62726 and 0.72866 fF/pin. These are *parameterized stress values*, not extracted interconnect estimates.

Architecture threshold remains >=10% integrated tile timing/throughput improvement, <=5% mapped area penalty, no workload class >5% regression, and fully qualified max-cap/max-slew checks. Not met.

Next action: run repaired, matched seven-point OpenSTA timing with electrically fail-closed CI; then integrate Wave32 RF arrival distributions. Do not spend further runs on purely abstract buffer thresholds without a new discriminator.
